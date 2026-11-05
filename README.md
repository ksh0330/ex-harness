# ex-harness

**과제 README가 있는 폴더의 터미널**에서 공개 자료 사용이 허용됐을 때 clone한다. `ex-harness` 폴더 안으로 이동하지 않는다.

```sh
git clone https://github.com/ksh0330/ex-harness
sh ex-harness/start.sh
```

실패 시 대체 명령(Python 3.10+):

```sh
python3 ex-harness/tools/start.py
```

`python`만 있으면 이름을 바꾼다. Windows PowerShell에서는 `python .\ex-harness\tools\start.py`.

**Codex가 열리면 `/model` 또는 제공 선택 화면에서 Sol 6.1을 선택**한다. 사용자 제공 안내의 대안은 Sol 6.0·Terra 5.6·Luna 6.0이며 Astra·Claude는 금지다. 실제 제공 목록과 현장 규정이 우선이다. 시작 실패 시 과제 폴더에서 `codex` 또는 제공 Codex 채팅을 연다. 업데이트·개인 키 설정은 하지 않는다.

모델 선택 후 **Codex 채팅에 최초 프롬프트 한 번** 입력한다:

```text
과제 README와 기존 AGENTS.md를 먼저 읽고 ex-harness/AGENTS.md와 ex-harness/templates/START.md를 보조로 읽어 P1 분석부터 P7 전달까지 진행해.
```

이 문장은 Python이 없어 설치하지 못해도 원본 지침을 읽는다. 이후 P1 분석부터 P7 검증·제출 점검까지 진행한다. 중요한 판단·DM 전송·실행 승인·화면 확인·세션 조작·최종 제출은 사용자가 한다. 터미널 붙여넣기는 `Ctrl+Shift+V`. 긴 요청/DM 응답은 IDE의 Markdown에 저장하고 해당 파일을 읽힌다.

시작 명령은 환경·과제 루트·계획을 출력하고 없는 지침/Skill만 추가한다. 기존 README·AGENTS·코드·Git·설정은 보존한다. 현재 폴더에 README가 없고 후보가 여러 개면 경로를 선택한다. CLI·채팅이 모두 없으면 감독자에게 제공 진입점을 문의한다.

**제출 주의:** 기본 배치는 과제 폴더 안에 `ex-harness/`와 그 내부 `.git`도 둔다. 전체 폴더 제출 시 이 원본도 포함되며 `.gitignore`로 제외되지 않는다. 설치기가 삭제하지 않는다. 과제 밖 형제 폴더 쓰기가 허용되고 제출 범위가 과제 폴더로 확정된 경우의 [외부 배치 명령](docs/QUICKSTART.md#clone-위치와-제출-범위)을 제공한다.

## 필요한 경우만

`--preview`: 무변경 확인, `--no-launch`: 설치만, `--target 경로`: 과제 루트, `--existing-session`: 현재 Codex 유지. 정확한 **현장 허용 모델 ID**를 이미 확인했다면 `--model 실제ID`를 붙여 최초 프롬프트도 자동 전달할 수 있다. 표시 이름을 ID로 추측하지 않는다. 기본 실행은 모델 선택 전에 요청을 보내지 않는다.

기존 `install.sh`는 preview가 기본이고 `--apply`로만 쓴다. 직접 설치도 기존 과제 README 폴더만 허용한다. 추가 패키지·Hook·MCP·Plugin 없이 동작한다.

Skill 8개의 **파일 존재**만 확인한다. Codex가 단계에 맞게 선택하고 미인식이면 `.agents/skills/<이름>/SKILL.md`, 충돌이면 원본 `ex-harness/skills/<이름>/SKILL.md`를 읽는다. 기존 보조 지침 충돌도 덮어쓰지 않고 원본을 안내한다. [시작 지침](templates/START.md)에 단계·결정·검증·로컬 커밋·UI·알고리즘·마감·인계를 정리했다.

Linux Bash·POSIX sh와 Windows Python을 검증했다. **실제 AI 대화·Skill 자동 호출·Hook 활성화·Cofa는 미검증**이며 CLI 인자는 가짜 CLI/PTY로 검증했다. [검증 기록](docs/VERIFICATION.md), [실패 복구](docs/QUICKSTART.md), [용어 설명](docs/BASICS.md). 설치·시작 로직은 네트워크에 연결하지 않으며 Codex는 현장 제공 도구·인증을 사용한다.

## 개발·검증

저장소 루트에서:

```sh
python -m unittest discover -s tests -v
python tools/check_repo.py
```

선택 연습 예제는 `python -m examples.web --db .run/repairs.sqlite3 --port 8000` 또는 `python -m examples.batch import examples/data/archive.csv --db .run/archive.sqlite3`다. 웹은 `0.0.0.0:8000`을 출력하며 사용자가 별도 터미널에서 실행한다. 인증 없는 합성 연습용이므로 실제 개인정보를 넣지 않는다. 대상 과제에는 `--with-examples` 선택 설치 시에만 `.harness/kit`에 복사한다.

자세한 사용은 [매뉴얼](docs/MANUAL.md), [구조·한계](docs/ARCHITECTURE.md), [공식 기능과 현장 구분](docs/SOURCES.md). 현재 [범위](docs/AGREEMENT.md)·[상태](docs/STATUS.md)·[결정](docs/DECISIONS.md)을 기록한다. [이전 아침 연습](docs/MORNING.md)과 [35분 모의시험](docs/SIMULATION.md)은 선택 자료다.

## 제한 환경

시험에서는 push·Codex 업데이트·개인 키·외부 AI·데이터 전송·Computer Use·설정 및 보안 우회를 하지 않는다.
MCP·Hook·Plugin·추가 에이전트 없이 기본 절차를 수행한다. 인터뷰·서면 합의·세션 교체·전체 테스트를 작은 작업마다 강제하지 않는다.

## 출발점

기존 81aad65의 증거 기반 검증·간결한 구현·상태 보존 원칙을 유지하고 고정 절차와 설치 부작용을 개선한다.
기존 공개 아이디어 출처: forrestchang/andrej-karpathy-skills(코딩 원칙), obra/superpowers(검증 후 완료 주장), mattpocock/skills(인계).
원문을 복사하지 않고 목적에 맞게 작성했다.
