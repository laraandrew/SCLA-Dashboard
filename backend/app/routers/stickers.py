# backend/app/routers/stickers.py
from __future__ import annotations

import os
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.car import Car
from app.utils.scraper import scrape_car_detail  # fallback if not in DB

# --- Pillow & QR ---
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:  # pragma: no cover
    raise RuntimeError("Pillow (PIL) is required for sticker generation.") from e

try:
    import qrcode
except Exception as e:  # pragma: no cover
    raise RuntimeError("qrcode package is required for sticker generation.") from e

# ---- paths ----
BASE_DIR = os.path.dirname(os.path.dirname(__file__))         # backend/app
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TEMPLATE_PATH = os.path.join(ASSETS_DIR, "sticker_template.png")

# A reasonably present on macOS; we’ll fallback to PIL’s default if missing.
DEFAULT_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

router = APIRouter(prefix="/stickers", tags=["stickers"])


# ---------- tiny helpers ----------

def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load TrueType font if available; fall back to PIL default."""
    if os.path.exists(DEFAULT_FONT_PATH):
        return ImageFont.truetype(DEFAULT_FONT_PATH, size=size)
    return ImageFont.load_default()

def _fmt_price_for_sticker(price_raw: Optional[str], price_num: Optional[int]) -> str:
    if price_raw and price_raw.strip():
        return price_raw.strip()
    if price_num and price_num > 0:
        return f"${price_num:,}"
    return "Not Available"

def _text_or_na(value: Optional[str]) -> str:
    v = (value or "").strip()
    return v if v else "Not Available"

def _shrink_to_fit(draw: ImageDraw.ImageDraw, text: str, max_width: int, start_font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Return a font that ensures `text` fits in `max_width` (never < 10px)."""
    size = start_font_size
    font = _load_font(size)
    while size > 10:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            return font
        size -= 1
        font = _load_font(size)
    return font

def _generate_sticker_bytes(data: dict) -> bytes:
    """Draw values onto the template exactly per your coordinates and return PNG bytes."""

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(
            f"Sticker template not found at {TEMPLATE_PATH}. "
            "Place 'sticker_template.png' in backend/app/assets/."
        )

    # 1) Load template
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 2) Fonts (base sizes; will shrink for long strings)
    font_small = _load_font(28)
    font_price = _load_font(70)

    # 3) Field coordinates (your exact map)
    # NOTE: these positions assume your provided PNG layout.
    positions = {
        "year": (40, 210),
        "make": (120, 210),
        "model": (330, 210),

        "vin": (130, 290),

        "mileage": (170, 340),          # will append “ mi” below
        "engine": (200, 400),
        "trans": (210, 450),

        "exterior_color": (235, 500),
        "interior_color": (235, 560),
        "stock": (225, 620),

        "price": (150, 660)
    }

    # 4) Box max widths (helps truncate/shrink to fit cleanly)
    #    Adjust if you tweak the template later.
    max_widths = {
        "year": 70,
        "make": 180,
        "model": 320,

        "vin": 680,

        "mileage": 300,
        "engine": 650,
        "trans": 650,

        "exterior_color": 650,
        "interior_color": 650,
        "stock": 650,

        "price": 450,  # big, but keep consistent with visual
    }

    # 5) Normalize data for rendering
    year   = _text_or_na(data.get("year"))
    make   = _text_or_na(data.get("make"))
    model  = _text_or_na(data.get("model"))
    vin    = _text_or_na(data.get("vin"))

    # For mileage on the sticker we want the raw string with “ mi” if numeric available
    mileage_str = data.get("mileage") or data.get("miles")
    if isinstance(mileage_str, (int, float)):
        mileage = f"{int(mileage_str):,} mi"
    else:
        mileage = _text_or_na(mileage_str)
        # if it's only digits and commas, append " mi"
        if mileage and mileage not in ("Not Available",) and any(ch.isdigit() for ch in mileage):
            mileage = f"{mileage} mi"

    engine = _text_or_na(data.get("engine"))
    trans  = _text_or_na(data.get("trans") or data.get("transmission"))

    exterior_color = _text_or_na(data.get("exterior_color"))
    interior_color = _text_or_na(data.get("interior_color"))
    stock  = _text_or_na(data.get("stock"))
    price  = _text_or_na(data.get("price"))

    # 6) Draw with shrink-to-fit for each line (black text except price)
    def draw_line(key: str, text: str, base_font: ImageFont.ImageFont, fill=(0, 0, 0)):
        x, y = positions[key]
        max_w = max_widths[key]
        font = _shrink_to_fit(draw, text, max_w, getattr(base_font, "size", 28))
        draw.text((x, y), text, font=font, fill=fill)

    # FIRST ROW
    draw_line("year", year, font_small)
    draw_line("make", make, font_small)
    draw_line("model", model, font_small)

    # VIN
    draw_line("vin", vin, font_small)

    # LEFT COLUMN
    draw_line("mileage", mileage, font_small)
    draw_line("engine", engine, font_small)
    draw_line("trans", trans, font_small)

    draw_line("exterior_color", exterior_color, font_small)
    draw_line("interior_color", interior_color, font_small)
    draw_line("stock", stock, font_small)

    # PRICE (red, large)
    # Ensure price fits in its box by shrinking if needed
    x_p, y_p = positions["price"]
    max_p = max_widths["price"]
    font_for_price = _shrink_to_fit(draw, price, max_p, getattr(font_price, "size", 70))
    draw.text((x_p, y_p), price, font=font_for_price, fill=(220, 0, 0))

    # 7) QR code at (40, 650) – same as your earlier layout
    url = (data.get("url") or "").strip()
    if url:
        try:
            qr_img = qrcode.make(url)
            qr_img = qr_img.resize((100, 100))
            img.paste(qr_img, (40, 650))
        except Exception:
            # If QR generation fails, skip silently (don’t fail the sticker)
            pass

    # 8) Encode as PNG
    out = BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


# ---------- API ----------

@router.get("/generate")
def generate_sticker(
    url: str = Query(..., description="Car detail URL"),
    format: str = Query("png", pattern="^(png|PNG)$"),
):
    """Create and return a sticker PNG for the listing at `url`."""
    # 1) Try DB
    db: Session = SessionLocal()
    car: Optional[Car] = None
    try:
        car = db.query(Car).filter_by(url=url).one_or_none()
    finally:
        db.close()

    # 2) If not in DB, scrape once on demand
    if not car:
        try:
            detail = scrape_car_detail(url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch detail: {e}")

        payload = {
            "year": detail.get("year") or "",
            "make": detail.get("make") or "",
            "model": detail.get("model") or "",
            "vin": detail.get("vin") or "",
            "mileage": detail.get("miles") or "",
            "engine": detail.get("engine") or "",
            "trans": detail.get("transmission") or "",
            "exterior_color": detail.get("exterior_color") or "",
            "interior_color": detail.get("interior_color") or "",
            "stock": detail.get("stock") or "",
            "price": _fmt_price_for_sticker(detail.get("price"), None),
            "url": url,
        }
    else:
        payload = {
            "year": str(car.year or "") or "",
            "make": car.make or "",
            "model": car.model or "",
            "vin": car.vin or "",
            "mileage": car.miles if car.miles is not None else "",
            "engine": car.engine or "",
            "trans": car.transmission or "",
            "exterior_color": car.exterior_color or "",
            "interior_color": car.interior_color or "",
            "stock": car.stock or "",
            "price": _fmt_price_for_sticker(car.price_raw, car.price),
            "url": car.url,
        }

    try:
        png_bytes = _generate_sticker_bytes(payload)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sticker generation failed: {e}")

    filename_base = (payload.get("stock") or payload.get("vin") or "sticker").replace("/", "-")
    headers = {
        "Content-Disposition": f'attachment; filename="{filename_base}.png"',
        "Cache-Control": "no-store",
    }
    return StreamingResponse(BytesIO(png_bytes), media_type="image/png", headers=headers)