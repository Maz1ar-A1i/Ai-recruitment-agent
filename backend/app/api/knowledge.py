"""Knowledge Base and RAG REST API endpoints."""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.knowledge import KnowledgeDocument, DocumentChunk
from app.schemas.knowledge import (
    KnowledgeDocCreate,
    KnowledgeDocResponse,
    KnowledgeQueryRequest,
    KnowledgeQueryResult,
)
from app.rag.document_processor import chunk_text
from app.rag.vector_store import rag_store
from app.tools.resume_parser import extract_text_from_bytes

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


@router.post("", response_model=KnowledgeDocResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_doc(payload: KnowledgeDocCreate, db: Session = Depends(get_db)):
    """Create a knowledge document from text and index its chunks in the RAG store."""
    doc_id = str(uuid.uuid4())
    chunks = chunk_text(payload.content)

    doc = KnowledgeDocument(
        id=doc_id,
        title=payload.title,
        filename=payload.filename,
        content=payload.content,
        document_type=payload.document_type or "guideline",
        chunks_count=len(chunks)
    )
    db.add(doc)

    for idx, c in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        chunk_entity = DocumentChunk(
            id=chunk_id,
            document_id=doc_id,
            chunk_index=idx,
            content=c,
            metadata_json={"document_id": doc_id, "title": payload.title}
        )
        db.add(chunk_entity)
        rag_store.add_chunk(
            chunk_id=chunk_id,
            document_title=payload.title,
            document_type=payload.document_type or "guideline",
            content=c,
            metadata={"document_id": doc_id}
        )

    db.commit()
    db.refresh(doc)
    return doc


@router.post("/upload", response_model=KnowledgeDocResponse, status_code=status.HTTP_201_CREATED)
async def upload_knowledge_file(
    file: UploadFile = File(...),
    title: str = Form(None),
    document_type: str = Form("guideline"),
    db: Session = Depends(get_db)
):
    """Upload a knowledge file (PDF, DOCX, TXT) and index chunks for RAG."""
    filename = file.filename or "guideline.txt"
    file_bytes = await file.read()

    try:
        content = extract_text_from_bytes(file_bytes, filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    if not content or len(content.strip()) < 10:
        raise HTTPException(status_code=400, detail="File content is too short or empty.")

    effective_title = title or filename.rsplit(".", 1)[0].replace("_", " ").title()
    payload = KnowledgeDocCreate(
        title=effective_title,
        content=content,
        document_type=document_type,
        filename=filename
    )
    return create_knowledge_doc(payload, db)


@router.get("", response_model=list[KnowledgeDocResponse])
def list_knowledge_docs(db: Session = Depends(get_db)):
    """List all knowledge documents."""
    docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()
    return docs


@router.get("/{doc_id}", response_model=KnowledgeDocResponse)
def get_knowledge_doc(doc_id: str, db: Session = Depends(get_db)):
    """Retrieve details and chunks of a knowledge document."""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Knowledge document with ID '{doc_id}' not found.")
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_doc(doc_id: str, db: Session = Depends(get_db)):
    """Delete a knowledge document and remove its chunks from the RAG store."""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Knowledge document with ID '{doc_id}' not found.")

    rag_store.delete_by_document_id(doc_id)
    db.delete(doc)
    db.commit()
    return None


@router.post("/query", response_model=list[KnowledgeQueryResult])
def query_knowledge_base(payload: KnowledgeQueryRequest):
    """Query the RAG vector store for relevant knowledge guidelines and policies."""
    results = rag_store.query(payload.query, top_k=payload.top_k or 3)
    return results
