from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import verify_token
from ..models.analysis import ChatMessage
from ..models.user import User
from ..services.chatbot import MindWatchChatbot

router = APIRouter()
chatbot = MindWatchChatbot()


def get_current_user(token: str, db: Session) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    spotify_data: Optional[Dict[str, Any]] = None
    youtube_data: Optional[Dict[str, Any]] = None
    whatsapp_data: Optional[Dict[str, Any]] = None


@router.post("/message")
async def send_message(
    request: ChatRequest,
    token: str,
    db: Session = Depends(get_db),
):
    user = get_current_user(token, db)

    response = await chatbot.chat(
        message=request.message,
        history=request.history or [],
        spotify_data=request.spotify_data,
        youtube_data=request.youtube_data,
        whatsapp_data=request.whatsapp_data,
    )

    chat_msg = ChatMessage(
        user_id=user.id,
        message=request.message,
        response=response,
    )
    db.add(chat_msg)
    db.commit()

    return {"response": response}


@router.get("/starters")
async def get_conversation_starters(token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    return {
        "starters": [
            "How is my mental wellness looking based on my data?",
            "What does my music taste say about my mood?",
            "Am I showing any signs of stress or anxiety?",
            "What patterns do you notice in my digital behavior?",
            "How can I improve my wellness score?",
            "What's my predicted mood for the next week?",
        ]
    }
