from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.auth import require_login, new_session_cookie_value, PASSWORD
from app.db import get_db, Car
from app.scraper import parse_listing
from app.sticker import render_sticker
from typing import Optional

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"])
)

@app.middleware("http")
async def auth_redirect(request: Request, call_next):
    if request.url.path.startswith("/static"):
        return await call_next(request)
    if request.url.path in ("/login", "/do-login"):
        return await call_next(request)
    try:
        require_login(request)
    except Exception:
        return RedirectResponse("/login")
    return await call_next(request)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):  # <-- accept request
    return env.get_template("login.html").render(
        request=request          # <-- pass request
    )

@app.post("/do-login")
def do_login(password: str = Form(...)):
    if password != PASSWORD:
        return RedirectResponse("/login?error=1", status_code=303)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("session", new_session_cookie_value(), httponly=True, samesite="Lax")
    return resp

@app.get("/", response_class=HTMLResponse)
def grid(request: Request, db=Depends(get_db), q: Optional[str] = None):
    cars = db.search(q) if q else db.list_cars()
    return env.get_template("grid.html").render(
        cars=cars,
        request=request          # <-- pass request
    )

@app.get("/cars/{car_id}", response_class=HTMLResponse)
def detail(car_id: int, request: Request, db=Depends(get_db)):
    car = db.get(car_id)
    if not car:
        return RedirectResponse("/", status_code=303)
    return env.get_template("detail.html").render(
        car=car,
        request=request          # <-- pass request
    )

@app.post("/cars")
def add_car(url: str = Form(...), db=Depends(get_db)):
    data = parse_listing(url)
    car = db.upsert_from_dict(data)
    return RedirectResponse(f"/cars/{car.id}", status_code=303)

@app.get("/cars/{car_id}/sticker.png")
def sticker(car_id: int, db=Depends(get_db)):
    car = db.get(car_id)
    if not car:
        return RedirectResponse("/", status_code=303)
    img = render_sticker(car)
    return StreamingResponse(
        img,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename=sticker-{car.stock or car.id}.png'}
    )
