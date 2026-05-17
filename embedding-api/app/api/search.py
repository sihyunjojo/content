from fastapi import APIRouter, Body
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/query", response_model=SearchResponse, summary="사용자 쿼리 기반 추천 콘텐츠 검색")
def search_query(
        payload: SearchRequest = Body(
            ...,
            openapi_examples={
                "default_example": {
                    "summary": "자연어 기반 애니메이션 추천 검색",
                    "description": "사용자가 원하는 분위기나 스토리의 키워드를 입력하여 관련 콘텐츠를 검색하는 예시입니다.",
                    "value": {
                        "query_text": "주인공이 먼치킨인데 힘을 숨기고 일상 생활을 하는 힐링 판타지 애니메이션 추천해줘"
                    }
                }
            }
        )
):
    """
    사용자의 자연어 질문(쿼리)을 입력받아, 가장 유사한 콘텐츠를 검색하여 반환합니다.
    (현재는 임시 응답을 반환하며, 향후 ChromaDB 및 SQLite와 연동된 RAG 검색 로직이 추가될 예정입니다.)
    """
    # TODO: 실제 검색 로직을 담당할 서비스(예: SearchService)를 호출해야 합니다.
    return SearchResponse(
        user_query=payload.query_text,
        results=["[임시 응답] 빙검의 마술사가 세계를 다스린다", "[임시 응답] 전생했더니 슬라임이었던 건에 대하여"]
    )
