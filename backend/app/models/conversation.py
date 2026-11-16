from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), default="Agricultural Consultation", nullable=False)

    farmer = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base, TimestampMixin):
    __tablename__ = "conversation_messages"

    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_role = Column(String(50), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)
    retrieved_sources = Column(JSON, default=list, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
