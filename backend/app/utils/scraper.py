# backend/app/utils/scraper.py
from __future__ import annotations
import re
import time
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.db import SessionLocal
from app.models.car import Car

BASE = "https://www.sportscarla.com"
XHR_URL = (
    "https://www.sportscarla.com/isapi_xml.php"
    "?module=inventory&sold=365_days&main=&limit={limit}&orderby=sold&offset={offset}"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
}

# ---------- URL collection (inventory) ----------

def _is_sold(card: BeautifulSoup) -> bool:
    if card.select_one('img.overlay[alt*="Sold" i], img.overlay[alt*="Pending" i]'):
        return True
    price = card.select_one(".price")
    if price and any(x in price.get_text(" ", strip=True).lower() for x in ("sold", "pending", "sale pending")):
        return True
    return False

def _extract_detail_url(card: BeautifulSoup) -> Optional[str]:
    a = (card.select_one(".vehicle_secp a[href]") or
         card.select_one(".hideBox a[href]") or
         card.select_one("a[href]"))
    return urljoin(BASE, a["href"]) if a and a.get("href") else None

def get_all_active_urls(limit: int = 36, max_pages: int = 25, delay_sec: float = 0.25) -> List[str]:
    urls: List[str] = []
    seen = set()

    for page in range(max_pages):
        offset = page * limit
        feed = XHR_URL.format(limit=limit, offset=offset)
        html = requests.get(feed, headers=HEADERS, timeout=20).text.strip()
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.car-col div.item")
        if not cards:
            break

        added = 0
        for card in cards:
            if _is_sold(card):
                continue
            u = _extract_detail_url(card)
            if not u or u in seen:
                continue
            seen.add(u)
            urls.append(u)
            added += 1

        if added == 0:
            break
        if delay_sec:
            time.sleep(delay_sec)

    return urls

# ---------- Detail page scraper ----------

_PRICE_NUM = re.compile(r"[\d,]+")

def _parse_price_to_int(price_str: Optional[str]) -> Optional[int]:
    if not price_str:
        return None
    s = price_str.replace(",", "")
    m = _PRICE_NUM.search(s)
    if not m:
        return None
    try:
        return int(m.group(0))
    except ValueError:
        return None

def scrape_car_detail(url: str) -> Dict[str, Optional[str]]:
    html = requests.get(url, headers=HEADERS, timeout=25).text
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "url": url,
        "year": "", "make": "", "model": "",
        "exterior_color": "", "interior_color": "",
        "stock": "", "vin": "",
        "miles": "", "transmission": "", "engine": "",
        "price": "", "body_style": "",
        "thumb": None,
    }

    # hero image (best-effort)
    hero = (soup.select_one("img#mainImage")
            or soup.select_one(".vehicle-image img")
            or soup.select_one("img.full")
            or soup.select_one("img[src*='imagetag']"))
    if hero and hero.get("src"):
        src = hero["src"]
        data["thumb"] = urljoin(BASE, src) if src.startswith("/") else src

    # Main spec blocks
    for elm in soup.select(".elm"):
        span = elm.find("span")
        if not span:
            continue
        label = span.get_text(strip=True).rstrip(":").lower()
        # try immediate text next to the span
        value = (span.next_sibling or "").strip() if span.next_sibling else ""
        # fallback: full text minus label
        if not value:
            text = elm.get_text(" ", strip=True)
            value = text[len(label):].lstrip(" :\u00A0") if text.lower().startswith(label) else text

        if "year" in label:
            data["year"] = value
        elif "make" in label:
            data["make"] = value
        elif "model" in label:
            data["model"] = value
        elif label in ("vin",):
            data["vin"] = value
        elif "mile" in label or "odometer" in label:
            data["miles"] = value
        elif "transmission" in label:
            data["transmission"] = value
        elif "engine" in label:
            data["engine"] = value
        elif "exterior" in label:
            data["exterior_color"] = value
        elif "interior" in label:
            data["interior_color"] = value
        elif "stock" in label:
            data["stock"] = value
        elif "price" in label:
            data["price"] = value
        elif "body" in label and "style" in label:
            data["body_style"] = value

    return data

# ---------- Persist (upsert) ----------

def _to_int_or_none(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    ss = re.sub(r"[^\d]", "", s)
    return int(ss) if ss.isdigit() else None

def upsert_car(session, detail: Dict[str, Optional[str]]) -> Car:
    """
    Upsert by URL (primary) and prefer VIN/stock if present for updates.
    """
    url = detail["url"]
    car = session.query(Car).filter_by(url=url).one_or_none()
    if not car and detail.get("vin"):
        car = session.query(Car).filter_by(vin=detail["vin"]).one_or_none()
    if not car and detail.get("stock"):
        car = session.query(Car).filter_by(stock=detail["stock"]).one_or_none()

    if not car:
        car = Car(url=url)
        session.add(car)

    # map fields
    car.vin = detail.get("vin") or car.vin
    car.stock = detail.get("stock") or car.stock
    car.year = _to_int_or_none(detail.get("year")) or car.year
    car.make = detail.get("make") or car.make
    car.model = detail.get("model") or car.model
    car.body_style = detail.get("body_style") or car.body_style
    car.exterior_color = detail.get("exterior_color") or car.exterior_color
    car.interior_color = detail.get("interior_color") or car.interior_color
    car.miles = _to_int_or_none(detail.get("miles")) or car.miles
    car.transmission = detail.get("transmission") or car.transmission
    car.engine = detail.get("engine") or car.engine
    car.price_raw = detail.get("price") or car.price_raw
    car.price = _parse_price_to_int(detail.get("price")) or car.price
    car.thumb = detail.get("thumb") or car.thumb
    car.status = "active"  # you can adjust if you later detect sold/pending on detail page

    return car

def scrape_urls_and_persist(limit: int = 36, max_pages: int = 25, delay_each: float = 0.15) -> Dict[str, int]:
    """
    1) Collect all active listing URLs.
    2) Scrape each detail page.
    3) Upsert into DB.
    """
    urls = get_all_active_urls(limit=limit, max_pages=max_pages)
    created, updated, errors = 0, 0, 0

    db = SessionLocal()
    try:
        for i, url in enumerate(urls, 1):
            try:
                detail = scrape_car_detail(url)
                before = db.query(Car).filter_by(url=url).one_or_none()
                car = upsert_car(db, detail)
                db.commit()
                if before is None:
                    created += 1
                else:
                    updated += 1
            except Exception:
                db.rollback()
                errors += 1
            if delay_each:
                time.sleep(delay_each)
    finally:
        db.close()

    return {"created": created, "updated": updated, "errors": errors, "total_urls": len(urls)}
