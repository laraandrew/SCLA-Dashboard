SCLA Dashboard 🚗📊

A full-stack dashboard built for SportscarLA, a classic car dealership — designed to show how product strategy and technical execution come together to transform messy workflows into a streamlined, scalable system.

✨ The Problem

SportscarLA’s inventory was buried in static HTML pages:

No single view of all listings.

Details like VINs, colors, and prices were inconsistent.

Marketing assets (stickers) were created manually in Photoshop — slow, error-prone, and impossible to scale.

This cost the business time, accuracy, and customer trust.

🛠 The Solution

I built an end-to-end product pipeline that:

Scrapes & Normalizes Data: Pulls live inventory automatically, de-duplicates, and standardizes attributes.

Structured API & Database: Centralizes data into a clean model (year, make, model, VIN, colors, price, etc.), accessible through FastAPI.

User-Friendly Dashboard (Next.js): Lets staff quickly browse, filter, and expand vehicle details.

Sticker Generator (One-Click): Produces pixel-perfect, branded PNG stickers with pricing, car details, and QR codes — no manual design needed.

🚗 Why It Matters (Product Lens)

For the Business: Cuts hours of manual entry, eliminates inconsistencies, and enables faster marketing output.

For Customers: Creates polished, trustworthy, and standardized car listings.

For Scale: Provides a repeatable framework that can be extended to multiple dealerships or marketplaces.

⚙️ Tech Stack

Backend: FastAPI, SQLAlchemy, BeautifulSoup, lxml, Pillow, qrcode

Frontend: Next.js (React)

Database: SQLite (swappable with Postgres)

Infra: Local dev now, portable to cloud

🚀 Quick Start
Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


API Docs: http://127.0.0.1:8000/docs

Key endpoints:

/scan/urls → Live inventory URLs

/scan/cars-db → Structured car dataset

/scan/detail?url=... → Scrape any detail page

/stickers/generate?url=... → Download PNG sticker

Frontend
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
npm run dev


Open http://localhost:3000

📊 My Role

Product Research: Shadowed dealership workflows to uncover bottlenecks.

Solution Design: Defined a clear pipeline from raw HTML → clean data model → frontend → marketing asset.

Execution: Delivered scraper, API, DB, UI, and sticker generator.

Product Thinking: Focused on usability — one-click stickers, intuitive card expansion, and clean insights.

🌟 What This Demonstrates

End-to-end product ownership: from ideation → MVP → iteration.

Bridging tech & business needs: translating pain points into scalable tools.

User-centric mindset: designed for dealership staff & customers, not just engineers.

Scalability vision: architecture ready for multi-dealer expansion.

📈 Next Steps

Add analytics to measure sticker usage and listing engagement.

Multi-dealer support for wider client adoption.

Explore cloud deployment for scale.

📜 License

MIT