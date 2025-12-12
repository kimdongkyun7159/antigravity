@echo off
chcp 65001 > nul
title Error Analyzer - AI 코드 에러 분석기

echo ============================================================
echo 🔍 Error Analyzer 시작 중...
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/2] 서버 시작 중...
start "Error Analyzer Server" cmd /k "python app.py"

timeout /t 3 /nobreak >nul

echo [2/2] 브라우저 열기...
start http://localhost:5000

echo.
echo ============================================================
echo ✅ Error Analyzer가 실행되었습니다!
echo    서버 주소: http://localhost:5000
echo    서버 종료: 서버 창을 닫으세요
echo ============================================================
echo.
pause
