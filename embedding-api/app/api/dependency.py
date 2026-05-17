from typing import Generator
from app.core.database import SessionLocal


def get_db() -> Generator:
    """
    API 요청이 들어올 때 DB 세션을 생성하고,
    요청 처리가 끝나면(성공하든 에러가 나든) 안전하게 세션을 닫아줍니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
