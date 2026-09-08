"""Pydantic schemas for Knowledge Documents and Chunks."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class KnowledgeDocCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field(..., min_length=10)
    document_type: Optional[str] = "guideline"  # guideline, policy, competency_framework
    filename: Optional[str] = None


class ChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class KnowledgeDocResponse(BaseModel):
    id: str
    title: str
    filename: Optional[str] = None
    document_type: str
    chunks_count: int
    created_at: datetime
    chunks: list[ChunkResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class KnowledgeQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3


class KnowledgeQueryResult(BaseModel):
    chunk_id: str
    document_title: str
    document_type: str
    content: str
    similarity_score: float
