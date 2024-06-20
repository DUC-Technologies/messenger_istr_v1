FROM python:3.12-slim

ENV DATABASE_URL='postgresql://{postgres}:{admin}@{localhost}:{5432}/{postgres}'\
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'\
  POETRY_VERSION=1.7.1

RUN apt-get update && \
    apt-get install -y curl&& \
    apt-get clean

# Установка Poetry через curl
RUN curl -sSL https://install.python-poetry.org | python3 -

# Копирование только файлов с зависимостями для кэширования в слое Docker
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Инициализация проекта:
RUN poetry install --no-interaction --no-ansi

# Создание папок и файлов для проекта:
COPY . /code



EXPOSE 81
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "81"]