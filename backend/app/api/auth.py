import urllib.parse

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..core.security import create_access_token, verify_token
from ..models.user import User

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/google")
async def google_login():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    query_string = urllib.parse.urlencode(params)
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{query_string}")


@router.get("/google/callback")
async def google_callback(
    code: str = None,
    error: str = None,
    db: Session = Depends(get_db),
):
    if error or not code:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?error=oauth_failed")

    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
            )
            token_data = token_response.json()

            if "access_token" not in token_data:
                return RedirectResponse(url=f"{settings.FRONTEND_URL}?error=token_exchange_failed")

            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            userinfo = userinfo_response.json()

        user = db.query(User).filter(User.google_id == userinfo["sub"]).first()
        if not user:
            existing = db.query(User).filter(User.email == userinfo["email"]).first()
            if existing:
                existing.google_id = userinfo["sub"]
                existing.picture = userinfo.get("picture")
                db.commit()
                db.refresh(existing)
                user = existing
            else:
                user = User(
                    email=userinfo["email"],
                    name=userinfo.get("name", userinfo["email"]),
                    picture=userinfo.get("picture"),
                    google_id=userinfo["sub"],
                )
                db.add(user)
                db.commit()
                db.refresh(user)

        token = create_access_token({"sub": str(user.id)})
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback?token={token}")

    except Exception:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?error=server_error")


@router.get("/me")
async def get_me(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "spotify_connected": user.spotify_connected,
        "google_fit_connected": user.google_fit_connected,
        "notion_connected": user.notion_connected,
    }


@router.get("/debug-config")
async def debug_config():
    """Shows the exact redirect URIs configured — compare with GCP."""
    return {
        "google_redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "google_client_id_set": bool(settings.GOOGLE_CLIENT_ID),
        "frontend_url": settings.FRONTEND_URL,
    }
