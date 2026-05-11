import random
from app.repositories.sqlite_repository import sqlite_repository

class SQLiteDiagService:
    """SQLite의 연결 상태 및 동작을 진단하는 비즈니스 로직을 담당합니다."""
    def __init__(self, repository):
        self.repository = repository

    def run_connectivity_test(self):
        """SQLite 저장 및 조회가 정상적으로 동작하는지 진단합니다."""
        log_message = f"SQLite 진단 로그_{random.randint(1, 10000)}"
        
        log_id = self.repository.add_log(log_message)
        if not log_id:
            return {"status": "error", "message": "SQLite에 로그 저장 실패."}

        retrieved_log = self.repository.get_log_by_id(log_id)
        if retrieved_log and retrieved_log[1] == log_message:
            return {"status": "ok", "message": "SQLite 저장 및 조회 진단에 성공했습니다."}
        else:
            return {"status": "error", "message": "SQLite 저장 후 조회했으나 데이터가 일치하지 않습니다."}

# 싱글톤 인스턴스 생성
sqlite_diag_service = SQLiteDiagService(repository=sqlite_repository)
