import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
