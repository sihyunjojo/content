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
    # response_chunks = []
    #
    # try:
    #     # 실시간 스트리밍 생성 옵션(stream=True)을 켭니다.
    #     stream_response = ollama.generate(
    #         model=llm_model_id,
    #         prompt=formatted_prompt,
    #         stream=True,
    #         options={
    #             "temperature": 0.0,  # 창의성을 제한하여 엉뚱한 루프에 빠지는 현상 원천 차단
    #             "num_predict": 256  # 답변 중간 잘림과 공백 출력을 방지하는 최적의 단어 수 제한
    #         }
    #     )
    #
    #     # 글자가 생성되는 즉시 터미널 화면에 뿌려주어 대기 시 답답함을 완벽히 해소합니다.
    #     for chunk in stream_response:
    #         text = chunk.get("response", "")
    #         print(text, end="", flush=True)
    #         response_chunks.append(text)
    #
    # except Exception as e:
    #     print(f"\n❌ Ollama 호출 중 에러 발생: {e}")
    #     response_chunks = ["Ollama 엔진과의 연결에 실패하여 답변을 생성할 수 없습니다."]
    #
    # print("\n")  # 스트리밍 완료 후 개행 처리
    #
    # # 모인 단어 조각들을 하나의 문장으로 예쁘게 묶어줍니다.
    # response = "".join(response_chunks).strip()
    #
    # # 혹시 모를 오작동으로 결과가 비어 있을 경우를 대비한 가혹 조건 안전장치
    # if not response or response.strip() == "":
    #     response = "로컬 LLM 응답을 수집했으나 비어 있는 값만 반환되었습니다."
    #     #     response = str(raw_response)
    #
    # generation_time = time.perf_counter() - start_time
    #
    # print(f"👉 답변 생성 완료 (소요시간: {generation_time:.2f}초)")
    # print("=" * 60 + "\n")

    try:
        # stream=False로 하나의 완벽한 dict 응답을 즉시 받아옵니다.
        api_response = ollama.generate(
            model=llm_model_id,
            prompt=formatted_prompt,
            stream=False,
            options={
                "temperature": 0.0,  # 일관된 답변을 위해 무작위성 제거
                "num_predict": 300,  # 답변이 중간에 잘리지 않도록 크기 소폭 상향
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

    # [수정] OpenAI 대신 로컬에 실행 중인 Ollama의 Qwen 모델을 호출합니다.
    # llm_model_id 매개변수를 사용하여 LLM 모델을 설정합니다.
    # 필요 이상으로 답변이 길어져 늘어지는 현상을 방지
    # HTTP 통신 대기 시간을 명시적으로 넉넉히 설정 (타임아웃 폭사 방지)
    # num_predict 제한을 없애서 답변이 잘리지 않고 끝까지 온전하게 완성되도록 만듭니다.
    # local_llm = ChatOllama(model=llm_model_id, temperature=0.5, num_predict=128, timeout=60)
    # local_llm = ChatOllama(model=llm_model_id, temperature=0.5, timeout=1200)

    # qwen3.5:0.8b는 매개변수가 매우 적은 극초경량 모델입니다.
    # 온도를 0.5로 주어 무작위성을 주면 프롬프트 지시사항을 무시하고 혼자 엉뚱한 토큰을 뱉다가 길을 잃고 무한 반복 상태에 빠지기 아주 쉽습니다.
    # temperature를 0.0으로 설정하여 모델이 엉뚱한 루프에 빠지는 것을 원천 차단합니다.
    # num_predict를 넉넉하게 256 혹은 512로 설정해 적절한 길이에서 멈추도록 안전장치를 둡니다.

    # # [temperature]: 답변의 창의성 및 무작위성 조절 (범위: 0.0 ~ 2.0)
    # # - 0.0: 완전한 결정론적 답변. 항상 가장 확률이 높은 단어만 선택 (RAG, 팩트 체크, 코드 작성에 필수).
    # # - 0.7 ~ 1.0: 일상적인 대화나 소설 쓰기 등 창의적이고 다양한 아이디어가 필요할 때 권장.
    # # - 높은 값을 줄수록 경량 모델(0.8b 등)은 헛소리(할루시네이션)를 하거나 무한 루프에 빠질 확률이 급증함.
    # temperature = 0.0,
    #
    # # [top_p]: 누적 확률 필터링 (Nucleus Sampling, 범위: 0.0 ~ 1.0)
    # # - 누적 확률이 p% 이내인 후보 단어군 중에서만 다음 단어를 선택함.
    # # - 예: 0.9로 설정 시, 상위 90% 확률에 드는 단어들만 후보로 두고 나머지는 과감히 배제.
    # # - temperature와 함께 사용되어 답변의 지나친 엇나감을 방지하는 안전망 역할을 함.
    # top_p = 0.9,
    #
    # # [top_k]: 후보 단어 개수 제한 (범위: 1 이상 정수)
    # # - 다음 단어를 예측할 때 확률이 가장 높은 상위 K개의 단어 중에서만 고르도록 강제함.
    # # - 예: 40으로 설정 시, 아무리 창의적인 모드(high temperature)여도 상위 40개 밖의 생뚱맞은 단어는 절대 안 씀.
    # # - 값이 낮을수록 답변이 일관되고 평이해지며, 높을수록 표현이 풍부해짐.
    # top_k = 40,
    #
    # # ==============================================================================
    # # 2. 텍스트 길이 및 멈춤 제어 (Length & Stopping)
    # # ==============================================================================
    #
    # # [num_predict]: 최대 생성 토큰(단어) 수 제한 (Ollama 고유 속성, 기존 max_tokens와 동일)
    # # - 이 값을 지정해 두면 모델이 폭주하여 무한 루프를 돌더라도 설정한 토큰 수에서 강제 제동을 걸어 끊어줌.
    # # - 경량 모델은 간결한 답변이 핵심이므로 256~512 정도로 걸어두는 것이 인프라 리소스 및 속도 면에서 매우 안전함.
    # num_predict = 256,
    #
    # # [stop]: 답변 생성을 즉시 멈출 특정 문자열(Stop Sequence) 리스트
    # # - 모델이 답변을 하다가 이 리스트에 지정된 단어(예: "\n", "질문:", "###")를 만나면 강제로 생성을 종료함.
    # # - RAG 프롬프트 템플릿과 연동하여 LLM이 혼자 북치고 장구치며 1인 다역(질문과 답변을 혼자 생성하는 현상)을 하는 것을 차단할 때 유용함.
    # stop = ["### 사용자 질문:", "\n\n"],
    #
    # # ==============================================================================
    # # 3. 인프라 및 네트워크 제어 (Infrastructure & Network)
    # # ==============================================================================
    #
    # # [timeout]: Ollama 서버와의 HTTP 통신 최대 대기 시간 (초 단위)
    # # - 로컬에서 대용량 모델을 처음 로드하거나 리소스 부족으로 답변이 지연될 때, 연결이 갑자기 폭사(Timeout Error)하는 것을 방지함.
    # # - GPU 성능이 여유롭지 않은 로컬 개발 환경에서는 최소 60초 이상 넉넉히 주는 것이 안전함.
    # timeout = 60,
    #
    # # [num_ctx]: 컨텍스트 윈도우 크기 설정 (기본값은 보통 2048 또는 4096)
    # # - 모델이 한 번에 기억하고 처리할 수 있는 최대 토큰 수 (프롬프트 + 참고 문서 + 생성할 답변 전체 합산).
    # # - RAG 성능 향상을 위해 참고 문서를 많이 쑤셔 넣어야 할 때 이 값을 4096 이나 8192 등으로 늘려서 사용함.
    # # - 단, 값을 너무 크게 잡으면 VRAM(메모리) 점유율이 늘어나 맥북이 버벅거릴 수 있음.
    # num_ctx = 4096

    # 이전 버전의 그거
    # local_llm = ChatOllama(
    #     model=llm_model_id,
    #     temperature=0.0,
    #     num_predict=256,
    #     timeout=60
    # )
    #
    # rag_chain = prompt | local_llm
    #
    # print("로컬 LLM 답변 생성 중 (GPU/CPU 연산)... \n")
    # start_time = time.perf_counter()
    # raw_response = rag_chain.invoke({
    #     "context": retrieved_text,
    #     "question": user_query
    # })
    #
    # # AIMessage 객체에서 가장 확실하게 텍스트 본문만 뽑아냅니다.
    # if hasattr(raw_response, 'content'):
    #     response = raw_response.content
    # else:
    #     response = str(raw_response)
    #
    # # 만약 완전히 공백으로 출력된다면, 날것의 출력을 그대로 대입해 줍니다.
    # if not response or response.strip() == "":
    #     response = str(raw_response)
    #
    # generation_time = time.perf_counter() - start_time
    #
    # print(f"🤖 로컬 AI의 추천 답변:\n{response}")
    # print(f"👉 답변 생성 완료 (소요시간: {generation_time:.2f}초)")
    # print("=" * 60 + "\n")

    return {
        "model_name": model_name,
        "embed_time": embed_time,
        "retrieve_time": retrieve_time,
        "generation_time": generation_time,
        "retrieved_text": retrieved_text,
        "llm_response": response
    }
