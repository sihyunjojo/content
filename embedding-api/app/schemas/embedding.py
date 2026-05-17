# app/schemas/embedding.py 새로 생성

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class EmbeddingInputChunk(BaseModel):
    content_code: str
    chunk_id: str
    text_content: str
    metadata: dict


class PipelineRequest(BaseModel):
    content_code: str
    text_content: str
    model_type: str = "bge-m3"
    custom_model_name: Optional[str] = None
    custom_vector_dimension: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    chunk_size: int = 500
    chunk_overlap: int = 50


class PipelineStatistics(BaseModel):
    total_original_characters: int
    total_chunks: int
    average_chunk_length: float


class PipelineResponse(BaseModel):
    message: str
    model_used: str
    vector_dimension: int
    statistics: PipelineStatistics
