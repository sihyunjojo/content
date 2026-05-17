from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query_text: str = Field(..., description="사용자가 입력한 검색어 (예: 특정 장르, 분위기, 스토리 등을 설명하는 문장)")


class SearchResponse(BaseModel):
    user_query: str = Field(..., description="요청 시 전달받은 원본 검색어")
    results: list[str] = Field(..., description="검색된 추천 콘텐츠 목록 (현재는 임시 응답)")
