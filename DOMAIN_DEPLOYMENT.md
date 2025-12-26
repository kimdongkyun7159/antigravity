# 도메인으로 채팅 앱 배포하기 🚀

본인 도메인이 있다면 전문적인 채팅 서비스로 만들 수 있습니다!

예: `chat.yourdomain.com` 또는 `yourdomain.com/chat`

---

## 🎯 최종 결과

**Before (개발 환경)**:
```
http://192.168.0.10:5000/chat
```

**After (프로덕션)**:
```
https://chat.yourdomain.com
```

✅ HTTPS (보안 연결)
✅ 깔끔한 URL
✅ 24시간 운영
✅ 빠른 속도

---

## 📋 사전 준비

### 필요한 것들
- [x] 도메인 (예: GoDaddy, Namecheap, Cloudflare 등에서 구매)
- [x] 클라우드 서버 (AWS, Google Cloud, DigitalOcean 등)
- [x] 신용카드 또는 체크카드 (서버 결제용)

### 비용 예상
| 항목 | 월 비용 | 연 비용 |
|------|---------|---------|
| **도메인** | - | $10-20 |
| **서버 (소규모)** | $5-10 | $60-120 |
| **SSL 인증서** | 무료 (Let's Encrypt) | 무료 |
| **총합** | ~$7 | ~$90 |

---

## 🚀 배포 방법

3가지 배포 방법을 소개합니다:

1. **AWS EC2** (가장 안정적)
2. **DigitalOcean** (가장 쉬움)
3. **Google Cloud** (무료 크레딧 제공)

---

## 방법 1: AWS EC2 배포 (추천)

### 1단계: EC2 인스턴스 생성

**AWS 콘솔 접속**: https://aws.amazon.com/console

1. **EC2 → Launch Instance**
2. **설정**:
   - Name: `ChatApp`
   - OS: Ubuntu 22.04 LTS
   - Instance type: `t2.micro` (프리티어)
   - Key pair: 새로 생성 (다운로드 보관!)
   - Security Group:
     - SSH (22) - 본인 IP만
     - HTTP (80) - 전체 허용
     - HTTPS (443) - 전체 허용
     - Custom (5000) - 전체 허용 (임시)

3. **Launch Instance** 클릭

### 2단계: 도메인 DNS 설정

**도메인 등록 업체 (GoDaddy, Namecheap 등) 관리 페이지**:

1. **A 레코드 추가**:
   ```
   Type: A
   Name: chat (또는 @)
   Value: [EC2 IP 주소]
   TTL: 300
   ```

2. **예시**:
   - `chat.yourdomain.com` → EC2 IP
   - 또는 `yourdomain.com` → EC2 IP

3. **저장 후 대기** (5-30분 소요)

**DNS 확인**:
```bash
nslookup chat.yourdomain.com
```

### 3단계: 서버 접속 및 설정

**SSH 접속**:
```bash
# Windows (PowerShell)
ssh -i "ChatApp.pem" ubuntu@chat.yourdomain.com

# Mac/Linux
chmod 400 ChatApp.pem
ssh -i ChatApp.pem ubuntu@chat.yourdomain.com
```

**시스템 업데이트**:
```bash
sudo apt update && sudo apt upgrade -y
```

### 4단계: Python 환경 설정

```bash
# Python 및 필수 패키지
sudo apt install python3-pip python3-venv git nginx certbot python3-certbot-nginx -y

# 프로젝트 클론
cd /home/ubuntu
git clone https://github.com/[your-username]/antigravity.git
cd antigravity

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 프로덕션 패키지 추가 설치
pip install gunicorn eventlet
```

### 5단계: Nginx 설정

```bash
sudo nano /etc/nginx/sites-available/chatapp
```

**다음 내용 붙여넣기** (파일 내용은 아래 nginx.conf 참조):

```nginx
server {
    listen 80;
    server_name chat.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Nginx 활성화**:
```bash
sudo ln -s /etc/nginx/sites-available/chatapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6단계: HTTPS 설정 (Let's Encrypt)

```bash
# SSL 인증서 자동 발급
sudo certbot --nginx -d chat.yourdomain.com

# 자동 갱신 확인
sudo certbot renew --dry-run
```

**프롬프트 응답**:
- Email: 본인 이메일
- Agree: Y
- Redirect HTTP to HTTPS: 2 (권장)

### 7단계: 서비스 자동 시작 설정

**Systemd 서비스 파일 생성**:
```bash
sudo nano /etc/systemd/system/chatapp.service
```

**내용** (아래 chatapp.service 참조):
```ini
[Unit]
Description=Chat Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/antigravity
Environment="PATH=/home/ubuntu/antigravity/venv/bin"
ExecStart=/home/ubuntu/antigravity/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**서비스 활성화**:
```bash
sudo systemctl daemon-reload
sudo systemctl start chatapp
sudo systemctl enable chatapp
sudo systemctl status chatapp
```

### 8단계: 방화벽 설정

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 9단계: 배포 완료! 🎉

이제 접속:
```
https://chat.yourdomain.com
```

---

## 방법 2: DigitalOcean 배포 (가장 쉬움)

### 1단계: Droplet 생성

**DigitalOcean 가입**: https://www.digitalocean.com

1. **Create → Droplets**
2. **설정**:
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic ($6/month)
   - Region: 가까운 지역 선택
   - Authentication: SSH keys 또는 Password
3. **Create Droplet**

### 2단계: DNS 설정

**DigitalOcean Networking → Domains**:

1. **도메인 추가**: `yourdomain.com`
2. **A 레코드**:
   ```
   Hostname: chat
   Value: [Droplet IP]
   ```

**또는 외부 도메인 사용**:
- 네임서버를 DigitalOcean으로 변경:
  ```
  ns1.digitalocean.com
  ns2.digitalocean.com
  ns3.digitalocean.com
  ```

### 3단계: 배포 (위 AWS 3-9단계 동일)

---

## 방법 3: Google Cloud Platform

### 1단계: VM 인스턴스 생성

**Google Cloud Console**: https://console.cloud.google.com

1. **Compute Engine → VM instances**
2. **CREATE INSTANCE**:
   - Name: `chatapp`
   - Region: asia-northeast3 (서울)
   - Machine type: e2-micro (프리티어)
   - Boot disk: Ubuntu 22.04 LTS
   - Firewall: HTTP, HTTPS 허용
3. **Create**

### 2단계: 고정 IP 할당

1. **VPC network → External IP addresses**
2. **RESERVE STATIC ADDRESS**
3. **Attach to**: chatapp

### 3단계: DNS 및 배포 (위와 동일)

---

## 🔧 프로덕션 환경 설정

### app.py 수정

**보안 강화**:
```python
# app.py 상단에 추가
import os
from dotenv import load_dotenv

load_dotenv()

# Socket.IO CORS 제한
socketio = SocketIO(app, cors_allowed_origins=[
    "https://chat.yourdomain.com",
    "https://yourdomain.com"
])

# Secret Key 환경 변수로
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
```

### .env 파일 생성

```bash
# 서버에서
cd /home/ubuntu/antigravity
nano .env
```

```env
SECRET_KEY=your-very-secret-key-here-change-this
GEMINI_API_KEY=your_gemini_key_if_needed
RAG_ENABLED=false
```

### 의존성 추가

```bash
pip install python-dotenv gunicorn eventlet
```

---

## 📊 성능 모니터링

### 서버 상태 확인

```bash
# 서비스 상태
sudo systemctl status chatapp

# 로그 확인
sudo journalctl -u chatapp -f

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 리소스 모니터링

```bash
# CPU/메모리 사용량
htop

# 디스크 용량
df -h

# 네트워크 연결
netstat -tulpn | grep 5000
```

---

## 🔄 업데이트 방법

**코드 업데이트 시**:
```bash
# SSH 접속 후
cd /home/ubuntu/antigravity
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart chatapp
```

**자동 배포 스크립트**:
```bash
nano update.sh
```

```bash
#!/bin/bash
cd /home/ubuntu/antigravity
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart chatapp
echo "✅ 업데이트 완료!"
```

```bash
chmod +x update.sh
./update.sh
```

---

## 🔐 보안 체크리스트

배포 전 확인사항:

- [ ] HTTPS 적용됨
- [ ] SSH 키 기반 인증
- [ ] 방화벽 설정 (UFW)
- [ ] 강력한 SECRET_KEY 사용
- [ ] CORS 도메인 제한
- [ ] 디버그 모드 비활성화
- [ ] 정기 백업 설정
- [ ] 서버 모니터링 설정

---

## 🐛 문제 해결

### 502 Bad Gateway
```bash
# 앱이 실행 중인지 확인
sudo systemctl status chatapp

# 재시작
sudo systemctl restart chatapp
```

### Socket.IO 연결 실패
```bash
# Nginx 설정 확인
sudo nginx -t

# WebSocket 업그레이드 헤더 확인
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" https://chat.yourdomain.com/socket.io
```

### 메모리 부족
```bash
# 스왑 메모리 추가 (2GB)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📈 확장 및 최적화

### 1. 다중 워커 (동시 접속자 증가 시)

```bash
# chatapp.service 수정
ExecStart=/home/ubuntu/antigravity/venv/bin/gunicorn --worker-class eventlet -w 4 --bind 127.0.0.1:5000 app:app
```

### 2. Redis 세션 저장소

```bash
# Redis 설치
sudo apt install redis-server -y
pip install redis flask-session
```

### 3. 로드 밸런서 (500명+ 동시 접속)

- AWS ELB 또는 Nginx 로드 밸런서
- 다중 서버 운영
- Redis Pub/Sub for Socket.IO scaling

### 4. CDN (정적 파일)

- Cloudflare
- AWS CloudFront
- CSS/JS 파일 캐싱

---

## 💰 비용 최적화

### 프리티어 활용
- **AWS**: 12개월 무료 (t2.micro)
- **Google Cloud**: $300 크레딧 (90일)
- **Oracle Cloud**: 평생 무료 (제한적)

### 저렴한 옵션
| 업체 | 플랜 | 월 비용 |
|------|------|---------|
| DigitalOcean | Basic | $6 |
| Vultr | Cloud Compute | $6 |
| Linode | Nanode | $5 |
| Hetzner | CX11 | €4.5 |

---

## 🎓 다음 단계

배포가 완료되었다면:

1. **모니터링 설정**
   - UptimeRobot (다운타임 알림)
   - Google Analytics (방문자 추적)

2. **백업 자동화**
   - 데이터베이스 일일 백업
   - S3에 자동 업로드

3. **CI/CD 파이프라인**
   - GitHub Actions
   - 자동 테스트 + 배포

4. **추가 기능**
   - 사용자 인증
   - 메시지 저장
   - 파일 전송

---

## 📞 지원

문제가 발생하면:

1. **로그 확인**: `sudo journalctl -u chatapp -f`
2. **GitHub Issues** 등록
3. **커뮤니티 문의**

---

## ✅ 배포 완료 체크리스트

- [ ] 서버 생성 완료
- [ ] 도메인 DNS 설정
- [ ] 앱 배포 완료
- [ ] Nginx 설정
- [ ] HTTPS 적용
- [ ] 서비스 자동 시작
- [ ] 방화벽 설정
- [ ] 테스트 완료
- [ ] 모니터링 설정

**축하합니다! 이제 전문적인 채팅 서비스를 운영하고 있습니다!** 🎉

```
https://chat.yourdomain.com
```
