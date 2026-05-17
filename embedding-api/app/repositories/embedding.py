from typing import List
from app.schemas.embedding import EmbeddingInputChunk
from app.core.database import chroma_client


class EmbeddingRepository:
    def __init__(self, default_collection_prefix: str = "content_embeddings"):
        self.default_collection_prefix = default_collection_prefix

    def _get_collection(self, dimension: int):
        # 벡터 차원이나 모델별로 컬렉션을 분리하여 차원 충돌(Dimension mismatch)을 방지합니다.
        collection_name = f"{self.default_collection_prefix}_{dimension}d"
        return chroma_client.get_or_create_collection(name=collection_name)

    async def add_embeddings(self, chunks: List[EmbeddingInputChunk], embeddings: List[List[float]]):
        if not embeddings:
            return

        # 첫 번째 임베딩의 차원 수를 확인하여 동적으로 컬렉션을 가져옵니다.
        dimension = len(embeddings[0])
        collection = self._get_collection(dimension)

        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [
            {
                "content_code": chunk.content_code,
                "original_text": chunk.text_content,
                **chunk.metadata
            }
            for chunk in chunks
        ]

        # ChromaDB 클라이언트의 API 특성에 맞게 수정
        # 비동기 처리가 필요하지만 현재 chromadb python client는 동기입니다.
        # 필요시 asyncio.to_thread 등을 활용할 수 있지만 일단 동기로 호출합니다.
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )


# 의존성 주입을 위한 팩토리 함수
def get_embedding_repository() -> EmbeddingRepository:
    return EmbeddingRepository()
