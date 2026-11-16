from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimestampMixin


class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    title = Column(String(255), nullable=False, index=True)
    source_organization = Column(String(200), default="GBPUAT Pantnagar / ICAR-VPKAS Almora", nullable=False)
    category = Column(String(100), default="Crop Management", nullable=False) # Package of Practices, Pest Management, Soil Health
    publication_date = Column(String(50), default="2025-2026", nullable=False)
    document_type = Column(String(50), default="PDF / Research Bulletin", nullable=False)
    file_path = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=True, nullable=False)

    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base, TimestampMixin):
    __tablename__ = "knowledge_chunks"

    document_id = Column(String(36), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, default=0, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    document = relationship("KnowledgeDocument", back_populates="chunks")
