# MindWatch — Mental Wellness Intelligence Platform

> **AI-powered mental wellness platform** that analyzes your digital behavior — Spotify music, YouTube content, WhatsApp chats, and Google Fit activity — using BERT, Fuzzy Logic, and Gemini AI to predict and track your mental wellness.

![MindWatch Dashboard](https://img.shields.io/badge/Status-Active-22C55E?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-A855F7?style=for-the-badge)

---

## What is MindWatch?

MindWatch is a full-stack mental wellness platform that does something no existing wellness app does — it **analyzes your actual digital behavior** instead of asking you how you feel. It connects to your real data sources and uses AI to surface patterns you didn't know existed.

### The Problem
Most people don't notice declining mental wellness until it becomes a crisis. Your Spotify listening habits, YouTube content diet, messaging patterns, and physical activity all contain early warning signals — but they're scattered across different apps with no unified analysis.

### The Solution
MindWatch aggregates all of this data, runs it through a multi-model AI pipeline (BERT for emotion detection, ML classifiers for content analysis, Mamdani Fuzzy Inference System for score fusion), and delivers a single unified **Wellness Score** with actionable insights.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MindWatch Platform                        │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────────────────────────┐   │
│  │   Frontend   │    │              Backend                  │   │
│  │  React + TS  │◄──►│  FastAPI + PostgreSQL + SQLAlchemy   │   │
│  │  Vite + TW   │    │                                      │   │
│  │  Framer Mo.  │    │  ┌────────────────────────────────┐  │   │
│  └──────────────┘    │  │        ML Pipeline             │  │   │
│                       │  │                                │  │   │
│  Data Sources:        │  │  BERT Emotion Classifier       │  │   │
│  ┌──────────────┐    │  │  → Linguistic Score            │  │   │
│  │   Spotify    │───►│  │                                │  │   │
│  │   YouTube    │───►│  │  TF-IDF + LogReg Classifier    │  │   │
│  │   WhatsApp   │───►│  │  → Consumption Score           │  │   │
│  │  Google Fit  │───►│  │                                │  │   │
│  └──────────────┘    │  │  Behavioral Engine             │  │   │
│                       │  │  → Behavioral Score            │  │   │
│  AI Services:         │  │                                │  │   │
│  ┌──────────────┐    │  │  Mamdani FIS (Fuzzy Logic)     │  │   │
│  │  Gemini AI   │◄──►│  │  → Unified Wellness Score      │  │   │
│  └──────────────┘    │  └────────────────────────────────┘  │   │
│                       └──────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

### Data Sources
| Source | What it analyzes |
|--------|-----------------|
| **Spotify** | Valence, energy, danceability, tempo across 50 recent tracks. Late-night listening patterns. |
| **YouTube** | Watch history classified into 11 emotional categories using ML. Dark content %, recovery content %, rumination patterns. |
| **WhatsApp** | Sentiment analysis, isolation score, late-night messaging ratio, message frequency trend, top words. |
| **Google Fit** | Daily steps, active minutes, heart rate, calorie burn. 7-day trends. |

### AI Models
| Model | Purpose | Technology |
|-------|---------|-----------|
| **BERT Emotion Classifier** | Classifies text into 6 emotions: sadness, joy, love, anger, fear, surprise | DistilBERT fine-tuned on emotion dataset |
| **Content Classifier** | Categorizes YouTube titles into 11 categories | TF-IDF + Logistic Regression (67.8% accuracy) |
| **Behavioral Engine** | Analyzes listening/messaging time patterns | Custom rule-based + statistical analysis |
| **Mamdani FIS** | Fuses all scores into one wellness output | scikit-fuzzy with 20 fuzzy rules |
| **Gemini AI Chatbot** | Personalized wellness coaching | Google Gemini Flash with user data context |
| **Prophet Forecaster** | 7-day wellness prediction | Facebook Prophet + simple moving average fallback |

### Dashboard Features
- Real-time wellness score with animated circular ring
- BERT-powered emotion analysis on chat data
- ML content diet score with category breakdown
- Behavioral pattern detection (sleep disruption, consistency)
- 7-day prediction chart with trend indicators
- AI chatbot with full access to your wellness data
- Dark / Light mode with persistent preference
- Aurora animated backgrounds + Glass morphism UI

---

## Tech Stack

### Backend
```
Python 3.9+         FastAPI 0.104       Uvicorn 0.24
SQLAlchemy 2.0      PostgreSQL          Alembic
python-jose         passlib[bcrypt]     pydantic-settings
httpx               beautifulsoup4      google-genai
torch               transformers        scikit-learn
scikit-fuzzy        prophet             joblib
pandas              numpy               vaderSentiment
```

### Frontend
```
React 18            TypeScript          Vite 5
Tailwind CSS 3      Framer Motion       Recharts
Zustand             Axios               Lucide React
Inter (Google Font)
```

---

## Project Structure

```
mindwatch/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          # Google OAuth 2.0 flow
│   │   │   ├── chat.py          # Gemini AI chatbot endpoint
│   │   │   ├── connectors.py    # Spotify, YouTube, WhatsApp, Google Fit
│   │   │   ├── analysis.py      # ML pipeline trigger endpoint
│   │   │   └── users.py         # User profile management
│   │   ├── connectors/
│   │   │   ├── spotify.py       # Spotify Web API + token refresh
│   │   │   ├── youtube.py       # HTML parser for Google Takeout
│   │   │   ├── whatsapp.py      # WhatsApp export parser
│   │   │   └── google_fit.py    # Google Fit REST API
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings
│   │   │   ├── database.py      # SQLAlchemy setup
│   │   │   └── security.py      # JWT creation/verification
│   │   ├── engines/
│   │   │   └── wellness_pipeline.py  # ML orchestration layer
│   │   ├── models/
│   │   │   ├── user.py          # User SQLAlchemy model
│   │   │   └── analysis.py      # Analysis, ChatMessage, RawData models
│   │   ├── services/
│   │   │   └── chatbot.py       # Gemini AI service
│   │   └── main.py              # FastAPI app, CORS, routers
│   ├── requirements.txt
│   └── .env.example             # ← copy to .env and fill in keys
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── effects/
│   │   │   │   ├── Aurora.tsx       # Animated gradient blobs
│   │   │   │   ├── BlurReveal.tsx   # Scroll reveal animation
│   │   │   │   ├── GlowBorder.tsx   # Gradient border wrapper
│   │   │   │   └── Magnetic.tsx     # Mouse attraction effect
│   │   │   ├── ChatBot.tsx          # Floating AI chat panel
│   │   │   ├── ScoreCard.tsx        # Animated circular score ring
│   │   │   ├── MoodBar.tsx          # Gradient progress bar
│   │   │   ├── InsightCard.tsx      # Color-coded insight pill
│   │   │   └── LoadingSpinner.tsx   # SVG spinner
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx      # Aurora hero + Bento grid
│   │   │   ├── Dashboard.tsx        # Main app (1200+ lines)
│   │   │   └── AuthCallback.tsx     # OAuth redirect handler
│   │   ├── store/
│   │   │   ├── authStore.ts         # Zustand auth state
│   │   │   └── themeStore.ts        # Dark/light mode state
│   │   └── utils/
│   │       └── api.ts               # Axios instance with token interceptor
│   └── .env.example                 # ← copy to .env
│
├── ml/
│   ├── engines/
│   │   ├── linguistic_engine.py     # BERT + VADER emotion analysis
│   │   ├── consumption_engine.py    # Content classification
│   │   ├── behavioral_engine.py     # Pattern analysis
│   │   ├── fuzzy_engine.py          # Mamdani FIS
│   │   └── predictor.py             # Prophet forecasting
│   ├── training/
│   │   ├── generate_training_data.py # Creates labeled dataset
│   │   └── train_content.py          # Trains TF-IDF + LogReg model
│   ├── models/
│   │   ├── bert_emotion_classifier/  # Pre-trained DistilBERT (not in repo — see Setup)
│   │   └── content_classifier.pkl    # Trained by you locally
│   └── utils/
│       └── preprocessor.py           # Text cleaning utilities
│
├── .gitignore
├── README.md
└── SETUP.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL running locally
- A Google Cloud project with OAuth 2.0 configured

### 1. Clone the repository
```bash
git clone https://github.com/RajanChauhan-07/Mindwatch.git
cd Mindwatch
```

### 2. Database
```bash
createdb mindwatch
```

### 3. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and fill in your API keys
cp .env.example .env
nano .env
```

### 4. Train the Content Classifier
```bash
cd ..
python ml/training/generate_training_data.py
python ml/training/train_content.py
# Output: ml/models/content_classifier.pkl
```

### 5. BERT Model
The BERT emotion classifier is not included in this repo due to file size (~250MB).

**Option A — Use the pre-trained model:**
Download `bert_emotion_classifier_final/` and place it at:
```
ml/models/bert_emotion_classifier/
```
Required files: `config.json`, `model.safetensors`, `tokenizer_config.json`, `tokenizer.json`, `label_config.json`

**Option B — VADER fallback (no download needed):**
If the BERT model folder is absent, the system automatically falls back to VADER sentiment analysis. All features still work.

### 6. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
```

### 7. Run
```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Open **http://localhost:5173**

---

## API Keys Required

See `backend/.env.example` for all required environment variables.

| Key | Where to get it |
|-----|----------------|
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | [console.cloud.google.com](https://console.cloud.google.com) → APIs & Services → Credentials → OAuth 2.0 Client |
| `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` | [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) |
| `GEMINI_API_KEY` | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |

### Required OAuth Redirect URIs

**Google Cloud Console:**
```
http://localhost:8000/api/auth/google/callback
http://localhost:8000/api/connectors/googlefit/callback
```

**Spotify Dashboard:**
```
http://127.0.0.1:8000/api/connectors/spotify/callback
```

**Google Fit (add to test users):**
- Go to APIs & Services → OAuth consent screen → Test users
- Add your Google account email

---

## How the ML Pipeline Works

```
User Data
    │
    ├─► WhatsApp messages ──► BERT Emotion Classifier ──► Linguistic Score (0-100)
    │                          (or VADER fallback)
    │
    ├─► YouTube history ───► TF-IDF + LogReg Classifier ► Consumption Score (0-100)
    │                          (11 categories, ML model)
    │
    ├─► Spotify plays ─────► Behavioral Engine ──────────► Behavioral Score (0-100)
    │                          (time patterns, consistency)
    │
    └─► All three scores ──► Mamdani FIS ───────────────► Unified Wellness Score
                               (20 fuzzy rules)              + Risk Level
                               Antecedents: Linguistic,      + Explanation
                               Consumption, Behavioral        + 7-Day Forecast
```

The Mamdani Fuzzy Inference System uses three antecedent variables (each with low/medium/high membership functions) and one consequent (wellness: critical/poor/moderate/good/excellent), connected by 20 expert-designed fuzzy rules.

---

## Screenshots

The app features:
- **Landing Page** — Aurora animated hero with bento feature grid
- **Dashboard** — Bento tile layout with big bold metrics
- **Score Ring** — Animated count-up with ambient color glow
- **Dark Mode** — True black (`#000`) with glass surface cards
- **Chatbot** — Floating AI panel with spring animations

---

## API Documentation

Once running, full interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Disclaimer

MindWatch is **not a medical device** and is not intended to diagnose, treat, cure, or prevent any mental health condition. It is a wellness awareness tool only. If you are experiencing a mental health crisis, please contact a qualified healthcare professional or a crisis helpline.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

Built by **Rajan Chauhan** · [GitHub](https://github.com/RajanChauhan-07)

> "Understanding yourself is the beginning of all wisdom." — Aristotle

---

## Deployment on Hugging Face Spaces

MindWatch ships with a `Dockerfile` that builds the React frontend and serves it alongside the FastAPI backend — no separate servers needed.

### Steps

**1. Create a new Space**
- Go to [huggingface.co/new-space](https://huggingface.co/new-space)
- Owner: your username
- Space name: `mindwatch` (or anything you like)
- SDK: **Docker**
- Visibility: Public or Private

**2. Add your API keys as Secrets**

In your Space → Settings → Repository secrets, add:

| Secret Name | Value |
|---|---|
| `SECRET_KEY` | Any long random string |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | `https://YOUR-SPACE-URL.hf.space/api/auth/google/callback` |
| `SPOTIFY_CLIENT_ID` | From Spotify Developer Dashboard |
| `SPOTIFY_CLIENT_SECRET` | From Spotify Developer Dashboard |
| `SPOTIFY_REDIRECT_URI` | `https://YOUR-SPACE-URL.hf.space/api/connectors/spotify/callback` |
| `GOOGLE_FIT_REDIRECT_URI` | `https://YOUR-SPACE-URL.hf.space/api/connectors/googlefit/callback` |
| `GEMINI_API_KEY` | From Google AI Studio |
| `FRONTEND_URL` | `https://YOUR-SPACE-URL.hf.space` |
| `DATABASE_URL` | (Optional) PostgreSQL URL from Supabase/Neon for persistent storage |

> Your Space URL is `https://huggingface.co/spaces/YOUR_USERNAME/mindwatch` — the app URL is `https://YOUR_USERNAME-mindwatch.hf.space`

**3. Update OAuth Redirect URIs**

In **Google Cloud Console** → Credentials → your OAuth Client, add:
```
https://YOUR_USERNAME-mindwatch.hf.space/api/auth/google/callback
https://YOUR_USERNAME-mindwatch.hf.space/api/connectors/googlefit/callback
```

In **Spotify Dashboard** → your app → Redirect URIs, add:
```
https://YOUR_USERNAME-mindwatch.hf.space/api/connectors/spotify/callback
```

**4. Push the repo to your Space**
```bash
# Add your HF Space as a remote
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/mindwatch

# Push (HF will build the Docker image automatically)
git push space main
```

**5. Wait for the build**
HF Spaces will build the Docker image (~5-10 minutes first time). Watch progress in the Space's "Logs" tab.

### Database Note

By default the app uses **SQLite** stored in `/tmp` (ephemeral — data resets on restart). For persistent data, set the `DATABASE_URL` secret to a free PostgreSQL from:
- [Supabase](https://supabase.com) — 500MB free
- [Neon](https://neon.tech) — 512MB free

Both give you a `postgresql://...` connection string to paste as the `DATABASE_URL` secret.

