#!/bin/bash
# 자동 배포 스크립트
# 사용법: ./deploy.sh

set -e  # 에러 발생 시 중단

echo "======================================"
echo "📦 채팅 앱 배포 스크립트"
echo "======================================"
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 현재 사용자 확인
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ root 사용자로 실행하지 마세요!${NC}"
    echo "일반 사용자로 실행: ./deploy.sh"
    exit 1
fi

# 프로젝트 디렉토리 확인
PROJECT_DIR="$HOME/antigravity"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 프로젝트 디렉토리를 찾을 수 없습니다: $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✅ 프로젝트 디렉토리: $PROJECT_DIR${NC}"

# 1. 최신 코드 가져오기
echo ""
echo -e "${YELLOW}[1/8] Git에서 최신 코드 가져오기...${NC}"
git pull origin main || {
    echo -e "${RED}⚠️  git pull 실패. 계속 진행합니다.${NC}"
}

# 2. 가상환경 활성화
echo -e "${YELLOW}[2/8] 가상환경 활성화...${NC}"
if [ ! -d "venv" ]; then
    echo "가상환경이 없습니다. 생성 중..."
    python3 -m venv venv
fi
source venv/bin/activate

# 3. 의존성 설치
echo -e "${YELLOW}[3/8] 의존성 패키지 설치...${NC}"
pip install -r requirements.txt
pip install gunicorn eventlet python-dotenv

# 4. 로그 디렉토리 생성
echo -e "${YELLOW}[4/8] 로그 디렉토리 생성...${NC}"
sudo mkdir -p /var/log/chatapp
sudo chown $USER:$USER /var/log/chatapp

# 5. Systemd 서비스 파일 복사
echo -e "${YELLOW}[5/8] Systemd 서비스 설정...${NC}"
sudo cp deployment/chatapp.service /etc/systemd/system/
sudo systemctl daemon-reload

# 6. 서비스 재시작
echo -e "${YELLOW}[6/8] 서비스 재시작...${NC}"
sudo systemctl restart chatapp
sudo systemctl enable chatapp

# 7. 상태 확인
echo -e "${YELLOW}[7/8] 서비스 상태 확인...${NC}"
sleep 2
if sudo systemctl is-active --quiet chatapp; then
    echo -e "${GREEN}✅ 서비스 실행 중!${NC}"
else
    echo -e "${RED}❌ 서비스 시작 실패!${NC}"
    echo "로그 확인:"
    sudo journalctl -u chatapp -n 50 --no-pager
    exit 1
fi

# 8. Nginx 재시작
echo -e "${YELLOW}[8/8] Nginx 재시작...${NC}"
if command -v nginx &> /dev/null; then
    sudo nginx -t && sudo systemctl reload nginx
    echo -e "${GREEN}✅ Nginx 재시작 완료${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo "======================================"
echo ""
echo "서비스 상태 확인: sudo systemctl status chatapp"
echo "로그 확인: sudo journalctl -u chatapp -f"
echo "Nginx 로그: sudo tail -f /var/log/nginx/chatapp_error.log"
echo ""
