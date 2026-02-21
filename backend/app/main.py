from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, SessionLocal
from .models import *  # noqa: F401, F403 — registers all models
from .routers.commodities import router as commodities_router, prices_router
from .routers.accounts import router as accounts_router
from .routers.transactions import router as transactions_router
from .routers.reports import router as reports_router
from .seed import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .database import Base
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="mxbcash",
    description="GnuCash-like personal finance tracker",
    version="0.1.0",
    lifespan=lifespan,
)

# All API routes under /api/v1 using a shared router prefix
from fastapi import APIRouter
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(commodities_router)
api_router.include_router(prices_router)
api_router.include_router(accounts_router)
api_router.include_router(transactions_router)
api_router.include_router(reports_router)

app.include_router(api_router)

# Serve frontend static files in production
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        return FileResponse(static_dir / "index.html")
