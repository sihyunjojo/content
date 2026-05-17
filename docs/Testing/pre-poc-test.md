# 🛠️ RAG 테스트 실행 전 체크리스트 (3단계)

## 1단계: 백그라운드에서 Ollama 서버 기동하기 (최초 1회)

로컬 LLM을 구동하기 위해 백그라운드에 Ollama 엔진을 실행해야 합니다.

터미널을 열고 혹시 꼬여있을지 모르는 기존 프로세스를 완전히 종료합니다.

```bash
killall Ollama
pkill ollama
```

터미널에서 서버를 직접 수동 실행합니다.  
(이 터미널 창은 테스트가 끝날 때까지 끄지 말고 그대로 두세요!)

```bash
ollama serve
```

### 📌 포트 충돌 관련 팁

만약 아래와 같은 에러가 발생한다면:

```bash
bind: address already in use
```

이미 Ollama가 백그라운드 앱으로 실행 중인 상태이므로  
이 단계는 생략하고 바로 2단계로 진행해도 됩니다.

---

## 2단계: 새 터미널 창에서 LLM 모델 다운로드하기 (최초 1회)

Ollama가 대기 시간 없이 즉시 답변을 생성할 수 있도록,  
사용할 정확한 모델을 미리 로컬 저장소에 확보합니다.

새 터미널 창(또는 탭: `Cmd + T`)을 하나 더 엽니다.

아래 명령어를 입력하여 성능 비교에 사용할 Qwen3.5 2B 모델을 다운로드합니다.

> Qwen3.5 라인업은 1.5B 체급이 존재하지 않으므로,  
> 성능과 속도가 가장 안정적인 2B 모델을 사용합니다.

```bash
ollama pull qwen3.5:2b
```

다운로드가 완료되면 아래 명령어로 정상적으로 설치되었는지 확인합니다.

```bash
ollama list
```

아래 모델이 목록에 보이면 성공입니다.

```text
qwen3.5:2b
qwen3.5:0.8b
```

---

## 3단계: 테스트 파일(`test/poc_test.py`) 최종 확인하기

pytest가 테스트 함수를 정상적으로 인식하고 실행할 수 있도록  
코드 구조를 확인합니다.

### 1️⃣ 모델 ID 확인

`test/poc_test.py` 상단에서 로컬에 다운로드한 모델명과 정확히 일치하는지 확인합니다.

```python
# qwen3.5:2b 모델로 정확하게 매칭되어 있는지 확인합니다.
llm_to_use = "qwen3.5:2b"
```

---

### 2️⃣ pytest 테스트 함수 확인

파일 최하단에 `test_`로 시작하는 함수가 반드시 있어야 합니다.

```python
def test_rag_performance_comparison():
    """
    pytest 실행을 위한 래퍼 함수
    """
    run_rag_performance_comparison()
    assert True
```

---

### 3️⃣ import 경로 확인

프로젝트 루트(`content`) 기준으로 import 경로가 올바른지 확인합니다.

```python
# 최상위 content 폴더 안에서 실행하므로, content. 을 뺀 경로로 지정합니다.
from poc.rag_test import rag_test_documents, rag_test_query, run_local_rag_poc
```

---

# 🚀 모든 준비 완료! 테스트 실행하기

위의 3단계 세팅이 모두 끝났다면,  
새 터미널 창에서 프로젝트 최상위 폴더(`content`)로 이동한 뒤 아래 명령어를 실행합니다.

```bash
cd /Users/josihyeon/project/content
python -m pytest -s
```

테스트가 정상 실행되면  
RAG 성능 비교 결과가 터미널에 출력됩니다.
