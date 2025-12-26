# Claude Plugins - Auto Skills Collection

> **코딩하면서 자동으로 활용하는** Claude Code Skills 라이브러리

**핵심**: 한 번 설정하면 Claude/Antigravity가 필요할 때 **자동으로 찾아서 사용**합니다! 🚀

---

## 📋 포함된 Skills

| Skill | 기능 | 인기도 | 자동 활성화 시점 |
|-------|------|--------|------------------|
| **GitHub Integration** | PR, Issue, CI/CD 관리 | ⭐ 25,100+ stars | GitHub URL/저장소 언급 시 |
| **Sentry Debugger** | 실시간 에러 분석 | ⭐ 공식 | 에러/디버깅 요청 시 |
| **Database Query** | SQL 쿼리 작성/최적화 | ⭐ 필수 도구 | 데이터베이스 작업 시 |
| **Code Intelligence** | 코드 분석/리팩토링 | ⭐ LSP 통합 | 코드 분석 요청 시 |

---

## 🚀 빠른 시작 (5분)

### 1️⃣ 자동 설정 실행 (한 번만)

```powershell
# 관리자 권한으로 실행
c:\antigravity\claude_plugins\setup_auto_skills.bat
```

**이게 전부입니다!** 이제 모든 프로젝트에서 자동으로 작동합니다! ✅

### 2️⃣ MCP 서버 연결 (선택사항)

Skills가 외부 서비스와 통신하려면 MCP 서버 연결 필요:

#### GitHub 연결
```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

#### Sentry 연결
```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

#### Database 연결 (PostgreSQL 예시)
```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "postgresql://user:pass@localhost:5432/mydb"
```

---

## 💡 사용 방법

### ✨ 자동 활성화 (추천)

**아무것도 하지 마세요!** Claude가 알아서 찾아서 씁니다:

```
당신: "GitHub에서 최근 PR 리뷰해줘"
Claude: [자동으로 GitHub Integration Skill 활성화] ✅

당신: "이 에러 왜 났어?"
Claude: [자동으로 Sentry Debugger Skill 활성화] ✅

당신: "user 테이블 스키마 보여줘"
Claude: [자동으로 Database Query Skill 활성화] ✅
```

### 🎯 실제 사용 예시

#### GitHub 작업
```
"feature 브랜치로 PR 만들어줘"
"bug 라벨 달린 이슈 전부 보여줘"
"마지막 CI 왜 실패했어?"
```

#### 에러 디버깅
```
"production 500 에러 원인 찾아줘"
"issue #12345 stack trace 보여줘"
"이 크래시 몇 명한테 영향 줬어?"
```

#### 데이터베이스 작업
```
"지난달 등록한 유저 보여줘"
"이 쿼리 최적화해줘"
"orders 테이블 스키마 뭐야?"
```

#### 코드 분석
```
"이 함수 어디서 정의됐어?"
"이 변수 어디서 쓰이는지 찾아줘"
"이 코드 리팩토링 제안해줘"
```

---

## 📂 폴더 구조

```
c:\antigravity\claude_plugins\
├── skills\                          ← Skills 정의 (자동 활성화)
│   ├── github_integration.md
│   ├── sentry_debugger.md
│   ├── database_query.md
│   └── code_intelligence.md
│
├── source\                          ← 원본 소스코드 (참고용, 향후 추가)
│
├── setup_auto_skills.bat            ← 자동 설정 스크립트
└── README.md                        ← 이 파일
```

---

## 🔧 고급 설정

### 프로젝트별 Skills 추가

프로젝트 전용 Skills는 프로젝트 폴더에:

```
your-project\
└── .claude\
    └── skills\
        └── custom_skill.md    ← 이 프로젝트에서만 활성화
```

### 새 Skill 추가하기

1. `c:\antigravity\claude_plugins\skills\` 폴더에 새 `.md` 파일 생성
2. Skill 형식으로 작성 (기존 파일 참고)
3. **즉시 자동 인식됨!** 재설정 불필요 ✅

### Skill 비활성화

특정 Skill 일시 비활성화:
```powershell
# 파일 이름 변경 (.md → .md.disabled)
ren "c:\antigravity\claude_plugins\skills\github_integration.md" "github_integration.md.disabled"
```

---

## ❓ FAQ

### Q: 설정 후 즉시 작동하나요?
**A**: 네! VSCode 재시작 없이 바로 사용 가능합니다.

### Q: 모든 프로젝트에서 작동하나요?
**A**: 네! 글로벌 설정이라 어떤 프로젝트든 자동 활성화됩니다.

### Q: MCP 서버 없이도 되나요?
**A**: Skills 자체는 작동하지만, 외부 서비스(GitHub, Sentry 등) 연결은 MCP 필요합니다.

### Q: Antigravity에서도 되나요?
**A**: Claude Code Skills 시스템을 따르는 모든 도구에서 작동합니다.

### Q: Skill 추가/수정하면 재설정 필요한가요?
**A**: 아니요! 파일만 수정하면 자동 반영됩니다.

---

## 🎯 다음 단계

### 추가 예정 Skills
- [ ] Notion Integration (문서 동기화)
- [ ] Slack Bot (알림 자동화)
- [ ] Jira Integration (이슈 트래킹)
- [ ] AWS CLI Helper (클라우드 관리)
- [ ] Docker Manager (컨테이너 관리)

### 직접 만들기
Skill 제작 가이드: https://code.claude.com/docs/en/skills.md

---

## 📚 참고 자료

- [Claude Code 공식 문서](https://code.claude.com/docs)
- [Skills 작성 가이드](https://code.claude.com/docs/en/skills.md)
- [MCP 서버 목록](https://mcpcat.io/guides/best-mcp-servers-for-claude-code/)
- [GitHub MCP Server](https://github.com/github/github-mcp-server) (25,100+ stars)
- [Sentry MCP 문서](https://docs.sentry.io/product/sentry-mcp/)

---

## 🆘 문제 해결

### "Skills가 자동 활성화 안 돼요"
1. 설정 스크립트 실행했는지 확인
2. 심볼릭 링크 확인: `dir "%USERPROFILE%\.claude\skills"`
3. Skills 파일 경로 확인: `dir "c:\antigravity\claude_plugins\skills"`

### "MCP 서버 연결 실패"
1. `claude --version` 명령어로 Claude CLI 설치 확인
2. API 키 설정 확인
3. 네트워크 연결 확인

### "관리자 권한 오류"
setup_auto_skills.bat 파일 우클릭 → "관리자 권한으로 실행"

---

**최종 업데이트**: 2025-12-26

**Made with** ❤️ **for Antigravity Projects**
