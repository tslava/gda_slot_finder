FROM python:3.9-slim

COPY poetry.lock pyproject.toml /src/
WORKDIR /src/
RUN pip install --upgrade pip && pip install poetry && poetry install --no-dev
COPY ./src /src/

ENTRYPOINT ["poetry", "run", "python", "/src/obyw-wniosek.py"]
