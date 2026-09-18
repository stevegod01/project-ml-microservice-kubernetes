#!/usr/bin/env bash
set -euo pipefail
# Authenticate separately with docker login; no implicit registry/account.
: "${IMAGE:?Set IMAGE to a registry/repository:version you own}"
: "${LOCAL_IMAGE:=udacity-inference:local}"
docker image inspect "$LOCAL_IMAGE" >/dev/null
docker tag "$LOCAL_IMAGE" "$IMAGE"
docker push "$IMAGE"
