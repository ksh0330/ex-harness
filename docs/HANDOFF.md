# 인계

목표: docs/AGREEMENT.md A1~A7을 만족하는 범용 FDE 하네스와 운용 자료.
현재 단계: P7 전달. 구현·운용 자료와 로컬 검증 종료, 사용자 직접 실습과 Cofa 수용은 미확인.
현재 개정: 10/31 아침 계획 변경을 반영한 MORNING·개인 Notion 요약·설치 가이드. 관련 설치 테스트 8개 OK (3.849초), check_repo errors=0. 이전 전체 24개 실행과 이번 관련 검증을 구분한다.
기준 커밋: 93df7c5 (공통 코어·예제), 9e54ffe (설치·지침). 시작 시 사용자 변경 없음.
검증된 환경: Python 3.12.10, Git Bash 5.2.37, codex-cli 0.165.0 (`--version`, `--help` 읽기만 실행).
Cofa: 미검증. 사용자 학습 완료: 미확인.

완료 증거: `python -m unittest discover -s tests -v`: 24 tests OK (8.572초), skip 없음. `python tools/check_repo.py`: skills=8, errors=0. Bash 문법·git diff --check 확인. 기준별 좌표는 docs/VERIFICATION.md.
실패 이력: 기존 Bash preview가 파일을 씀 → 교체·회귀 검증. 테스트용 SQLite 연결 미종료로 Windows cleanup 실패 → 명시적 closing 후 관련 테스트 통과.
공식 quick_validate.py는 PyYAML 부재로 실행 중단. 의존성 없는 제한된 메타데이터 검사로 대체했으며 공식 검증과 동일하다고 주장하지 않는다.
추가 완료: QUICKSTART·MANUAL·ARCHITECTURE·SOURCES·SIMULATION, 터미널 SVG, 가상 과제 README 2개. 설치 후 문서 링크 회귀 테스트. 별도 에이전트의 스킬 텍스트 시뮬레이션과 지적 2건 수정·재확인.
계획 변경: 사용자에게 긴 학습·시뮬레이션 시간이 없다. 확인된 날짜는 10/31이며 08시 이동 중 학습·09시 사전 테스트로 축소했다.
다음 1번: docs/MORNING.md 또는 개인 Notion 요약을 08시에 읽고, 09시에는 여섯 환경 점검 항목만 확인한다. 실제 실행 전 체크하지 않는다.
다음: 관찰된 실패가 있을 때만 MORNING의 수정 판단표에 따라 관련 안내·설치기·대상 앱을 좁게 수정한다. 긴 모의시험은 선택이다.
핵심 근거: Brunch 참가 후기. Tistory는 보조 해설이며 다른 행사의 시간·모델·점수를 이번 규칙으로 복사하지 않는다. 본시험 데이터는 외부 Notion·채팅·GitHub로 옮기지 않는다.
진행/파일 상태: 이번 준비 작업 파일만 변경했다. 시작 시 사용자 변경 없음. 최종 문서·지침·설치기 보강을 P7 커밋에 포함한다. 최종 SHA·원격 push 일치는 대화 최종 보고 또는 git log/ls-remote로 확인한다.
실행: 저장소 루트에서 `python -m examples.web --db .run/repairs.sqlite3 --port 8000` (사용자 별도 터미널). 이 작업에서 계속 실행 중인 서버 없음.
배치: `python -m examples.batch import examples/data/archive.csv --db .run/archive.sqlite3`, 이후 `python -m examples.batch export --db .run/archive.sqlite3`.
결정: docs/DECISIONS.md. 핵심 흐름은 추가 외부 연결·Hook·MCP·Subagent 없이 실행된다. 이번 준비의 독립 스킬 검토에만 에이전트 1개를 사용했다.
알려진 한계: 인증 없음, 중복 import, 동시 export snapshot, 공식 YAML validator 부재, 실제 UI 클릭·Cofa·사용자 이해도 미확인. 기존 업무 DB에 예제를 연결하지 않는다.
주의: 기존 대상 파일을 덮어쓰거나 Git identity를 설정하지 않는다. 인계만으로 실패 코드를 커밋하지 않는다.
이 인계는 세션 종료 지시가 아니다.
