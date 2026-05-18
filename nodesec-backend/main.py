import os
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from database import engine, Base

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("nodesec")


# ── Request Logger Middleware ──
class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        response = await call_next(request)

        duration = round((time.time() - start) * 1000, 2)

        logger.info(
            f"{request.method} {request.url.path} "
            f"-> {response.status_code} ({duration}ms)"
        )

        return response


# ── Lifespan (Database Startup/Shutdown) ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables verified/created")

    except Exception as e:
        logger.warning(f"Database not connected: {e}")

    yield

    try:
        await engine.dispose()

    except Exception as e:
        logger.warning(f"Error closing DB: {e}")


# ── FastAPI App ──
app = FastAPI(
    title="NodeSec API",
    version="1.0.0",
    description="Passive Attack Surface Intelligence Platform",
    lifespan=lifespan,
)


# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Custom Middleware ──
app.add_middleware(RequestLoggerMiddleware)


# ── Global Exception Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error. Please try again."
        },
    )


# ── Import Routers ──
from routers.auth import router as auth_router
from routers.domains import router as domain_router
from routers.scan import router as scan_router
from routers.findings import router as finding_router
from routers.reports import router as report_router


# ── API Prefix ──
API_PREFIX = "/api/v1"


# ── Include Routers ──
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(domain_router, prefix=API_PREFIX)
app.include_router(scan_router, prefix=API_PREFIX)
app.include_router(finding_router, prefix=API_PREFIX)
app.include_router(report_router, prefix=API_PREFIX)


# ── Root Route ──
@app.get("/")
async def root():
    return {
        "message": "NodeSec API Running",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }


# ── Health Check ──
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "db": "connected",
        "version": "1.0.0"
    }