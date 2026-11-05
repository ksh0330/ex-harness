# ex-harness

**과제 README가 있는 폴더의 터미널**에서 공개 자료 사용이 허용됐을 때 clone한다. `ex-harness` 폴더 안으로 이동하지 않는다.

```sh
git clone https://github.com/ksh0330/ex-harness
sh ex-harness/start.sh
```

시작 명령 하나가 환경·과제 루트·설치 계획을 출력하고, 없는 지침/Skill만 추가한 뒤 대화형 Codex에 P1 분석 시작 지침을 전달한다. 기존 README·AGENTS·사용자 변경·설정은 보존한다. 후보가 여러 개면 번호 또는 경로를 선택한다.

Linux Bash·POSIX `sh`(Ubuntu 24.04), Windows PowerShell의 Python 진입점을 실제 검증했다. **CLI 전달은 가짜 CLI/PTY로 검증했으며 실제 AI 대화·Skill 인식·Cofa는 미검증**이다. Python 기본 설치를 가정하지 않는다. [검증 기록](docs/VERIFICATION.md).

| 상황 | 과제 README 폴더 터미널에 입력 |
|---|---|
| `bash` 실행 실패, `sh` 사용 가능 | `sh ex-harness/start.sh` (두 스크립트 모두 POSIX 호환) |
| 셸 스크립트 불가, Python 3.10+ 확인됨 | `python3 ex-harness/tools/start.py` (`python`만 확인되면 이름 교체) |
| Windows PowerShell | `python .\ex-harness\tools\start.py` |
| 이미 Codex가 실행 중 | 시작 명령 뒤 `--existing-session` 추가 또는 아래 문장 입력 |

Python이 없거나 버전이 낮으면 **파일 설치·Codex 실행 없이** 다음 대안을 출력한다. 제공된 **Codex 채팅**에 한 문장 입력한다.

```text
과제 README와 기존 AGENTS.md를 먼저 읽고 ex-harness/AGENTS.md와 ex-harness/templates/START.md를 보조로 읽어 P1 분석부터 P7 전달까지 진행해.
```

CLI가 없거나 실행 실패해도 위 문장으로 제공 채팅에서 진행한다. CLI·채팅 모두 없으면 감독자에게 제공 진입점을 문의한다. 런타임 설치·업데이트·보안 우회는 하지 않는다. 긴 요청·담당자 DM은 플랫폼 IDE 편집기에 Markdown으로 저장하고 Codex에 그 파일을 읽힌다.

## 필요한 경우만

`--preview`는 무변경 계획 확인, `--no-launch`는 설치 후 채팅용 문장 출력, `--target 경로`는 과제 루트 지정이다. 기존 `install.sh`는 계속 preview가 기본이며 `--apply`로만 쓴다. 부트스트랩은 이 설치기를 재사용한다. 추가 패키지·Hook·MCP·Plugin 없이 동작한다.

Skill 8개의 **파일 존재**만 확인한다. 목록에 인식되면 사용하고, 미인식이면 `.agents/skills/verify/SKILL.md`를 직접 읽힌다. 이름 충돌은 보존하며 원본 `ex-harness/skills/verify/SKILL.md`를 읽힌다. [시작 지침](templates/START.md)에 P1~P7·중요 결정·검증된 로컬 커밋·UI·알고리즘 보강·인계를 정리했다.

낯선 용어는 [처음 쓰는 사람 설명](docs/BASICS.md), 실패 원인별 다음 행동은 [빠른 시작](docs/QUICKSTART.md)을 참고한다. 설치·시작 로직은 네트워크에 연결하지 않는다. Codex 사용은 현장에서 허용된 도구·인증만 사용한다.

## 개발·검증

저장소 루트에서 웹 연습 서버를 실행한다. 사용자가 별도 터미널에서 계속 실행한다.

```bash
python -m examples.web --db .run/repairs.sqlite3 --port 8000
```

출력은 `Listening on 0.0.0.0:8000`. 로컬 브라우저는 `http://localhost:8000`, IDE 미리보기는 실제 출력된 포트와 `/`를 지정한다.
등록 → 검색 → 처리 시작 → 완료를 확인한다. 인증 없는 연습 서버이므로 실제 개인정보를 넣지 않는다.

별도의 비웹 예제는 자료 보관 CSV를 같은 검증·SQLite 코어로 처리한다.

```bash
python -m examples.batch import examples/data/archive.csv --db .run/archive.sqlite3
python -m examples.batch export --db .run/archive.sqlite3
```

첫 명령은 `{"imported": 3}`, 두 번째는 레코드와 상태별 집계를 JSON으로 출력한다.
재수입은 새 레코드를 추가한다. 중복 제거는 구현하지 않았다. `--output 새파일.json`은 기존 파일을 덮어쓰지 않는다.
대상 프로젝트에 예제가 필요하면 설치 시 `--with-examples`를 추가하고 `.harness/kit`에서 위 명령을 실행한다.
이 선택을 하지 않으면 대상 앱 코드·DB는 설치하지 않는다.

```bash
python -m unittest discover -s tests -v
python tools/check_repo.py
```

선택형 스킬 8개는 [skills](skills)에 있다. 복잡한 과제에서 필요한 스킬만 사용한다.
시간이 없으면 [08시 아침 요약·09시 점검](docs/MORNING.md)부터 읽는다. 용어·명령·저장소 구조·현장 수정 판단·복사용 프롬프트를 한곳에 모았다.
자세한 내용은 [빠른 시작](docs/QUICKSTART.md), [명령 실습 매뉴얼](docs/MANUAL.md)을 참고한다. [35분 모의시험](docs/SIMULATION.md)은 선택 자료다.
[구조·재사용·한계](docs/ARCHITECTURE.md), [공식 기능과 Cofa 구분](docs/SOURCES.md), [실제 검증 결과](docs/VERIFICATION.md)도 제공한다.
현재 구현·검증 상태는 [STATUS](docs/STATUS.md), 범위는 [AGREEMENT](docs/AGREEMENT.md), 결정 이유는 [DECISIONS](docs/DECISIONS.md)를 참고한다.
Cofa 실제 실행과 사용자의 운용 실습은 별도로 확인해야 한다.

## 제한 환경

시험에서는 push·Codex 업데이트·개인 키·외부 AI·데이터 전송·Computer Use·설정 및 보안 우회를 하지 않는다.
MCP·Hook·Plugin·추가 에이전트 없이 기본 절차를 수행한다. 인터뷰·서면 합의·세션 교체·전체 테스트를 작은 작업마다 강제하지 않는다.

## 출발점

기존 81aad65의 증거 기반 검증·간결한 구현·상태 보존 원칙을 유지하고 고정 절차와 설치 부작용을 개선한다.
기존 공개 아이디어 출처: forrestchang/andrej-karpathy-skills(코딩 원칙), obra/superpowers(검증 후 완료 주장), mattpocock/skills(인계).
원문을 복사하지 않고 목적에 맞게 작성했다.
