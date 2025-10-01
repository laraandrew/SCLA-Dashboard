import os, time, asyncio, httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

BACKEND = os.getenv("BACKEND_URL", "http://backend:8000")
SCRAPE_URL = os.getenv("SCRAPE_URL", "")
INTERVAL = int(os.getenv("SCAN_INTERVAL", "3600"))
API_TOKEN = os.getenv("API_TOKEN", "")

class Car(BaseModel):
    url: str
    year: int | None = None
    make: str | None = None
    model: str | None = None
    miles: int | None = None
    price: float | None = None

async def upsert_car(client: httpx.AsyncClient, car: Car):
    headers = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}
    await client.post(f"{BACKEND}/cars/", json=car.model_dump(), headers=headers)

async def scan_once():
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(SCRAPE_URL)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # TODO: Replace with real selectors for SportscarLA inventory
        cards = soup.select(".inventory-card")
        for c in cards:
            link = c.select_one("a").get("href")
            title = c.select_one(".title").get_text(strip=True)
            price_txt = c.select_one(".price").get_text(strip=True).replace("$","").replace(",","")
            miles_txt = c.select_one(".miles").get_text(strip=True).replace(",","")
            year, make, model = title.split(" ", 3)[:3]
            car = Car(
                url=link,
                year=int(year),
                make=make,
                model=model,
                miles=int(miles_txt.split()[0]),
                price=float(price_txt.split()[0])
            )
            await upsert_car(client, car)

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(scan_once())
        except Exception as e:
            print("[worker] scan error:", e)
        time.sleep(INTERVAL)
