# ── Stage 1: Build React frontend ────────────────────────────────────────────
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci --prefer-offline

COPY frontend/ ./

# Empty VITE_API_URL = same-origin (frontend and backend served together)
ENV VITE_API_URL=""
RUN npm run build


# ── Stage 2: Python backend + serve frontend ──────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt ./requirements.txt

# Install psycopg2 is optional — skip it if Postgres libs fail (SQLite fallback)
RUN pip install --no-cache-dir -r requirements.txt || \
    (sed -i '/psycopg2/d' requirements.txt && pip install --no-cache-dir -r requirements.txt)

# App source
COPY backend/ ./backend/
COPY ml/       ./ml/

# Built frontend → served as static files by FastAPI
COPY --from=frontend-builder /frontend/dist ./static/

# SQLite DB lives in /tmp by default (ephemeral on HF free tier)
# Override DATABASE_URL secret to use PostgreSQL for persistence
ENV DATABASE_URL="sqlite:////tmp/mindwatch.db"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/backend

# Hugging Face Spaces uses port 7860
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
