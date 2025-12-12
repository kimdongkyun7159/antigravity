# Error Analyzer - RAG 기반 AI 에러 분석 시스템 🤖

**Python 코드 에러를 자동으로 감지하고 AI가 최적의 해결책을 제시**하는 차세대 에러 분석 도구

## 🚀 주요 기능

### ✨ RAG (Retrieval-Augmented Generation) 통합
- **7개 분석 엔진 통합**: File Handler, Code Validator, Executor, Error Analyzer, Pattern Learner, Advanced Analyzer, Database
- **Vector DB 검색**: ChromaDB로 과거 유사 에러 자동 검색
- **Gemini AI 분석**: 모든 정보를 종합하여 최적의 해결책 생성
- **학습 시스템**: 매 분석마다 Vector DB에 저장되어 계속 학습

### 🔍 기본 분석 기능
- **자동 에러 감지**: Python 코드 syntax, import, runtime 에러 자동 탐지
- **해결책 제시**: 구체적인 수정 방법을 한글로 설명
- **과거 사례 검색**: SQLite + Vector DB 기반 유사 케이스 검색
- **안전 실행**: 위험한 코드 차단, 타임아웃 보호
- **모던 UI**: Glassmorphism 디자인, 반응형 레이아웃

## 📦 시스템 아키텍처

```
코드 입력
    ↓
RAG Orchestrator (오케스트레이터)
    ↓
7개 엔진 병렬 실행
    ↓
Vector DB 유사 사례 검색 (ChromaDB)
    ↓
Gemini AI 종합 분석
    ↓
최적의 해결책 제시
```

## 🎯 빠른 시작

### 1. 기본 설치 및 실행

```bash
cd c:\Antigravity\error_analyzer
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000` 접속

### 2. RAG 기능 활성화 (선택)

**Gemini API 키 설정**:
```bash
setup_api_key.bat
```

또는 `.env` 파일 직접 수정:
```
GEMINI_API_KEY=your_api_key_here
```

**API 키 발급**: https://makersuite.google.com/app/apikey

## 💡 사용 방법

### 기본 분석 모드
1. 웹 브라우저에서 http://localhost:5000 접속
2. 에러가 있는 Python 코드 붙여넣기
3. "분석" 버튼 클릭
4. 에러 타입, 설명, 해결책 확인

### RAG 분석 모드 (API 키 설정 시)
1. API 엔드포인트: `POST /api/analyze-rag`
2. 7개 엔진 + Vector DB + Gemini AI 종합 분석
3. 과거 55% 이상 유사 사례 자동 참조
4. AI가 생성한 맞춤형 해결책 제공

## 🔧 핵심 모듈

### 기존 엔진 (7개)
1. **File Handler** - 파일 읽기/업로드 (`.py`, `.html`, `.js` 지원)
2. **Code Validator** - AST 기반 정적 분석
3. **Code Executor** - 안전한 별도 프로세스 실행
4. **Error Analyzer** - 8가지 에러 패턴 자동 분류
5. **Pattern Learner** - 에러 통계 및 패턴 학습
6. **Advanced Analyzer** - Ruff/Pylint/mypy/Bandit 린터 통합
7. **Error Database** - SQLite 기반 학습 시스템

### RAG 시스템 (NEW)
- **RAG Orchestrator** - 7개 엔진 통합 및 조율
- **Vector Database** - ChromaDB 기반 유사도 검색
- **LLM Integration** - Gemini API 통합

## 📊 분석 예시

**입력 코드** (51줄의 복잡한 데이터 분석 코드):
```python
import seaborn as sns
class DataAnalyzer:
    # ... 복잡한 로직 ...
```

**RAG 분석 결과**:
```
✅ 7개 엔진 실행 완료
✅ Vector DB에서 55% 유사 사례 발견
✅ Gemini AI 종합 분석

📌 에러: ModuleNotFoundError: No module named 'seaborn'
💡 해결책:
   1. pip install seaborn
   2. 설치 확인: python -c "import seaborn"
   3. 가상환경 확인

📊 과거 23번 동일 에러 → 100% pip로 해결
```

## 🛡️ 보안 기능

- 위험한 코드 패턴 사전 차단 (`os.system`, `eval` 등)
- 30초 실행 타임아웃
- 별도 프로세스 격리
- 파일 크기 제한 (10MB)

## 💾 데이터베이스

### SQLite (error_history.db)
- 에러 타입별 분류
- 발생 빈도 추적
- 해결책 성공률 통계

### ChromaDB (Vector DB)
- 에러 임베딩 저장
- 의미적 유사도 검색
- 과거 사례 학습

## 🎨 UI 특징

- **Glassmorphism** 효과
- **Dark Mode** 기본 적용
- **실시간 라인 카운터**
- **코드 하이라이팅**
- **원클릭 복사** 기능

## 📈 성능

- **기본 분석**: ~1초
- **RAG 분석**: ~10-15초 (AI 처리 포함)
- **Vector 검색**: ~100ms
- **지원 에러 타입**: 8가지 (ModuleNotFoundError, ImportError, NameError, SyntaxError, IndentationError, TypeError, AttributeError, IndexError)

## 🔐 환경 변수

`.env` 파일에서 설정:
```
GEMINI_API_KEY=your_api_key        # Gemini API 키
RAG_ENABLED=true                    # RAG 기능 활성화
TOP_K_SIMILAR_ERRORS=5             # 검색할 유사 사례 개수
```

## 📁 프로젝트 구조

```
error_analyzer/
├── app.py                     메인 서버
├── modules/                   7개 엔진 + RAG
│   ├── file_handler.py
│   ├── code_validator.py
│   ├── code_executor.py
│   ├── error_analyzer.py
│   ├── pattern_learner.py
│   ├── advanced_analyzer.py
│   ├── error_database.py
│   ├── rag_orchestrator.py    (NEW) RAG 오케스트레이터
│   ├── vector_database.py     (NEW) Vector DB
│   ├── llm_integration.py     (NEW) Gemini API
│   └── config.py              (NEW) 설정 관리
├── data/
│   ├── error_history.db       SQLite DB
│   └── chroma/                Vector DB
├── templates/                 HTML
├── static/                    CSS/JS
├── start_server.bat          서버 시작
├── setup_api_key.bat         API 키 설정
├── cleanup.bat               프로젝트 정리
└── requirements.txt          패키지 목록
```

## 🛠️ 기술 스택

- **Backend**: Flask + Python 3.13
- **Frontend**: Vanilla JS + Modern CSS
- **Database**: SQLite + ChromaDB (Vector DB)
- **AI/ML**: Gemini Pro API, ChromaDB Embeddings
- **Analysis**: AST, subprocess, Ruff, Pylint, mypy, Bandit

## 📝 라이센스 & 문의

Created with ❤️ using RAG technology

---

**프로젝트 상태**: ✅ 100% 완료 (RAG 통합)  
**버전**: 2.0.0  
**최종 업데이트**: 2025-12-12  
**특징**: RAG 기반 AI 종합 분석 시스템

