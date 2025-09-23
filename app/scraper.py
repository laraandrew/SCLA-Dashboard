# app/scraper.py
import requests, re
from bs4 import BeautifulSoup
from typing import Dict, Optional

def _clean(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = re.sub(r"\s+", " ", s).strip()
    return s or None

def parse_listing(url: str) -> Dict:
    # Fetch page
    r = requests.get(url, timeout=20, headers={"User-Agent": "StickerDashboard/1.0 (+github)"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Base record (fields match app.db.Car)
    rec = {
        "year": None,
        "make": None,
        "model": None,
        "vin": None,
        "odometer": None,
        "engine": None,
        "transmission": None,
        "exterior": None,
        "interior": None,
        "stock": None,
        "price": None,
        "url": url,
        "thumb_url": None,
        "status": "OnLot",
    }

    # Thumbnail from OpenGraph (same page’s main image)
    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        rec["thumb_url"] = og_img["content"]

    # EXACT site-specific logic from your working script:
    # Loop over all .elm elements, read <span> label, value = next_sibling text
    for elm in soup.select(".elm"):
        label_tag = elm.find("span")
        if not label_tag:
            continue
        label = (label_tag.get_text(strip=True) or "").lower()
        # The value is usually a NavigableString sibling after <span>
        value = label_tag.next_sibling
        value = _clean(str(value)) if value is not None else None
        if not value:
            # fallback: maybe the value is inside the same node minus the <span>
            value = _clean(elm.get_text(" ", strip=True).replace(label_tag.get_text(strip=True), "", 1))

        if not label:
            continue
        if "year" in label:
            rec["year"] = int(re.sub(r"[^\d]", "", value)) if value and re.search(r"\d", value) else None
        elif "make" in label:
            rec["make"] = value
        elif "model" in label:
            rec["model"] = value
        elif "vin" in label:
            rec["vin"] = value
        elif "miles" in label or "odometer" in label or "mileage" in label:
            if value:
                miles = re.sub(r"[^\d,]", "", value)
                rec["odometer"] = (miles + " mi") if miles else value
        elif "engine" in label:
            rec["engine"] = value
        elif "transmission" in label:
            rec["transmission"] = value
        elif "exterior" in label:
            rec["exterior"] = value
        elif "interior" in label:
            rec["interior"] = value
        elif "stock" in label:
            rec["stock"] = value
        elif "price" in label or "our price" in label or "asking" in label:
            if value:
                rec["price"] = re.sub(r"[^0-9$,.]", "", value).strip() or value

    # If title exposes Y/M/M, try to fill missing pieces
    if not rec["year"] or not rec["make"] or not rec["model"]:
        title = soup.find("meta", property="og:title")
        if title and title.get("content"):
            t = title["content"]
            # Try to grab a 4-digit year and a couple words after
            m = re.search(r"(19\d{2}|20\d{2})\s+([A-Za-z\-]+)\s+(.+)", t)
            if m:
                rec["year"] = rec["year"] or int(m.group(1))
                rec["make"] = rec["make"] or m.group(2)
                if not rec["model"]:
                    # keep model concise
                    rec["model"] = re.sub(r"\s{2,}", " ", m.group(3)).split("|")[0].strip()

    # Final tidy
    for k in ("make", "model", "vin", "engine", "transmission",
              "exterior", "interior", "stock", "price"):
        rec[k] = _clean(rec[k])

    return rec
