import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# 💡 SQLite 설정인 경우, 데이터베이스 파일이 저장될 폴더가 없다면 자동으로 만들어줍니다.
if settings.DATABASE_URL.startswith("sqlite"):
    # "sqlite:///./data/metadata.db" 에서 "./data/metadata.db" 경로만 추출합니다.
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()