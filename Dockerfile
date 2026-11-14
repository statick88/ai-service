FROM python:3.12.16-slim-bookworm AS deps

WORKDIR /app

COPY requirements-dev.txt ./
RUN python -m pip install --no-cache-dir -r requirements-dev.txt


FROM deps AS check

COPY pyproject.toml ./
COPY app ./app
COPY tests ./tests

CMD ["/bin/sh", "-c", "ruff check app tests && mypy app tests && python -m pytest"]


FROM python:3.12.16-slim-bookworm AS runtime

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt && python -m pip check

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
