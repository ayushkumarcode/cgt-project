#!/bin/bash
# Quick Docker test - runs leaders against real MK1/MK2/MK3 engine
set -e
cd "$(dirname "$0")/../../game/extracted/COMP34612_Student"
docker run --rm --platform linux/amd64 \
  -v "$(pwd)/project_files:/app" \
  -v "$(pwd)/test_harness.py:/app/test_harness.py" \
  stackelberg-test
