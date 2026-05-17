from fastapi import APIRouter
from app.services.diag.sqlite_service import sqlite_diag_service
from pydantic import BaseModel, Field

router = APIRouter()


class SQLiteDiagResponse(BaseModel):
    status: str = Field(..., description="진단 결과 상태 (예: 'ok', 'error')")
    message: str = Field(..., description="진단 결과에 대한 상세 메시지")


@router.get("/connectivity", response_model=SQLiteDiagResponse, summary="SQLite 연결 및 상태 진단")
def check_sqlite_connectivity():
    """
    현재 시스템이 메타데이터 저장용 SQLite 데이터베이스와 정상적으로 통신할 수 있는지 확인합니다.
    간단한 테스트용 테이블 생성, 데이터 삽입 및 조회를 통해 R/W 권한과 연결 상태를 검증합니다.
    """
    try:
        result = sqlite_diag_service.run_connectivity_test()
        return result
    except Exception as e:
        return {"status": "error", "message": f"SQLite 진단 중 예외 발생: {str(e)}"}
