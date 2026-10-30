# 기능 근거와 검증 경계

공식 문서 확인일: 2026-10-31 (KST). 아래 페이지를 실제 열어 본문을 확인했다.
이 문서는 사전 준비 조사 결과다. 시험 중 외부 검색·연결 허용을 뜻하지 않는다.
공식 기능은 버전·계정·관리 정책에 따라 달라진다. Cofa의 제공 CLI와 과제 안내가 현장 기준이다.

| 공식 자료 | 이번 설계에 반영한 내용 |
|---|---|
| [Developer commands](https://learn.chatgpt.com/docs/developer-commands) | CLI slash 명령, side chat·review·compact·resume. 입력창의 `/`로 현장 목록 확인 |
| [CLI reference](https://learn.chatgpt.com/docs/cli/reference) | CLI 실행 옵션. 로컬 `--help`와 교차 확인 |
| [Build skills](https://learn.chatgpt.com/docs/build-skills) | name·description frontmatter, `.agents/skills`, 명시 호출·직접 파일 읽기 대안 |
| [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | 전역에서 프로젝트 하위로 지침 탐색, 디렉터리별 override 우선. 임의의 `.harness/AGENTS.md`는 자동 로드 경로로 간주하지 않음 |
| [Hooks](https://learn.chatgpt.com/docs/hooks) | lifecycle 확장과 trust 검토. 하네스는 Hook을 설치하지 않음 |
| [MCP](https://learn.chatgpt.com/docs/extend/mcp) | 외부 시스템의 도구·정보 연결. 핵심 개발 절차와 분리 |
| [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) | 독립 작업 위임, 모델 상속과 추가 토큰 비용. 단일 세션 대안 유지 |
| [Package your plugin](https://developers.openai.com/plugins/build/plugins) | 스킬과 선택적 연결 기능의 패키징. 이 저장소는 로컬 스킬 폴더로 배포하며 Plugin을 설치하지 않음 |
| [Iterating development workflows](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex) | 지침·계획·상태의 분리와 실제 근거. 예제의 고정 문서·승인 절차를 모든 작업에 강제하지 않음 |

## 공식 / 로컬 / Cofa 구분

| 기능 | 공식 문서 | 이번 Work에서 확인 | Cofa에서 확인할 것 / 대안 |
|---|---|---|---|
| Codex CLI | 지원 | `codex --version`: 0.165.0, `--help` | 제공 버전·실행·로그인 유지 / 제공 터미널과 지시만 사용 |
| Slash commands | 지원 | 문서 확인. TUI 상호작용 미실행 | `/` 목록 / 자연어 지시 |
| 모델 선택 | `/model`, CLI `--model` | CLI 옵션 존재. 계정별 모델 목록 미조회 | 허용 목록 확인. 사용자 안내: Sol 6.1·Terra 5.6·Luna 6.0, Astra 제한 |
| AGENTS.md | 지원 | 본 저장소 지침으로 사용, 설치 시 보존 테스트 | 기존 override·우선 지침 / 명시적으로 보조 지침 읽기 |
| Skills | 지원 | 8개 파일의 제한된 metadata 검사. 설치·충돌 보존 테스트 | `/skills` 또는 `$` 목록 / SKILL.md 직접 읽기 |
| Hooks | 지원 | 문서만 확인, 설치·동작 미실행 | 필요성·허용 여부. 없으면 명령 직접 실행 |
| MCP | 지원 | 문서와 CLI help만 확인, 신규 서버 연결 안 함 | 외부 연결은 시험 제한 준수. 로컬 파일·Mock 대안 |
| Plugins | 지원 | CLI help에 plugin 존재. 설치 안 함 | 관리 정책·외부 권한. 스킬 파일 직접 사용 |
| Subagents | 지원 | 이 준비 작업의 스킬 시나리오 검토에 1개 사용 | 요청·허용·지원 확인. 메인 세션에서 구현 후 리뷰 |
| Side chat | `/side`, `/btw` 문서화 | 문서만 확인 | 명령 존재 / 주 세션에서 짧게 질문 |
| Review | 지원 | `codex review --help` 확인. CLI 모델 리뷰 자체는 미실행 | `/review` 목록 / cross-review 직접 지시 |
| Compact | 지원 | 문서만 확인 | `/compact` 지원 / 상태 파일과 범위 축소 |
| Resume | 지원 | `codex resume --help` 확인 | 저장 세션 목록·선택 / 새 세션에서 Handoff 읽기 |
| Handoff | 저장소 워크플로 | 실제 상태 문서 작성 | 전용 내장 명령으로 가정하지 않음. Markdown 직접 읽기 |

CLI help는 옵션의 존재 증거이며 모델 호출·TUI 동작·Cofa 지원의 증거가 아니다.
가상 출력은 [MANUAL](MANUAL.md), 실제 실행 결과는 [VERIFICATION](VERIFICATION.md)에 구분한다.
`learn.../extend/plugins`는 404였다. 공식 Build skills가 연결한 Package your plugin 페이지를 사용했다.

## 시험 안내의 출처

일정(2026-10-31 10:00~14:00), 최대 과제 180분·후속 6문항 각 5분, 제공 모델과 금지 행위는 사용자가 제공한 안내다.
이번 작업에서 주최 측 원본이나 Cofa 정책 화면을 독립 검증하지 않았다. 현장에서 최신 안내와 상충하면 현장 안내를 따른다.
