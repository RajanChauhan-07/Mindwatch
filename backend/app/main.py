import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
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


# ── Paths ─────────────────────────────────────────────────────────────────────
_static_dir  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
_index_html  = os.path.join(_static_dir, "index.html")
_assets_dir  = os.path.join(_static_dir, "assets")

# Extensions that must return a real 404 — never serve index.html for these
_STATIC_EXTS = (
    ".js", ".mjs", ".css", ".ico", ".png", ".jpg", ".jpeg", ".svg",
    ".webp", ".woff", ".woff2", ".ttf", ".eot", ".map", ".txt",
)


def _no_cache_html() -> FileResponse:
    """Return index.html with headers that prevent browser caching."""
    r = FileResponse(_index_html, media_type="text/html")
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


# ── Static assets ─────────────────────────────────────────────────────────────
# Mount /assets — Vite puts all JS/CSS chunks here.
# This prefix is specific enough that it never clashes with /api routes.
if os.path.exists(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

# Serve individual root-level static files (favicon.svg, robots.txt, etc.)
if os.path.exists(_static_dir):
    for _fname in os.listdir(_static_dir):
        _fpath = os.path.join(_static_dir, _fname)
        if os.path.isfile(_fpath) and _fname != "index.html":
            def _make_file_route(fp: str):
                async def _route():
                    return FileResponse(fp)
                return _route
            app.add_api_route(
                f"/{_fname}",
                _make_file_route(_fpath),
                include_in_schema=False,
                methods=["GET"],
            )


# ── SPA entry ─────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def serve_root():
    if os.path.exists(_index_html):
        return _no_cache_html()
    return {"app": "MindWatch API", "version": "1.0.0", "docs": "/docs"}


# ── 404 handler — serves SPA for React routes ─────────────────────────────────
@app.exception_handler(404)
async def spa_404_handler(request: Request, exc):
    path = request.url.path

    # Return real 404 for API routes, docs, and file-extension assets.
    # This prevents the browser from caching index.html as a .js file.
    if (
        path.startswith("/api/")
        or path.startswith("/assets/")
        or path in ("/docs", "/redoc", "/openapi.json")
        or any(path.endswith(ext) for ext in _STATIC_EXTS)
    ):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    # For React Router paths (/dashboard, /auth/callback, etc.) serve the SPA
    if os.path.exists(_index_html):
        return _no_cache_html()

    return JSONResponse({"detail": "Not Found"}, status_code=404)
