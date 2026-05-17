import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional

from fastapi import Depends
from langchain_community.embeddings import HuggingFaceEmbeddings

# 로컬 유틸리티 및 영속성 레이어 의존성
from app.services.text_processing import preprocess_text, chunk_text
from app.repositories.embedding import EmbeddingRepository, get_embedding_repository

# 독립 격리된 데이터 전송 객체(DTO) 레이어 의존성
from app.schemas.embedding import (
    PipelineRequest,
    PipelineStatistics,
    PipelineResponse
)


class BaseEmbeddingService(ABC):
    """임베딩 서비스 구현을 위한 추상 베이스 클래스"""

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def vector_dimension(self) -> int:
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        pass


class BGEM3EmbeddingService(BaseEmbeddingService):
    """BGE-M3 모델 기반 다국어 특화 임베딩 서비스"""

    def __init__(self, model_name: str = "BAAI/bge-m3", vector_dimension: int = 1024):
        self._model_name = model_name
        self._vector_dimension = vector_dimension
        self._embedding_model = HuggingFaceEmbeddings(model_name=self._model_name)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def vector_dimension(self) -> int:
        return self._vector_dimension

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """HuggingFace 입출력 블로킹 연산을 스레드 풀로 격리하여 비동기 처리"""
        return await asyncio.to_thread(self._embedding_model.embed_documents, texts)

    async def embed_query(self, text: str) -> List[float]:
        """단일 쿼리 임베딩 추출 연산 비동기 처리"""
        return await asyncio.to_thread(self._embedding_model.embed_query, text)


class NomicEmbeddingService(BaseEmbeddingService):
    """Nomic Embed v2 MoE 기반 컨텍스트 특화 임베딩 서비스"""

    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v2-moe", vector_dimension: int = 768):
        self._model_name = model_name
        self._vector_dimension = vector_dimension
        self._embedding_model = HuggingFaceEmbeddings(
            model_name=self._model_name,
            model_kwargs={"trust_remote_code": True}
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def vector_dimension(self) -> int:
        return self._vector_dimension

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """HuggingFace 입출력 블로킹 연산을 스레드 풀로 격리하여 비동기 처리"""
        return await asyncio.to_thread(self._embedding_model.embed_documents, texts)

    async def embed_query(self, text: str) -> List[float]:
        """단일 쿼리 임베딩 추출 연산 비동기 처리"""
        return await asyncio.to_thread(self._embedding_model.embed_query, text)


class EmbeddingFactory:
    """임베딩 서비스 객체를 관리하고 무거운 중복 로드를 방지하는 싱글톤 캐시 팩토리"""

    _registry: Dict[str, Type[BaseEmbeddingService]] = {
        "bge-m3": BGEM3EmbeddingService,
        "nomic-moe": NomicEmbeddingService
    }
    _instances: Dict[str, BaseEmbeddingService] = {}

    @classmethod
    def get_service(cls, model_type: str, model_name: Optional[str] = None,
                    vector_dimension: Optional[int] = None) -> BaseEmbeddingService:
        """설정 기반 고유 키를 활용해 인스턴스를 캐싱 및 반환 (OOM 방지)"""
        model_type_lower = model_type.lower()
        if model_type_lower not in cls._registry:
            supported_models = ", ".join(cls._registry.keys())
            raise ValueError(f"지원하지 않는 임베딩 모델입니다: {model_type}. 지원 목록: [{supported_models}]")

        final_model_name = model_name if model_name and model_name.strip() else "default"
        final_dimension = vector_dimension if vector_dimension else "default"
        cache_key = f"{model_type_lower}:{final_model_name}:{final_dimension}"

        if cache_key not in cls._instances:
            service_class = cls._registry[model_type_lower]
            kwargs = {}
            if model_name and model_name.strip():
                kwargs["model_name"] = model_name
            if vector_dimension:
                kwargs["vector_dimension"] = vector_dimension

            cls._instances[cache_key] = service_class(**kwargs)

        return cls._instances[cache_key]


class EmbeddingPipelineService:
    """텍스트 전처리, 분할, 벡터 변환 및 적재를 관장하는 통합 비즈니스 오케스트레이터"""

    def __init__(self, embedding_repository: EmbeddingRepository):
        self.repo = embedding_repository

    async def run_process_and_embed_pipeline(self, request: PipelineRequest) -> PipelineResponse:
        """입력 텍스트 원본에 대한 정제부터 ChromaDB 영속화까지 통합 파이프라인 수행"""
        embedding_service = EmbeddingFactory.get_service(
            model_type=request.model_type,
            model_name=request.custom_model_name,
            vector_dimension=request.custom_vector_dimension
        )

        cleaned_text = preprocess_text(request.text_content)
        chunks = chunk_text(
            content_code=request.content_code,
            text=cleaned_text,
            metadata=request.metadata,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )

        total_original_chars = len(cleaned_text)

        if not chunks:
            return PipelineResponse(
                message="No chunks generated from the text.",
                model_used=embedding_service.model_name,
                vector_dimension=embedding_service.vector_dimension,
                statistics=PipelineStatistics(
                    total_original_characters=total_original_chars,
                    total_chunks=0,
                    average_chunk_length=0.0
                )
            )

        texts_to_embed = [chunk.text_content for chunk in chunks]
        embeddings = await embedding_service.embed_documents(texts_to_embed)

        await self.repo.add_embeddings(chunks, embeddings)

        total_chunks = len(chunks)
        avg_chunk_len = sum(len(text) for text in texts_to_embed) / total_chunks

        return PipelineResponse(
            message="Successfully processed, embedded, and stored chunks.",
            model_used=embedding_service.model_name,
            vector_dimension=embedding_service.vector_dimension,
            statistics=PipelineStatistics(
                total_original_characters=total_original_chars,
                total_chunks=total_chunks,
                average_chunk_length=round(avg_chunk_len, 2)
            )
        )


def get_embedding_pipeline_service(
        repo: EmbeddingRepository = Depends(get_embedding_repository)
) -> EmbeddingPipelineService:
    """FastAPI Depends용 파이프라인 서비스 의존성 주입 팩토리 인터페이스"""
    return EmbeddingPipelineService(embedding_repository=repo)
