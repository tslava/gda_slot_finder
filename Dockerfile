FROM python:3.9-slim

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && pip install poetry && poetry install --only main

COPY ./src ./src

# Environment variables should be provided at runtime via:
# docker run --env-file .env <image>
# or
# docker run -e TELEGRAM_BOT_TOKEN=... <image>

ENTRYPOINT ["poetry", "run", "python", "src/obyw-wniosek.py"]
