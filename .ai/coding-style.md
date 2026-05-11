# Coding Style & Conventions

이 문서는 프로젝트 내에서 코드를 작성할 때 준수해야 할 코딩 스타일과 컨벤션을 정의합니다.
AI 어시스턴트는 코드를 제안하거나 수정할 때 반드시 이 규칙을 따라야 합니다.

## 1. 네이밍 규칙 (Naming Conventions)
- **클래스 및 인터페이스**: PascalCase 사용 (예: `UserRepository`, `PaymentService`)
- **변수 및 메서드**: camelCase 사용 (예: `getUserInfo()`, `totalAmount`)
- **상수**: UPPER_SNAKE_CASE 사용 (예: `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)

## 2. 파일 및 폴더 구조
- 파일명은 포함하고 있는 핵심 클래스나 기능의 이름과 일치해야 합니다.
- 각 도메인(기능)별로 폴더를 분리하여 응집도를 높입니다.

## 3. 주석 및 문서화 (Comments & Documentation)
- 복잡한 비즈니스 로직이 포함된 메서드에는 반드시 그 의도(Why)를 설명하는 주석을 작성합니다.
- 공용 API나 인터페이스에는 Javadoc(또는 해당 언어의 표준 문서화 포맷) 스타일의 주석을 달아줍니다.

## 4. 기타 원칙
- **클린 코드**: 메서드는 하나의 역할만 수행하도록 작게 유지합니다.
- **오류 처리**: 발생 가능한 예외 상황을 고려하여 적절한 예외 처리(Try-Catch, Error Return 등)를 구현합니다.
*(필요에 따라 프로젝트 언어와 환경에 맞는 세부 규칙을 추가하세요.)*