#!/usr/bin/env bash
# Run Alembic after removing macOS AppleDouble (._*) files.
#
# The repository lives on an ExFAT volume, so macOS may create files such as
# alembic/versions/._xxxx.py. Alembic loads every *.py in the versions
# directory, and those binary files cause:
#   SyntaxError: source code string cannot contain null bytes
#
# Usage is identical to alembic, e.g.:
#   scripts/alembic.sh upgrade head
#   scripts/alembic.sh revision --autogenerate -m "add column"

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

find "$ROOT_DIR/alembic" -name '._*' -delete

exec uv run --project "$ROOT_DIR" alembic "$@"
