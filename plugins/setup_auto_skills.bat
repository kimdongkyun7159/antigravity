@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  Claude Plugins Auto-Setup                                  ║
echo ║  한 번만 실행하면 모든 프로젝트에서 자동 활성화!           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [경고] 관리자 권한이 필요합니다!
    echo 이 스크립트를 마우스 우클릭 후 "관리자 권한으로 실행"해주세요.
    echo.
    pause
    exit /b 1
)

echo [1/4] 설정 디렉토리 확인 중...

REM Claude 설정 폴더 생성 (없으면)
if not exist "%USERPROFILE%\.claude" (
    echo    └─ .claude 폴더 생성 중...
    mkdir "%USERPROFILE%\.claude"
)

if not exist "%USERPROFILE%\.claude\skills" (
    echo    └─ .claude\skills 폴더 생성 중...
    mkdir "%USERPROFILE%\.claude\skills"
)

echo    ✓ 설정 폴더 준비 완료
echo.

echo [2/4] 기존 심볼릭 링크 확인 중...

REM 기존 심볼릭 링크가 있으면 제거
if exist "%USERPROFILE%\.claude\skills\antigravity_plugins" (
    echo    └─ 기존 링크 제거 중...
    rmdir "%USERPROFILE%\.claude\skills\antigravity_plugins"
)

echo    ✓ 확인 완료
echo.

echo [3/4] Skills 자동 연결 중...

REM 심볼릭 링크 생성
mklink /D "%USERPROFILE%\.claude\skills\antigravity_plugins" "c:\antigravity\claude_plugins\skills"

if %errorlevel% equ 0 (
    echo    ✓ 심볼릭 링크 생성 성공!
    echo.
    echo [4/4] Skills 목록 확인 중...
    echo.
    dir /b "c:\antigravity\claude_plugins\skills"
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║  ✓ 설정 완료!                                               ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo 이제 Claude Code가 자동으로 다음 Skills를 사용합니다:
    echo   • GitHub Integration (PR, Issue, CI/CD)
    echo   • Sentry Error Debugger (에러 분석)
    echo   • Database Query Assistant (SQL 작업)
    echo   • Code Intelligence (코드 분석)
    echo.
    echo 💡 Tips:
    echo   - Skills는 자동으로 활성화됩니다 (명령어 불필요)
    echo   - 새 Skills 추가 시 자동으로 인식됩니다
    echo   - 프로젝트별 설정 필요 없음!
    echo.
) else (
    echo    ✗ 심볼릭 링크 생성 실패
    echo.
    echo 대안: 수동 복사 방법
    echo   xcopy /E /I /Y "c:\antigravity\claude_plugins\skills" "%USERPROFILE%\.claude\skills\antigravity_plugins"
    echo.
)

echo.
echo 설정 위치: %USERPROFILE%\.claude\skills\
echo.
pause
