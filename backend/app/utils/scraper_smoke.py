# backend/app/utils/scraper_smoke.py
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from app.utils.scraper import (
    get_all_active_urls,
    scrape_car_detail,
    scrape_urls_and_persist,
)
from app.db import SessionLocal
from app.models.car import Car


def cmd_urls(args: argparse.Namespace) -> int:
    urls: List[str] = get_all_active_urls(limit=args.limit, max_pages=args.pages)
    print(json.dumps({"total": len(urls), "sample": urls[: min(5, len(urls))], "all": urls}, indent=2))
    return 0


def cmd_one(args: argparse.Namespace) -> int:
    if not args.url:
        print("Error: --url is required for 'one'", file=sys.stderr)
        return 2
    data = scrape_car_detail(args.url)
    print(json.dumps(data, indent=2))
    # Basic sanity checks
    missing = [k for k in ("year", "make", "model") if not (data.get(k) or "").strip()]
    if missing:
        print(f"Note: missing fields: {', '.join(missing)}", file=sys.stderr)
    return 0


def cmd_persist(args: argparse.Namespace) -> int:
    result = scrape_urls_and_persist(limit=args.limit, max_pages=args.pages)
    print(json.dumps(result, indent=2))
    return 0


def cmd_db(args: argparse.Namespace) -> int:
    db = SessionLocal()
    try:
        q = db.query(Car).order_by(Car.id.desc())
        total = q.count()
        items = q.offset(args.offset).limit(args.limit).all()
        out = []
        for c in items:
            out.append(
                {
                    "id": c.id,
                    "url": c.url,
                    "stock": c.stock,
                    "vin": c.vin,
                    "year": c.year,
                    "make": c.make,
                    "model": c.model,
                    "body_style": c.body_style,
                    "exterior_color": c.exterior_color,
                    "interior_color": c.interior_color,
                    "miles": c.miles,
                    "transmission": c.transmission,
                    "engine": c.engine,
                    "price": c.price,
                    "price_raw": c.price_raw,
                    "thumb": c.thumb,
                    "status": c.status,
                }
            )
        print(json.dumps({"count": total, "items": out}, indent=2))
        return 0
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m app.utils.scraper_smoke",
        description="Smoke-test the SportscarLA scraper and DB pipeline.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # urls
    p_urls = sub.add_parser("urls", help="Fetch URL list from inventory (non-sold).")
    p_urls.add_argument("--limit", type=int, default=36)
    p_urls.add_argument("--pages", type=int, default=5)
    p_urls.set_defaults(func=cmd_urls)

    # one
    p_one = sub.add_parser("one", help="Scrape a single car detail page by URL.")
    p_one.add_argument("--url", required=True, help="Detail page URL")
    p_one.set_defaults(func=cmd_one)

    # persist
    p_persist = sub.add_parser("persist", help="Collect URLs -> scrape each -> upsert into DB.")
    p_persist.add_argument("--limit", type=int, default=36)
    p_persist.add_argument("--pages", type=int, default=10)
    p_persist.set_defaults(func=cmd_persist)

    # db
    p_db = sub.add_parser("db", help="Read back cars from DB (for verification).")
    p_db.add_argument("--limit", type=int, default=10)
    p_db.add_argument("--offset", type=int, default=0)
    p_db.set_defaults(func=cmd_db)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
