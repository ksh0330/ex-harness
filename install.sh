#!/bin/sh
# POSIX entry point. Installer previews by default; start.sh selects bootstrap.
set -eu
HARNESS_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
entry=install.py
if [ "${1-}" = --start ]; then
  shift
  entry=start.py
  printf 'cwd=%s\nharness=%s\n' "$(pwd)" "$HARNESS_ROOT"
  for name in bash sh python3 python codex; do
    printf '%s=' "$name"
    command -v "$name" || printf '%s\n' 'not found'
  done
fi
for runtime in python3 python; do
  if command -v "$runtime" >/dev/null 2>&1; then
    if "$runtime" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
      exec "$runtime" "$HARNESS_ROOT/tools/$entry" "$@"
    else
      printf '%s\n' "$runtime -c version check failed (requires Python 3.10+); trying next runtime." >&2
    fi
  fi
done
printf '%s\n' 'Python 3.10+ unavailable; no installation or Codex launch performed. Automatic recovery: no.' >&2
printf '%s\n' 'Next: in the provided Codex chat, enter this one sentence:' >&2
printf '과제 README와 기존 AGENTS.md를 먼저 읽고 "%s/AGENTS.md"와 "%s/templates/START.md"를 보조로 읽어 P1 분석부터 P7 전달까지 진행해.\n' "$HARNESS_ROOT" "$HARNESS_ROOT" >&2
printf '%s\n' 'If no Codex chat/CLI is available, ask the proctor for the provided entry point; do not install or change security settings.' >&2
exit 2
