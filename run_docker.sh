#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
IMAGE="${IMAGE:-udacity-inference:local}"
PORT="${PORT:-8000}"
docker build --tag "$IMAGE" .
docker run --rm --init -p "127.0.0.1:${PORT}:8080" "$IMAGE"
