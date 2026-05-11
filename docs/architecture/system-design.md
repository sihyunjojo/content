# System Design & Architecture

## 1. 아키텍처 개요 (Architecture Overview)
본 시스템은 사용자의 기분, 가용 시간, 선호 플랫폼에 맞추어 콘텐츠를 추천해 주는 RAG(검색 증강 생성) 기반 아키텍처입니다.

**데이터 수집 파이프라인:**
유튜브/라프텔 데이터 수집 ──> FastAPI 적재 스크립트 ──> Embedding ──> 벡터 DB (Chroma)

**실시간 추천 파이프라인:**
사용자 질문 ──> FastAPI 서버 ──> 질문 임베딩 ──> 벡터 DB 검색 (Retrieval) ──> LLM (Generation) ──> 추천 답변 제공

## 2. 기술 스택 (Tech Stack)
* **언어:** Python 3.11+
* **패키지 매니저:** Poetry
* **Backend Framework:** FastAPI (비동기 처리, Pydantic 검증 지원)
* **RAG Orchestration:** LangChain 또는 LlamaIndex
* **Vector Database:** ChromaDB (로컬/개발용) 또는 Qdrant (운영용)
* **Relational Database:** PostgreSQL 또는 SQLite (시청 기록, 전체 메타데이터 관리)

## 3. 핵심 동작 흐름 (Data Flow)

### 3.1 데이터 적재 파이프라인 (Data Ingestion)
1. 유튜브 API, 라프텔 크롤링을 통해 콘텐츠 정보를 수집.
2. 수집된 텍스트(제목, 줄거리 등)를 `text-embedding-3-small` 모델을 통해 벡터화(청킹 및 임베딩).
3. 추출된 벡터 데이터 및 메타데이터(장르, 플랫폼, 러닝타임 등)를 벡터 DB에 저장.

### 3.2 실시간 추천 파이프라인 (RAG Inference)
1. 사용자의 자연어 질문 입력 (예: "오늘 회사에서 힘들었어. 머리 식히며 볼 애니 추천해줘").
2. 입력된 질문을 동일한 임베딩 모델로 벡터 변환.
3. 변환된 질문 벡터로 벡터 DB에서 가장 유사도가 높은 상위 콘텐츠 추출 (Retrieval).
4. 사용자 질문, 추출된 콘텐츠 정보, 지시문을 결합하여 프롬프트 생성.
5. `gpt-4o-mini` 모델이 맥락을 반영한 최종 추천 코멘트와 리스트를 생성하여 응답 (Generation).

## 4. 주요 인프라/설계 결정 사항 (Design Decisions)
* **LLM 및 임베딩 모델 선택:** 개인 프로젝트 특성상 비용 효율성이 중요한 점을 고려하여 가성비가 뛰어난 로컬 llm
* **서버 인프라:** 사용자 1인 기준이므로 경량화된 환경인 오라클 클라우드 프리 티어 또는 AWS EC2 프리 티어(`t3.micro`) (1 vCPU, 1GB~2GB RAM, SSD 10~20GB)에 배포할 수 있도록 설계했습니다.
* **비동기 프레임워크 도입:** 외부 LLM 호출 및 DB 검색 시 발생할 수 있는 병목 현상을 최소화하기 위해 FastAPI를 채택했습니다.