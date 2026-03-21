import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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


@app.get("/api")
async def api_root():
    return {"app": "MindWatch API", "version": "1.0.0", "status": "running", "docs": "/docs"}


# ── Static frontend ───────────────────────────────────────────────────────────
# Mounted LAST so API routes take precedence.
# StaticFiles with html=True automatically serves index.html for unknown paths
# (handles React client-side routing without a manual catch-all).
_static_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "static")
)

if os.path.exists(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")
