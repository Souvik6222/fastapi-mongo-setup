# fastapi-mongo-setup 🚀

[![PyPI version](https://badge.fury.io/py/fastapi-mongo-setup.svg)](https://badge.fury.io/py/fastapi-mongo-setup)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-mongo-setup.svg)](https://pypi.python.org/pypi/fastapi-mongo-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Stop writing MongoDB boilerplate for FastAPI!**
`fastapi-mongo-setup` is a powerful Python CLI tool that instantly scaffolds a professional, industry-standard FastAPI + MongoDB project — including optional **JWT authentication**, **Docker containerization**, and **test scaffolding**.

---

## ⚡ Installation

```bash
pip install fastapi-mongo-setup
```

## 🛠️ Usage

### Interactive Mode (Recommended)
Just run the command and answer the prompts:
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
Use command-line flags directly:
```bash
mongo-setup                # Base setup (DB + CRUD)
mongo-setup --auth         # + JWT Authentication
mongo-setup --docker       # + Docker containerization
mongo-setup --test         # + Pytest tests & Ruff linter
mongo-setup --all          # Everything included
```

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
    ├── config.py           # Pydantic Settings configuration loader
    ├── utils/
    │   ├── db.py           # Async Motor connection manager
    │   └── helpers.py      # ObjectId serialization helpers
    ├── tasks/
    │   ├── router.py       # GET / POST / DELETE endpoints
    │   ├── schemas.py      # Pydantic validation models
    │   └── service.py      # Database CRUD logic
    └── auth/               # 🔐 (with --auth)
        ├── router.py       # /auth/register, /auth/login, /auth/me
        ├── schemas.py      # UserCreate, UserLogin, Token models
        ├── service.py      # Create user, find user by email
        ├── dependencies.py # JWT creation & verification
        └── utils.py        # Password hashing with bcrypt
```

---

## 🚀 Running Your Generated Project

### With Docker (Recommended) 🐳
```bash
docker-compose up --build
```

### Without Docker
```bash
pip install -r requirements.txt
python main.py
```

Open `http://localhost:8000/docs` to see your Swagger UI!

---

## 🔐 Auth Endpoints (with `--auth`)

| Method | Endpoint          | Description                    | Auth Required |
|--------|-------------------|--------------------------------|---------------|
| POST   | `/auth/register`  | Create a new user account      | ❌            |
| POST   | `/auth/login`     | Get a JWT access token         | ❌            |
| GET    | `/auth/me`        | Get current user's profile     | ✅ Bearer     |

## 🧪 Testing (with `--test`)

Run the pre-built test suite:
```bash
pytest
```

The generated tests cover:
- ✅ Root endpoint health check
- ✅ Task CRUD operations (create, list, delete)
- ✅ Auth registration & login flow (with `--auth`)
- ✅ Unauthorized access protection (with `--auth`)

### Linting
```bash
ruff check .       # Check for issues
ruff format .      # Auto-format code
```

## 🐳 Docker Setup (with `--docker`)

| File                 | Purpose                                           |
|----------------------|---------------------------------------------------|
| `Dockerfile`         | Python 3.11-slim image with your FastAPI app       |
| `docker-compose.yml` | Orchestrates FastAPI + MongoDB 7 containers        |
| `.dockerignore`      | Keeps the Docker image clean and small             |

---

## 🏗 Why this exists?

Setting up `Motor` (async MongoDB driver) with FastAPI typically requires repetitive boilerplate: connection managers, lifespans, ObjectId serialization, JWT auth plumbing, Docker configs, and test infrastructure. This tool does all of that for you in **one command**, providing a clean, modular architecture designed for scaling.

## 🤝 Contributing
Found a bug or want to request a feature? Feel free to [open an issue](https://github.com/Souvik6222/fastapi-mongo-setup/issues) or submit a pull request!
