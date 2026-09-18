#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8000}"
curl --fail --show-error --silent --max-time 10 \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"CHAS":0,"RM":6.575,"TAX":296,"PTRATIO":15.3,"B":396.9,"LSTAT":4.98}]}' \
  "http://127.0.0.1:${PORT}/predict"
printf '\n'
