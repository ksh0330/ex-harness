#!/usr/bin/env bash
# Preview first. Apply: bash /path/to/ex-harness/install.sh --apply
set -eu
HARNESS_ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
for runtime in python3 python; do
  if command -v "$runtime" >/dev/null 2>&1 && "$runtime" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
    exec "$runtime" "$HARNESS_ROOT/tools/install.py" "$@"
  fi
done
printf '%s\n' 'Python 3.10+ unavailable. Do not install/update runtimes in a restricted exam. Read docs/QUICKSTART.md and use the direct prompt.' >&2
exit 2
