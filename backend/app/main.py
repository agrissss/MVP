"""FastAPI lietojuma ieejas punkts."""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .database import init_db
from .api import documents as documents_api
from .api import meta as meta_api
from .api import imports as imports_api
from .api import sections as sections_api
from .api import suggest as suggest_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Tiesību aktu un oficiālo datu pārlūks",
    description=(
        "MVP platforma Latvijas tiesību aktu un oficiālo atvērto datu "
        "meklēšanai. **Nav juridiska konsultācija** — autoritatīvais teksts "
        "vienmēr atrodas oficiālajā avotā."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Gzip kompresija — samazina JSON atbilžu izmēru (parasti 60-80%)
app.add_middleware(GZipMiddleware, minimum_size=500)


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Pievieno Cache-Control galvenes taksonomijām un ieteikumiem.

    - /api/topics, /api/sources, /api/doc-types, /api/statuses — public, 5 min
    - /api/suggest — private, 30 sec (mainās ar datiem, bet lietotāja UX dēļ OK īsi)
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if request.method == "GET":
            if path in ("/api/topics", "/api/sources", "/api/doc-types", "/api/statuses"):
                response.headers.setdefault("Cache-Control", "public, max-age=300")
            elif path == "/api/suggest":
                response.headers.setdefault("Cache-Control", "public, max-age=30")
        return response


app.add_middleware(CacheControlMiddleware)

app.include_router(documents_api.router)
app.include_router(meta_api.router)
app.include_router(imports_api.router)
app.include_router(sections_api.router)
app.include_router(suggest_api.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "Tiesību aktu un oficiālo datu pārlūks",
        "version": "0.1.0",
        "docs": "/docs",
        "disclaimer": (
            "Šī sistēma nav juridiska konsultācija. Autoritatīvais teksts "
            "vienmēr ir oficiālajā avotā."
        ),
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
