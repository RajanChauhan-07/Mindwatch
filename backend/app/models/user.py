import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text

from ..core.database import Base
from ..core.types import GUID


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=False)
    spotify_connected = Column(Boolean, default=False)
    spotify_token = Column(Text, nullable=True)
    google_fit_connected = Column(Boolean, default=False)
    google_fit_token = Column(Text, nullable=True)
    notion_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
