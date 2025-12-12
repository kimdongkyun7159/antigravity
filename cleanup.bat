@echo off
chcp 65001 >nul
echo ============================================================
echo 🧹 Error Analyzer 프로젝트 정리
echo ============================================================
echo.
echo 다음 파일/폴더를 삭제합니다:
echo.
echo [테스트 파일]
echo   - test_complex_code.py
echo   - test_rag.py
echo   - test_rag_error.py
echo   - test_rag_final.py
echo   - test_rag_simple.py
echo.
echo [캐시 폴더]
echo   - modules\__pycache__\
echo.
echo [임시 파일]
echo   - .vscode\ (선택적)
echo.
echo ⚠️ 주의: 이 작업은 되돌릴 수 없습니다!
echo.
set /p CONFIRM="정말로 정리하시겠습니까? (Y/N): "

if /i NOT "%CONFIRM%"=="Y" (
    echo.
    echo ❌ 정리가 취소되었습니다.
    pause
    exit /b
)

echo.
echo 🧹 정리 시작...
echo.

REM 테스트 파일 삭제
echo 📝 테스트 파일 삭제 중...
del /q test_complex_code.py 2>nul
del /q test_rag.py 2>nul
del /q test_rag_error.py 2>nul
del /q test_rag_final.py 2>nul
del /q test_rag_simple.py 2>nul
echo    ✅ 테스트 파일 삭제 완료

REM 캐시 폴더 삭제
echo 📦 캐시 폴더 삭제 중...
rmdir /s /q modules\__pycache__ 2>nul
echo    ✅ 캐시 폴더 삭제 완료

REM uploads 폴더 내용물 삭제 (폴더는 유지)
echo 📂 uploads 폴더 초기화 중...
del /q uploads\* 2>nul
echo    ✅ uploads 폴더 초기화 완료

echo.
echo ============================================================
echo ✅ 정리 완료!
echo ============================================================
echo.
echo 남은 핵심 파일:
echo   ✅ app.py (메인 서버)
echo   ✅ modules/ (7개 엔진 + RAG)
echo   ✅ templates/ (웹 UI)
echo   ✅ static/ (CSS/JS)
echo   ✅ data/ (SQLite + Vector DB)
echo   ✅ README.md
echo   ✅ requirements.txt
echo   ✅ start_server.bat
echo   ✅ setup_api_key.bat
echo.
pause
