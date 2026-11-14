# AI Service

Minimal FastAPI baseline for the Proyecto Integrador recommendation service. It exposes
only a health endpoint; no recommendation or machine-learning behavior is included.

## Requirements

- Docker Engine 29.9.3 or compatible
- Docker Compose 5.7.0 or compatible

## Run

Start the development runtime with Docker Compose:

```bash
COMPOSE_DISABLE_ENV_FILE=1 docker compose up --build ai-service
```

The service health check is available at `GET /health` and responds with:

```json
{"status":"ok"}
```

The runtime publishes port 8000 on loopback only, at `http://127.0.0.1:8000`.

## Verify

Run the same checks used in continuous integration in a clean container:

```bash
COMPOSE_DISABLE_ENV_FILE=1 docker compose run --build --rm --no-deps ai-check
```

The `ai-check` service installs the pinned `requirements-dev.txt` environment and
runs Ruff, mypy, and pytest. No host Python dependencies are used.
The runtime uses `requirements.txt`, a complete freeze of its direct and transitive
dependencies, and checks dependency consistency during the image build.
The runtime pins match the corresponding entries in `requirements-dev.txt`.

## Continuous integration

GitHub Actions runs the Docker Compose verification for every pull request, pushes
to `main`, and manual dispatches after `.github/workflows/ci.yml` is published.
Blocking merges still requires repository administrators to configure the CI status
check as a required branch-protection rule separately.
