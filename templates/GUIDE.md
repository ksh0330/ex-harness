# 설치된 하네스 안내

이 폴더는 보조 지침과 원본 하네스의 운용 자료다. 대상 과제 README·기존 AGENTS가 우선이다.
원본의 검증 기록은 사전 준비 환경 결과이며 이 프로젝트·Cofa의 통과 증거가 아니다.

1. [빠른 시작](docs/QUICKSTART.md), [명령 실습](docs/MANUAL.md)을 필요한 만큼 읽는다.
2. 기존 AGENTS가 있으면 `과제 지침을 먼저 따르고 .harness/AGENTS.md를 보조로 읽어`라고 직접 입력한다.
3. [설치된 스킬](../.agents/skills)은 기존 이름 충돌 시 보존된다. 충돌한 버전을 새 버전으로 간주하지 않는다.
4. [구조와 한계](docs/ARCHITECTURE.md), [가상 모의시험](docs/SIMULATION.md), [공식 기능 경계](docs/SOURCES.md)를 참고한다.
5. templates/STATUS.md는 골격이다. 현재 과제 상태는 실제 사실을 과제 지정 위치에 기록한다.

`--with-examples`를 선택한 경우에만 kit/에 Python 코드가 있다. kit/에서 `python -m examples.web --port 8000` 또는 배치 명령을 실행한다.
설치는 파일을 추가할 뿐 서버 실행·Git 작업·Codex 설정 변경·외부 연결을 수행하지 않는다.
