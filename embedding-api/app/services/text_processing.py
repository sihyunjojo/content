import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.schemas.embedding import EmbeddingInputChunk


def preprocess_text(text: str) -> str:
    """
    텍스트에서 HTML 태그를 제거하고 불필요한 공백을 정규화합니다.
    """
    if not text:
        return ""

    # HTML 태그 제거
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")

    # 불필요한 공백 제거 및 정규화
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def chunk_text(
        content_code: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
) -> List[EmbeddingInputChunk]:
    """
    전처리된 텍스트를 재귀적 문자 분할 방식으로 청킹합니다.
    """
    if not text:
        return []

    metadata = metadata or {}

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = text_splitter.split_text(text)

    result = []
    for i, chunk_text in enumerate(chunks):
        chunk_id = f"{content_code}_{i}"

        # 메타데이터에 청크 인덱스 추가 (기존 메타데이터 보존)
        chunk_metadata = metadata.copy()
        chunk_metadata["chunk_index"] = i

        chunk = EmbeddingInputChunk(
            content_code=content_code,
            chunk_id=chunk_id,
            text_content=chunk_text,
            metadata=chunk_metadata
        )
        result.append(chunk)

    return result
