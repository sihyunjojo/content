import random
import time
from app.repositories.embedding_repository import embedding_repository

class ChromaDiagService:
    """ChromaDB의 연결 상태 및 동작을 진단하는 비즈니스 로직을 담당합니다."""
    def __init__(self, repository):
        self.repository = repository

    def run_connectivity_test(self):
        """ChromaDB 저장 및 조회가 정상적으로 동작하는지 진단합니다."""
        collection_name = "diag_chroma_collection"
        test_id = f"diag_content_{random.randint(1, 10000)}"
        test_vector = [random.random() for _ in range(10)]
        test_text = "이것은 ChromaDB 연결을 진단하기 위한 샘플 콘텐츠입니다."
        
        self.repository.add_content_vector(
            collection_name=collection_name,
            content_id=test_id,
            vector=test_vector,
            text_content=test_text,
            metadata={"category": "diag", "source": "api"},
        )
        time.sleep(1)
        search_results = self.repository.search_similar_contents(
            collection_name=collection_name,
            query_vector=test_vector,
            top_k=5
        )
        found_ids = search_results.get("ids", [[]])[0]
        if test_id in found_ids:
            return {"status": "ok", "message": "ChromaDB 저장 및 조회 진단에 성공했습니다."}
        else:
            return {"status": "error", "message": "ChromaDB 저장 후 조회했으나 해당 ID를 찾을 수 없습니다."}

# 싱글톤 인스턴스 생성
chroma_diag_service = ChromaDiagService(repository=embedding_repository)
