from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..config import BJ_TZ
from . import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, nullable=True, index=True) # Can be linked to a user
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(BJ_TZ))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(BJ_TZ), onupdate=lambda: datetime.now(BJ_TZ))

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", lazy="selectin")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # system, user, assistant, tool
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(BJ_TZ))
    
    # Optional: store tool calls or extra metadata if needed
    # For now, we store JSON in content if it's complex, or just text.
    
    session = relationship("ChatSession", back_populates="messages")
