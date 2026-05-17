import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings


class ChromaRepository:
    def __init__(self):
        """
        ChromaDB 클라이언트 초기화 및 연결을 담당합니다.
        설정은 .env 파일에서 관리됩니다.
        """
        self.client = chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT,
            settings=ChromaSettings(allow_reset=settings.CHROMADB_ALLOW_RESET)
        )

    def get_or_create_collection(self, collection_name: str):
        """
        컬렉션을 가져오거나 새로 생성합니다.
        """
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_content_vector(self, collection_name: str, content_id: str, vector: list[float], text_content: str,
                           metadata: dict):
        """
        컨텐츠의 임베딩 벡터와 메타데이터를 저장합니다.
        [WORKAROUND] KeyError('_type') 오류 우회를 위해 documents와 metadatas를 일시적으로 비활성화합니다.
        이는 chromadb 라이브러리 특정 버전의 버그일 수 있습니다.
        """
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            ids=[content_id],
            embeddings=[vector]
            # documents=[text_content], # WORKAROUND
            # metadatas=[metadata]      # WORKAROUND
        )

    def search_similar_contents(self, collection_name: str, query_vector: list[float], top_k: int = 5):
        """
        유사한 컨텐츠를 검색합니다.
        """
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

    def heartbeat(self):
        """ChromaDB 서버의 상태를 확인합니다."""
        return self.client.heartbeat()


# 싱글톤 인스턴스 생성
chroma_repository = ChromaRepository()
