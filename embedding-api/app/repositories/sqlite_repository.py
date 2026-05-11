import sqlite3
from app.core.config import settings, PROJECT_ROOT

class SQLiteRepository:
    def __init__(self):
        """
        SQLite 데이터베이스 연결을 관리합니다.
        DATABASE_URL을 기반으로 절대 경로를 생성합니다.
        """
        # 1. 상대 경로를 가져옵니다. (예: ./test.db)
        relative_db_path = settings.DATABASE_URL.split("///")[1]
        
        # 2. 프로젝트 루트를 기준으로 절대 경로를 생성합니다.
        self.db_path = PROJECT_ROOT / relative_db_path
        
        # 3. 데이터베이스 파일이 위치할 디렉터리가 존재하지 않으면 생성합니다.
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._create_table_if_not_exists()

    def _get_connection(self):
        """데이터베이스 커넥션을 반환합니다."""
        return sqlite3.connect(self.db_path)

    def _create_table_if_not_exists(self):
        """진단 로그를 저장할 테이블을 생성합니다."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diag_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def add_log(self, message: str) -> int:
        """진단 로그를 추가하고, 생성된 로그의 ID를 반환합니다."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO diag_logs (log_message) VALUES (?)", (message,))
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_log_by_id(self, log_id: int) -> tuple | None:
        """ID로 특정 로그를 조회합니다."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, log_message FROM diag_logs WHERE id = ?", (log_id,))
        log = cursor.fetchone()
        conn.close()
        return log

# 싱글톤 인스턴스 생성
sqlite_repository = SQLiteRepository()
