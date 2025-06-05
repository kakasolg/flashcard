
```
# 지능형 플래시카드 앱 (Intelligent Flashcard App)

## 📝 프로젝트 설명

본 프로젝트는 사용자의 학습 효율을 극대화하기 위해 설계된 지능형 플래시카드 애플리케이션입니다. LLM(Large Language Model)과 LangGraph를 활용하여 사용자와의 상호작용을 통해 플래시카드를 생성하고, 개인화된 학습 경험을 제공합니다. MongoDB를 주 데이터베이스로, 벡터 저장소를 의미론적 검색에 사용하여 학습 콘텐츠 간의 연관성을 파악하고 맞춤형 복습을 지원합니다.

## ✨ 핵심 기능

* **🤖 LLM 기반 대화형 플래시카드 생성**: 사용자와의 질문/답변을 통해 LLM이 플래시카드의 앞면, 뒷면, 시각적 단서 등을 생성합니다.
* **🧠 간격 반복 학습 시스템 (SRS)**: 효과적인 암기를 위해 과학적인 복습 스케줄을 제공합니다. (예: SM-2 알고리즘 기반)
* **🖼️ 멀티미디어 플래시카드**: 텍스트뿐만 아니라 이미지, 오디오 링크, 시각적 단서 등을 포함할 수 있습니다.
* **📊 개인별 기억 용량(Chunking) 최적화**: 사용자의 기억 용량을 테스트하고, 이에 맞춰 학습 콘텐츠의 양을 조절합니다.
* **🏰 강화된 기억의 궁전**: 사용자가 정의한 로사이(loci) 구조와 플래시카드를 연동하여 기억 효과를 높입니다.
* **📈 학습 상호작용 히스토리 및 분석**: 사용자의 모든 질문/답변 기록을 저장하고, 이를 분석하여 어떤 내용을 잘 기억하고 어려워하는지 파악합니다.
* **🔍 의미론적 검색**: 벡터 저장소를 활용하여 키워드 검색을 넘어 내용의 의미를 기반으로 관련 플래시카드를 검색합니다.
* **💡 사용자 맞춤형 피드백 및 문제 출제**: 학습 기록 및 이해도를 바탕으로 LLM이 개인화된 피드백을 제공하고 리마인드 문제를 출제합니다.
* **⚙️ API 기반 백엔드 및 웹 UI/UX**: 확장성을 고려한 API 서버와 사용자 친화적인 웹 인터페이스를 제공합니다.

## 🛠️ 기술 스택

* **언어**: Python
* **LLM 오케스트레이션**: LangGraph
* **주 데이터베이스**: MongoDB
* **벡터 저장소**: ChromaDB, FAISS 등 (플래시카드 내용의 의미론적 검색용)
* **패키지 관리**: `uv`
* **주요 Python 라이브러리 (예정)**:
    * `numpy`
    * `matplotlib` (학습 분석 시각화)
    * `requests` (외부 API 연동)
    * LLM SDK (예: OpenAI Python SDK)
    * 웹 프레임워크 (예: FastAPI, Flask)
    * 기타 데이터 처리 및 애플리케이션 로직 라이브러리
* **프론트엔드 (예정)**: 최신 웹 프레임워크 (예: React, Vue, Svelte)

## 📂 예상 프로젝트 구조

```

flashcard_app/
├── .venv/ # 가상 환경
├── core/ # 애플리케이션 핵심 로직 (또는 src/flashcard_logic/)
│ ├── init.py
│ ├── models.py # 데이터 모델 (FlashCard, ChunkingProfile 등)
│ ├── srs_engine.py # 간격 반복 학습 엔진
│ ├── palace.py # 기억의 궁전 및 청킹 관련 로직
│ ├── multimedia.py # 멀티미디어 제공 로직
│ ├── llm_integration.py # LLM 및 LangGraph 연동 로직
│ └── ... # 기타 모듈
├── tests/ # 테스트 코드
├── main.py # 애플리케이션 실행 진입점 (또는 app.py)
├── flashcard_app_plan.md # 개발 계획
├── pyproject.toml # uv로 관리되는 의존성 파일
└── README.md # 프로젝트 소개



````
## 🚀 시작하기 (초기 단계)

1.  **저장소 복제**:
    ```bash
    git clone <repository-url>
    cd flashcard_app
    ```
2.  **가상 환경 생성 및 활성화 (uv 사용)**:
    ```bash
    uv venv --python 3.12 .venv # 또는 원하는 파이썬 버전
    source .venv/bin/activate   # macOS/Linux
    # .venv\Scripts\activate    # Windows
    ```
3.  **의존성 설치 (uv 사용)**:
    ```bash
    uv add <package1> <package2> ...
    # 또는 pyproject.toml이 있다면:
    # uv sync
    ```
4.  **데이터베이스 설정**:
    * 로컬 또는 클라우드에 MongoDB 인스턴스 설정.
    * 선택한 벡터 저장소 설정.
5.  **환경 변수 설정**:
    * API 키 (LLM, 외부 서비스 등) 및 데이터베이스 연결 정보 설정.

## ▶️ 실행 방법 (개발 초기)

초기 CLI 버전 또는 데모는 다음 명령으로 실행할 수 있습니다 (개발 진행에 따라 변경):
```bash
python main.py
````
