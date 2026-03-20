import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text

from ..core.database import Base
from ..core.types import GUID


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey("users.id"))
    analysis_date = Column(DateTime, default=datetime.utcnow)
    overall_wellness_score = Column(Float, nullable=True)
    linguistic_score = Column(Float, nullable=True)
    consumption_score = Column(Float, nullable=True)
    behavioral_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    linguistic_details = Column(Text, nullable=True)
    consumption_details = Column(Text, nullable=True)
    behavioral_details = Column(Text, nullable=True)
    predictions = Column(Text, nullable=True)
    insights = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class RawData(Base):
    __tablename__ = "raw_data"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey("users.id"))
    source = Column(String)
    data_type = Column(String)
    raw_content = Column(Text)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
