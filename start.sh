#!/bin/sh
# This file and install.sh are POSIX-compatible; no Bash requirement or chmod.
set -eu
HARNESS_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
set -- --start "$@"
. "$HARNESS_ROOT/install.sh"
