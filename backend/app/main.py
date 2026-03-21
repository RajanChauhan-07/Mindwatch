import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.database import Base, engine

from .models.user import User  # noqa: F401
from .models.analysis import Analysis, ChatMessage, RawData  # noqa: F401

from .api import auth, users, connectors, analysis, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MindWatch API",
    description="Mental Wellness AI Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/api/auth",       tags=["auth"])
app.include_router(users.router,      prefix="/api/users",      tags=["users"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["connectors"])
app.include_router(analysis.router,   prefix="/api/analysis",   tags=["analysis"])
app.include_router(chat.router,       prefix="/api/chat",       tags=["chat"])


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ── Static frontend (Docker build only) ──────────────────────────────────────
_static_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static")
)
_index_html = os.path.join(_static_dir, "index.html")

# Mount /assets so Vite-built JS/CSS/images are served directly.
# This does NOT conflict with /api/* routes.
_assets_dir = os.path.join(_static_dir, "assets")
if os.path.exists(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")


@app.get("/", include_in_schema=False)
async def serve_root():
    if os.path.exists(_index_html):
        return FileResponse(_index_html)
    return {"app": "MindWatch API", "version": "1.0.0", "docs": "/docs"}


@app.exception_handler(404)
async def spa_404_handler(request: Request, exc):
    """
    For any path that FastAPI doesn't recognise:
    - /api/* paths  → real 404 JSON (the API route simply doesn't exist)
    - everything else → serve index.html so React Router handles it
      (covers /dashboard, /auth/callback, etc.)
    """
    path = request.url.path
    if path.startswith("/api/") or path in ("/docs", "/redoc", "/openapi.json"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    if os.path.exists(_index_html):
        return FileResponse(_index_html, media_type="text/html")
    return JSONResponse({"detail": "Not Found"}, status_code=404)
