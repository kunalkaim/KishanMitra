from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ChatMessageInput(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=2, json_schema_extra={"example": "What are the recommended sowing times and varieties for rice in Uttarakhand?"})
    crop_context: Optional[str] = None
    district_context: Optional[str] = "Haridwar"


class KnowledgeSourceOut(BaseModel):
    source_id: Optional[str] = None
    document_title: str
    publisher: Optional[str] = "Directorate of Extension Education, GBPUAT Pantnagar"
    source_organization: str
    category: str
    publication_date: Optional[str] = "2020-05-02"
    page_start: Optional[int] = 1
    page_end: Optional[int] = 1
    source_url: Optional[str] = None
    relevance_score: float
    snippet: str
    is_historical: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class ChatMessageOut(BaseModel):
    id: str
    sender_role: str
    content: str
    answer_mode: Optional[str] = "rag"
    retrieval_status: Optional[str] = "success"
    generation_status: Optional[str] = "success"
    provider_name: Optional[str] = "Google Gemini"
    has_historical_warning: Optional[bool] = False
    follow_up_questions: Optional[List[str]] = []
    retrieved_sources: List[KnowledgeSourceOut] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageOut] = []

    model_config = ConfigDict(from_attributes=True)


class RetrieveInput(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=3, ge=1, le=10)
    crop_filter: Optional[str] = None
    district_filter: Optional[str] = None


class RetrieveOutput(BaseModel):
    query: str
    chunks_count: int
    results: List[Dict[str, Any]]


class KnowledgeStatsOut(BaseModel):
    # High-level overview statistics
    total_documents: int
    indexed_documents: int
    scanned_documents: int
    total_knowledge_chunks: int
    
    # Granular, reconciled statistics distinguishing catalogued, physical, relational, and vector layers
    total_catalogued_documents: int
    physically_staged_documents: int
    documents_successfully_extracted: int
    extracted_pages: int
    generated_chunks: int
    relational_chunk_records: int
    active_vector_embeddings: int
    documents_pending_ocr: int

    embedding_dimension: int
    embedding_model: str
    vector_store: str
    supported_languages: List[str]
    state_coverage: str
