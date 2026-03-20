import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..connectors.google_fit import GoogleFitConnector
from ..connectors.spotify import SpotifyConnector
from ..connectors.whatsapp import WhatsAppAnalyzer
from ..connectors.youtube import YouTubeAnalyzer
from ..core.config import settings
from ..core.database import get_db
from ..core.security import verify_token
from ..models.user import User

router = APIRouter()


def get_current_user(token: str, db: Session) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Spotify ──────────────────────────────────────────────────────────────────

@router.get("/spotify/connect")
async def spotify_connect(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    connector = SpotifyConnector()
    auth_url = connector.get_auth_url(str(user.id))
    return RedirectResponse(url=auth_url)


@router.get("/spotify/callback")
async def spotify_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db),
):
    if error or not code:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?spotify_error=1")

    try:
        connector = SpotifyConnector()
        token_data = await connector.exchange_code(code)

        if not state:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?spotify_error=1")

        user = db.query(User).filter(User.id == state).first()
        if not user:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?spotify_error=1")

        user.spotify_token = json.dumps(token_data)
        user.spotify_connected = True
        db.commit()

        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?spotify_connected=1")
    except Exception:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?spotify_error=1")


@router.get("/spotify/analysis")
async def spotify_analysis(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)

    if not user.spotify_connected or not user.spotify_token:
        raise HTTPException(status_code=400, detail="Spotify not connected")

    try:
        token_data = json.loads(user.spotify_token)
        connector = SpotifyConnector(access_token=token_data.get("access_token"))

        try:
            analysis = await connector.get_full_analysis()
        except Exception:
            # Token likely expired — attempt refresh
            refresh_token = token_data.get("refresh_token")
            if not refresh_token:
                user.spotify_connected = False
                db.commit()
                raise HTTPException(status_code=401, detail="Spotify token expired. Please reconnect Spotify.")

            refreshed = await connector.refresh_access_token(refresh_token)
            if "access_token" not in refreshed:
                user.spotify_connected = False
                db.commit()
                raise HTTPException(status_code=401, detail="Spotify token refresh failed. Please reconnect Spotify.")

            # Save new token and retry
            token_data["access_token"] = refreshed["access_token"]
            if "refresh_token" in refreshed:
                token_data["refresh_token"] = refreshed["refresh_token"]
            user.spotify_token = json.dumps(token_data)
            db.commit()

            connector.access_token = refreshed["access_token"]
            analysis = await connector.get_full_analysis()

        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify analysis failed: {str(e)}")


@router.get("/spotify/status")
async def spotify_status(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return {"connected": user.spotify_connected}


# ── YouTube ───────────────────────────────────────────────────────────────────

@router.post("/youtube/analyze")
async def youtube_analyze(
    token: str,
    watch_history: UploadFile = File(...),
    search_history: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    get_current_user(token, db)

    try:
        watch_content = await watch_history.read()
        watch_html = watch_content.decode("utf-8", errors="ignore")

        search_html = None
        if search_history:
            search_content = await search_history.read()
            search_html = search_content.decode("utf-8", errors="ignore")

        analyzer = YouTubeAnalyzer()
        videos = analyzer.parse_watch_history(watch_html)
        searches = analyzer.parse_search_history(search_html) if search_html else []

        result = analyzer.analyze(videos, searches)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube analysis failed: {str(e)}")


# ── WhatsApp ──────────────────────────────────────────────────────────────────

@router.post("/whatsapp/analyze")
async def whatsapp_analyze(
    token: str,
    chat_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    get_current_user(token, db)

    try:
        content = await chat_file.read()
        text = content.decode("utf-8", errors="ignore")

        analyzer = WhatsAppAnalyzer()
        messages = analyzer.parse_chat(text)
        result = analyzer.analyze(messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WhatsApp analysis failed: {str(e)}")


# ── Google Fit ────────────────────────────────────────────────────────────────

@router.get("/googlefit/connect")
async def googlefit_connect(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    connector = GoogleFitConnector()
    auth_url = connector.get_auth_url(str(user.id))
    return RedirectResponse(url=auth_url)


@router.get("/googlefit/callback")
async def googlefit_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db),
):
    if error or not code:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?fit_error=1")

    try:
        connector = GoogleFitConnector()
        token_data = await connector.exchange_code(code)

        if "error" in token_data:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?fit_error=1")

        if not state:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?fit_error=1")

        user = db.query(User).filter(User.id == state).first()
        if not user:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?fit_error=1")

        user.google_fit_token = json.dumps(token_data)
        user.google_fit_connected = True
        db.commit()

        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?fit_connected=1")
    except Exception as e:
        print(f"[GoogleFit] Callback error: {e}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?fit_error=1")


@router.get("/googlefit/analysis")
async def googlefit_analysis(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)

    if not user.google_fit_connected or not user.google_fit_token:
        raise HTTPException(status_code=400, detail="Google Fit not connected")

    try:
        token_data = json.loads(user.google_fit_token)
        connector = GoogleFitConnector(
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
        )
        analysis = await connector.get_full_analysis()

        # Persist refreshed token if it changed
        if connector.access_token != token_data.get("access_token"):
            token_data["access_token"] = connector.access_token
            user.google_fit_token = json.dumps(token_data)
            db.commit()

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Fit analysis failed: {str(e)}")


@router.get("/googlefit/status")
async def googlefit_status(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return {"connected": user.google_fit_connected}


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/status")
async def connectors_status(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return {
        "spotify": user.spotify_connected,
        "google_fit": user.google_fit_connected,
        "notion": user.notion_connected,
    }
