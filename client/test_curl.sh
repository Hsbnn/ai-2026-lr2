#!/usr/bin/env bash

set -e

FASTAPI="http://localhost:8000"
OLLAMA="http://localhost:11434"

echo "--- POST ${OLLAMA}/api/generate (direct Ollama) ---"
curl -sS "${OLLAMA}/api/generate" \
    -H "Content-Type: application/json" \
    -d '{"model":"qwen2.5:0.5b","prompt":"Reply with: pong","stream":false}'
echo

echo "--- POST ${FASTAPI}/generate ---"
curl -sS "${FASTAPI}/generate" \
    -H "Content-Type: application/json" \
    -d '{"prompt":"Say hello in one word."}'
echo

echo "--- POST ${FASTAPI}/generate (spam PoC) ---"
curl -sS "${FASTAPI}/generate" \
    -H "Content-Type: application/json" \
    -d '{"system":"You are a spam classifier. Answer with SPAM or HAM and one short reason.","prompt":"Message: CONGRATULATIONS!!! You won a $1000 gift card. Click http://bit.ly/xx now.\nVerdict:"}'
echo
