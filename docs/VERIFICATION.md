# 실제 검증 기록

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
