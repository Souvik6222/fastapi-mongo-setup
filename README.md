# fastapi-mongo-setup 🚀

[![PyPI version](https://badge.fury.io/py/fastapi-mongo-setup.svg)](https://badge.fury.io/py/fastapi-mongo-setup)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-mongo-setup.svg)](https://pypi.python.org/pypi/fastapi-mongo-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Stop writing MongoDB boilerplate for FastAPI!**
`fastapi-mongo-setup` is a powerful Python CLI tool that instantly scaffolds a professional, industry-standard FastAPI + MongoDB project — including optional **JWT authentication** and **Docker containerization**.

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
```

### Flag Mode
Or use command-line flags directly:
```bash
mongo-setup                # Base setup (DB + CRUD)
mongo-setup --auth         # + JWT Authentication
mongo-setup --docker       # + Docker containerization
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
This starts both your FastAPI app **and** a MongoDB instance automatically. No local MongoDB installation needed!

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

## 🐳 Docker Setup (with `--docker`)

| File                 | Purpose                                           |
|----------------------|---------------------------------------------------|
| `Dockerfile`         | Python 3.11-slim image with your FastAPI app       |
| `docker-compose.yml` | Orchestrates FastAPI + MongoDB 7 containers        |
| `.dockerignore`      | Excludes unnecessary files from the Docker build   |

---

## 🏗 Why this exists?

Setting up `Motor` (async MongoDB driver) with FastAPI typically requires repetitive boilerplate: connection managers, lifespans, ObjectId serialization, JWT auth plumbing, and Docker configs. This tool does all of that for you in **one command**, providing a clean, modular architecture designed for scaling.

## 🤝 Contributing
Found a bug or want to request a feature? Feel free to [open an issue](https://github.com/Souvik6222/fastapi-mongo-setup/issues) or submit a pull request!
