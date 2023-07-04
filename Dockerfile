FROM python:3.9-slim
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
COPY vnz.py .
CMD ["poetry", "run", "python", "gda_slot_finder/vnz.py"]
