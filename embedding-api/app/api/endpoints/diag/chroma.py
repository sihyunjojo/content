from fastapi import APIRouter
from app.services.diag.chroma_service import chroma_diag_service
from app.repositories.embedding_repository import embedding_repository

router = APIRouter()

@router.get("/connectivity")
def check_chromadb_connectivity():
    """
    실제 데이터 저장/조회를 통해 ChromaDB와의 연결을 종합적으로 진단합니다.
    """
    try:
        heartbeat = embedding_repository.heartbeat()
        result = chroma_diag_service.run_connectivity_test()
        result["chromadb_heartbeat"] = heartbeat
        return result
    except Exception as e:
        return {"status": "error", "message": f"ChromaDB 진단 중 예외 발생: {str(e)}"}
