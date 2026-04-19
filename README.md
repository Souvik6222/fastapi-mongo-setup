```
███████╗ █████╗ ███████╗████████╗      ███╗   ███╗ ██████╗ ███╗   ██╗ ██████╗  ██████╗ 
██╔════╝██╔══██╗██╔════╝╚══██╔══╝      ████╗ ████║██╔═══██╗████╗  ██║██╔════╝ ██╔═══██╗
█████╗  ███████║███████╗   ██║   █████╗██╔████╔██║██║   ██║██╔██╗ ██║██║  ███╗██║   ██║
██╔══╝  ██╔══██║╚════██║   ██║   ╚════╝██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║██║   ██║
██║     ██║  ██║███████║   ██║         ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║╚██████╔╝╚██████╔╝
╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝         ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝
```

<div align="center">

Stop writing MongoDB boilerplate for FastAPI.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248?style=flat&logo=mongodb)](https://motor.readthedocs.io)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://pypi.python.org/pypi/fastapi-mongo-setup)
[![PyPI](https://img.shields.io/pypi/v/fastapi-mongo-setup?color=orange&label=PyPI&logo=pypi&logoColor=white)](https://badge.fury.io/py/fastapi-mongo-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## The Problem

Every new FastAPI + MongoDB project starts the same way — copy-pasting the same `motor` connection setup, the same Pydantic schemas, the same CRUD boilerplate, the same JWT auth scaffold. It's tedious, error-prone, and a waste of time.

`fastapi-mongo-setup` is a CLI that eliminates all of it. One command gives you a clean, production-ready project structure with async MongoDB, optional JWT auth, Docker, tests, and a resource generator — so you can skip straight to building.

---

## Installation

```bash
pip install fastapi-mongo-setup
```

---

## Usage

### Interactive Mode (Recommended)

```bash
mongo-setup
```

```
Welcome to fastapi-mongo-setup!
Include JWT Authentication? (y/N): y
Include Docker setup? (y/N): y
Include Test scaffolding? (y/N): y
```

### Flag Mode

| Command | What you get |
|---|---|
| `mongo-setup` | Base setup — DB connection + CRUD |
| `mongo-setup --auth` | + JWT Authentication |
| `mongo-setup --docker` | + Docker containerization |
| `mongo-setup --test` | + Pytest tests & Ruff linter |
| `mongo-setup --all` | Everything — full production stack |

---

## Resource Generator

Generate complete API modules on the fly — no copy-pasting:

```bash
mongo-setup resource products
mongo-setup resource blog_posts
mongo-setup resource orders
```

Each command creates a full `src/<name>/` module with `router.py`, `schemas.py`, and `service.py`. Then register it in `main.py`:

```python
from src.products.router import router as products_router
app.include_router(products_router)
```

---

## Generated Project Structure

```
your-project/
├── .env
├── requirements.txt
├── main.py                 # FastAPI entry point with MongoDB lifespan
├── Dockerfile              # (--docker)
├── docker-compose.yml      # (--docker)
├── pytest.ini              # (--test)
├── .ruff.toml              # (--test)
├── tests/                  # (--test)
│   ├── conftest.py
│   ├── test_tasks.py
│   └── test_auth.py        # (--auth)
└── src/
    ├── config.py
    ├── utils/
    │   ├── db.py           # Async Motor connection manager
    │   └── helpers.py      # ObjectId serialization helpers
    ├── tasks/              # Default CRUD module
    ├── auth/               # (--auth)
    │   ├── router.py
    │   ├── schemas.py
    │   ├── service.py
    │   ├── dependencies.py
    │   └── utils.py
    └── <your_resource>/    # (resource generator)
        ├── router.py
        ├── schemas.py
        └── service.py
```

---

## Quick Start

**With Docker**

```bash
mongo-setup --all
docker-compose up --build
```

**Without Docker**

```bash
mongo-setup --all
pip install -r requirements.txt
python main.py
```

Open `http://localhost:8000/docs` — your Swagger UI is ready.

---

## Auth Endpoints (`--auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Create a new user account | No |
| `POST` | `/auth/login` | Get a JWT access token | No |
| `GET` | `/auth/me` | Get current user profile | Yes (Bearer) |

---

## Resource Endpoints (per generated resource)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/<name>/` | Create item |
| `GET` | `/<name>/` | List all items |
| `GET` | `/<name>/{id}` | Get by ID |
| `PUT` | `/<name>/{id}` | Update item |
| `DELETE` | `/<name>/{id}` | Delete item |

---

## Testing (`--test`)

```bash
pytest          # Run all tests
ruff check .    # Lint
ruff format .   # Auto-format
```

---

## Docker (`--docker`)

| File | Purpose |
|---|---|
| `Dockerfile` | Python 3.11-slim image with your FastAPI app |
| `docker-compose.yml` | Orchestrates FastAPI + MongoDB 7 containers |
| `.dockerignore` | Keeps the image lean and clean |

---

## Contributing

Found a bug or want a new feature? [Open an issue](https://github.com/Souvik6222/fastapi-mongo-setup/issues) or submit a PR — contributions are welcome.