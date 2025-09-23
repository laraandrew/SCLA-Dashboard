# Sticker Dashboard (FastAPI)

One-password dashboard for your dealership:
- Grid of cars (thumbnail + title).
- Detail view with fields.
- **Generate & Download Sticker** button (on demand).
- Paste listing URL to add a new car.

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export APP_PASSWORD="changeme"
export SESSION_SECRET="$(python -c 'import secrets;print(secrets.token_hex(32))')"
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/login
```

## Deploy on Render (recommended)
- Create a new Web Service from this repo.
- Render will use `render.yaml` automatically.
- Set/rotate **APP_PASSWORD** and **SESSION_SECRET** in the dashboard.
- A small persistent disk is configured for SQLite.

## Env vars
- `APP_PASSWORD` – the single shared password for login.
- `SESSION_SECRET` – random 32+ char string to sign cookies.

## Notes
- Stickers are generated on demand (no storage bloat).
- Thumbnails are hotlinked or cached small images if needed.
- Scraper is dealership-specific; edit `app/scraper.py` mappings as site HTML changes.
