from fastapi import APIRouter
from app.services.diag.chroma_service import chroma_diag_service
from app.repositories.chroma_repository import chroma_repository
from pydantic import BaseModel, Field

router = APIRouter()


class ChromaDiagResponse(BaseModel):
    status: str = Field(..., description="진단 결과 상태 (예: 'ok', 'error')")
    message: str = Field(..., description="진단 결과에 대한 상세 메시지")
    chromadb_heartbeat: int | None = Field(None, description="ChromaDB 서버에서 반환한 현재 시간(나노초 단위), 연결 실패 시 null")


@router.get("/connectivity", response_model=ChromaDiagResponse, summary="ChromaDB 연결 및 상태 진단")
def check_chromadb_connectivity():
    """
    현재 시스템이 ChromaDB 벡터 데이터베이스와 정상적으로 통신할 수 있는지 확인합니다.
    - 서버 핑(Heartbeat) 체크
    - 간단한 테스트 데이터 삽입 및 조회(Round-trip) 테스트를 수행합니다.
    """
    try:
        heartbeat = chroma_repository.heartbeat()
        result = chroma_diag_service.run_connectivity_test()
        result["chromadb_heartbeat"] = heartbeat
        return result
    except Exception as e:
        return {"status": "error", "message": f"ChromaDB 진단 중 예외 발생: {str(e)}"}
