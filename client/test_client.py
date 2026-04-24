"""Внешний клиент для проверки Ollama и FastAPI из хоста.

Скрипт запускается вне контейнера и делает два типа запросов:
1. Напрямую в Ollama по проброшенному порту ``11434``.
2. В FastAPI-обёртку по порту ``8000``.

Через FastAPI отправляется простой prompt на тему спама, чтобы
показать применимость LLM к задаче распознавания спама.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from typing import Any, Dict


FASTAPI_URL = "http://localhost:8000"
OLLAMA_URL = "http://localhost:11434"


def get_json(url: str) -> Dict[str, Any]:
    """Выполнить GET-запрос и вернуть JSON-ответ.

    Args:
        url: Полный URL эндпоинта.

    Returns:
        Распарсенный JSON-ответ.
    """

    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Выполнить POST-запрос с JSON-телом и вернуть JSON-ответ.

    Args:
        url: Полный URL эндпоинта.
        payload: Тело запроса в виде словаря (будет сериализовано в JSON).

    Returns:
        Распарсенный JSON-ответ.
    """

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    """Запустить набор проверок LLM-сервиса и напечатать ответы.

    Returns:
        Код возврата процесса (0 — всё отработало без исключений).
    """

    print("POST direct Ollama /api/generate")
    ollama_resp = post_json(
        f"{OLLAMA_URL}/api/generate",
        {
            "model": "qwen2.5:0.5b",
            "prompt": "Reply with the single word: pong",
            "stream": False,
        },
    )
    print(json.dumps(ollama_resp, ensure_ascii=False, indent=2))

    print("\nPOST FastAPI /generate")
    gen = post_json(
        f"{FASTAPI_URL}/generate",
        {"prompt": "Say hello in one word."},
    )
    print(json.dumps(gen, ensure_ascii=False, indent=2))

    print("\nPOST FastAPI /generate (spam PoC)")
    spam_poc = post_json(
        f"{FASTAPI_URL}/generate",
        {
            "system": (
                "You are a spam classifier. "
                "Answer with SPAM or HAM and one short reason."
            ),
            "prompt": (
                "Message: CONGRATULATIONS!!! You won a $1000 gift card. "
                "Click http://bit.ly/xx now.\nVerdict:"
            ),
        },
    )
    print(json.dumps(spam_poc, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
