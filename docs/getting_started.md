# 실행 가이드 (Getting Started)

본 문서는 프로젝트 설정, 데이터베이스 실행 및 로컬 서버 구동 방법을 안내.

---

## 🛠 1. 초기 설정 (최초 1회 실행)
프로젝트를 처음 세팅할 때 **한 번만** 수행하면 되는 과정.

### 1.1 요구 사항 (Prerequisites)
- **Python**: `>= 3.14`
- **패키지 관리자**: Poetry
- **Docker**: ChromaDB 컨테이너 실행용 (권장)

### 1.2 의존성 패키지 설치
`pyproject.toml` 및 파이썬 모듈(`app`)이 `embedding-api` 디렉토리 하위에 위치하므로, 패키지 인식과 모듈 임포트를 위해 **반드시 해당 디렉토리로 이동 후** 작업을 수행.

프로젝트 루트 디렉토리(`content`) 기준:
```bash
cd embedding-api
poetry install
```

> **참고**: `playwright` 의존성이 포함되어 있음. 스크립트 실행에 브라우저 바이너리가 필요한 경우 아래 명령어를 추가로 실행.
> ```bash
> poetry run playwright install
> ```

---

## 🚀 2. 서버 구동 (매번 실행)
개발 및 서비스 구동 시 매번 수행해야 하는 단계.

### 2.1 데이터베이스 (ChromaDB) 실행
본 프로젝트는 벡터 데이터베이스로 ChromaDB를 사용. 서버 실행 전 ChromaDB 환경 구성이 필요.

**Docker를 통한 ChromaDB 실행 (권장)**
```bash
docker run -p 8000:8000 chromadb/chroma
```
*(로컬 환경에서 인메모리나 디스크 모드로 ChromaDB를 사용할 경우 이 단계를 생략하거나 환경 변수를 재설정.)*

### 2.2 서버 (FastAPI) 실행
DB 환경 구성이 완료되면 아래 명령어를 통해 로컬 서버를 실행. 서버 실행 시 **현재 경로는 반드시 `embedding-api` 디렉토리**여야 함.

현재 터미널 위치가 루트 디렉토리(`content`)인 경우:
```bash
cd embedding-api
poetry run uvicorn app.main:app --reload
```

현재 터미널 위치가 `docs` 등 다른 하위 디렉토리인 경우, 프로젝트 루트로 이동한 후 진입:
```bash
cd ../embedding-api
poetry run uvicorn app.main:app --reload
```

*(ChromaDB가 8000 포트를 점유하여 포트 충돌이 발생하는 경우, `--port 8080` 플래그 등을 사용하여 포트를 변경.)*

### 2.3 접속 및 테스트
서버 구동 후 브라우저를 통해 아래 주소로 접속하여 API 정상 동작 여부를 확인.
- **API 문서 (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs) (서버 포트에 맞게 변경)

---

## 🧪 3. 진단 테스트 (Diagnostics)
서버 구동 후, 핵심 컴포넌트(ChromaDB, SQLite 등)가 정상적으로 연결되어 작동하는지 터미널에서 API를 호출하여 확인하는 방법.

서버가 실행 중인 상태에서 새로운 터미널 창을 열고 아래 명령어들을 실행.

### 3.1 ChromaDB 연결 진단
벡터 데이터베이스(ChromaDB)와의 연결 상태를 점검.

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/diag/chroma/connectivity' \
  -H 'accept: application/json'
```

### 3.2 SQLite 연결 진단 (해당 시)
관계형 데이터베이스(SQLite)와의 연결 상태를 점검.

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/diag/sqlite/connectivity' \
  -H 'accept: application/json'
```
