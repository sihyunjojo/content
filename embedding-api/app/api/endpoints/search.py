from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SearchRequest(BaseModel):
    query_text: str

@router.post("/query")
def search_query(payload: SearchRequest):
    """
    사용자의 텍스트 쿼리를 받아 검색 결과를 반환하는 메인 엔드포인트입니다.
    (현재는 임시 응답을 반환합니다.)
    """
    # TODO: 실제 검색 로직을 담당할 서비스(예: SearchService)를 호출해야 합니다.
    return {
        "user_query": payload.query_text,
        "results": ["여기에 실제 검색 결과가 담길 예정입니다."]
    }
