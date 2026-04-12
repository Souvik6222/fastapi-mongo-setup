# fastapi-mongo-setup

A Python CLI package that automatically creates a MongoDB connection structure for FastAPI projects.

## Installation

```bash
pip install fastapi-mongo-setup
```

## Usage

Navigate to the root of your FastAPI project and run:

```bash
mongo-setup
```

This command will:
- Check if the `src/utils` directory exists (creates it if it doesn't).
- Generate a `src/utils/db.py` file containing an asynchronous `Database` class using `motor`. This includes `connect_to_mongodb` and `close_mongodb_connection` methods.
- Generate a `src/utils/helpers.py` file with a `serialize_doc` function to convert MongoDB `ObjectId` types to plain strings.
- Automatically append `MONGODB_URL` and `DATABASE_NAME` variables to your `.env` file.
