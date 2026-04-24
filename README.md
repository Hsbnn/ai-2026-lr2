# Проверка спама через LLM

В проекте собран простой контейнер с `Ollama` и `FastAPI`.
Модель, которая используется для запросов, это `qwen2.5:0.5b`.

Снаружи открыты два порта:

- `8000` для FastAPI
- `11434` для Ollama

## Что есть в проекте

- `Dockerfile`
- `start.sh`
- `app/main.py`
- `app/requirements.txt`
- `client/test_curl.sh`
- `client/test_client.py`
- `tests/test_main.py`

## Если Docker ещё не установлен

```bash
brew install colima docker gh
colima start --cpu 4 --memory 6
docker version
```

## Сборка

```bash
cd /Users/evarnak/Desktop/ai_2026/lr2
docker build -t spam-llm:latest .
```

Первая сборка идёт дольше, потому что образ скачивает модель.

## Запуск

```bash
docker run -d --name spam-llm -p 8000:8000 -p 11434:11434 spam-llm:latest
```

## Проверка

Готовые скрипты:

```bash
bash client/test_curl.sh
python3 client/test_client.py
```

Тесты:

```bash
docker run --rm \
  -v "/Users/evarnak/Desktop/ai_2026/lr2/app:/app" \
  -v "/Users/evarnak/Desktop/ai_2026/lr2/tests:/app/tests" \
  --entrypoint python3 spam-llm:latest \
  -m unittest discover -s /app/tests -v
```

Можно проверить и вручную.

Прямой запрос в Ollama:

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:0.5b","prompt":"Reply with: pong","stream":false}'
```

Запрос через FastAPI:

```bash
curl http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Say hello in one word."}'
```

Пример по теме спама:

```bash
curl http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"system":"You are a spam classifier. Answer with SPAM or HAM and one short reason.","prompt":"Message: CONGRATULATIONS!!! You won a $1000 gift card. Click http://bit.ly/xx now.\nVerdict:"}'
```

## Что сделано

- контейнер сделан на `ubuntu:22.04`
- внутри есть `python3`
- внутри установлен `Ollama`
- модель `qwen2.5:0.5b` загружается в образ
- есть быстрый тест обращения к `Ollama`
- внутри работает `FastAPI`
- у сервиса один endpoint `POST /generate`
- порт FastAPI проброшен наружу
- порт Ollama тоже проброшен наружу
- есть внешний тест через `curl`
- есть внешний тест через Python
- есть простые unit-тесты
- у функций есть docstring
