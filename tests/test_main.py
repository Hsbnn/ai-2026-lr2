"""Простые тесты для FastAPI-обёртки над Ollama."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class GenerateEndpointTests(unittest.TestCase):
    """Небольшие тесты endpoint `POST /generate`."""

    @classmethod
    def setUpClass(cls) -> None:
        """Создать HTTP-клиент для тестов FastAPI."""

        cls.client = TestClient(main.app)

    def test_generate_returns_model_response(self) -> None:
        """Проверить, что endpoint возвращает ответ Ollama."""

        async def fake_call_ollama(payload: dict) -> dict:
            self.assertEqual(payload["model"], main.MODEL_NAME)
            self.assertEqual(payload["prompt"], "Say hello in one word.")
            self.assertEqual(payload["stream"], False)
            return {"model": main.MODEL_NAME, "response": "Hello!"}

        with patch("main.call_ollama", new=fake_call_ollama):
            response = self.client.post(
                "/generate",
                json={"prompt": "Say hello in one word."},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"model": main.MODEL_NAME, "response": "Hello!"},
        )

    def test_generate_forwards_system_and_custom_model(self) -> None:
        """Проверить передачу `system` и явного имени модели."""

        async def fake_call_ollama(payload: dict) -> dict:
            self.assertEqual(payload["model"], "qwen2.5:0.5b")
            self.assertEqual(payload["system"], "You are a spam classifier.")
            self.assertEqual(payload["prompt"], "Message: Buy now\nVerdict:")
            return {"model": "qwen2.5:0.5b", "response": "SPAM"}

        with patch("main.call_ollama", new=fake_call_ollama):
            response = self.client.post(
                "/generate",
                json={
                    "model": "qwen2.5:0.5b",
                    "system": "You are a spam classifier.",
                    "prompt": "Message: Buy now\nVerdict:",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"model": "qwen2.5:0.5b", "response": "SPAM"},
        )


if __name__ == "__main__":
    unittest.main()
