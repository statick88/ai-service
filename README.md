# AI Service

This repository provides the Proyecto Integrador recommendation-service baseline: a FastAPI container with only `GET /health`. It returns exactly `{"status":"ok"}`. Recommendations, models, datasets, BI calculations, and NestJS integration are not part of this baseline.

## Quick start from a fork

1. Fork this repository in GitHub, then clone **your fork**.
2. Add the shared repository as `upstream`, create a worktree and branch, and enter it:

   ```bash
   git clone https://github.com/<your-account>/ai-service.git
   cd ai-service
   git remote add upstream https://github.com/statick88/ai-service.git
   git fetch upstream
   git worktree add ../ai-service-feature -b feature/my-change upstream/main
   cd ../ai-service-feature
   export COMPOSE_DISABLE_ENV_FILE=1
   docker compose up -d --build
   ```

   Replace `<your-account>` with your GitHub account. The literal `docker compose up -d --build` command starts the development runtime; no host Python or Node installation is needed.

3. Confirm readiness and the health contract:

   ```bash
   docker compose ps ai-service
   docker compose logs --no-color --tail 80 ai-service
   curl --fail http://127.0.0.1:8000/health
   ```

   The response body is exactly `{"status":"ok"}`.

## Development runtime

The default `ai-service` target is for local development. It bind-mounts only `./app` read-only and runs Uvicorn reload, so source edits reload the service without rebuilding. Dependencies are baked into the image: after changing dependency manifests, rebuild with `docker compose up -d --build`.

The production-style `runtime` Docker target remains immutable and runs Uvicorn without reload. The `ai-check` container has no host mounts and runs the complete baseline checks in its own image.

### Concurrent worktrees

Each worktree needs a unique Compose project name and host port. Keep `COMPOSE_DISABLE_ENV_FILE=1` exported, then use, for example:

```bash
AI_SERVICE_PORT=18001 docker compose -p ai-feature-one up -d --build
curl --fail http://127.0.0.1:18001/health
AI_SERVICE_PORT=18001 docker compose -p ai-feature-one down --remove-orphans
```

The service is always published to loopback only. Stop only the project you started; do not run global Docker cleanup.

## Verification

Run the development Compose contract check (it uses Python's standard library and the public `docker compose config --format json` output):

```bash
COMPOSE_DISABLE_ENV_FILE=1 python3 scripts/test_compose_contract.py
```

Run the complete lint, type, and test suite in its immutable check container:

```bash
COMPOSE_DISABLE_ENV_FILE=1 docker compose -p ai-check-local run --build --rm --no-deps ai-check
```

The check runs Ruff, strict mypy, and pytest. It verifies this baseline; it is not a guarantee against every regression in functionality that does not exist yet.

## Pull requests and CI

Open a pull request from a branch in your fork to the upstream `main` branch and link the relevant issue. For a private upstream repository, your GitHub account needs fork and pull-request access from a maintainer.

After this workflow is published, GitHub Actions runs on pull requests, `main`, and manual dispatch. It validates Compose configuration and the development contract, runs the container checks, boots the runtime with a bounded wait, verifies the exact health response, prints bounded logs on failure, and stops only its own Compose project. Required merge checks remain a separate repository-administrator setting. As the sole maintainer, you do not need to require another reviewer before merging.

Project tracking: <https://github.com/users/statick88/projects/9>.
