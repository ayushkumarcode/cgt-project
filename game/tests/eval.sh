#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROJ="$ROOT/game/extracted/COMP34612_Student/project_files"
docker run --rm --platform linux/amd64 \
  -v "$PROJ:/app" \
  -v "$ROOT/game/src/leaders.py:/app/leaders_code.py" \
  -v "$ROOT/game/tests/full_eval.py:/app/full_eval.py" \
  stackelberg-test python3 /app/full_eval.py
