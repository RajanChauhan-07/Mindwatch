# MindWatch Setup Guide

## Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL running locally

## Database Setup
```bash
createdb mindwatch
```

## Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Frontend Setup
```bash
cd frontend
npm install
```

## API Keys Required

### 1. backend/.env
Fill in these values:

```env
DATABASE_URL=postgresql://YOUR_MAC_USERNAME@localhost:5432/mindwatch
SECRET_KEY=mindwatch-super-secret-key-change-in-production

# Google OAuth -> https://console.cloud.google.com
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Spotify -> https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID=YOUR_SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/connectors/spotify/callback

# Gemini AI (FREE) -> https://aistudio.google.com/app/apikey
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

FRONTEND_URL=http://localhost:5173
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 2. frontend/.env
```env
VITE_API_URL=http://localhost:8000
```

## Google OAuth Setup
1. Go to https://console.cloud.google.com
2. Create a new project named "mindwatch-app"
3. Enable APIs: Google Identity API, Google Fit API, People API
4. Go to "OAuth consent screen" -> External -> fill in app name
5. Go to "Credentials" -> Create Credentials -> OAuth Client ID
6. Application type: Web Application
7. Add Authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
8. Copy Client ID and Client Secret into `backend/.env`

## Spotify Setup
1. Go to https://developer.spotify.com/dashboard
2. Create a new app named "MindWatch"
3. Add Redirect URI: `http://127.0.0.1:8000/api/connectors/spotify/callback`
4. Go to User Management -> add your Spotify account email as a test user
5. Copy Client ID and Client Secret into `backend/.env`

## Gemini AI Setup
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select your "mindwatch-app" project
4. Copy the key into `backend/.env` as GEMINI_API_KEY

## Run the App

### Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Open: http://localhost:5173

## API Documentation
Once the backend is running, visit: http://localhost:8000/docs
