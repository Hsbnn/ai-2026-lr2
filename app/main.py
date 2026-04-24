"""FastAPI-обёртка над Ollama для простого PoC по распознаванию спама.

В контейнере одновременно работают два процесса:
1. ``ollama serve`` с моделью ``qwen2.5:0.5b``;
2. FastAPI-сервис, который наружу предоставляет один endpoint
   ``POST /generate`` и просто пересылает запросы в Ollama.

Идея PoC: внешний клиент отправляет prompt на тему спама в FastAPI,
а FastAPI передаёт его в локальный Ollama и возвращает ответ модели.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL_NAME: str = os.getenv("MODEL_NAME", "qwen2.5:0.5b")
REQUEST_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "120"))

app = FastAPI(
    title="Spam Detection LLM Service",
    description="Простая FastAPI-обёртка над Ollama с Qwen2.5:0.5B.",
    version="1.0.0",
)


class GenerateRequest(BaseModel):
    """Тело запроса для пересылки prompt в Ollama.

    Attributes:
        prompt: Пользовательский prompt для модели.
        system: Необязательный system prompt.
        model: Имя модели Ollama; по умолчанию используется
            ``qwen2.5:0.5b``.
    """

    prompt: str = Field(..., min_length=1, description="Текст запроса к LLM")
    system: Optional[str] = Field(default=None, description="System prompt")
    model: Optional[str] = Field(default=None, description="Имя модели Ollama")


class GenerateResponse(BaseModel):
    """Ответ сервиса на запрос ``/generate``.

    Attributes:
        model: Имя модели, обработавшей запрос.
        response: Текст ответа модели.
    """

    model: str
    response: str


async def call_ollama(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Отправить JSON-запрос в Ollama и вернуть JSON-ответ.

    Args:
        payload: Тело запроса для Ollama ``/api/generate``.

    Returns:
        JSON-ответ Ollama в виде словаря.

    Raises:
        HTTPException: При ошибках сети или неуспешном статусе ответа.
    """

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned {resp.status_code}: {resp.text[:500]}",
        )

    return resp.json()


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    """Переслать запрос в Ollama и вернуть ответ модели.

    Это основной и единственный endpoint FastAPI-сервиса, который
    оборачивает Ollama, как требуется в задании.

    Args:
        req: Тело запроса :class:`GenerateRequest`.

    Returns:
        :class:`GenerateResponse` с именем модели и её ответом.
    """

    model = req.model or MODEL_NAME
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": req.prompt,
        "stream": False,
    }
    if req.system:
        payload["system"] = req.system

    data = await call_ollama(payload)
    return GenerateResponse(
        model=data.get("model", model),
        response=data.get("response", ""),
    )
