@echo off
chcp 65001 >nul
echo ============================================================
echo 🔑 Gemini API 키 설정
echo ============================================================
echo.

REM .env 파일이 없으면 생성
if not exist .env (
    echo 📝 .env 파일 생성 중...
    copy .env.example .env >nul
    echo ✅ .env 파일이 생성되었습니다
    echo.
) else (
    echo ℹ️ .env 파일이 이미 존재합니다
    echo.
)

echo 📋 설정 방법:
echo.
echo 1. VS Code나 메모장으로 .env 파일을 여세요:
echo    notepad .env
echo.
echo 2. GEMINI_API_KEY= 뒤에 발급받은 API 키를 입력하세요
echo.
echo 3. 파일을 저장하세요
echo.
echo 4. Error Analyzer 서버를 재시작하세요:
echo    python app.py
echo.
echo ============================================================
echo 📚 API 키 발급 방법
echo ============================================================
echo.
echo 1. 브라우저에서 접속:
echo    https://makersuite.google.com/app/apikey
echo.
echo 2. Google 계정으로 로그인
echo.
echo 3. "Create API Key" 버튼 클릭
echo.
echo 4. 생성된 키를 복사하여 .env 파일에 붙여넣기
echo.
echo ============================================================

REM .env 파일 열기
set /p OPEN="지금 .env 파일을 열까요? (Y/N): "
if /i "%OPEN%"=="Y" (
    notepad .env
    echo.
    echo ✅ .env 파일을 저장한 후 서버를 재시작하세요!
) else (
    echo.
    echo 나중에 .env 파일을 직접 편집하세요
)

echo.
echo ============================================================
pause
