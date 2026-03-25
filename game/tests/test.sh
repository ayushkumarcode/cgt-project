#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROJ="$ROOT/game/extracted/COMP34612_Student/project_files"
docker run --rm --platform linux/amd64 \
  -v "$PROJ:/app" \
  -v "$ROOT/game/src/leaders.py:/app/leaders_code.py" \
  -v "$ROOT/game/tests/test_runner.py:/app/test_runner.py" \
  stackelberg-test python3 /app/test_runner.py
