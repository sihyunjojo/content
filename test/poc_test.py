import time

# rag_test.py에서 정의된 RAG 시나리오 데이터와 실행 함수를 임포트합니다.
from poc.rag_test import rag_test_documents, rag_test_query, run_local_rag_poc

# 임베딩 모델 로드를 위한 라이브러리
from langchain_community.embeddings import HuggingFaceEmbeddings


def test_rag_performance_comparison():
    """
    다양한 임베딩 모델을 사용하여 RAG PoC 시나리오의 성능을 비교하고 결과를 보고합니다.
    """
    print("=" * 80)
    print(" 🚀 RAG PoC 임베딩 모델 성능 비교 테스트를 시작합니다.")
    print("=" * 80)

    all_results = {}
    
    # 사용할 LLM 모델 ID를 정의합니다.
    # 필요에 따라 다른 LLM 모델을 여기에 추가하여 비교할 수 있습니다.
    # qwen3.5:2b
    # llama3:8b
    # ~/.ollama/models/
    # todo : ollama run qwen3.5:0.8b
    # 위 코드를 선제적으로 해주어야지 해당 모델을 찾아 들어감.
    # llm_to_use = "qwen3.5:0.8b"
    # todo : ollama pull qwen3.5:2b
    llm_to_use = "qwen3.5:2b"

    # 1. Nomic Embed v2 MoE 모델 검증
    print("\n[초기화] Nomic Embed v2 MoE 로컬 메모리 로드 중...")
    nomic_embeddings = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v2-moe",
        model_kwargs={"trust_remote_code": True}
    )
    nomic_results = run_local_rag_poc(
        embedding_model=nomic_embeddings,
        model_name="Nomic-MoE-v2",
        documents=rag_test_documents,
        user_query=rag_test_query,
        llm_model_id=llm_to_use # LLM 모델 ID 전달
    )
    all_results["Nomic-MoE-v2"] = nomic_results

    # 2. BGE-M3 모델 검증
    print("\n[초기화] BGE-M3 로컬 메모리 로드 중...")
    bge_embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3"
    )
    bge_results = run_local_rag_poc(
        embedding_model=bge_embeddings,
        model_name="BGE-M3",
        documents=rag_test_documents,
        user_query=rag_test_query,
        llm_model_id=llm_to_use # LLM 모델 ID 전달
    )
    all_results["BGE-M3"] = bge_results

    print("\n" + "=" * 90)
    print(" 📊 RAG PoC 임베딩 모델 성능 비교 리포트")
    print("=" * 90)

    # 모델별 메트릭 정보 출력
    print(f"{'메트릭':<30} | " + " | ".join([f"{name:^25}" for name in all_results.keys()]))
    print("-" * 90)

    # 임베딩 시간
    embed_time_row = [f"{all_results[name]['embed_time']:.4f}초" for name in all_results.keys()]
    print(f"{'[*] 임베딩 및 DB 적재 시간':<30} | " + " | ".join([f"{t:^25}" for t in embed_time_row]))

    # 검색 시간
    retrieve_time_row = [f"{all_results[name]['retrieve_time']:.4f}초" for name in all_results.keys()]
    print(f"{'[*] 검색 (Retrieval) 시간':<30} | " + " | ".join([f"{t:^25}" for t in retrieve_time_row]))

    # 답변 생성 시간
    generation_time_row = [f"{all_results[name]['generation_time']:.4f}초" for name in all_results.keys()]
    print(f"{'[*] 답변 생성 (Generation) 시간':<30} | " + " | ".join([f"{t:^25}" for t in generation_time_row]))
    print("-" * 90)

    # 검색된 콘텐츠 비교
    print(f"\n{'[검색된 콘텐츠 비교]':<90}")
    for model_name, results in all_results.items():
        print(f"\n--- [{model_name}] 검색된 콘텐츠 ---")
        print(results['retrieved_text'])

    # LLM 답변 비교
    print(f"\n{'[LLM 답변 비교]':<90}")
    for model_name, results in all_results.items():
        print(f"\n--- [{model_name}] LLM 답변 ---")
        print(results['llm_response'])

    print("\n" + "=" * 90)
    print(" ✅ RAG PoC 임베딩 모델 성능 비교 테스트 완료.")
    print("=" * 90)


if __name__ == "__main__":
    test_rag_performance_comparison()
