
# Test Final — app

Lightweight FastAPI application implementing users, projects and document management with optional AWS integration.

## Overview

This folder contains the application code for the Test Final project. It uses FastAPI for the HTTP API, SQLAlchemy (or an ORM configured in `database.py`) for persistence, and includes controllers, CRUD modules, models, schemas and routers organized by feature.

Key features
- User management (registration, authentication)
- Project management
- Document uploads/metadata (with AWS support in `services/aws_setup.py` and `crud/aws_crud.py`)

## Repo structure (important files)

- `main.py` — FastAPI app factory / entrypoint
- `config.py` — configuration and constants
- `database.py` — DB session setup
- `dependencies.py` — dependency injection helpers (auth, DB session, etc.)
- `controllers/` — HTTP request handlers
- `crud/` — data access logic
- `models/` — ORM models
- `schemas/` — Pydantic request/response schemas
- `routers/` — API route declarations
- `services/aws_setup.py` — AWS client/setup code

## Requirements

- Python 3.10+ recommended
- See top-level `requirements.txt` or `pyproject.toml` for exact dependencies (FastAPI, uvicorn, SQLAlchemy, pydantic, boto3, pytest, etc.)

## Environment

The app reads configuration from environment variables. A `.env` file is present in this folder (not committed). Typical variables include:

- `DATABASE_URL` — Database connection string
- `SECRET_KEY` — JWT / session secret
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` — (optional) for AWS S3
- Any other variables referenced in `config.py`

Create a `.env` in this folder or export variables into your shell before running.

## Quickstart (local)

1. Install [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer):

```powershell
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:

```powershell
poetry install
```

3. Run the app in development mode:

```powershell
# from repository root
poetry run fastapi dev
```

4. Open the interactive API docs at `http://127.0.0.1:8000/docs`.

## Running tests

Tests live in the `tests/` folder. Run them with pytest from repo root:

```powershell
poetry run pytest
```

Unit tests cover authentication, documents, projects and users (see `tests/test_*.py`). If tests need database fixtures or AWS mocks, inspect `tests/conftest.py`.

```powershell
poetry run ruff check .
```

## API Endpoints (summary)

The app exposes endpoints grouped by router. Example routes (see `routers/*.py` for exact paths):

- Authentication
	- `POST /auth/login` — obtain a token
	- `POST /auth/signup` — create user
- Projects
	- `GET /projects` — list
	- `POST /projects` — create
- Project
	- `GET /project/{id}/info` — detail
	- `PUT /project/{id}/info` — update detail
	- `DELETE /project/{id}` — delete
	- `POST /project/{project_id}/invite?user_id={user_id}` — invite user
- Documents
	- `GET /project/{id}/documents` — list
	- `POST /project/{id}/documents` — create document
	- `GET /document/{id}` — detail
	- `POST /document/{id}` — update detail
	- `DELETE /document/{id}` — delete

Refer to the router files (`routers/user_route.py`, `routers/project_route.py`, `routers/document_route.py`) for the authoritative endpoints, request/response schemas and required authentication.

## AWS / S3 Integration

This project includes optional AWS support:
- `services/aws_setup.py` — initializes S3 client
- `crud/aws_crud.py` — helper methods for upload/download

If you plan to use S3, set the AWS env vars and ensure the IAM credentials have the required S3 permissions.

## Docker & Deployment

- A `Dockerfile` and `docker-compose.yml` are present at the repo root. They can be used to containerize the app and any dependent services (DB).
- There's an `deployments/ecs-task-definition.json` sample for AWS ECS — adjust environment variables, image and IAM role before use.

## Troubleshooting

- If the app fails to connect to the DB, verify `DATABASE_URL` and that migrations (if any) were applied.
- For AWS issues, check credentials and region. Use IAM policies with least privilege.

## License & Contact

See repository root for license information. For questions about this app, open an issue or contact the maintainer listed in the repo.
