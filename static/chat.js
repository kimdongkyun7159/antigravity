// 채팅 앱 JavaScript - Socket.IO 실시간 통신

// 전역 변수
let socket;
let username = '';
let isConnected = false;

// DOM 요소
const elements = {
    usernameInput: document.getElementById('usernameInput'),
    username: document.getElementById('username'),
    joinBtn: document.getElementById('joinBtn'),
    messageInput: document.getElementById('messageInput'),
    messageText: document.getElementById('messageText'),
    sendBtn: document.getElementById('sendBtn'),
    leaveBtn: document.getElementById('leaveBtn'),
    chatMessages: document.getElementById('chatMessages'),
    currentUsername: document.getElementById('currentUsername'),
    userCount: document.getElementById('userCount')
};

// Socket.IO 연결 초기화
function initializeSocket() {
    socket = io();

    // 연결 성공
    socket.on('connect', () => {
        console.log('Socket.IO 연결 성공');
        isConnected = true;
    });

    // 연결 해제
    socket.on('disconnect', () => {
        console.log('Socket.IO 연결 해제');
        isConnected = false;
    });

    // 메시지 수신
    socket.on('message', (data) => {
        displayMessage(data);
    });

    // 사용자 입장 알림
    socket.on('user_joined', (data) => {
        displaySystemMessage(`${data.username}님이 입장했습니다.`);
        updateUserCount(data.user_count);
    });

    // 사용자 퇴장 알림
    socket.on('user_left', (data) => {
        displaySystemMessage(`${data.username}님이 퇴장했습니다.`);
        updateUserCount(data.user_count);
    });

    // 사용자 수 업데이트
    socket.on('user_count', (data) => {
        updateUserCount(data.count);
    });

    // 에러 처리
    socket.on('error', (error) => {
        console.error('Socket.IO 에러:', error);
        alert('채팅 서버 연결에 문제가 발생했습니다.');
    });
}

// 채팅방 입장
function joinChat() {
    const inputUsername = elements.username.value.trim();

    if (!inputUsername) {
        alert('닉네임을 입력해주세요.');
        elements.username.focus();
        return;
    }

    if (inputUsername.length < 2) {
        alert('닉네임은 2글자 이상이어야 합니다.');
        elements.username.focus();
        return;
    }

    username = inputUsername;

    // Socket.IO 연결
    if (!socket) {
        initializeSocket();
    }

    // 서버에 입장 알림
    socket.emit('join', { username: username });

    // UI 전환
    elements.usernameInput.style.display = 'none';
    elements.messageInput.style.display = 'flex';
    elements.currentUsername.textContent = `${username}(으)로 접속 중`;

    // 환영 메시지 제거
    const welcomeMsg = elements.chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    // 메시지 입력창에 포커스
    elements.messageText.focus();

    displaySystemMessage('채팅방에 입장했습니다. 즐거운 대화 되세요! 😊');
}

// 메시지 전송
function sendMessage() {
    const message = elements.messageText.value.trim();

    if (!message) {
        return;
    }

    if (!isConnected) {
        alert('서버 연결이 끊어졌습니다. 페이지를 새로고침해주세요.');
        return;
    }

    // 서버로 메시지 전송
    socket.emit('message', {
        username: username,
        message: message,
        timestamp: new Date().toISOString()
    });

    // 입력창 초기화
    elements.messageText.value = '';
    elements.messageText.focus();
}

// 채팅방 나가기
function leaveChat() {
    if (confirm('정말 채팅방을 나가시겠습니까?')) {
        // 서버에 퇴장 알림
        socket.emit('leave', { username: username });

        // Socket 연결 종료
        if (socket) {
            socket.disconnect();
            socket = null;
        }

        // UI 초기화
        elements.usernameInput.style.display = 'flex';
        elements.messageInput.style.display = 'none';
        elements.username.value = '';
        elements.chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>환영합니다! 👋</h2>
                <p>아래에서 닉네임을 입력하고 채팅을 시작하세요.</p>
            </div>
        `;
        username = '';
        isConnected = false;
    }
}

// 메시지 표시
function displayMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message' + (data.username === username ? ' own' : '');

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = data.username.charAt(0).toUpperCase();

    const content = document.createElement('div');
    content.className = 'message-content';

    const usernameSpan = document.createElement('div');
    usernameSpan.className = 'message-username';
    usernameSpan.textContent = data.username;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = data.message;

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = formatTime(data.timestamp);

    content.appendChild(usernameSpan);
    content.appendChild(bubble);
    content.appendChild(time);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 시스템 메시지 표시
function displaySystemMessage(message) {
    const systemDiv = document.createElement('div');
    systemDiv.className = 'system-message';
    systemDiv.textContent = message;

    elements.chatMessages.appendChild(systemDiv);
    scrollToBottom();
}

// 사용자 수 업데이트
function updateUserCount(count) {
    elements.userCount.textContent = `${count}명 온라인`;
}

// 시간 포맷팅
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// 스크롤 맨 아래로
function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

// 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', () => {
    // 입장 버튼
    elements.joinBtn.addEventListener('click', joinChat);

    // 닉네임 입력 시 엔터키
    elements.username.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            joinChat();
        }
    });

    // 전송 버튼
    elements.sendBtn.addEventListener('click', sendMessage);

    // 메시지 입력 시 엔터키
    elements.messageText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 나가기 버튼
    elements.leaveBtn.addEventListener('click', leaveChat);

    // 페이지 닫기 전 경고
    window.addEventListener('beforeunload', (e) => {
        if (isConnected && username) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    // 페이지 언로드 시 소켓 정리
    window.addEventListener('unload', () => {
        if (socket) {
            socket.emit('leave', { username: username });
            socket.disconnect();
        }
    });
});

// 입력창에 포커스
elements.username.focus();
