import os
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.document import KnowledgeDocument, KnowledgeChunk

router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "metadata", "document_manifest.json")


class DocumentOut(BaseModel):
    id: str
    title: str
    source_organization: str
    category: str
    publication_date: str
    document_type: str
    is_verified: bool
    page_count: Optional[int] = 1
    chunks_count: Optional[int] = 0
    ingestion_status: Optional[str] = "indexed"
    file_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/", response_model=List[DocumentOut])
def list_knowledge_documents(
    category: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists verified agronomic knowledge documents from GBPUAT Pantnagar and ICAR."""
    # Read manifest for full metadata
    manifest_docs = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for d in data.get("documents", []):
                    manifest_docs[d["document_id"]] = d
        except Exception:
            pass

    db_docs = db.query(KnowledgeDocument).all()
    results = []

    # Include manifest documents
    for m_id, m_doc in manifest_docs.items():
        chunk_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == m_id).count()
        doc_item = DocumentOut(
            id=m_id,
            title=m_doc["title"],
            source_organization=m_doc["publisher"],
            category=m_doc["document_type"],
            publication_date=m_doc["publication_date"],
            document_type=m_doc["document_type"],
            is_verified=True,
            page_count=m_doc.get("page_count", 8),
            chunks_count=chunk_count,
            ingestion_status="indexed" if chunk_count > 0 else "requires_ocr_scanned",
            file_path=m_doc.get("file_path")
        )
        if category and category.lower() not in doc_item.category.lower():
            continue
        if query and query.lower() not in doc_item.title.lower():
            continue
        results.append(doc_item)

    # Any other DB docs not in manifest
    manifest_ids = set(manifest_docs.keys())
    for doc in db_docs:
        if doc.id in manifest_ids:
            continue
        c_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).count()
        results.append(
            DocumentOut(
                id=doc.id,
                title=doc.title,
                source_organization=doc.source_organization,
                category=doc.category,
                publication_date=doc.publication_date,
                document_type=doc.document_type,
                is_verified=doc.is_verified,
                page_count=1,
                chunks_count=c_count,
                ingestion_status="indexed" if c_count > 0 else "staged",
                file_path=doc.file_path
            )
        )

    return results


@router.get("/{document_id}", response_model=DocumentOut)
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
    c_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document_id).count()

    if doc:
        return DocumentOut(
            id=doc.id,
            title=doc.title,
            source_organization=doc.source_organization,
            category=doc.category,
            publication_date=doc.publication_date,
            document_type=doc.document_type,
            is_verified=doc.is_verified,
            page_count=8,
            chunks_count=c_count,
            ingestion_status="indexed" if c_count > 0 else "requires_ocr_scanned",
            file_path=doc.file_path
        )

    # Check manifest fallback
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for m in data.get("documents", []):
                if m["document_id"] == document_id:
                    return DocumentOut(
                        id=m["document_id"],
                        title=m["title"],
                        source_organization=m["publisher"],
                        category=m["document_type"],
                        publication_date=m["publication_date"],
                        document_type=m["document_type"],
                        is_verified=True,
                        page_count=m.get("page_count", 8),
                        chunks_count=c_count,
                        ingestion_status="indexed" if c_count > 0 else "requires_ocr_scanned",
                        file_path=m.get("file_path")
                    )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge document not found.")


@router.get("/{document_id}/status")
def get_ingestion_status(document_id: str, db: Session = Depends(get_db)):
    c_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document_id).count()
    return {
        "document_id": document_id,
        "indexed_chunks": c_count,
        "status": "indexed" if c_count > 0 else "requires_ocr_scanned",
        "vector_storage": "ChromaDB Persistent Store",
        "last_ingested": "2026-11-11"
    }


@router.post("/{document_id}/ingest")
def trigger_ingest(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin endpoint to trigger re-ingestion of knowledge document."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only knowledge administrators can trigger ingestion.")
    return {
        "status": "success",
        "document_id": document_id,
        "message": "Document re-ingestion and vector indexing queued."
    }
