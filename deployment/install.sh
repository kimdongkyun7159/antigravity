#!/bin/bash
# 서버 초기 설정 스크립트
# EC2/Droplet에서 처음 실행하는 스크립트

set -e

echo "======================================"
echo "🚀 채팅 앱 서버 초기 설정"
echo "======================================"
echo ""

# 색상
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 도메인 입력 받기
echo -e "${YELLOW}도메인을 입력하세요 (예: chat.yourdomain.com):${NC}"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ 도메인이 비어있습니다!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 도메인: $DOMAIN${NC}"
echo ""

# 1. 시스템 업데이트
echo -e "${YELLOW}[1/10] 시스템 업데이트...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
echo -e "${YELLOW}[2/10] 필수 패키지 설치...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    htop \
    curl

# 3. 프로젝트 클론
echo -e "${YELLOW}[3/10] 프로젝트 클론...${NC}"
cd ~
if [ ! -d "antigravity" ]; then
    echo "GitHub repository URL을 입력하세요:"
    read -r REPO_URL
    git clone "$REPO_URL" antigravity
else
    echo "프로젝트가 이미 존재합니다."
fi

# 4. 가상환경 생성
echo -e "${YELLOW}[4/10] Python 가상환경 생성...${NC}"
cd ~/antigravity
python3 -m venv venv
source venv/bin/activate

# 5. 의존성 설치
echo -e "${YELLOW}[5/10] Python 패키지 설치...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn eventlet python-dotenv

# 6. 환경 변수 설정
echo -e "${YELLOW}[6/10] 환경 변수 파일 생성...${NC}"
cp deployment/.env.example .env

# 랜덤 SECRET_KEY 생성
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/change-this-to-a-very-long-random-string-min-32-chars/$SECRET_KEY/" .env

echo ".env 파일이 생성되었습니다. 필요 시 수정하세요."

# 7. 로그 디렉토리
echo -e "${YELLOW}[7/10] 로그 디렉토리 생성...${NC}"
sudo mkdir -p /var/log/chatapp
sudo chown $USER:$USER /var/log/chatapp

# 8. Nginx 설정
echo -e "${YELLOW}[8/10] Nginx 설정...${NC}"
sudo cp deployment/nginx.conf /etc/nginx/sites-available/chatapp

# 도메인 자동 치환
sudo sed -i "s/chat.yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/chatapp

# 심볼릭 링크 생성
sudo ln -sf /etc/nginx/sites-available/chatapp /etc/nginx/sites-enabled/

# 기본 사이트 비활성화
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 테스트
sudo nginx -t

# 9. Systemd 서비스
echo -e "${YELLOW}[9/10] Systemd 서비스 설정...${NC}"
sudo cp deployment/chatapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start chatapp
sudo systemctl enable chatapp

# 10. 방화벽 설정
echo -e "${YELLOW}[10/10] 방화벽 설정...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Nginx 재시작
sudo systemctl restart nginx

echo ""
echo "======================================"
echo -e "${GREEN}✅ 초기 설정 완료!${NC}"
echo "======================================"
echo ""
echo -e "${BLUE}다음 단계:${NC}"
echo ""
echo "1️⃣  DNS 설정 확인:"
echo "   nslookup $DOMAIN"
echo ""
echo "2️⃣  HTTP 접속 테스트:"
echo "   curl http://$DOMAIN"
echo ""
echo "3️⃣  SSL 인증서 발급:"
echo "   sudo certbot --nginx -d $DOMAIN"
echo ""
echo "4️⃣  서비스 상태 확인:"
echo "   sudo systemctl status chatapp"
echo ""
echo "5️⃣  완료 후 접속:"
echo "   https://$DOMAIN/chat"
echo ""
echo "======================================"
echo ""
