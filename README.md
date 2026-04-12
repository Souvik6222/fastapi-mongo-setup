# fastapi-mongo-setup 🚀

[![PyPI version](https://badge.fury.io/py/fastapi-mongo-setup.svg)](https://badge.fury.io/py/fastapi-mongo-setup)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-mongo-setup.svg)](https://pypi.python.org/pypi/fastapi-mongo-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Stop writing MongoDB boilerplate for FastAPI!** 
`fastapi-mongo-setup` is a fast, lightweight Python CLI tool that instantly scaffolds a professional, industry-standard FastAPI + MongoDB project structure. It generates async DB connections, Pydantic settings, and a fully functional CRUD router in one command.

---

## ⚡ Installation

Install globally or within your virtual environment:

```bash
pip install fastapi-mongo-setup
```

## 🛠️ Usage

Navigate to the root of your empty (or existing) FastAPI project and run:

```bash
mongo-setup
```

### What does this command do?
Instantly, it generates the following modular architecture:

```text
fastapi-project/
├── .env                   # Auto-populated with MONGODB_URL and DATABASE_NAME
├── requirements.txt       # Dependencies (fastapi, motor, pydantic-settings, etc)
├── main.py                # FastAPI entry point with MongoDB Lifespan logic
└── src/
    ├── config.py          # Configuration loader using Pydantic Settings
    ├── utils/             # Database core
    │   ├── db.py          # Asynchronous Motor connection manager
    │   └── helpers.py     # MongoDB ObjectId Serialization helpers
    └── tasks/             # Complete pre-built API module
        ├── router.py      # GET/POST/DELETE endpoints
        ├── schemas.py     # Pydantic validation models
        └── service.py     # Database CRUD logic
```

## 🚀 Running Your Generated Project

Once the files are created, just install the dependencies and start the built-in demo server!

```bash
# 1. Install required packages
pip install -r requirements.txt

# 2. Run the server
python main.py
```

Go to `http://localhost:8000/docs` to see your automatically generated Swagger UI with a fully functional `Tasks` API connected to your MongoDB!

---

## 🏗 Why this exists?

Setting up `Motor` (the async MongoDB driver) with FastAPI usually requires copy-pasting code to handle connections, lifespans, and fixing `ObjectId` serialization errors. This minimalist tool does all of that for you, providing a clean abstraction layer and a modular structure designed for scaling.

## 🤝 Contributing
Found a bug or want to request a feature? Feel free to open an issue or submit a pull request!
