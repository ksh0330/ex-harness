# 기능 근거와 검증 경계

## 2026-11-05 최종 개편 확인

- [공식 CLI 명령](https://learn.chatgpt.com/docs/developer-commands?surface=cli) 본문과 로컬 `codex --help`에서 대화형 `[PROMPT]`, `--model`, `/model` 문서 근거를 확인했다. 기본 시작은 모델 선택 후 지시 1회이며, 확인한 ID를 지정할 때만 자동 전달한다. 실제 TUI 모델 선택/모델 응답은 미검증이다.
- [공식 Skill 경로](https://learn.chatgpt.com/docs/build-skills)는 `.agents/skills` 탐색을 설명한다. 하네스는 파일 존재/내용만 확인하며 실제 자동 호출을 입증하지 않는다.
- [공식 Hook](https://learn.chatgpt.com/docs/hooks)은 제공 기능·신뢰 검토를 설명한다. 공식 지원은 현장 허용과 다르다. 이번 작업은 Hook을 설치/활성화하지 않았으며 지침의 단계 점검으로 운영한다.
- 사용자가 제공한 **11/05 재시험 안내**: Cofa Probe 내부 터미널/편집기/Browser/DM, 제공 Codex CLI, Sol 6.1·Sol 6.0·Terra 5.6·Luna 6.0 권장, Astra·Claude 금지, 업데이트 금지, 공개 clone 허용, 시험 push/외부 전송 금지, Ctrl+Shift+V, RAM 16GB, 제출 10GB 이하, 코딩 최대 180분·서술형 30분·최종 23:00 종료, 서술형 AI/붙여넣기 금지. 주최 측 원본·현장 화면을 독립 확인한 기록은 아니며 최신 현장 안내가 우선이다. 아래 이전 일정은 현재 일정이 아니다.

## 2026-11-05 Bootstrap 공식 근거

사전 개선 작업에서 아래 공식 페이지 본문과 로컬 CLI 0.166.0 도움말을 확인했다. 현장 검색·외부 전송 허용 근거로 쓰지 않는다.

| 자료 | 반영 |
|---|---|
| [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli) | 대화형 `codex [PROMPT]`, 작업 디렉터리·resume. 로컬 `codex --help`의 `[PROMPT]`·resume과 교차 확인 |
| [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) | `codex exec`는 비대화형 단발 실행. 시작 프로그램에서 사용하지 않음 |
| [Build skills](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills` 탐색, 변경 자동 감지·목록 미갱신 시 재시작. 파일 존재와 실제 인식 분리 |

사용자가 제공한 Cofa 안내의 범위는 Codex CLI 사용·Node.js 버전 확인이다. Python 기본 설치·정확한 버전을 보장하는 근거는 제공되지 않았다. 시작 프로그램이 실제 런타임을 확인하며 Cofa는 미검증이다.
프롬프트 전달은 로컬 가짜 CLI·PTY 경계에서 검증한다. 실제 AI 호출이나 대화·Skill 활성화를 검증했다고 표시하지 않는다.

## 이전 공식 조사 기록

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

## 10/31 계획 변경에 참고한 자료

- 핵심 참가 후기: [Luka의 Brunch 글](https://brunch.co.kr/@luma/5). 낯선 환경 적응·README 우선·설명과 인계를 반영했다. 다른 행사의 모델·시간·문항·배점은 적용하지 않는다.
- [Cofa 공식 Probe](https://www.getcofa.com/ko/probe): 결과물과 과정·검증·설명을 함께 확인한다는 제품 안내. 실제 응시 규칙을 대체하지 않는다.
- [Tistory Q&A 글](https://donggrri.tistory.com/248): 보조 해설. 일반 HTTP로 본문을 읽었다. 독립 참가 후기/이번 시험 규칙으로 사용하지 않는다.
- 사용자 최신 확인: 학습은 10/31 08시, 사전 테스트는 09시. 긴 시뮬레이션은 선택으로 변경.

### 기존 시험 안내

일정(2026-10-31 10:00~14:00), 최대 과제 180분·후속 6문항 각 5분, 제공 모델과 금지 행위는 사용자가 제공한 안내다.
이번 작업에서 주최 측 원본이나 Cofa 정책 화면을 독립 검증하지 않았다. 현장에서 최신 안내와 상충하면 현장 안내를 따른다.
