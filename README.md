# ex-harness

낯선 프로젝트에서 문제를 좁히고 구현·검증·인계를 수행하는 범용 FDE 하네스.
과제 답안·외부 AI 연결·자동 설정 변경을 포함하지 않는다. 기존 프로젝트의 스택과 규칙을 우선한다.
이 사전 준비용 저장소는 2차 예선 결과 통지 전까지 공개 상태를 유지한다.

## 안전한 설치

과제 폴더의 Bash 터미널에서, 공개 자료 사용이 허용된 경우만 실행한다.

```bash
git clone https://github.com/ksh0330/ex-harness /tmp/ex-harness
bash /tmp/ex-harness/install.sh          # 변경 계획만 출력
bash /tmp/ex-harness/install.sh --apply  # 없는 파일만 추가
```

Python 3.10+가 필요하다. 설치기는 패키지를 설치하지 않고 네트워크에 연결하지 않는다.
기존 AGENTS.md·스킬·docs·Git 설정은 보존한다. 기존 AGENTS가 있으면 아래 문장을 Codex에 직접 입력한다.

```text
과제 README와 기존 AGENTS.md를 먼저 읽고 .harness/AGENTS.md를 보조 지침으로 읽어.
요청의 수용 기준과 관련 코드부터 확인하고 가장 작은 실행 흐름을 구현·검증해.
```

설치가 불가능하면 이 두 문장만 직접 지시해도 핵심 절차를 사용할 수 있다.
스킬이 보이지 않으면 `.agents/skills/verify/SKILL.md를 읽고 수행해`처럼 요청한다.
기존 스킬 이름이 충돌하면 보존되므로 원본 하네스 경로의 SKILL.md를 직접 읽는다.

## 개발·검증

```bash
python -m unittest discover -s tests -v
python tools/check_repo.py
```

선택형 스킬 8개는 [skills](skills)에 있다. 복잡한 과제에서 필요한 스킬만 사용한다.
현재 구현·검증 상태는 [STATUS](docs/STATUS.md), 범위는 [AGREEMENT](docs/AGREEMENT.md), 결정 이유는 [DECISIONS](docs/DECISIONS.md)를 참고한다.
Cofa 실제 실행과 사용자의 운용 실습은 별도로 확인해야 한다.

## 제한 환경

시험에서는 push·Codex 업데이트·개인 키·외부 AI·데이터 전송·Computer Use·설정 및 보안 우회를 하지 않는다.
MCP·Hook·Plugin·추가 에이전트 없이 기본 절차를 수행한다. 인터뷰·서면 합의·세션 교체·전체 테스트를 작은 작업마다 강제하지 않는다.

## 출발점

기존 81aad65의 증거 기반 검증·간결한 구현·상태 보존 원칙을 유지하고 고정 절차와 설치 부작용을 개선한다.
기존 공개 아이디어 출처: forrestchang/andrej-karpathy-skills(코딩 원칙), obra/superpowers(검증 후 완료 주장), mattpocock/skills(인계).
원문을 복사하지 않고 목적에 맞게 작성했다.
