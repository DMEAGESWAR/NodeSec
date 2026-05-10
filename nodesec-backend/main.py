import os
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config import settings
from database import engine, Base

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("nodesec")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration}ms)")
        return response


# ── App lifespan ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created")
    yield
    await engine.dispose()


# ── Create app ──
app = FastAPI(
    title="NodeSec API",
    version="1.0.0",
    description="Passive Attack Surface Intelligence Platform",
    lifespan=lifespan,
)

# ── CORS ──
ALLOWED_ORIGINS = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(RequestLoggerMiddleware)


# ── Exception handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."},
    )


# ── Routers ──
from routers.auth import router as auth_router
from routers.domains import router as domain_router
from routers.scan import router as scan_router
from routers.findings import router as finding_router
from routers.reports import router as report_router

API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(domain_router, prefix=API_PREFIX)
app.include_router(scan_router, prefix=API_PREFIX)
app.include_router(finding_router, prefix=API_PREFIX)
app.include_router(report_router, prefix=API_PREFIX)


# ── Health check ──
@app.get("/health")
async def health():
    return {"status": "ok", "db": "connected", "version": "1.0.0"}