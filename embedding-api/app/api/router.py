from fastapi import APIRouter
from app.api.endpoints.diag import chroma as chroma_diag_router
from app.api.endpoints.diag import sqlite as sqlite_diag_router
from app.api.endpoints import search as search_router

# 💡 main.py에서 불러 쓸 통합 라우터 인스턴스
api_router = APIRouter()

# --- 진단(Diagnostics) 라우터 ---
api_router.include_router(chroma_diag_router.router, prefix="/diag/chroma", tags=["Diagnostics - ChromaDB"])
api_router.include_router(sqlite_diag_router.router, prefix="/diag/sqlite", tags=["Diagnostics - SQLite"])

# --- 메인 기능 라우터 ---
api_router.include_router(search_router.router, tags=["Search"])
