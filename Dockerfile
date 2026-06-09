# Используем официальный образ python
FROM python:3.12-slim

# Копируем бинарник uv из официального образа astral-sh
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Настройки Python и uv
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    DATABASE_URL='postgresql://{postgres}:{admin}@{localhost}:{5432}/{postgres}'

# Устанавливаем системные зависимости, если они нужны (например, для psycopg2 или scylla-driver)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Копируем файлы зависимостей для кэширования слоев Docker
COPY pyproject.toml uv.lock /code/

# Устанавливаем ТОЛЬКО основные зависимости (пропуская dev и dev_auth группы)
# --frozen гарантирует, что uv не будет пытаться обновить lock-файл во время сборки
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Копируем оставшийся код проекта
COPY . /code

EXPOSE 81

# Запуск приложения
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "81"]