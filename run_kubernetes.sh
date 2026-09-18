#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${IMAGE:?Set IMAGE to a built image available to the selected cluster}"
NAMESPACE="${NAMESPACE:-default}"
PORT="${PORT:-8000}"
kubectl create deployment housing-inference --image="$IMAGE" --port=8080 \
  --namespace="$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout status deployment/housing-inference --namespace="$NAMESPACE" --timeout=120s
kubectl port-forward deployment/housing-inference "${PORT}:8080" --namespace="$NAMESPACE"
