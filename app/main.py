from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from .config import settings
from .database import Base, SessionLocal, engine
from .models import Item, User
from .routers import auth, items, tasks
from .security import hash_password

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

DEMO_ITEMS = [
    ("LAP-014", "Laptop stand, aluminium", 42, 1499.0, 10),
    ("KEY-220", "Mechanical keyboard", 8, 3499.0, 10),
    ("MSE-031", "Wireless mouse", 120, 699.0, 25),
    ("CAB-007", "USB-C cable, 1 m", 4, 249.0, 30),
    ("MON-270", "27-inch monitor", 15, 12999.0, 5),
]


def seed() -> None:
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username == settings.admin_username)):
            db.add(User(username=settings.admin_username, hashed_password=hash_password(settings.admin_password), role="admin"))
        if settings.seed_demo and not db.scalar(select(Item).limit(1)):
            for sku, name, qty, price, reorder in DEMO_ITEMS:
                db.add(Item(sku=sku, name=name, quantity=qty, price=price, reorder_level=reorder))
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    seed()
    yield


app = FastAPI(
    title="TaskDesk API",
    description="Task and inventory management with JWT auth and role-based access.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(items.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
