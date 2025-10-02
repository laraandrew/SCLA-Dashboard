SCLA Dashboard

A full-stack dashboard that transforms messy dealership inventory into a structured, user-friendly system. Built to show how technical execution and product thinking combine: from understanding business needs, to designing data pipelines, to presenting clean insights and customer-ready outputs.

✨ What Problem It Solves

SportscarLA, a classic car dealership, had their inventory buried inside static HTML pages with no easy way to:

See all listings in one place

Standardize details like VINs, colors, and prices

Generate marketing assets (stickers) without manual Photoshop work

The pain points were clear: time wasted, inconsistent information, and no scalable workflow.

🛠 The Solution

This project delivers an end-to-end product pipeline:

Scraping Layer – Automatically pulls all live inventory from the dealership site. Handles pagination, avoids duplicate entries, and normalizes data.

Database & API – Stores vehicles in a structured format (year, make, model, VIN, colors, price, etc.). Exposed via a FastAPI backend with clean, documented endpoints.

Frontend Dashboard – Next.js UI that allows easy browsing, filtering, and detail expansion of every car listing.

Sticker Generator – One-click “Generate Sticker” button that produces a pixel-perfect PNG sticker with pricing, key details, and a QR code to the live listing.

🚗 Why This Matters (Product Lens)

For the business: saves hours of manual data entry and design work, while ensuring accuracy in every listing.

For customers: creates a polished, consistent, and trustworthy presentation of cars.

For scale: the same framework could support multiple dealerships, e-commerce storefronts, or marketplaces.

⚙️ Tech Stack (Execution)

Backend: FastAPI, SQLAlchemy, BeautifulSoup, lxml, Pillow, qrcode

Frontend: Next.js, React

Database: SQLite (swappable for Postgres)

Infra: Built for local dev now, designed with portability for cloud

🚀 Getting Started

Backend

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


API Docs: http://127.0.0.1:8000/docs

Endpoints of note:

/scan/urls – live inventory URLs

/scan/cars-db – structured car dataset

/scan/detail?url=... – scrape any detail page

/stickers/generate?url=... – download PNG sticker

Frontend
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
npm run dev


Open http://localhost:3000

📊 My Role

Product Research: Identified dealership workflow pain points

Solution Design: Defined pipeline from ingestion → data model → frontend → marketing asset

Tech Execution: Implemented scraper, API, database, frontend, and sticker generator

Product Thinking: Optimized for user experience (single click sticker generation, clean card expansion, intuitive data presentation)

🌟 Takeaways

This project demonstrates:

How to bridge business problems and technical execution

A focus on end users (dealership staff & customers) rather than just code correctness

The ability to own a product lifecycle: ideation → MVP → iteration

📈 Next Steps

Add analytics to measure sticker usage and page views

Support multiple dealerships as clients

Explore cloud deployment and scaling

License

MIT