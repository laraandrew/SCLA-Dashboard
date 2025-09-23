# app/sticker.py
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode, os

TEMPLATE_PATH = os.environ.get("STICKER_TEMPLATE", "templates/sticker_template.png")

# Try env var first, then common macOS/Linux fonts; fallback to PIL default
CANDIDATE_FONTS = [
    os.environ.get("STICKER_FONT"),
    "/Library/Fonts/Arial Bold.ttf",                       # macOS
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",# Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def load_font(size: int):
    for p in CANDIDATE_FONTS:
        if p and os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except OSError:
                pass
    return ImageFont.load_default()

def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
    """Word-wrap text to fit a max pixel width."""
    if not text:
        return [""]
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = w if not line else f"{line} {w}"
        if draw.textlength(test, font=font) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_text(draw, pos, text, max_width, font, fill="black", line_spacing_ratio=0.35):
    """Draw word-wrapped text starting at pos."""
    x, y = pos
    lines = wrap_lines(draw, text, font, max_width)
    # robust line height
    ascent, descent = font.getmetrics()
    line_h = ascent + descent
    spacing = int(line_h * line_spacing_ratio)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += line_h + spacing

def render_sticker(car) -> BytesIO:
    # Map car fields -> your coordinate layout
    data = {
        "year":           str(car.year or "").strip(),
        "make":           str(car.make or "").strip(),
        "model":          str(car.model or "").strip(),
        "vin":            (car.vin or "").strip(),
        "mileage":        (car.odometer or "").strip(),
        "engine":         (car.engine or "").strip(),
        "trans":          (car.transmission or "").strip(),
        "exterior_color": (car.exterior or "").strip(),
        "interior_color": (car.interior or "").strip(),
        "stock":          (car.stock or "").strip(),
        "price":          (car.price or "").strip(),
        "url":            (car.url or "").strip(),
    }

    # Load template & drawing context
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Fonts
    font        = load_font(28)   # body values
    font_price  = load_font(70)   # price highlight
    font_header = load_font(42)   # header Y/M/M if you want slightly larger

    # ---- ABSOLUTE COORDINATES (tweak as needed) ----
    # (These are the positions you shared.)
    positions = {
        "year": (40, 210),
        "make": (120, 210),
        "model": (330, 210),
        "vin": (130, 290),
        "mileage": (170, 340),
        "engine": (200, 400),
        "trans": (210, 450),
        "exterior_color": (235, 500),
        "interior_color": (235, 560),
        "stock": (225, 620),
        "price": (150, 660),
    }

    # Max text width for wrapped fields (adjust if you need more/less room)
    MAX_W = 300
    MAX_W_PRICE = 400  # give price a little more room if you’d like

    # Header fields (if your template shows blank boxes at the top)
    # If your template already prints "YEAR MAKE MODEL" labels, we just draw values.
    for key in ("year", "make", "model"):
        val = data[key] or "Not Available"
        draw_text(draw, positions[key], val, max_width=MAX_W, font=font_header, fill="black")

    # Body values (labels already on the template)
    for key in ("vin","mileage","engine","trans","exterior_color","interior_color","stock"):
        val = data[key] or "Not Available"
        draw_text(draw, positions[key], val, max_width=MAX_W, font=font, fill="black")

    # Price (red, big)
    price_text = data["price"] or "Not Available"
    # If price is like '48750', add a dollar sign & thousands formatting
    if price_text.replace(",", "").replace("$", "").isdigit():
        try:
            price_text = "${:,}".format(int(price_text.replace(",", "").replace("$", "")))
        except Exception:
            pass
    draw_text(draw, positions["price"], price_text, max_width=MAX_W_PRICE, font=font_price, fill="red", line_spacing_ratio=0.15)

    # QR Code (bottom-left per your example)
    qr_url = data["url"] or "https://example.com"
    qr = qrcode.QRCode(box_size=3, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((100, 100))
    img.paste(qr_img, (40, 650))

    # Return as bytes
    out = BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out
