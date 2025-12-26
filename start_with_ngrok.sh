#!/bin/bash
# 채팅 앱을 ngrok으로 실행하는 스크립트

echo "======================================"
echo "💬 실시간 채팅 앱 - 원격 접속 모드"
echo "======================================"
echo ""
echo "📌 이 스크립트를 실행하면:"
echo "   1. Flask 서버 시작"
echo "   2. ngrok으로 공개 URL 생성"
echo "   3. 전 세계 어디서나 접속 가능!"
echo ""
echo "⚠️  먼저 ngrok을 설치하세요:"
echo "   https://ngrok.com/download"
echo ""
echo "======================================"
echo ""

# Flask 서버 백그라운드 실행
echo "🚀 Flask 서버 시작 중..."
python app.py &
SERVER_PID=$!
sleep 3

echo ""
echo "🌐 ngrok 터널 생성 중..."
echo "   생성된 URL을 친구들에게 공유하세요!"
echo ""

# ngrok 실행
ngrok http 5000

# 종료 시 Flask 서버도 종료
kill $SERVER_PID
