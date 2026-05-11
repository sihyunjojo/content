from fastapi import APIRouter
from app.services.diag.sqlite_service import sqlite_diag_service

router = APIRouter()

@router.get("/connectivity")
def check_sqlite_connectivity():
    """
    실제 데이터 저장/조회를 통해 SQLite와의 연결을 종합적으로 진단합니다.
    """
    try:
        result = sqlite_diag_service.run_connectivity_test()
        return result
    except Exception as e:
        return {"status": "error", "message": f"SQLite 진단 중 예외 발생: {str(e)}"}
