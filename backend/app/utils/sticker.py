from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

def generate_sticker_text(img: Image.Image, data: dict) -> Image.Image:
    draw = ImageDraw.Draw(img)
    font_large = ImageFont.truetype(FONT_PATH, size=72)
    font_small = ImageFont.truetype(FONT_PATH, size=36)
    draw.text((40, 40), f"${int(data.get('price', 0)):,}", font=font_large, fill=(0,0,0))
    draw.text((40, 130), f"{data.get('year','?')} {data.get('make','')} {data.get('model','')}", font=font_small, fill=(0,0,0))
    draw.text((40, 180), f"{int(data.get('miles',0)):,} mi", font=font_small, fill=(0,0,0))
    return img

def generate_sticker(data: dict) -> bytes:
    img = Image.new("RGB", (1200, 800), (255,255,255))
    img = generate_sticker_text(img, data)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
