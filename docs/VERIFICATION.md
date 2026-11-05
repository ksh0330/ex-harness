# 실제 검증 기록

## 2026-11-05 Bootstrap 개편 — 현재 증거

아래 10/31 기록과 구분한다. 현장 Cofa·실제 AI 대화·Skill 활성화·UI 클릭·IDE 붙여넣기·세션 재개는 미검증이다. 이번 작업은 공개 일반 지침과 합성 프로젝트만 사용하며 push·새 외부 연결·개인 키를 사용하지 않았다.

| 환경/명령 | 실제 결과 |
|---|---|
| Windows PowerShell, Python 3.12.9, Git Bash 5.3.9, Node 24.18.1, Codex CLI 0.166.0 | 버전/도움말 확인. Bootstrap의 Windows npm Node 진입점에서도 `--help`: exit=0, `[PROMPT]` 존재 |
| Ubuntu 24.04 (WSL), Python 3.12.3, `/usr/bin/bash`, `/usr/bin/sh` | `pwd`, `command -v`·Python 버전·Linux 확인. Windows npm codex 경로가 보이는 사실을 Linux용 CLI 실행 성공으로 간주하지 않음 |
| Windows `python -m unittest discover -s tests -v` | **45개 중 40 통과·5 skip**, 19.416초, exit=0 |
| Ubuntu `python3 -m unittest discover -s tests -v` | **45개 중 43 통과·2 skip**, 18.485초, exit=0 |
| 출력 문구 수정 후 Windows `python -m unittest discover -s tests -p test_start.py -v` | 21개 중 16 통과·5 skip, 7.136초, exit=0 |
| 코드 커밋 `3aa6ecd`를 새 로컬 clone 후 Ubuntu Bootstrap 회귀 | 21개 중 19 통과·2 skip, 3.856초, exit=0, LOCAL_CLONE_SMOKE_OK. 네트워크 없이 로컬 Git clone 사용 |
| 최종 운용 문서 변경 후 Windows `python -m unittest discover -s tests -p test_install.py -v` | 8개 통과, 3.678초, exit=0. 설치본 상대 링크·보존·재실행 확인 |
| Windows/Ubuntu `python[3] tools/check_repo.py` | skills=8/errors=0, exit=0; 원래 8개 이름·제한된 metadata·문서 링크 검사 |
| Ubuntu `sh -n start.sh install.sh`, `bash -n start.sh install.sh` | exit=0 |
| 공식 skill-creator `quick_validate.py`를 각 8개에 `python -X utf8`로 실행 | 8개 모두 `Skill is valid!`, exit=0. 기본 cp949는 UnicodeDecodeError였고 인코딩 모드만 바꿔 재확인 |
| `git diff --check`, 첫 커밋 전 `git diff --cached --check` | exit=0 |

Windows의 skip: POSIX 전용 격리/PTY 4개, PS1 실행 정책 차단 1개. Linux의 skip: PowerShell 전용 2개. PS1을 허용하려고 정책을 변경하거나 우회하지 않았으며, **PowerShell의 Python 직접 실행은 실제 통과**했다.
초기 샌드박스에서 Bash 3221225794·HTTP 10013·junction 권한으로 실패했다. 승인된 로컬 검증에서 기존 테스트 24개와 전체 회귀를 실행해 환경 제한과 구분했다. 이 로컬 실행 권한이 시험 환경의 우회 허용을 뜻하지 않는다.

### 요구된 회귀 조건과 테스트 경계

주요 증거: `tests/test_start.py`의 테스트 이름으로 연결한다. 위치는 향후 편집으로 이동할 수 있다.

| 조건 | 증거/결과 |
|---|---|
| 정상 Bash·POSIX sh·실행 비트 불필요 | `test_bash_and_posix_sh_without_execute_bit_requirement`: Linux 실제 셸, 설치 후 채팅 대안까지 |
| README 폴더 아래 clone 배치에서 시작 | `test_real_sh_with_pty_launches_fake_cli_from_readme_directory`: **`sh ex-harness/start.sh`**, 실제 Linux PTY·가짜 CLI로 cwd/한 개 prompt 전달 확인. 실제 AI 호출 아님 |
| Windows PowerShell | `test_powershell_python_entry_preserves_project`: 실제 PowerShell에서 Python 공통 진입점 실행 |
| Python 없음·낮음·실행 실패 | `test_python_absent_low_or_broken_runtime_falls_back_without_install`: 격리 PATH·실패 stub, 무설치/대안 확인. 실제 구버전 Python 환경은 미검증 |
| Bash 실행 불가 | `test_bash_broken_sh_and_python_fallback`: Bash 실패 stub·실제 sh·Python 대체 선택 |
| Bash·sh 둘 다 없음 | `test_python_entry_without_any_shell`: 빈 PATH에서 Python 절대 경로로 시작·설치. Python도 없으면 제공 채팅 대안(실제 플랫폼 입력 미검증) |
| Git 없음 | 위 빈 PATH + `test_one_command_installs_and_passes_single_interactive_prompt`: Git init/설정 생성 없음 |
| 상위 README·하네스 내부 실행·다중 후보 | `test_target_parent_child_and_harness_locations`, `test_ambiguous_root_requires_number_or_path_and_no_noninteractive_guess`, `test_no_readme_and_harness_target_rejected` |
| 기존 AGENTS·사용자 변경·2회 실행 | `test_repeat_preserves_readme_agents_dirty_files_and_identity`, 기존 `test_apply_preserves_existing_and_repeat_is_identical` |
| 실제 Git staged/unstaged 변경 보존 | `test_real_git_staged_user_work_and_config_are_preserved`: 합성 Git 저장소에서 index 내용·README·config 보존, 하네스 자동 stage 없음 |
| Skill 미인식/충돌 | `test_skill_conflict_uses_source_fallback_does_not_claim_activation`: 원본 경로와 미확인 출력. 실제 Codex 목록 인식은 미검증 |
| Codex 없음·help 미지원·실행 실패 | `test_missing_or_unsupported_cli_prints_chat_fallback`, `test_cli_failure_is_not_success_and_does_not_retry` |
| 설치 도중 오류 | `test_install_io_failure_rolls_back_new_files_and_never_launches`, `test_preflight_failure_never_launches`, `test_source_skill_missing_fails_before_mutation` |
| 기존 세션·비TTY·preview | `test_existing_session_or_no_tty_does_not_nest_cli`, `test_preview_no_writes_no_cli` |
| Hook 없음 | `test_one_command_installs_and_passes_single_interactive_prompt`: 추가 설정·Hook·외부 의존성 없이 fake CLI 전달 |
| 에디터 입력 전달 | QUICKSTART의 플랫폼 내부 Markdown→짧은 채팅 지시 절차 검토. 실제 IDE 붙여넣기/AI가 메모를 읽는 동작은 **미검증** |
| 단계별 로컬 커밋·Handoff | 이번 실제 로컬 커밋 `3aa6ecd`(P4)와 이 개편을 마무리하는 P7 커밋, 최신 HANDOFF·STATUS. 타 과제의 자율 커밋/실제 resume은 **미검증** |
| 실제 UI·알고리즘 개선 | 운영 지침·Skill 보강. 기존 HTTP/CSV 기능 회귀 통과. 실제 UI 조작·특정 과제의 최적화 성과는 **미검증** |

설치기는 파일 추가만 수행하며 Skill의 런타임 활성화를 검증하지 않는다. 정상 I/O 예외 시 신규 파일만 rollback하고 빈 디렉터리는 남길 수 있다. 강제 종료는 부분 파일이 남을 수 있다. 실제 CLI 인증·터미널·정책은 현장에서 확인한다.

## 이전 검증 기록 (2026-10-31)

검증 환경: Windows Work, Python 3.12.10, Git Bash 5.2.37, Codex CLI 0.165.0.
기준일: 2026-10-31 KST. 이 기록은 Cofa 실행·사용자 학습 완료를 의미하지 않는다.

## 현재까지 실제 실행

- `python -m unittest discover -s tests -v`: P5에서 **23 tests OK**, 7.704초, 종료 코드 0.
- `python tools/check_repo.py`: P5에서 **skills=8; errors=0**, 종료 코드 0. 제한된 frontmatter·로컬 Markdown 링크 검사다.
- Git Bash `bash -n install.sh`, `git diff --check`: 종료 코드 0.
- `codex --version`, `codex --help`, `codex review --help`, `codex resume --help`: 읽기 전용 실행 확인. 모델 호출·TUI 상호작용 검증 아님.

P6에서 설치된 문서 링크 회귀 테스트를 추가했다. 최종 전체 재실행 결과는 아래에 기록했다.

## 수용 기준별 근거

파일:줄 좌표는 아래에 기록했다. 테스트 이름은 unittest 출력에서 검색할 수 있다.

| 기준 | 실제 증거 | 한계 |
|---|---|---|
| A1 설치 보존 | test_preview_creates_nothing, test_apply_preserves_existing_and_repeat_is_identical, test_link_escape_is_rejected, test_preflight_rejects_blocked_parent_without_partial_install, test_bash_wrapper | Git Bash/Windows에서 실행. Linux·Cofa는 미검증. 설치 중 디스크 장애·악의적 동시 파일 변경은 미검증 |
| A2 외부 기능 없는 코어 | 실행 코드의 import는 표준 라이브러리·저장소 모듈만. HTTP 요청은 loopback. test_optional_installed_kit_runs_outside_source | Codex 서비스 자체의 오프라인 실행 보장이 아니라 코어·예제·지침에 추가 연결이 필요 없다는 뜻 |
| A3 재사용·정확성 | test_http_full_flow_persists_and_batch_exports_same_records, test_csv_import_export_and_no_overwrite, test_database_error_mid_batch_rolls_back, test_concurrent_transitions_allow_one_winner, test_export_includes_more_than_one_page | 실제 브라우저 클릭·운영 부하·외부 API·인증은 검증하지 않음 |
| A4 상황별 스킬 | 5개 텍스트 시나리오를 별도 에이전트로 검토, 아래 기록 | 행동 시뮬레이션이지 Cofa 에이전트 실제 실행·사용자 운용 검증은 아님 |
| A5 운용 문서 | MANUAL·QUICKSTART·SOURCES, check_repo 및 설치 문서 링크 테스트 | 제공 버전·현장 허용 확인 필요. 공식 TUI 명령은 문서 근거 |
| A6 모의시험·학습 | SIMULATION·examples/tasks 2개, PM 결정·실패·중단·재개·인계·설명 체크 | 사용자의 35분 직접 수행·이해도는 미확인 |
| A7 최종 저장 | 아래 최종 검증·Git 기록 | 원격 확인 전 push 성공으로 표시하지 않음 |

## 실패를 통해 확인한 것

1. 기존 Bash 설치기는 인자 없이 실행해도 파일을 생성했다. preview 무변경 테스트가 실패한 뒤 wrapper를 교체했고 회귀 검증했다.
2. core 테스트를 구현 전에 실행해 fde.records 미존재로 실패함을 확인한 뒤 코어를 구현했다. 이후 상태·검색·배치 검증이 통과했다.
3. 오류 주입 테스트 두 곳에서 SQLite 연결을 닫지 않아 Windows 임시 폴더 삭제가 실패했다. 동일 증상 2건 뒤 반복을 멈추고 테스트 연결/앱 연결 두 가설을 보고했다. 테스트 연결의 명시적 close 후 관련 3개 테스트와 전체 테스트가 통과했다.
4. 공식 skill-creator의 quick_validate.py 실행은 `ModuleNotFoundError: No module named 'yaml'`로 중단됐다. PyYAML을 설치하지 않고 tools/check_repo.py의 제한된 포맷 검사로 대체했다. 공식 YAML validator 통과로 표시하지 않는다.

## 스킬의 독립 텍스트 시나리오 검토

별도 에이전트가 파일 수정·외부 전송 없이 지침을 읽고 첫 행동·실행 경계·종료 행동을 답했다.

| 가상 요청 | 검토 결과 |
|---|---|
| 버튼 문구만 변경, 구현 위임 | 관련 파일만 변경·해당 검증, 인터뷰·합의·재승인 강제 없음 |
| 실패 테스트·사용자 변경이 있는 중단·handoff | 구현 중단, 사실과 실패 보존, 자동 stage/commit·세션 교체 없음 |
| 명확한 README·인터뷰 대상 없는 agreement·구현 | 명세 근거로 기준 작성 후 구현 진행, 실무자 확인을 만들지 않음 |
| 별도 세션 없는 cross-review | 현재 세션에서 읽기·관련 검증, 독립 검증으로 표시하지 않음 |
| Cofa 시험 중 push 요청 | 시험 제한 해제로 간주하지 않고 로컬 보존 |

검토에서 발견한 두 모호함을 수정했다: 시험 중 push 요청의 처리, 리뷰 테스트의 임시 파일 허용 경계.
동일 에이전트가 수정된 두 파일을 다시 읽고 해당 모호함 해소를 보고했다. 실제 사용자/모델 운용 반복 시험은 아니다.

## 최종 재실행·좌표·Git

실제 재실행 명령과 출력 요지 (종료 코드 모두 0):

```text
python -m unittest discover -s tests -v
Ran 24 tests in 8.572s
OK

python tools/check_repo.py
skills=8; errors=0 (restricted frontmatter/link check; not the official YAML validator)

bash -n install.sh
(출력 없음)

git diff --check
(공백 오류 없음. Windows README 줄바꿈 정규화 안내만 출력)
```

24개: core 5개 + examples 11개 + install 8개. skip 없음.

| 판정 근거 | 파일:줄 |
|---|---|
| 설치 계획·경로 사전 검사 | tools/install.py:24 |
| preview·명시적 적용·기존 파일 보존 | tools/install.py:74, tests/test_install.py:29, tests/test_install.py:35 |
| 설치된 가이드 링크 | tests/test_install.py:64 |
| 링크 이탈 차단 | tests/test_install.py:90 |
| 공통 입력 검사·일괄 저장·상태·검색 | fde/records.py:26, fde/records.py:64, fde/records.py:81, fde/records.py:94 |
| 실제 HTTP와 CLI의 같은 데이터 사용 | tests/test_examples.py:56 |
| 실제 서버 명령·0.0.0.0·배정 포트·health | tests/test_examples.py:174 |
| CSV→공통 스키마 어댑터 | examples/batch.py:15 |
| DB 실패 중간 rollback·동시 전환 | tests/test_examples.py:144, tests/test_examples.py:152 |
| 설치된 선택 예제 실행 | tests/test_examples.py:165 |
| 시험 push 요청 경계·리뷰 임시 파일 경계 | AGENTS.md:33, skills/cross-review/SKILL.md:7 |

비밀값 패턴 검사도 실행했다: 대상 코드·스킬·문서에서 API key/token·private key 대표 패턴 일치 0건. 이는 완전한 비밀값 탐지 보장이 아니다.
공식 문서만 열었으며 신규 MCP·Hook·Plugin·개인 키를 설정하지 않았다. 테스트 서버·자식 프로세스는 각 테스트에서 종료했다.

구현 기준 커밋: `9e54ffe`(설치·지침), `93df7c5`(코어·예제).
최종 변경에는 설치용 GUIDE·문서/그림/과제 카드 복사와 링크 회귀 테스트, 지침 경계 보강이 포함된다.
이 기록과 최종 인계를 포함하는 P7 커밋의 SHA 및 원격 push 확인은 작업 최종 보고에 남긴다. 확인 명령: `git log -1 --oneline`, `git ls-remote origin refs/heads/main`.

## 남아 있는 사용자·현장 수용

- Cofa: 제공 CLI·허용 모델·/명령·스킬 탐색·포트 전달·제출 절차를 직접 확인해야 한다.
- 사용자: QUICKSTART 09:00 체크리스트와 모의시험을 직접 수행하고 구조·약점을 설명해야 한다. 이 작업이 사용자의 이해도를 대신 확인하지 않는다.
- 브라우저: 정적 HTML 응답·HTTP/DB 흐름은 검증했으나 실제 버튼 클릭·렌더링·Cofa 미리보기는 미검증이다.
- 운영 범위: 인증·규제·실제 고객 API·대용량·일관된 export snapshot은 미구현/미검증이다.
- 공식 skill validator: PyYAML 부재. 제한된 메타데이터 검사만 수행했다.

## 10/31 아침 운용 계획 개정

사용자 시간 제약에 따라 MORNING·개인 Notion 요약을 작성하고 모의시험을 선택으로 변경했다.
핵심 참가 후기는 Brunch, 공식 제품 안내는 Cofa, Tistory는 보조 해설로 구분했다.
앱 코어는 바꾸지 않았다. 설치기에 MORNING 복사만 추가하고 실제 파일 내용 일치·설치 링크 회귀를 확인했다.

- `python -m unittest discover -s tests -p test_install.py -v`: **8 tests OK**, 3.849초, 종료 0.
- `python tools/check_repo.py`: **skills=8; errors=0**, 종료 0.
- `git diff --check`: 공백 오류 없음, 종료 0.
- 전체 24개 결과는 위의 이전 전체 실행 기록이다. 이번 변경에는 설치 관련 8개와 문서/스킬 검사를 적용했다.
- GitHub 연결의 저장소 metadata: public, 기본 브랜치 main 확인. Notion 개인 페이지 생성 후 읽어 날짜·용어·명령·핵심 후기·코드 블록 저장을 확인했다.
- 실제 Cofa 실행·사용자 학습·35분 모의시험은 아직 검증하지 않았다. 시간 제약을 수용 완료로 바꾸지 않는다.

## 초보자용 사용 안내 개정

- 사용자 수준에 맞춰 BASICS에 입력 위치·여섯 핵심말·주문→제작→확인 흐름·질문 문장·나머지 용어 풀이를 작성했다.
- AGENTS에 처음 쓰는 용어를 뜻·예·행동으로 설명하는 규칙을 추가했다. Notion은 핵심 용어와 결과 판단을 먼저, 나머지 사전은 접어서 보도록 변경했다.
- 새 PC 설치·시작 절차는 추가하지 않았다. 저장소가 열린 준비용 Codex 새 대화 프롬프트 한 개를 포함하고 이전 PC에 고정된 D: 경로는 제거했다.
- Notion 읽기에서 발견한 잘못된 자동 링크 `http://install.py/install.sh`는 실제 파일 이름의 코드 표기로 수정했다.
- `python -m unittest discover -s tests -p test_install.py -v`: **8 tests OK**, 4.521초, 종료 0. BASICS·MORNING의 설치본 내용 일치와 가이드 링크까지 검증했다.
- `python tools/check_repo.py`: **skills=8; errors=0**, 종료 0. `git diff --check`: 공백 오류 없음, 종료 0.
- 앱 코어는 변경하지 않았다. 사용자 직접 활용·이해도와 Cofa 현장 동작은 계속 미확인이다.
