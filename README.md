# Ping Me

MVP backend for configurable forms, grouped submissions, answers, scheduled reminders,
and realtime `reminder.due` delivery.

## Stack

- Python 3.12, FastAPI, Socket.IO
- SQLAlchemy async, PostgreSQL 15, Alembic
- RabbitMQ scheduler/worker delivery
- Poetry, pytest, Ruff, Docker Compose

## Docker MVP Start

Create the environment file once:

```bash
cp .env.example .env
```

For a shared or production-like environment, replace `SECRET_KEY` and database
credentials before starting. Then build and start the complete stack:

```bash
docker compose up --build -d
docker compose ps
```

Compose waits for PostgreSQL, applies `alembic upgrade head` in the one-shot
`migrate` service, and only then starts the API, reminder scheduler, and worker.
The container services override the localhost database and RabbitMQ addresses from
`.env` with Docker network addresses.

Check the running service:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

`/health/live` only confirms that the process is serving requests. `/health/ready`
returns `200` only when PostgreSQL is on the current Alembic head and RabbitMQ is
reachable; otherwise it returns `503`.

Useful URLs:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- RabbitMQ management: http://localhost:15673 (`guest` / `guest` locally)

Run migrations again explicitly after a branch change when needed:

```bash
docker compose run --rm migrate
```

Stop the stack without deleting database data:

```bash
docker compose down
```

## Test Frontend

With the Docker stack running, serve the static test frontend from the repository
root:

```bash
poetry run python -m http.server 5173 --directory test_frontend
```

Open http://localhost:5173 and follow the numbered flow: health, register and email
confirmation (or login), form creation, reminder creation, answer submission, history,
and realtime delivery. When SMTP is not configured, verification/reset codes are
written to the API container log:

```bash
docker compose logs api
```

The frontend connects to `http://localhost:8000`, sends bearer tokens to REST, passes
the access token in Socket.IO auth, and includes the refresh cookie in auth requests.

## Local Poetry Start

Install dependencies and start PostgreSQL/RabbitMQ from Compose:

```bash
poetry install
cp .env.example .env
docker compose up -d db rabbitmq
```

The application reads process environment variables directly. Export `.env` into the
current shell before running migrations or the server:

```bash
set -a
source .env
set +a
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

The `.env.example` localhost ports match Compose: PostgreSQL `5436`, RabbitMQ `5673`,
and the API `8000`. By default the API runs its reminder scheduler in-process. To use
the separate local processes instead, set `REMINDER_SCHEDULER_ENABLED=false`, then run:

```bash
poetry run python -m app.services.reminder_scheduler
poetry run python -m app.services.reminder_worker
```

## Tests and Quality

The suite requires the isolated PostgreSQL service. A run where the suite is skipped
because `test_db` is unavailable is not a successful check.

```bash
docker compose up -d test_db
docker compose ps test_db
poetry run pytest -q
poetry run ruff check .
```

The equivalent container test run is:

```bash
docker compose --profile testing run --build --rm test_runner
```

The test database URL is
`postgresql+asyncpg://test_user:test_password@localhost:5435/test_db`. The test fixture
refuses to run against a database not named `test_db`, resets its schema, and applies
all migrations before tests execute.

## API Contract

The frontend-facing contract is in `docs/API_CONTRACT.md`; generated OpenAPI is in
`docs/openapi.json`. After an API schema change, regenerate it with:

```bash
poetry run python scripts/export_openapi.py
```

## Production Notes

- Set `ENVIRONMENT=production`, a strong `SECRET_KEY`, explicit `CORS_ORIGINS`, and
  `COOKIE_SECURE=true`.
- Run migrations as a separate deploy job before API/scheduler/worker rollout.
- Run exactly one reminder scheduler and one or more reminder workers.
- Disable the API's in-process scheduler with `REMINDER_SCHEDULER_ENABLED=false` when a
  separate scheduler is deployed.
- Configure SMTP and `PUSH_WEBHOOK_URL` for external notification delivery.
- Request logs include `x-request-id`; keep `SQLALCHEMY_ECHO=false` outside debugging.
