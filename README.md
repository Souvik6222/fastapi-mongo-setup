# fastapi-mongo-setup 🚀

[![PyPI version](https://badge.fury.io/py/fastapi-mongo-setup.svg)](https://badge.fury.io/py/fastapi-mongo-setup)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-mongo-setup.svg)](https://pypi.python.org/pypi/fastapi-mongo-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Stop writing MongoDB boilerplate for FastAPI!**
`fastapi-mongo-setup` is a powerful CLI tool that scaffolds production-ready FastAPI + MongoDB projects — with optional **JWT auth**, **Docker**, **tests**, a **resource generator**, and **auto-start support**.

---

## ⚡ Installation

```bash
pip install fastapi-mongo-setup
```

## 🛠️ Usage

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
```bash
mongo-setup                # Base setup (DB + CRUD)
mongo-setup --auth         # + JWT Authentication
mongo-setup --docker       # + Docker containerization
mongo-setup --test         # + Pytest tests & Ruff linter
mongo-setup --all          # Everything included
```

### 🧩 Resource Generator (NEW!)
Generate new API modules on the fly — no more copy-pasting boilerplate:
```bash
mongo-setup resource products
mongo-setup resource blog_posts
mongo-setup resource orders
```

Each generates a complete `src/<name>/` module with:
- `router.py` — Full CRUD endpoints (POST, GET, GET by ID, PUT, DELETE)
- `schemas.py` — Pydantic Create, Update, and Response models
- `service.py` — MongoDB CRUD operations with serialization

---

## 📁 Generated Project Structure

```text
your-project/
├── .env                    # Environment variables (auto-populated)
├── requirements.txt        # All dependencies
├── main.py                 # FastAPI entry point with MongoDB lifespan
├── Dockerfile              # 🐳 (with --docker)
├── docker-compose.yml      # 🐳 (with --docker)
├── .dockerignore           # 🐳 (with --docker)
├── pytest.ini              # 🧪 (with --test)
├── .ruff.toml              # 🧹 (with --test)
├── tests/                  # 🧪 (with --test)
│   ├── conftest.py         # Async test client setup
│   ├── test_tasks.py       # Task endpoint tests
│   └── test_auth.py        # Auth endpoint tests (with --auth)
└── src/
    ├── config.py           # Pydantic Settings configuration
    ├── utils/
    │   ├── db.py           # Async Motor connection manager
    │   └── helpers.py      # ObjectId serialization helpers
    ├── tasks/              # Default CRUD module
    │   ├── router.py
    │   ├── schemas.py
    │   └── service.py
    ├── auth/               # 🔐 (with --auth)
    │   ├── router.py
    │   ├── schemas.py
    │   ├── service.py
    │   ├── dependencies.py
    │   └── utils.py
    └── <your_resource>/    # 🧩 (with resource command)
        ├── router.py       # Full CRUD (POST, GET, GET/:id, PUT, DELETE)
        ├── schemas.py      # Create, Update, Response models
        └── service.py      # MongoDB operations
```

---

## 🚀 Quick Start

### With Docker 🐳
```bash
mongo-setup --all
docker-compose up --build
```

### Without Docker
```bash
mongo-setup --all
pip install -r requirements.txt
python main.py
```

### Add a New Resource
```bash
mongo-setup resource products
```
Then add to your `main.py`:
```python
from src.products.router import router as products_router
app.include_router(products_router)
```

Open `http://localhost:8000/docs` to see your Swagger UI!

---

## 🔐 Auth Endpoints (with `--auth`)

| Method | Endpoint          | Description                    | Auth Required |
|--------|-------------------|--------------------------------|---------------|
| POST   | `/auth/register`  | Create a new user account      | ❌            |
| POST   | `/auth/login`     | Get a JWT access token         | ❌            |
| GET    | `/auth/me`        | Get current user's profile     | ✅ Bearer     |

## 🧩 Resource Generator Endpoints

Each `mongo-setup resource <name>` generates:

| Method | Endpoint           | Description       |
|--------|--------------------|-------------------|
| POST   | `/<name>/`         | Create item       |
| GET    | `/<name>/`         | List all items    |
| GET    | `/<name>/{id}`     | Get by ID         |
| PUT    | `/<name>/{id}`     | Update item       |
| DELETE | `/<name>/{id}`     | Delete item       |

## 🧪 Testing (with `--test`)

```bash
pytest                 # Run all tests
ruff check .           # Lint code
ruff format .          # Auto-format code
```

## 🐳 Docker (with `--docker`)

| File                 | Purpose                                           |
|----------------------|---------------------------------------------------|
| `Dockerfile`         | Python 3.11-slim image with your FastAPI app       |
| `docker-compose.yml` | Orchestrates FastAPI + MongoDB 7 containers        |
| `.dockerignore`      | Keeps the Docker image clean and small             |

---

## 🤝 Contributing
Found a bug or want to request a feature? Feel free to [open an issue](https://github.com/Souvik6222/fastapi-mongo-setup/issues) or submit a pull request!
