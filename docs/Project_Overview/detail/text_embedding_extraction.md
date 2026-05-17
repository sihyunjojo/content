# 텍스트 임베딩 추출

이 문서는 텍스트 전처리(`text_processing.md`) 이후에 수행되는 텍스트 임베딩 추출 기능의 구현 상세 및 설계 가이드라인을 정의합니다. `ai_recommendation_system_architecture.md`에 명시된 RAG 파이프라인의 데이터 적재 및 검색 단계와 밀접하게 연동됩니다.

## 기능 개요
* **목적:** 전처리된 콘텐츠 텍스트(유튜브/라프텔 데이터 등)와 사용자의 질문을 벡터 형태의 임베딩(숫자 배열)으로 변환하는 것입니다.

## 주요 요구 사항
* **임베딩 모델 교체 가능성 (Pluggable Embedding Model):** 
  현재 사용할 구체적인 임베딩 모델(예: text-embedding-3-small 등)은 명확히 고정되지 않았거나 향후 변경될 수 있습니다. 시스템(FastAPI 등) 전체 구조에 영향을 주지 않도록 유연하게 설계되어야 합니다. 
  임베딩 추출 기능은 특정 모델에 종속되지 않도록 인터페이스(예: LangChain/LlamaIndex 래퍼)를 통해 추상화되어야 하며, 의존성 주입(DI)이나 환경 변수 설정 등을 통해 구체적인 모델 구현체를 쉽게 변경할 수 있도록 구현해야 합니다.

## 설계해야 할 주요 사안

1. **공통 임베딩 인터페이스 및 모델 어댑터 (Interface & Adapter):**
   * `LangChain` 등의 RAG 오케스트레이션 도구에서 제공하는 기본 임베딩 클래스를 상속받거나, 독자적인 `BaseEmbeddingService` 프로토콜을 정의합니다.
   * `OpenAIEmbedding`, `HuggingFaceEmbedding` 등 여러 모델을 갈아끼울 수 있는 어댑터 패턴을 구현합니다.

2. **비동기 배치 메서드 설계 (Async Batching):**
   * `async def embed_documents(texts: list[str]) -> list[list[float]]` 형식의 비동기 다중 처리 인터페이스를 구성합니다.
   * 사용자 쿼리용 단일 임베딩 `async def embed_query(text: str) -> list[float]` 도 함께 설계합니다.

3. **환경 변수 기반 모델 팩토리 (Configuration via Poetry/Env):**
   * `.env` 파일과 `pydantic-settings`를 활용하여 런타임에 사용할 임베딩 모델의 종류, 차원(Dimension), API Key 등을 관리하고, 팩토리 패턴을 통해 적절한 클래스를 반환하도록 구성합니다.

---

## 데이터 구조 및 처리 파이프라인 (Data Pipeline & Schema)

이 섹션은 원본 텍스트가 어떻게 수치화(Embedding)되고, 최종적으로 벡터 DB(ChromaDB)에 어떤 형태로 적재되는지 그 원리와 구조를 상세히 설명합니다.

### 1. 입력 데이터 구조 (Input Schema)
`text_processing.md` 모듈에서 전달되는 단일 청크(Chunk, 의미 단위로 분할된 텍스트)의 명세입니다. 임베딩의 대상이 되는 텍스트 원본과, 이후 검색 및 데이터 조인에 필요한 메타데이터를 포함합니다.

```python
class EmbeddingInputChunk(BaseModel):
    content_code: str                 # 콘텐츠 식별 코드 (예: youtube-VIDEOID)
    chunk_id: str                     # 청크 고유 식별자 (예: youtube-VIDEOID_0)
    text_content: str                 # 벡터화 대상 원본 텍스트 (예: "오늘 회사에서 있었던 일...")
    metadata: dict[str, Any]          # 장르, 플랫폼 등 필터링을 위한 부가 정보
```

### 2. 임베딩 모델의 변환 원리 (Embedding Process)
임베딩 모델(예: OpenAI의 `text-embedding-3-small`)의 유일한 역할은 **"인간의 언어(텍스트)를 기계가 의미(Semantic)를 이해하고 계산할 수 있는 다차원 수치 배열(벡터)로 변환"**하는 것입니다.

*   **변환 과정:** `EmbeddingInputChunk` 내의 `text_content`만을 추출하여 모델에 입력합니다.
*   **출력 결과:** 모델은 해당 텍스트의 의미적 좌표를 나타내는 고정된 길이의 실수 배열(Float Array)을 반환합니다.
    *   *예시 (차원이 1536인 모델의 경우):* `text_content` ➜ `[0.0123, -0.0456, 0.1129, ..., -0.0034]` (총 1536개의 숫자)

이 변환된 숫자 배열(`embeddings`)을 통해 기계는 텍스트 간의 수학적 거리(예: 코사인 유사도)를 계산하여 "의미가 비슷한" 텍스트를 찾아낼 수 있습니다.

### 3. 출력 및 벡터 DB 저장 구조 (Vector DB Ingestion Schema)

임베딩 모듈의 최종 목적은 **"변환된 임베딩 벡터"와 "그 벡터가 무엇을 의미하는지 알려주는 원본/메타데이터"를 하나로 결합하여 벡터 DB에 적재 가능한 표준 포맷으로 구성하는 것**입니다.

단순히 숫자 배열(벡터)만 벡터 DB에 저장하면, 검색 시스템이 해당 벡터를 찾더라도 "이 숫자가 원래 어떤 텍스트였는지" 복원할 수 없습니다. 따라서 벡터 DB는 유사도 검색을 위한 **벡터 데이터**와, 검색 이후 식별을 위한 **메타데이터(Payload)**를 하나의 레코드(Record)로 묶어 관리합니다.

#### 3.1. 벡터 DB 레코드의 3대 구성 요소
1. **ID (`ids`)**: 각 청크를 유일하게 식별하는 키입니다. (`chunk_id` 사용)
2. **Embedding (`embeddings`)**: 모델이 생성한 다차원 수치 배열. (기계가 유사도 검색을 수행하는 기준)
3. **Metadata (`metadatas`)**: 벡터에 부여되는 '페이로드(Payload)'. 검색 결과로 반환되어 LLM에게 제공될 원본 텍스트(`original_text`)와, SQLite 마스터 데이터와의 조인을 위한 외래 키(`content_code`), 그리고 메타데이터 필터링(예: "유튜브 플랫폼만 검색")에 사용될 정보가 모두 포함됩니다.

#### 3.2. 데이터 적재 스펙 (ChromaDB API 기준)
실제 구현 시, 입력된 텍스트 리스트를 벡터화한 후 아래와 같은 스펙으로 벡터 DB에 삽입(`add`)합니다.

```python
# ChromaDB Data Ingestion Specification
chroma_collection.add(
    # 1. 고유 식별자 (ID)
    ids=[chunk.chunk_id for chunk in input_chunks],             
    
    # 2. 벡터화 (Embedding)
    # text_content들을 모델에 통과시켜 얻은 숫자 배열 리스트
    embeddings=embed_model.embed_documents([chunk.text_content for chunk in input_chunks]), 
    
    # 3. 페이로드 (Metadata)
    # 검색 완료 후 반환되어 사용될 실제 텍스트 및 조인 키 정보
    metadatas=[{                                                
        "content_code": chunk.content_code,                     # RDBMS 조인용 Foreign Key
        "original_text": chunk.text_content,                    # RAG 프롬프트 구성을 위한 원본 텍스트
        **chunk.metadata                                        # 부가 필터링 데이터 (플랫폼, 장르 등)
    } for chunk in input_chunks]
)
```

**※ 요약:** 임베딩 모듈은 텍스트를 기계가 읽을 수 있는 숫자(`embeddings`)로 변환하고, 이를 다시 인간/LLM이 읽을 수 있는 원본 텍스트/정보(`metadatas`)와 함께 묶어 벡터 DB에 저장하는 역할을 수행합니다.

**※ 참고:** 벡터 DB(ChromaDB)와 정형 DB(SQLite)의 상세한 저장소 분담 및 RAG 검색 흐름은 전체 아키텍처 문서(`ai_recommendation_system_architecture.md`)를 참고하시기 바랍니다.