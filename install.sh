#!/usr/bin/env bash
# 사용법: 과제 작업 폴더 루트에서  bash /tmp/h/install.sh
# 기존 파일은 덮어쓰지 않는다. 여러 번 실행해도 안전하다.
set -eu

H="$(cd "$(dirname "$0")" && pwd)"
W="$(pwd)"
echo "[harness] 작업 폴더: $W"

# 1) AGENTS.md: 없으면 생성, 과제 AGENTS.md가 있으면 뒤에 덧붙임 (과제 규칙이 우선)
if [ -f AGENTS.md ]; then
  if grep -q "HARNESS-BEGIN" AGENTS.md; then
    echo "[harness] AGENTS.md 이미 적용됨"
  else
    printf '\n\n' >> AGENTS.md
    cat "$H/AGENTS.md" >> AGENTS.md
    echo "[harness] 과제의 기존 AGENTS.md 뒤에 하네스 규칙을 덧붙임"
  fi
else
  cp "$H/AGENTS.md" AGENTS.md
  echo "[harness] AGENTS.md 생성"
fi

# 2) 스킬: .agents/skills/<이름>/SKILL.md
mkdir -p .agents/skills
for d in "$H"/skills/*/; do
  n="$(basename "$d")"
  if [ -e ".agents/skills/$n" ]; then
    echo "[harness] 스킬 $n 이미 있음, 건너뜀"
  else
    cp -r "$d" ".agents/skills/$n"
  fi
done
echo "[harness] 스킬 설치: $(ls .agents/skills | tr '\n' ' ')"

# 3) 상태 문서와 가이드
mkdir -p docs .harness
[ -f docs/STATUS.md ] || cp "$H/templates/STATUS.md" docs/STATUS.md
cp "$H/README.md" .harness/GUIDE.md

# 4) git 확인 (push는 하지 않는다)
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git config user.name  >/dev/null 2>&1 || git config user.name  "candidate"
  git config user.email >/dev/null 2>&1 || git config user.email "candidate@local"
  echo "[harness] git 저장소 확인됨. 커밋은 [P단계] 태그로, push 금지"
else
  echo "[harness] git 저장소가 아님. 커밋 기록을 남기려면:"
  echo "          git init && git add -A && git commit -m '[P0] 과제 시작 상태'"
fi

cat <<'EOF'

==================== 다음 순서 ====================
1) codex            (실행, 신뢰 확인 나오면 작업 폴더 맞는지 확인)
2) /status          (모델, 권한 확인)
3) /model           (6.1 Sol, medium 선택)
4) /skills          (discover 등 8개가 보이는지 확인)
5) $discover        (P1 발굴 시작)
가이드 다시 보기: 새 터미널에서  less .harness/GUIDE.md
===================================================
EOF
