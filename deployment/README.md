# 배포 파일 📦

도메인을 사용하여 채팅 앱을 배포하기 위한 설정 파일들입니다.

## 📁 파일 구조

```
deployment/
├── README.md              # 이 파일
├── nginx.conf             # Nginx 웹서버 설정
├── chatapp.service        # Systemd 서비스 설정
├── .env.example           # 환경 변수 예시
├── install.sh             # 서버 초기 설정 스크립트
└── deploy.sh              # 업데이트 배포 스크립트
```

## 🚀 빠른 시작 (처음 배포하는 경우)

### 1단계: 서버 준비

AWS EC2, DigitalOcean, Google Cloud 등에서 서버를 생성하세요.

**권장 사양**:
- OS: Ubuntu 22.04 LTS
- CPU: 1 Core
- RAM: 1GB
- Storage: 10GB

### 2단계: SSH 접속

```bash
ssh -i your-key.pem ubuntu@your-server-ip
```

### 3단계: 초기 설정 스크립트 실행

```bash
# 프로젝트 다운로드 (또는 git clone)
curl -o install.sh https://raw.githubusercontent.com/your-username/antigravity/main/deployment/install.sh

# 실행 권한 부여
chmod +x install.sh

# 스크립트 실행
./install.sh
```

**스크립트가 자동으로 수행하는 작업**:
1. 시스템 업데이트
2. 필수 패키지 설치
3. 프로젝트 클론
4. Python 가상환경 생성
5. 의존성 설치
6. Nginx 설정
7. Systemd 서비스 등록
8. 방화벽 설정

### 4단계: DNS 설정

도메인 등록 업체에서 A 레코드 추가:
```
Type: A
Name: chat (또는 @)
Value: [서버 IP 주소]
```

### 5단계: SSL 인증서 발급

```bash
sudo certbot --nginx -d chat.yourdomain.com
```

**완료!** 이제 `https://chat.yourdomain.com/chat` 접속 가능!

---

## 🔄 업데이트 배포 (코드 수정 후)

코드를 수정하고 GitHub에 push한 후:

```bash
cd ~/antigravity
./deployment/deploy.sh
```

**자동으로 수행하는 작업**:
1. 최신 코드 가져오기 (git pull)
2. 의존성 업데이트
3. 서비스 재시작
4. 상태 확인

---

## 📋 수동 설정 (install.sh를 사용하지 않는 경우)

### 1. Nginx 설정

```bash
# 파일 복사
sudo cp nginx.conf /etc/nginx/sites-available/chatapp

# 도메인 변경
sudo nano /etc/nginx/sites-available/chatapp
# chat.yourdomain.com을 본인 도메인으로 수정

# 활성화
sudo ln -s /etc/nginx/sites-available/chatapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Systemd 서비스

```bash
# 파일 복사
sudo cp chatapp.service /etc/systemd/system/

# 경로 확인 (필요시 수정)
sudo nano /etc/systemd/system/chatapp.service

# 활성화
sudo systemctl daemon-reload
sudo systemctl start chatapp
sudo systemctl enable chatapp
```

### 3. 환경 변수

```bash
# 프로젝트 루트에서
cp deployment/.env.example .env

# SECRET_KEY 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# .env 파일 수정
nano .env
```

---

## 🔧 설정 파일 상세 설명

### nginx.conf

**주요 설정**:
- Port 80/443 리스닝
- Socket.IO WebSocket 프록시
- HTTPS 리다이렉션
- 정적 파일 캐싱
- 보안 헤더 추가

**수정이 필요한 부분**:
```nginx
server_name chat.yourdomain.com;  # ← 본인 도메인
```

### chatapp.service

**주요 설정**:
- Gunicorn + eventlet worker
- 자동 재시작 정책
- 로그 파일 위치
- 환경 변수 로드

**수정이 필요한 부분**:
```ini
User=ubuntu                                    # ← 사용자명
WorkingDirectory=/home/ubuntu/antigravity      # ← 프로젝트 경로
```

### .env.example

**필수 환경 변수**:
- `SECRET_KEY`: Flask 세션 암호화 키 (반드시 변경!)
- `FLASK_ENV`: production (프로덕션 환경)
- `DEBUG`: False (디버그 모드 비활성화)

**선택 환경 변수**:
- `GEMINI_API_KEY`: AI 기능 사용 시
- `RAG_ENABLED`: RAG 기능 활성화 여부

---

## 🐛 문제 해결

### 서비스가 시작되지 않음

```bash
# 로그 확인
sudo journalctl -u chatapp -n 50

# 수동 실행 테스트
cd ~/antigravity
source venv/bin/activate
gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 app:app
```

### Nginx 502 Bad Gateway

```bash
# 앱이 실행 중인지 확인
sudo systemctl status chatapp

# 포트가 열려있는지 확인
netstat -tulpn | grep 5000
```

### SSL 인증서 발급 실패

```bash
# DNS 전파 확인
nslookup chat.yourdomain.com

# 포트 80이 열려있는지 확인
sudo ufw status
curl http://chat.yourdomain.com
```

### 메모리 부족

```bash
# 스왑 메모리 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📊 모니터링

### 서비스 상태

```bash
# 서비스 확인
sudo systemctl status chatapp

# 실시간 로그
sudo journalctl -u chatapp -f

# Nginx 로그
sudo tail -f /var/log/nginx/chatapp_access.log
sudo tail -f /var/log/nginx/chatapp_error.log
```

### 리소스 사용량

```bash
# CPU/메모리
htop

# 디스크
df -h

# 네트워크
netstat -tulpn | grep 5000
```

---

## 🔒 보안 체크리스트

- [ ] SSH 키 기반 인증 사용
- [ ] 비밀번호 로그인 비활성화
- [ ] UFW 방화벽 활성화
- [ ] 강력한 SECRET_KEY 사용
- [ ] HTTPS 적용 (Let's Encrypt)
- [ ] 정기 업데이트 (apt update)
- [ ] 로그 모니터링 설정
- [ ] 백업 자동화

---

## 📈 성능 최적화

### 다중 워커 설정

```bash
# chatapp.service 수정
ExecStart=/home/ubuntu/antigravity/venv/bin/gunicorn \
    --worker-class eventlet \
    --workers 4 \  # ← 워커 수 증가
    --bind 127.0.0.1:5000 \
    app:app
```

### Redis 세션 저장소

```bash
# Redis 설치
sudo apt install redis-server -y
pip install redis flask-session

# app.py에 추가
# SESSION_TYPE = 'redis'
# SESSION_REDIS = redis.from_url('redis://localhost:6379')
```

---

## 🆘 지원

문제가 발생하면:

1. **로그 확인**: `sudo journalctl -u chatapp -f`
2. **GitHub Issues** 등록
3. **상세 문서**: `../DOMAIN_DEPLOYMENT.md` 참조

---

## 📚 관련 문서

- [도메인 배포 가이드](../DOMAIN_DEPLOYMENT.md)
- [원격 접속 가이드](../REMOTE_ACCESS_GUIDE.md)
- [채팅 앱 README](../CHAT_APP_README.md)

---

**배포 성공을 기원합니다!** 🚀
