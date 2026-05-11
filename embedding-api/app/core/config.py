from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str

    # 💡 데이터베이스 및 벡터 DB 관련 설정 변수 추가
    DATABASE_URL: str
    CHROMADB_PATH: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()