from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import verify_token
from ..models.user import User

router = APIRouter()


def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/profile")
async def get_profile(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "spotify_connected": user.spotify_connected,
        "google_fit_connected": user.google_fit_connected,
        "notion_connected": user.notion_connected,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.delete("/account")
async def delete_account(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    db.delete(user)
    db.commit()
    return {"message": "Account deleted successfully"}
