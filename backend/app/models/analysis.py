import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    analysis_date = Column(DateTime, default=datetime.utcnow)
    overall_wellness_score = Column(Float, nullable=True)
    linguistic_score = Column(Float, nullable=True)
    consumption_score = Column(Float, nullable=True)
    behavioral_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    linguistic_details = Column(JSON, nullable=True)
    consumption_details = Column(JSON, nullable=True)
    behavioral_details = Column(JSON, nullable=True)
    predictions = Column(JSON, nullable=True)
    insights = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class RawData(Base):
    __tablename__ = "raw_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    source = Column(String)
    data_type = Column(String)
    raw_content = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
