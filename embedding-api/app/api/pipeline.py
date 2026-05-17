from fastapi import APIRouter, HTTPException, Depends, Body
from app.services.embedding import (
    PipelineRequest,
    PipelineResponse,
    EmbeddingPipelineService,
    get_embedding_pipeline_service
)

router = APIRouter()


@router.post("/process-and-embed", response_model=PipelineResponse, summary="텍스트 전처리부터 벡터 저장까지 통합 파이프라인 수행")
async def process_and_embed_pipeline(
        request: PipelineRequest = Body(
            ...,
            openapi_examples={
                "default_example": {
                    "summary": "애니메이션 리뷰 기본 예시",
                    "description": "장송의 프리렌 리뷰 데이터를 기반으로 BGE-M3 모델 임베딩을 수행하는 예시입니다.",
                    "value": {
                        "content_code": "youtube-vX8_2k9lq",
                        "text_content": "이번 영상에서는 최고의 명작 애니메이션 '장송의 프리렌'을 리뷰해 보겠습니다. 주인공 프리렌이 용사 일행과 마왕을 토벌한 후의 이야기를 다루고 있는데요. 화려한 액션보다는 잔잔한 감동과 인간 관계에 대한 깊은 철학을 담고 있습니다. 작화 퀄리티부터 OST까지 무엇 하나 빠지지 않는 추천작입니다.",
                        "model_type": "bge-m3",
                        "custom_model_name": "BAAI/bge-m3",
                        "custom_vector_dimension": 1024,
                        "metadata": {
                            "title": "[리뷰] 잔잔한 감동의 갓작 '장송의 프리렌'",
                            "genre": "애니메이션 리뷰",
                            "platform": "youtube"
                        },
                        "chunk_size": 300,
                        "chunk_overlap": 50
                    }
                }
            }
        ),
        pipeline_service: EmbeddingPipelineService = Depends(get_embedding_pipeline_service)
):
    """
    한 번의 API 호출로 입력된 텍스트 데이터를 전처리하고 임베딩하여 벡터 DB에 저장합니다.

    - **1. 텍스트 전처리**: HTML 태그를 제거하고 다중 공백을 하나로 정규화합니다.
    - **2. 텍스트 청킹**: 설정된 `chunk_size` 및 `chunk_overlap` 기준으로 텍스트를 나눕니다.
    - **3. 임베딩 추출**: 요청 시 지정한 `model_type`과 파라미터를 기반으로 동적으로 모델을 선택해 벡터로 변환합니다.
    - **4. DB 저장**: 변환된 벡터와 식별자(`content_code`), 기타 `metadata`를 묶어 ChromaDB에 안전하게 보관합니다.
    """
    if not request.text_content:
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")

    try:
        # 모든 비즈니스 로직은 서비스 레이어가 캡슐화하여 처리
        return await pipeline_service.run_process_and_embed_pipeline(request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
