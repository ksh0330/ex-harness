# 인계

2026-11-05 현재 개편 기준. 이전 인계는 Git 기록에 보존된다. 이 문서는 세션 종료 지시가 아니다.

목표: AGREEMENT B1~B7. Linux 제한 환경 우선, 과제 README 폴더에서 clone 후 한 번의 시작 명령으로 분석을 시작할 수 있게 한다. 기존 설치기·8개 Skill·사용자 파일을 보존한다.

현재 단계: P7 로컬 구현·문서 전달. 코드 기준 `3aa6ecd` (`[P4] 제한 환경 Bootstrap과 실패 복구 및 진입점 검증`). 운용 지침·검증 기록은 이 문서를 포함하는 P7 커밋에 저장한다. 처음 Git 상태는 clean이었고 현재 변경은 이번 작업뿐이다. 최종 상태/커밋은 `git status --short`, `git log -2 --oneline`으로 확인한다. push는 하지 않았다.

핵심 파일·흐름: start.sh → POSIX install.sh --start → tools/start.py의 환경·루트 선택 → tools/install.py의 기존 plan/apply_plan → 실제 과제 cwd에서 대화형 codex [PROMPT]. tools/start.py는 8개 파일 존재만 확인한다. templates/START.md와 기존 Skill은 P1~P7·중요 결정·로컬 커밋·검증·UI/알고리즘 보강·인계를 안내한다.

선택 이유: Python이 확인될 때만 기존 설치기를 재사용한다. Python 없음은 새 설치 프레임워크 대신 원본 지침을 읽는 채팅 한 문장으로 대체한다. exec는 단발 명령이므로 사용하지 않는다. Windows PS1 정책은 변경하지 않고 검증된 Python 직접 진입을 안내한다.

검증 환경: Windows PowerShell·Python 3.12.9·Git Bash 5.3.9·Node 24.18.1·Codex CLI 0.166.0. Ubuntu 24.04/WSL·Python 3.12.3·Bash·POSIX sh. 초기 샌드박스의 DLL/HTTP/junction 실패와 승인된 로컬 실행을 구분한다.

검증: Windows 전체 45개 중 40 통과·5 skip(19.416초), Ubuntu 전체 45개 중 43 통과·2 skip(18.485초). 출력 문구 수정 후 Windows 관련 21개 중 16 통과·5 skip(7.136초). check_repo skills=8/errors=0. 공식 quick_validate는 UTF-8 모드로 8개 valid. sh/bash 문법·diff 공백 검사 통과. 상세 조건과 테스트 이름은 VERIFICATION에 있다.
코드 커밋의 새 로컬 clone에서도 Ubuntu Bootstrap 21개 중 19 통과·2 skip(3.856초), LOCAL_CLONE_SMOKE_OK. 문서 마무리 후 설치 회귀 8개 통과(3.678초), check_repo·공백 검사 통과.

사용자에게 전달할 입력 위치:

- 과제 README 폴더의 터미널: `git clone https://github.com/ksh0330/ex-harness`, 다음 `sh ex-harness/start.sh`.
- Bash 실패 시 sh로 같은 명령. 셸 스크립트 불가·Python 3.10+ 확인 시 `python3 ex-harness/tools/start.py`. PowerShell은 `python .\ex-harness\tools\start.py`.
- Python 없음: 제공 Codex 채팅에 `과제 README와 기존 AGENTS.md를 먼저 읽고 ex-harness/AGENTS.md와 ex-harness/templates/START.md를 보조로 읽어 P1 분석부터 P7 전달까지 진행해.`
- 이미 Codex 안이면 시작 명령 뒤 `--existing-session`. 실제 경로가 다르면 출력한 경로 사용. 긴 요청/DM은 플랫폼 IDE의 Markdown 메모로 읽힌다.

실패 대응: 모호한 루트는 번호/경로 선택, 비TTY는 --target. 설치 실패는 Codex 시작 금지·신규 파일 rollback(빈 폴더 가능). CLI 부재/실패는 제공 채팅 문장으로 대체. 런타임 설치·권한 우회·설정/identity 변경·push 없음.

남은 한계: 실제 AI 세션·Skill 목록 인식·Cofa·UI 클릭·IDE 붙여넣기·resume은 미검증. 시작 전달은 가짜 CLI/실제 PTY 경계 검증이다. 낮은 Python 버전·Bash 오류는 PATH/stub 모의 조건이다. 선택 PS1은 현재 실행 정책에 막혔다. 강제 종료는 부분 파일이 남을 수 있으며 자동 업그레이드/덮어쓰기는 없다. 사용자/실무자 응답을 만들지 않았다.

다음 행동: 현장에서 제공 CLI/Skill 인식·허용된 미리보기·IDE 입력을 확인한다. 공개 원격에 이 변경을 게시하려면 별도 사용자 push 승인이 필요하다. 시험에서는 push 금지. 로컬 단계별 커밋과 HANDOFF 저장은 완료 범위이며 실제 세션 교체를 실행했다는 뜻이 아니다.

재개 시 과제 루트 터미널에서 `codex resume`으로 기존 세션을 선택하거나 `codex`로 새 세션을 시작한다(지원은 현장 --help 확인). 새 채팅에는 README·AGENTS·이 HANDOFF·STATUS를 읽고 git status 확인 후 이어가라고 입력한다. 기존 세션과 같은 파일을 동시 수정하지 않고 사용자 파일·Codex 설정을 수정하지 않는다. 계속 실행 중인 테스트 서버는 없다.
