# 최소한의 텍스트 전처리 및 청킹 (Minimal Text Preprocessing & Chunking)

이 문서는 RAG(Retrieval Augmented Generation) 시스템에서 임베딩을 위해 수집된 텍스트 데이터를 가공하는 최소한의 필수적인 전처리 및 청킹 전략을 정의합니다. 사용자에게 이미 "선별된 데이터"가 있다고 가정하더라도, 임베딩 모델의 제약사항과 검색 정확도 향상을 위해 이 단계는 여전히 중요합니다.

## 0. 전처리 모듈 입력 데이터 구조 (Preprocessing Module Input Data Structure)

텍스트 전처리 및 청킹 모듈의 입력으로 예상되는 데이터 구조는 다음과 같습니다. 이는 SQLite에 저장된 원본 데이터 레코드에서 텍스트 콘텐츠를 추출하여 전달하는 형태가 될 것입니다.

-   **`content_code` (str)**: 각 콘텐츠를 고유하게 식별하는 코드. 플랫폼별 접두사를 포함하여 어떤 플랫폼의 콘텐츠인지 추측 가능하게 합니다. (예: `youtube-VIDEOID123`, `laftel-ANIMEID456`)
-   **`text_content` (str)**: 전처리 및 청킹이 필요한 실제 텍스트 내용. (예: 유튜브 자막, 동영상 설명, 라프텔 줄거리 등)
-   **`metadata` (dict, optional)**: 해당 텍스트와 관련된 추가 메타데이터. (예: 제목, 장르, 사용자 평점 등)

**예시 입력 데이터:**
```python
{
    "content_code": "youtube-VIDEOID123",
    "text_content": "<html><p>이것은 <b>유튜브</b> 동영상의 자막입니다. <a href='...'>링크</a></p></html>",
    "metadata": {
        "title": "재미있는 영상",
        "genre": "코미디",
        "user_rating": 9
    }
}
```

## 1. 왜 필요한가? (Why it's Essential)

1.  **임베딩 모델의 토큰 제한**: 대부분의 임베딩 모델은 한 번에 처리할 수 있는 텍스트 길이에 엄격한 제한이 있습니다. 아무리 잘 선별된 데이터라도 이 제한을 초과하면 임베딩 자체가 불가능합니다.
2.  **검색 정확도 향상**: RAG 시스템의 핵심은 사용자의 질문에 가장 관련성 높은 정보를 효율적으로 찾아내는 것입니다. 긴 텍스트를 의미 있는 작은 단위(청크)로 나누면, 특정 질문에 대한 관련성이 높은 청크를 정확하게 검색할 확률이 높아집니다.
3.  **임베딩 품질 유지**: 불필요한 노이즈(특수 문자, 과도한 공백 등)는 임베딩 모델이 텍스트의 핵심 의미를 파악하는 데 방해가 될 수 있습니다. 기본적인 전처리는 임베딩 품질을 일정 수준으로 유지하는 데 기여합니다.

## 2. 최소한의 텍스트 전처리 (Minimal Text Preprocessing)

선별된 데이터라고 하더라도, 임베딩 모델의 효율적인 처리를 위해 다음의 기본적인 전처리 단계를 거치는 것이 좋습니다.

-   **불필요한 공백 제거 및 정규화**: 여러 개의 공백을 하나의 공백으로 줄이고, 텍스트 양 끝의 공백을 제거합니다. 이는 텍스트의 일관성을 유지하고, 불필요한 토큰 생성을 방지합니다.
    -   **예시**: `re.sub(r'\s+', ' ', text).strip()`
-   **HTML 태그 제거 (선택적이지만 권장)**: 웹에서 수집된 데이터의 경우, 눈에 보이지 않는 HTML 태그가 포함되어 있을 수 있습니다. 이는 임베딩 품질을 저하시킬 수 있으므로 제거하는 것이 좋습니다.
    -   **예시**: `BeautifulSoup` 라이브러리 활용

## 3. 텍스트 청킹 (Text Chunking)

임베딩 모델의 토큰 제한을 준수하고 검색 정확도를 높이기 위해, 전처리된 텍스트는 반드시 의미 있는 청크로 분할되어야 합니다.

-   **재귀적 문자 분할 (Recursive Character Text Splitting)**: 가장 권장되는 기본적인 청킹 전략입니다.
    -   **원리**: 텍스트를 다양한 구분자(예: `\n\n`, `\n`, `.`, ` ` 등)를 사용하여 재귀적으로 분할합니다. 이는 의미 있는 경계를 최대한 유지하면서 텍스트를 작은 단위로 나눌 수 있게 합니다.
    -   **청크 크기 (Chunk Size)**: 임베딩 모델의 최대 입력 길이를 고려하여 적절한 크기를 설정합니다. (예: 500~1000 토큰)
    -   **청크 오버랩 (Chunk Overlap)**: 청크 간에 약간의 중복을 두어, 한 청크의 끝과 다음 청크의 시작 부분에서 문맥이 끊어지는 것을 방지합니다. (예: 50~100 토큰)
    -   **권장 라이브러리**: `LangChain`의 `RecursiveCharacterTextSplitter`를 사용하면 쉽게 구현할 수 있습니다.

### 3.1. 청킹 결과 데이터 구조 (Chunking Output Data Structure)

전처리 및 청킹 모듈의 최종 출력은 **바로 다음 파이프라인인 임베딩 추출(`text_embedding_extraction.md`) 기능의 입력으로 직접 연결(Pydantic 스키마 연동)**됩니다. 각 청크는 원본 콘텐츠의 `content_code`와 메타데이터를 함께 포함해야 합니다.

```python
[
    {
        "content_code": "youtube-VIDEOID123",
        "chunk_id": "youtube-VIDEOID123_0", # content_code와 청크 인덱스를 조합한 고유 ID
        "text_content": "이것은 유튜브 동영상의 자막입니다. 첫 번째 청크 내용...",
        "metadata": {
            "title": "재미있는 영상",
            "genre": "코미디",
            "user_rating": 9,
            "chunk_index": 0 # 몇 번째 청크인지
        }
    },
    {
        "content_code": "youtube-VIDEOID123",
        "chunk_id": "youtube-VIDEOID123_1",
        "text_content": "두 번째 청크 내용입니다. 문맥 유지를 위한 오버랩...",
        "metadata": {
            "title": "재미있는 영상",
            "genre": "코미디",
            "user_rating": 9,
            "chunk_index": 1
        }
    }
    # ...
]
```

## 4. 구현 시 고려사항

-   **라이브러리 활용**: Python의 `re` 모듈(정규 표현식), `BeautifulSoup` (HTML 파싱), `LangChain` (텍스트 스플리터) 등을 활용하면 효율적으로 구현할 수 있습니다.
-   **토큰 계산**: `chunk_size`를 설정할 때는 사용하려는 임베딩 모델의 토크나이저를 사용하여 실제 토큰 수를 계산하는 것이 가장 정확합니다. (예: `tiktoken` 라이브러리)

## 5. 실제 구현 단계 (Actionable Steps)

이러한 최소한의 전처리 및 청킹 단계를 `embedding-api` 프로젝트 내에서 구현하기 위한 구체적인 지침입니다.

1.  **필요 라이브러리 설치 확인**:
    -   `pyproject.toml` 파일에 `beautifulsoup4` (HTML 태그 제거용) 및 `langchain-text-splitters` (청킹용) 의존성이 추가되어 있는지 확인합니다.
    -   만약 없다면, `poetry add beautifulsoup4 langchain-text-splitters` 명령어를 통해 추가합니다.

2.  **전처리 및 청킹 모듈 생성**:
    -   `embedding-api/app/services/` 디렉토리 내에 `text_processing.py` 파일을 생성합니다.
    -   이 파일 안에 `preprocess_text` 함수와 `chunk_text` 함수를 정의합니다. (위 예시 코드 참조)

3.  **`preprocess_text` 함수 구현**:
    -   `re` 모듈을 사용하여 불필요한 공백을 제거하고 텍스트를 정규화하는 로직을 작성합니다.
    -   웹 스크래핑 데이터의 경우 `BeautifulSoup`를 사용하여 HTML 태그를 제거하는 로직을 추가합니다.

4.  **`chunk_text` 함수 구현**:
    -   `langchain_text_splitters.RecursiveCharacterTextSplitter`를 사용하여 텍스트를 청킹하는 로직을 작성합니다.
    -   `chunk_size`와 `chunk_overlap` 매개변수를 적절히 설정합니다. (예: `chunk_size=500`, `chunk_overlap=50`)

5.  **데이터 수집 스크립트(`collect_youtube_data.py`)와 연동**:
    -   데이터 수집 스크립트에서 원본 텍스트 데이터를 가져온 후, `text_processing.py`의 함수들을 호출하여 전처리 및 청킹을 수행합니다.
    -   청킹된 결과는 다음 단계인 **임베딩 추출 모듈(`text_embedding_extraction.md` 참조)**로 전달될 준비가 됩니다.

### 5.1. 전처리된 데이터의 처리 방식 (How Processed Data is Handled)

전처리 및 청킹을 거친 텍스트 데이터(청크)는 별도의 영구 저장소에 저장되지 않습니다. 대신, 다음과 같은 흐름으로 처리됩니다.

1.  **다음 단계(임베딩)로 전달**: 각 텍스트 청크 데이터(`chunk_id`, `content_code`, `text_content`, `metadata`)는 곧바로 **임베딩 모듈(`text_embedding_extraction.md`)**로 전달되어 벡터로 변환됩니다.
2.  **벡터 DB 저장 (ChromaDB)**: 생성된 임베딩 벡터와 메타데이터는 포인터 역할을 하는 `content_code`와 함께 **ChromaDB에 저장**됩니다.
3.  **원본 데이터 참조 (SQLite)**: RAG 시스템에서 추천 시, ChromaDB 검색 결과로 나온 `content_code`를 사용하여 **SQLite에서 콘텐츠 상세 정보(원본 데이터)를 다시 조회(JOIN)**하여 활용합니다.

이러한 최소한의 전처리 및 청킹 단계를 통해, 선별된 데이터가 임베딩 모델에 최적화되어 RAG 시스템의 성능을 극대화할 수 있습니다.
