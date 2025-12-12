# Gemini API 키 설정 가이드

## 📝 API 키 발급 방법

1. **Google AI Studio 접속**
   - URL: https://makersuite.google.com/app/apikey
   - Google 계정으로 로그인

2. **API 키 생성**
   - "Create API Key" 버튼 클릭
   - 생성된 키를 복사

## ⚙️ API 키 설정 방법

### 방법 1: .env 파일 사용 (권장) ✨

1. `.env.example` 파일을 `.env`로 복사:
   ```bash
   copy .env.example .env
   ```

2. `.env` 파일 열기:
   - VS Code에서 `c:\Antigravity\error_analyzer\.env` 파일 열기

3. API 키 입력:
   ```
   GEMINI_API_KEY=실제_발급받은_API_키_입력
   ```

4. 저장 후 서버 재시작:
   ```bash
   python app.py
   ```

### 방법 2: 환경변수 설정 (임시)

**Windows PowerShell**:
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
python app.py
```

**CMD**:
```cmd
set GEMINI_API_KEY=your_api_key_here
python app.py
```

**Linux/Mac**:
```bash
export GEMINI_API_KEY="your_api_key_here"
python app.py
```

## ✅ 설정 확인

서버가 실행되면 다음과 같이 표시됩니다:

```
============================================================
🚀 RAG Orchestrator 초기화 중...
============================================================
✅ Gemini API 연결 완료
📦 Vector Database 초기화 중...
✅ Vector Database 초기화 완료
✅ RAG 모드 활성화
============================================================
```

또는 Health Check API로 확인:
```bash
curl http://localhost:5000/api/health
```

응답에 `"rag_enabled": true`가 표시되면 성공! 🎉

## 🔒 보안 주의사항

- `.env` 파일은 `.gitignore`에 추가하세요
- API 키를 절대 코드에 직접 입력하지 마세요
- API 키를 공개 저장소에 올리지 마세요

## 💰 비용 안내

- Gemini API는 무료 사용량 제한이 있습니다
- 초과 시 요금이 부과될 수 있으니 주의하세요
- 자세한 내용: https://ai.google.dev/pricing
