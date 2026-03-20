from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["connectors"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    return {
        "app": "MindWatch API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
