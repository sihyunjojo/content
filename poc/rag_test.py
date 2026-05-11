# ==============================================================================
# [RAG 기반 콘텐츠 추천 시스템 - 아키텍처 및 요구사항 검증(PoC) 적합성 보고]
# ==============================================================================
#
# 본 PoC 코드는 아래 설계 문서들의 핵심 가설과 필수 요구사항을 100% 검증하도록 설계되었습니다.
# 1. 시스템 설계서 (System Design & Architecture)
# 2. 기능 명세서 (Feature: RAG 기반 추천 시스템)
#
# ------------------------------------------------------------------------------
# 🎯 [검증 적합성 분석: 설계서 및 요구사항과의 매칭]
# ------------------------------------------------------------------------------
#
# ✅ 1. 아키텍처 및 핵심 동작 흐름 검증 (System Design 1장, 3장)
#    - [설계서 사양]: 데이터 수집 ──> 임베딩 ──> 벡터 DB ──> 유사도 검색 ──> LLM 답변 생성
#    - [PoC 검증]:
#      * 1단계(더미 데이터 준비) 및 2단계(Chroma 적재)를 통해 '데이터 Ingestion' 흐름 검증.
#      * 3단계(사용자 질문 검색) 및 4단계(LLM 답변 생성)를 통해 'RAG Inference' 전체 파이프라인 검증.
#
# ✅ 2. 100% 로컬 및 오픈소스 기술 스택 정합성 검증 (System Design 2장)
#    - [설계서 사양]: Python 3.11, LangChain, ChromaDB, Local 임베딩 및 Local LLM 사용 (외부 API 배제)
#    - [PoC 검증]:
#      * langchain_community 및 langchain_ollama 패키지를 활용한 오프라인 런타임 호환성 확보.
#      * 로컬 메모리상에서 돌아가는 고성능 다국어 임베딩 모델(Nomic v2 MoE / BGE-M3) 탑재 및 인메모리 테스트 검증.
#      * 외부 유료 API 비용 및 보안 우려가 전혀 없는 오픈소스 로컬 LLM(Ollama: Qwen3.5) 연동 흐름 검증.
#      * 추가 인프라 구축 없이 로컬 메모리 상에서 작동하는 'Chroma(In-Memory)'를 통해 빠른 기술 검증.
#
# ✅ 3. 사용자 시나리오 흐름 검증 (Feature 2장)
#    - [명세서 사양]: 사용자 입력 ──> 벡터 DB 검색 ──> 추천 콘텐츠 획득 ──> LLM 프롬프트 전달 및 응답
#    - [PoC 검증]:
#      * 사용자 쿼리("기분이 꿀꿀해... 스트레스 확 풀리는 거 추천해 줄래?") 입력 시,
#        Chroma DB가 '은혼'(스트레스 해소물)을 정확히 찾아 반환하는지 검증.
#      * 찾아낸 '은혼'의 원본 텍스트(Context)를 프롬프트에 합성하여 로컬 LLM이 정확히 인지하는지 검증.
#
# ✅ 4. 상세 요구사항 및 데이터 팩트 제어 검증 (Feature 3장, 4장)
#    - [명세서 사양]: 감정적 미사여구를 배제하고, 철저히 제공된 후보 콘텐츠에 기반해 직관적으로 추천 사유 작성.
#    - [PoC 검증]:
#      * '페르소나 제어 프롬프트'를 적용하여 로컬 LLM이 할루시네이션(환각) 없이 오직 Chroma DB에서 검출된
#        콘텐츠 데이터에만 기반해 담백하고 신뢰성 있는 추천 사유를 작성하는지 검증.
#
# ------------------------------------------------------------------------------
# 🚀 [PoC 실행을 위한 사전 작업 - 100% 오프라인]
# ------------------------------------------------------------------------------
# 1. Ollama 설치 및 로컬 LLM 다운로드:
#    (Ollama 가 구동 중인 상태에서 터미널에 입력)
#    $ ollama pull qwen3.5:1.5b
#
# 2. 가상환경 진입 후 필수 의존성 설치:
#    $ pip install langchain langchain-community langchain-ollama chromadb einops sentence-transformers
#
#    ※ 주의: Nomic MoE 임베딩 구동을 위해 'einops'와 'sentence-transformers' 패키지가 필수적입니다.
#    ※ 외부 API Key(.env)는 전혀 사용하지 않습니다.
# ==============================================================================


# ==============================================================================
# [퇴근 후 콘텐츠 추천 시스템 - RAG PoC(Proof of Concept) 검증 시나리오]
# ==============================================================================
#
# 💡 1. 이 PoC는 무엇을 검증하나요?
#    - 사용자가 기분이나 상황(예: "오늘 회사에서 깨졌어...")을 자연어로 말했을 때,
#    - 벡터 DB(Chroma)에서 "의미상 가장 알맞은 콘텐츠"를 AI가 수학적으로 잘 찾아내는지(Retrieval),
#    - 외부 API 의존성이 전혀 없는 100% 로컬 자원(인메모리 및 로컬 LLM) RAG 아키텍처의 핵심 파이프라인 동작을 검증합니다.
#
# ⚙️ 2. 사전 준비 사항 (로컬 환경 세팅)
#    - Python 3.11+ 및 Poetry(또는 pip) 환경
#    - Ollama 데몬 실행 및 로컬 모델 적재 완료 환경
#
# 🏃‍♂️ 3. 실행 방법
#    $ python <파일명>.py
#
# 🔄 4. 핵심 데이터 흐름 (Data Flow)
#    [더미 데이터] ──> [HuggingFace 로컬 임베딩] ──> [Chroma 벡터 DB (메모리 로드)]
#                                                               │ (유사도 검색)
#    [사용자 질문] ──> [HuggingFace 로컬 임베딩] ──> [가장 적절한 콘텐츠 1개 추출]
#                                                               │
#    [사용자 질문 + 추출된 콘텐츠 + 다정한 프롬프트] ──> [Ollama 로컬 LLM 최종 답변 생성]
# ==============================================================================

import time
import ollama

# 벡터 DB 관련 라이브러리
from langchain_community.vectorstores import Chroma

# RAG 시나리오를 위한 더미 데이터 및 사용자 질문
rag_test_documents = [
    "힐링 캠핑 애니메이션: '유루캠'. 자연 속에서 캠핑하는 여고생들의 잔잔하고 평화로운 일상을 담은 힐링물. 피곤한 퇴근 후 보기 좋습니다.",
    "열혈 액션 판타지: '나의 히어로 아카데미아'. 주인공이 역경을 딛고 최고의 히어로가 되는 가슴 뜨거운 성장물. 동기부여가 필요할 때 좋습니다.",
    "웃음 폭발 개그물: '은혼'. 기상천외한 우주인들과 사무라이들이 얽히는 예측 불허의 코미디. 스트레스를 날려버리고 싶을 때 추천합니다.",
    "잔잔한 일상 유튜브: '플리 채널'. 편안한 로파이 음악과 함께 비 내리는 창밖 풍경을 보여주는 2시간짜리 ASMR 영상. 멍 때리기 좋습니다.",
    "감동적인 영화: '인터스텔라'. 우주를 배경으로 한 SF 영화로, 인류의 생존을 위한 탐험과 가족애를 다룹니다. 깊은 감동과 여운을 선사합니다."
]

rag_test_query = "나는 지금 퇴근하고 오자마자 재밌고 가벼운 컨텐츠를 보고 싶어."


def run_local_rag_poc(embedding_model, model_name: str, documents: list, user_query: str,
                      llm_model_id: str = "qwen3.5:0.8b"):
    """
    OpenAI API Key 없이, 100% 로컬 자원만 사용하여 RAG PoC 시나리오를 구동합니다.
    성능 지표 (임베딩, 검색, 답변 생성 시간)를 반환합니다.
    llm_model_id: 사용할 Ollama LLM 모델의 ID (예: "qwen3.5:2b")
    """
    print(f"\n" + "=" * 60)
    print(f" 🚀 현재 실행 임베딩 모델: [{model_name}] (100% 로컬 구동)")
    print("=" * 60)

    print("--- [1단계] 더미 데이터 준비 ---")
    # documents는 외부에서 전달받습니다.

    print("--- [2단계] 로컬 임베딩 및 Chroma DB 적재 ---")
    start_time = time.perf_counter()

    # 전달받은 HuggingFaceEmbeddings를 활용해 로컬 메모리 안에서 임베딩 진행
    vectorstore = Chroma.from_texts(
        texts=documents,
        embedding=embedding_model,
        collection_name=f"local_poc_{model_name.lower().replace('-', '_')}"
    )

    embed_time = time.perf_counter() - start_time
    print(f"👉 임베딩 및 DB 적재 완료 (소요시간: {embed_time:.4f}초)")

    # 검색기(Retriever) 설정: 유사도가 가장 높은 문서 1개 검출
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

    print("--- [3단계] 사용자 질문 및 검색 (Retrieval) ---")
    # user_query는 외부에서 전달받습니다.

    # Nomic 모델 규격에 맞게 쿼리 접두사 분기 처리
    if "nomic" in model_name.lower():
        search_query = f"search_query: {user_query}"
    else:
        search_query = user_query

    print(f"사용자 질문: {user_query}")

    start_time = time.perf_counter()
    retrieved_docs = retriever.invoke(search_query)
    retrieve_time = time.perf_counter() - start_time

    retrieved_text = "\n".join([doc.page_content for doc in retrieved_docs])
    print(f"👉 검색 완료 (소요시간: {retrieve_time:.4f}초)")
    print(f"\n[검색된 콘텐츠]\n{retrieved_text}\n")

    print("--- [4단계] 프롬프트 합성 및 로컬 LLM 답변 생성 (Generation) ---")

    # ⚠️ 중요: 줄 맨 앞의 모든 들여쓰기를 제거하여 벽 끝에 바짝 붙여서 선언합니다.
    template = """당신은 콘텐츠 추천 봇입니다. 아래 제공된 추천 후보 콘텐츠를 바탕으로 질문에 자연스럽고 위트 있게 답변해 주세요. 제공된 콘텐츠 이외의 정보는 절대 가공하거나 지어내어 말하지 마세요.

    ### 추천 후보 콘텐츠:
    {context}

    ### 사용자 질문:
    {question}

    답변:"""

    formatted_prompt = template.format(context=retrieved_text, question=user_query)

    print("로컬 LLM 답변 생성 중 (Ollama SDK 직접 연산 & 스트리밍)... \n")
    start_time = time.perf_counter()

    # [개선 2] LangChain ChatOllama의 Qwen3.5 파싱 버그를 완벽히 우회하기 위해 Ollama SDK를 직접 사용합니다.
    print("🤖 로컬 AI의 추천 답변:")

    try:
        # [Ollama SDK 직접 호출 - 동기 방식]
        # LangChain ChatOllama의 내부 파싱 버그(Thinking 태그 필터링 중 한글 답변 유실)를
        # 완벽히 우회하기 위해 로우 레벨(Raw Level)의 Ollama 공식 Python SDK를 사용합니다.
        # pytest 환경에서의 Stdout 버퍼 가로채기(Capture) 현상으로 인한 데이터 누수를 방지하고자
        # stream=False(동기 호출) 옵션을 적용하여 API 응답 전체를 단일 객체로 안전하게 확보합니다.
        api_response = ollama.generate(
            model=llm_model_id,
            prompt=formatted_prompt,
            stream=False,  # True 설정 시 실시간 생성(Generator) 모드로 동작하며, False 시 최종 답변 완료 후 반환됨

            # 모델의 텍스트 생성 경향과 인프라 제어를 위한 세부 튜닝 옵션
            options={
                # [temperature]: 답변의 창의성 및 무작위성 제어 (범위: 0.0 ~ 2.0)
                # - 0.2: 결정론적(Deterministic) 답변에 가까운 저온(Low Temp) 설정.
                # - RAG 아키텍처에서 제공된 '추천 후보 콘텐츠'의 팩트(Fact) 테두리를 벗어나지 않고,
                #   허구의 정보를 지어내는 할루시네이션(환각)을 극도로 억제하면서도 미세한 표현의 자연스러움을 살림.
                "temperature": 0.2,

                # [num_predict]: 최대 생성 토큰(단어) 수 제한 (기존 LLM의 max_tokens와 동일)
                # - 300: 문맥 추론 단계에서 답변이 도중에 뚝 끊겨버리는 현상을 원천 방지하는 안정적인 크기.
                # - 특히 Qwen3.5와 같은 추론형 모델은 최종 응답(response) 전에 생각 과정(thinking)을 먼저 전개하므로,
                #   이 값이 너무 작으면 생각 단계에서 제한 값을 다 소진해 실제 추천 사유를 뱉지 못하는 버그를 유발함.
                # - 리소스 낭비와 무한 루프 폭주를 완벽히 통제하면서도 온전한 한글 문장 출력을 보장하는 최적의 한계선.
                "num_predict": 300,

                # [top_p]: 누적 확률 필터링 (Nucleus Sampling, 범위: 0.0 ~ 1.0, 기본값: 0.9)
                # - 단어를 선택할 때 누적 확률이 p% 이내인 단어 후보군들만 남기고 나머지는 과감히 필터링함.
                # - 예: 0.9로 설정 시 상위 90% 안에 드는 상식적인 단어들만 후보로 삼아 엉뚱한 외계어가 나오는 것을 방지.
                # - temperature와 시너지를 이루어 '너무 산으로 가지 않는 선에서의 창의적인 문장'을 완성함.
                "top_p": 0.9,

                # [top_k]: 최상위 후보 단어 개수 제한 (범위: 1 이상 정수, 기본값: 40)
                # - 단어를 고를 때 확률이 가장 높은 최상위 K개의 단어만 후보군으로 강제 제한함.
                # - 예: 40 설정 시 아무리 무작위 온도가 높더라도 상위 40위 밖의 완전히 뚱딴지같은 단어는 절대 선택되지 않음.
                # - 이 값이 너무 작으면 로봇처럼 지극히 뻔한 단어만 반복해서 쓰고, 너무 크면 문맥 흐름이 어색해짐.
                "top_k": 40,

                # [repeat_penalty]: 동일 단어 및 문장 반복 억제 가중치 (범위: 0.0 ~ 2.0, 기본값: 1.1)
                # - 1.0보다 큰 값을 주면 모델이 이전에 뱉었던 단어를 다시 반복할 때 패널티(감점)를 부여함.
                # - qwen3.5:2b 같은 경량 모델이 특정 공백이나 한글 조사, 혹은 "추천합니다"라는 말을 무한 앵무새처럼
                #   반복해서 뱉으며 루프에 갇히는 현상을 수학적으로 제어해 주는 아주 고마운 속성.
                "repeat_penalty": 1.1,

                # ==============================================================================
                # 2. 컨텍스트 및 메모리 스펙 제어 (Context & Memory)
                # ==============================================================================

                # [num_ctx]: 컨텍스트 윈도우 크기 설정 (단위: 토큰 수, 기본값: 2048)
                # - 모델이 한 번에 머릿속에 기억할 수 있는 입력(프롬프트 + Vector DB 검색 결과)과 출력의 최대 총합 크기.
                # - RAG 파이프라인 구축 시 수많은 참고 문서(Context)를 우겨 넣어야 할 때 이 값을 4096이나 8192로 늘려야 함.
                # - 이 값이 너무 작으면 과거 대화나 전달한 참고 문서를 LLM이 앞부분부터 망각(Truncate)하기 시작함.
                # - 단, 애플 실리콘 맥에서 이 값을 너무 늘리면 통합 메모리(RAM) 점유율이 올라가 가속 성능이 저하될 수 있음.
                "num_ctx": 4096,

                # ==============================================================================
                # 3. 인프라 가속 및 스레드 제어 (Hardware & Multi-Threading)
                # ==============================================================================

                # [num_thread]: 연산에 사용할 CPU 코어/스레드 개수 (기본값: 시스템 최적 코어 수 자동 지정)
                # - 로컬 하드웨어 리소스를 얼마나 집중해서 태울지 수동으로 제한을 걸어주는 속성.
                # - 백그라운드에 웹 서버나 DB, 다른 개발 툴을 동시에 띄워놓고 PoC 테스트를 수행할 때,
                #   맥북 전체 시스템이 LLM 연산 때문에 완전히 멈춰버리는(Freeze) 병목을 방지하기 위해 스레드를 수동 제한함.
                # - M1 Pro 8코어 기준, 시스템 안정성을 확보하려면 4나 6 정도로 지정해 두는 것이 멀티태스킹에 용이함.
                "num_thread": 6,

                # [num_gqa]: Grouped-Query Attention 그룹 수 (고급 아키텍처 제어 속성)
                # - 디바이스 VRAM 및 캐시 메모리 대역폭 점유를 최적화하여 큰 컨텍스트(num_ctx)에서도 추론 속도가
                #   느려지지 않게 방어해 주는 속성으로, 특정 소형 모델 미세 조정 시 하드웨어 캐시 최적화에 사용됨.
                # "num_gqa": 8,

                # [stop]: 모델 생성을 즉시 정지시킬 텍스트 패턴 시퀀스 (Stop Sequence)
                # - 모델이 텍스트를 쭉 생성하다가 아래 배열에 포함된 문자열을 만나는 순간, 즉시 문장 완성을 멈추고 제어를 반환함.
                # - RAG 프롬프트 템플릿 아래쪽에 "### 사용자 질문:"이나 "### 답변 완료" 같은 구분선 패턴을 정의해 두고
                #   이를 stop 속성에 넣어두면, LLM이 1인 다역으로 가상의 대화를 혼자 이어서 폭주하는 현상을 완벽히 차단함.
                "stop": ["### 사용자 질문:", "\n\n\n"]
            }
        )

        # 응답 구조 파싱
        if isinstance(api_response, dict):
            raw_content = api_response.get("response", "").strip()
            thinking_content = api_response.get("thinking", "").strip()
        else:
            raw_content = getattr(api_response, "response", "").strip()
            thinking_content = getattr(api_response, "thinking", "").strip()

        # 만약 생각(thinking) 영역만 채워지고 최종 답변(response)이 비어있다면,
        # 사용자가 진행 상황을 볼 수 있도록 생각 메커니즘 텍스트를 답변으로 즉시 치환합니다.
        if (not raw_content or raw_content == "") and thinking_content:
            # 생각 과정 텍스트를 최종 답변으로 우회 대입해 줍니다.
            response = f"[추론 답변]\n{thinking_content}"
        else:
            response = raw_content

    except Exception as e:
        print(f"\n❌ Ollama 호출 중 에러 발생: {e}")
        response = f"Ollama 엔진 호출 중 예외 발생: {str(e)}"

        # 양끝 여백 정리
    response = response.strip()

    # 최종 안전장치
    if not response or response.strip() == "":
        response = f"[경고] 응답 수신은 성공했으나 데이터가 비어있습니다."

    generation_time = time.perf_counter() - start_time

    # 터미널에 답변 깔끔하게 출력
    print(response)
    print("\n")

    print(f"👉 답변 생성 완료 (소요시간: {generation_time:.2f}초)")
    print("=" * 60 + "\n")

    return {
        "model_name": model_name,
        "embed_time": embed_time,
        "retrieve_time": retrieve_time,
        "generation_time": generation_time,
        "retrieved_text": retrieved_text,
        "llm_response": response
    }
