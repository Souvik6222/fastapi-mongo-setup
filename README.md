# fastapi-mongo-setup 🚀

[![PyPI version](https://badge.fury.io/py/fastapi-mongo-setup.svg)](https://badge.fury.io/py/fastapi-mongo-setup)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-mongo-setup.svg)](https://pypi.python.org/pypi/fastapi-mongo-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Stop writing MongoDB boilerplate for FastAPI!**
`fastapi-mongo-setup` is a fast, lightweight Python CLI tool that instantly scaffolds a professional, industry-standard FastAPI + MongoDB project structure — including an optional **JWT authentication system**.

---

## ⚡ Installation

```bash
pip install fastapi-mongo-setup
```

## 🛠️ Usage

### Basic Setup (DB + CRUD)
Navigate to your project folder and run:
```bash
mongo-setup
```

### With Authentication 🔐
Add a complete JWT auth system (register, login, protected routes):
```bash
mongo-setup --auth
```

---

## 📁 Generated Project Structure

### Without `--auth`
```text
your-project/
├── .env                   # MONGODB_URL, DATABASE_NAME, PORT
├── requirements.txt       # fastapi, motor, pydantic-settings, etc.
├── main.py                # FastAPI entry point with MongoDB lifespan
└── src/
    ├── config.py          # Pydantic Settings configuration loader
    ├── utils/
    │   ├── db.py          # Async Motor connection manager
    │   └── helpers.py     # ObjectId serialization helpers
    └── tasks/
        ├── router.py      # GET / POST / DELETE endpoints
        ├── schemas.py     # Pydantic validation models
        └── service.py     # Database CRUD logic
```

### With `--auth` (adds these files)
```text
└── src/
    ├── config.py          # Now includes SECRET_KEY, ALGORITHM, etc.
    └── auth/              # 🔐 Complete Auth Module
        ├── router.py      # /auth/register, /auth/login, /auth/me
        ├── schemas.py     # UserCreate, UserLogin, Token models
        ├── service.py     # Create user, find user by email
        ├── dependencies.py # JWT creation & verification, get_current_user
        └── utils.py       # Password hashing with bcrypt
```

Plus auto-updates to:
- **`.env`** → adds `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- **`requirements.txt`** → adds `python-jose`, `passlib`, `bcrypt`
- **`main.py`** → registers the auth router automatically

---

## 🚀 Running Your Generated Project

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python main.py
```

Open `http://localhost:8000/docs` to see your Swagger UI with fully functional **Tasks CRUD** and (if `--auth` was used) **Authentication** endpoints!

---

## 🔐 Auth Endpoints (when using `--auth`)

| Method | Endpoint          | Description                    | Auth Required |
|--------|-------------------|--------------------------------|---------------|
| POST   | `/auth/register`  | Create a new user account      | ❌            |
| POST   | `/auth/login`     | Get a JWT access token         | ❌            |
| GET    | `/auth/me`        | Get current user's profile     | ✅ Bearer     |

---

## 🏗 Why this exists?

Setting up `Motor` (async MongoDB driver) with FastAPI typically requires repetitive boilerplate: connection managers, lifespans, ObjectId serialization, and JWT auth plumbing. This tool does all of that for you in **one command**, providing a clean, modular architecture designed for scaling.

## 🤝 Contributing
Found a bug or want to request a feature? Feel free to [open an issue](https://github.com/Souvik6222/fastapi-mongo-setup/issues) or submit a pull request!
