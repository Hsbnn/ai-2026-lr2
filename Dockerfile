FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OLLAMA_HOST=0.0.0.0:11434 \
    OLLAMA_MODELS=/root/.ollama/models

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        ca-certificates \
        procps \
        zstd \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

RUN set -eux; \
    ollama serve & \
    OLLAMA_PID=$!; \
    for i in $(seq 1 60); do \
        if curl -sf http://127.0.0.1:11434/api/tags >/dev/null; then break; fi; \
        sleep 1; \
    done; \
    ollama pull qwen2.5:0.5b; \
    kill "$OLLAMA_PID"; \
    wait "$OLLAMA_PID" 2>/dev/null || true

COPY app /app
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8000 11434

ENTRYPOINT ["/start.sh"]
