from fastapi import APIRouter
from pydantic import BaseModel

# 💡 main.py에서 불러 쓸 통합 라우터 인스턴스
api_router = APIRouter()

# 1. 헬스체크 API
@api_router.get("/health")
def health_check():
    return {"status": "ok", "message": "API 라우터가 정상적으로 연결되었습니다."}

# 2. 검색 요청 바디 정의 (Pydantic)
class SearchRequest(BaseModel):
    query_text: str  # 사용자가 입력한 검색어/질문

# 3. 실시간 임베딩 및 검색 API
@api_router.post("/query")
def search_query(payload: SearchRequest):
    # 나중에 여기서 ChromaDB 유사도 비교를 수행하게 됩니다.
    return {
        "user_query": payload.query_text,
        "results": ["여기에 검색된 결과 텍스트가 담겨 나갈 예정입니다."]
    }