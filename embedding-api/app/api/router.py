from fastapi import APIRouter
from app.api.diag import chroma as chroma_diag_router, sqlite as sqlite_diag_router
from app.api import pipeline as pipeline_router, search as search_router  # 통합 파이프라인 추가

# 💡 main.py에서 불러 쓸 통합 라우터 인스턴스
api_router = APIRouter()

# --- 진단(Diagnostics) 라우터 ---
api_router.include_router(chroma_diag_router.router, prefix="/diag/chroma", tags=["Diagnostics - ChromaDB"])
api_router.include_router(sqlite_diag_router.router, prefix="/diag/sqlite", tags=["Diagnostics - SQLite"])

# --- 메인 기능 라우터 ---
api_router.include_router(search_router.router, tags=["Search"])

# --- 전처리부터 임베딩/저장까지의 통합 파이프라인 ---
api_router.include_router(pipeline_router.router, prefix="/pipeline", tags=["Pipeline"])
