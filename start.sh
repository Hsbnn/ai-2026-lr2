#!/usr/bin/env bash

set -euo pipefail

OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
MODEL_NAME="${MODEL_NAME:-qwen2.5:0.5b}"
FASTAPI_HOST="${FASTAPI_HOST:-0.0.0.0}"
FASTAPI_PORT="${FASTAPI_PORT:-8000}"

echo "[start.sh] launching ollama serve on ${OLLAMA_HOST}"
ollama serve &
OLLAMA_PID=$!

cleanup() {
    echo "[start.sh] stopping ollama (pid=${OLLAMA_PID})"
    kill "${OLLAMA_PID}" 2>/dev/null || true
    wait "${OLLAMA_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "[start.sh] waiting for ollama HTTP..."
for i in $(seq 1 120); do
    if curl -sf "${OLLAMA_URL}/api/tags" >/dev/null; then
        echo "[start.sh] ollama is up (after ${i}s)"
        break
    fi
    sleep 1
done

if ! curl -sf "${OLLAMA_URL}/api/tags" >/dev/null; then
    echo "[start.sh] ERROR: ollama did not become ready in time" >&2
    exit 1
fi

echo "[start.sh] self-test: asking '${MODEL_NAME}' a trivial question..."
SELF_TEST=$(curl -sf "${OLLAMA_URL}/api/generate" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"${MODEL_NAME}\",\"prompt\":\"Reply with the single word: ok\",\"stream\":false}" \
    || echo '{"response":"<FAILED>"}')
echo "[start.sh] self-test response: ${SELF_TEST}"

echo "[start.sh] launching FastAPI on ${FASTAPI_HOST}:${FASTAPI_PORT}"
cd /app
exec python3 -m uvicorn main:app --host "${FASTAPI_HOST}" --port "${FASTAPI_PORT}"
