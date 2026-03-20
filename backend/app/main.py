import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.database import Base, engine

# Import all models before create_all so SQLAlchemy registers them
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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/auth",        tags=["auth"])
app.include_router(users.router,       prefix="/api/users",       tags=["users"])
app.include_router(connectors.router,  prefix="/api/connectors",  tags=["connectors"])
app.include_router(analysis.router,    prefix="/api/analysis",    tags=["analysis"])
app.include_router(chat.router,        prefix="/api/chat",        tags=["chat"])


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    # If static frontend exists, serve it; otherwise return API info
    static_index = os.path.join(
        os.path.dirname(__file__), "..", "..", "static", "index.html"
    )
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {"app": "MindWatch API", "version": "1.0.0", "status": "running", "docs": "/docs"}


# ── Static frontend (served when Docker-built) ──────────────────────────────
_static_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static")
)

if os.path.exists(_static_dir):
    _assets_dir = os.path.join(_static_dir, "assets")
    if os.path.exists(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Catch-all that returns index.html for client-side routing."""
        # Let API and known static paths fall through
        skip = ("api/", "docs", "redoc", "openapi.json", "health", "assets/")
        if any(full_path.startswith(s) for s in skip):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        index_html = os.path.join(_static_dir, "index.html")
        return FileResponse(index_html)
