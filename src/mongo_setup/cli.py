import os
import pathlib
import argparse


def init():
    parser = argparse.ArgumentParser(
        description="Scaffold a production-ready FastAPI + MongoDB project"
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Include a full JWT authentication module (register, login, protected routes)"
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Include Dockerfile, docker-compose.yml, and .dockerignore"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include all optional features (auth + docker)"
    )
    args = parser.parse_args()

    # --all shortcut enables everything
    if args.all:
        args.auth = True
        args.docker = True

    # =============================================
    # INTERACTIVE MODE: If no flags passed, ask user
    # =============================================
    if not args.auth and not args.docker:
        print("\n" + "=" * 50)
        print("  Welcome to fastapi-mongo-setup!")
        print("  Let's configure your project.")
        print("=" * 50 + "\n")

        auth_answer = input("Include JWT Authentication? (y/N): ").strip().lower()
        args.auth = auth_answer in ("y", "yes")

        docker_answer = input("Include Docker setup? (y/N): ").strip().lower()
        args.docker = docker_answer in ("y", "yes")
        print()

    include_auth = args.auth
    include_docker = args.docker

    print("Initializing full-fledged MongoDB FastAPI project structure...")
    if include_auth:
        print("  [+] JWT Authentication module")
    if include_docker:
        print("  [+] Docker containerization files")

    # Base directories
    src_dir = pathlib.Path("src")
    utils_dir = src_dir / "utils"
    tasks_dir = src_dir / "tasks"

    utils_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir.mkdir(parents=True, exist_ok=True)

    # =============================================
    # 1. src/config.py
    # =============================================
    config_file = src_dir / "config.py"
    if not config_file.exists():
        with open(config_file, "w", encoding="utf-8") as f:
            f.write('from pydantic_settings import BaseSettings\n')
            f.write('\n')
            f.write('class Settings(BaseSettings):\n')
            f.write('    mongodb_url: str = "mongodb://localhost:27017"\n')
            f.write('    database_name: str = "fastapi_db"\n')
            f.write('    port: int = 8000\n')
            if include_auth:
                f.write('    secret_key: str = "your-super-secret-key-change-this"\n')
                f.write('    algorithm: str = "HS256"\n')
                f.write('    access_token_expire_minutes: int = 30\n')
            f.write('\n')
            f.write('    class Config:\n')
            f.write('        env_file = ".env"\n')
            f.write('\n')
            f.write('settings = Settings()\n')
        print(f"Created {config_file}")
    else:
        print(f"{config_file} already exists, skipping.")
        if include_auth:
            print("  NOTE: Please add these fields to your Settings class in config.py:")
            print('    secret_key: str = "your-super-secret-key-change-this"')
            print('    algorithm: str = "HS256"')
            print('    access_token_expire_minutes: int = 30')

    # =============================================
    # 2. src/utils/db.py
    # =============================================
    db_file = utils_dir / "db.py"
    if not db_file.exists():
        with open(db_file, "w", encoding="utf-8") as f:
            f.write('from motor.motor_asyncio import AsyncIOMotorClient\n')
            f.write('from src.config import settings\n')
            f.write('\n')
            f.write('class Database:\n')
            f.write('    client: AsyncIOMotorClient = None\n')
            f.write('    db = None\n')
            f.write('\n')
            f.write('db = Database()\n')
            f.write('\n')
            f.write('async def connect_to_mongodb():\n')
            f.write('    db.client = AsyncIOMotorClient(settings.mongodb_url)\n')
            f.write('    db.db = db.client[settings.database_name]\n')
            f.write("    await db.client.admin.command('ping')\n")
            f.write('    print("Connected to MongoDB!")\n')
            f.write('\n')
            f.write('async def close_mongodb_connection():\n')
            f.write('    if db.client:\n')
            f.write('        db.client.close()\n')
            f.write('        print("Closed MongoDB connection.")\n')
        print(f"Created {db_file}")
    else:
        print(f"{db_file} already exists, skipping.")

    # =============================================
    # 3. src/utils/helpers.py
    # =============================================
    helpers_file = utils_dir / "helpers.py"
    if not helpers_file.exists():
        with open(helpers_file, "w", encoding="utf-8") as f:
            f.write('def serialize_doc(doc):\n')
            f.write('    """Convert MongoDB ObjectId to string"""\n')
            f.write('    if doc and "_id" in doc:\n')
            f.write('        doc["id"] = str(doc["_id"])\n')
            f.write('        del doc["_id"]\n')
            f.write('    return doc\n')
            f.write('\n')
            f.write('def serialize_docs(docs):\n')
            f.write('    return [serialize_doc(doc) for doc in docs]\n')
        print(f"Created {helpers_file}")
    else:
        print(f"{helpers_file} already exists, skipping.")

    # =============================================
    # 4. src/tasks/schemas.py
    # =============================================
    schemas_file = tasks_dir / "schemas.py"
    if not schemas_file.exists():
        with open(schemas_file, "w", encoding="utf-8") as f:
            f.write('from pydantic import BaseModel, Field\n')
            f.write('from typing import Optional\n')
            f.write('\n')
            f.write('class TaskCreate(BaseModel):\n')
            f.write('    title: str = Field(..., example="Buy groceries")\n')
            f.write('    description: Optional[str] = Field(None, example="Milk, Eggs, Bread")\n')
            f.write('    completed: bool = False\n')
            f.write('\n')
            f.write('class TaskResponse(TaskCreate):\n')
            f.write('    id: str\n')
        print(f"Created {schemas_file}")
    else:
        print(f"{schemas_file} already exists, skipping.")

    # =============================================
    # 5. src/tasks/service.py
    # =============================================
    service_file = tasks_dir / "service.py"
    if not service_file.exists():
        with open(service_file, "w", encoding="utf-8") as f:
            f.write('from src.utils.db import db\n')
            f.write('from src.utils.helpers import serialize_doc, serialize_docs\n')
            f.write('from bson import ObjectId\n')
            f.write('\n')
            f.write('class TaskService:\n')
            f.write('    @staticmethod\n')
            f.write('    def get_collection():\n')
            f.write('        return db.db["tasks"]\n')
            f.write('\n')
            f.write('    @staticmethod\n')
            f.write('    async def create_task(task_data: dict) -> dict:\n')
            f.write('        result = await TaskService.get_collection().insert_one(task_data)\n')
            f.write('        created_task = await TaskService.get_collection().find_one({"_id": result.inserted_id})\n')
            f.write('        return serialize_doc(created_task)\n')
            f.write('\n')
            f.write('    @staticmethod\n')
            f.write('    async def get_all_tasks() -> list:\n')
            f.write('        cursor = TaskService.get_collection().find()\n')
            f.write('        tasks = await cursor.to_list(length=100)\n')
            f.write('        return serialize_docs(tasks)\n')
            f.write('\n')
            f.write('    @staticmethod\n')
            f.write('    async def delete_task(task_id: str) -> bool:\n')
            f.write('        result = await TaskService.get_collection().delete_one({"_id": ObjectId(task_id)})\n')
            f.write('        return result.deleted_count > 0\n')
        print(f"Created {service_file}")
    else:
        print(f"{service_file} already exists, skipping.")

    # =============================================
    # 6. src/tasks/router.py
    # =============================================
    router_file = tasks_dir / "router.py"
    if not router_file.exists():
        with open(router_file, "w", encoding="utf-8") as f:
            f.write('from fastapi import APIRouter, HTTPException\n')
            f.write('from typing import List\n')
            f.write('from src.tasks.schemas import TaskCreate, TaskResponse\n')
            f.write('from src.tasks.service import TaskService\n')
            f.write('\n')
            f.write('router = APIRouter(prefix="/tasks", tags=["Tasks"])\n')
            f.write('\n')
            f.write('@router.post("/", response_model=TaskResponse)\n')
            f.write('async def create_task(task: TaskCreate):\n')
            f.write('    created_task = await TaskService.create_task(task.model_dump())\n')
            f.write('    return created_task\n')
            f.write('\n')
            f.write('@router.get("/", response_model=List[TaskResponse])\n')
            f.write('async def get_tasks():\n')
            f.write('    return await TaskService.get_all_tasks()\n')
            f.write('\n')
            f.write('@router.delete("/{task_id}")\n')
            f.write('async def delete_task(task_id: str):\n')
            f.write('    success = await TaskService.delete_task(task_id)\n')
            f.write('    if not success:\n')
            f.write('        raise HTTPException(status_code=404, detail="Task not found")\n')
            f.write('    return {"message": "Task deleted successfully"}\n')
        print(f"Created {router_file}")
    else:
        print(f"{router_file} already exists, skipping.")

    # =============================================
    # 7. main.py (conditionally includes auth router)
    # =============================================
    main_file = pathlib.Path("main.py")
    if not main_file.exists():
        with open(main_file, "w", encoding="utf-8") as f:
            f.write('from fastapi import FastAPI\n')
            f.write('from contextlib import asynccontextmanager\n')
            f.write('import uvicorn\n')
            f.write('from src.config import settings\n')
            f.write('from src.utils.db import connect_to_mongodb, close_mongodb_connection\n')
            f.write('from src.tasks.router import router as tasks_router\n')
            if include_auth:
                f.write('from src.auth.router import router as auth_router\n')
            f.write('\n')
            f.write('@asynccontextmanager\n')
            f.write('async def lifespan(app: FastAPI):\n')
            f.write('    # Startup: Connect to DB\n')
            f.write('    await connect_to_mongodb()\n')
            f.write('    yield\n')
            f.write('    # Shutdown: Close DB\n')
            f.write('    await close_mongodb_connection()\n')
            f.write('\n')
            f.write('app = FastAPI(lifespan=lifespan, title="FastAPI MongoDB App")\n')
            f.write('\n')
            f.write('# Register routers\n')
            f.write('app.include_router(tasks_router)\n')
            if include_auth:
                f.write('app.include_router(auth_router)\n')
            f.write('\n')
            f.write('@app.get("/")\n')
            f.write('async def root():\n')
            f.write('    return {"message": "Welcome to the FastAPI + MongoDB Boilerplate!"}\n')
            f.write('\n')
            f.write('if __name__ == "__main__":\n')
            f.write('    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)\n')
        print(f"Created {main_file}")
    else:
        print(f"{main_file} already exists, skipping.")
        if include_auth:
            print("  NOTE: Please add these lines to your main.py:")
            print('    from src.auth.router import router as auth_router')
            print('    app.include_router(auth_router)')

    # =============================================
    # 8. .env (appends missing variables)
    # =============================================
    env_file = pathlib.Path(".env")
    env_content = ""
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            env_content = f.read()

    with open(env_file, "a", encoding="utf-8") as f:
        if env_content and not env_content.endswith("\n"):
            f.write("\n")
        if "MONGODB_URL" not in env_content:
            if include_docker:
                f.write("MONGODB_URL=mongodb://mongo:27017\n")
            else:
                f.write("MONGODB_URL=mongodb://localhost:27017\n")
        if "DATABASE_NAME" not in env_content:
            f.write("DATABASE_NAME=fastapi_db\n")
        if "PORT" not in env_content:
            f.write("PORT=8000\n")
        if include_auth:
            if "SECRET_KEY" not in env_content:
                f.write("SECRET_KEY=your-super-secret-key-change-this\n")
            if "ALGORITHM" not in env_content:
                f.write("ALGORITHM=HS256\n")
            if "ACCESS_TOKEN_EXPIRE_MINUTES" not in env_content:
                f.write("ACCESS_TOKEN_EXPIRE_MINUTES=30\n")

    print("Updated .env file with environment variables.")

    # =============================================
    # 9. requirements.txt (creates or appends)
    # =============================================
    req_file = pathlib.Path("requirements.txt")
    req_content = ""
    if req_file.exists():
        with open(req_file, "r", encoding="utf-8") as f:
            req_content = f.read()

    base_deps = ["fastapi", "uvicorn", "motor", "python-dotenv", "pydantic", "pydantic-settings"]
    auth_deps = ["python-jose[cryptography]", "passlib[bcrypt]", "bcrypt"]

    deps_to_add = []
    for dep in base_deps:
        if dep not in req_content:
            deps_to_add.append(dep)
    if include_auth:
        for dep in auth_deps:
            if dep not in req_content:
                deps_to_add.append(dep)

    if deps_to_add:
        with open(req_file, "a", encoding="utf-8") as f:
            if req_content and not req_content.endswith("\n"):
                f.write("\n")
            for dep in deps_to_add:
                f.write(dep + "\n")
        print(f"Updated {req_file} with dependencies.")
    else:
        print(f"{req_file} already has all required dependencies.")

    # =============================================
    # AUTH MODULE (only when --auth is passed)
    # =============================================
    if include_auth:
        print("\n--- Setting up JWT Authentication module ---")
        auth_dir = src_dir / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)

        # auth/__init__.py
        auth_init = auth_dir / "__init__.py"
        if not auth_init.exists():
            with open(auth_init, "w", encoding="utf-8") as f:
                f.write("")

        # =============================================
        # A1. src/auth/utils.py (Password Hashing)
        # =============================================
        auth_utils = auth_dir / "utils.py"
        if not auth_utils.exists():
            with open(auth_utils, "w", encoding="utf-8") as f:
                f.write('from passlib.context import CryptContext\n')
                f.write('\n')
                f.write('pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")\n')
                f.write('\n')
                f.write('def hash_password(password: str) -> str:\n')
                f.write('    """Hash a plain-text password using bcrypt."""\n')
                f.write('    return pwd_context.hash(password)\n')
                f.write('\n')
                f.write('def verify_password(plain_password: str, hashed_password: str) -> bool:\n')
                f.write('    """Verify a plain-text password against its hash."""\n')
                f.write('    return pwd_context.verify(plain_password, hashed_password)\n')
            print(f"Created {auth_utils}")
        else:
            print(f"{auth_utils} already exists, skipping.")

        # =============================================
        # A2. src/auth/schemas.py (Pydantic Models)
        # =============================================
        auth_schemas = auth_dir / "schemas.py"
        if not auth_schemas.exists():
            with open(auth_schemas, "w", encoding="utf-8") as f:
                f.write('from pydantic import BaseModel, Field\n')
                f.write('\n')
                f.write('class UserCreate(BaseModel):\n')
                f.write('    name: str = Field(..., example="John Doe")\n')
                f.write('    email: str = Field(..., example="john@example.com")\n')
                f.write('    password: str = Field(..., min_length=6, example="secret123")\n')
                f.write('\n')
                f.write('class UserLogin(BaseModel):\n')
                f.write('    email: str = Field(..., example="john@example.com")\n')
                f.write('    password: str = Field(..., example="secret123")\n')
                f.write('\n')
                f.write('class UserResponse(BaseModel):\n')
                f.write('    id: str\n')
                f.write('    name: str\n')
                f.write('    email: str\n')
                f.write('\n')
                f.write('class Token(BaseModel):\n')
                f.write('    access_token: str\n')
                f.write('    token_type: str = "bearer"\n')
            print(f"Created {auth_schemas}")
        else:
            print(f"{auth_schemas} already exists, skipping.")

        # =============================================
        # A3. src/auth/service.py (DB Logic for Users)
        # =============================================
        auth_service = auth_dir / "service.py"
        if not auth_service.exists():
            with open(auth_service, "w", encoding="utf-8") as f:
                f.write('from src.utils.db import db\n')
                f.write('from src.utils.helpers import serialize_doc\n')
                f.write('from src.auth.utils import hash_password\n')
                f.write('\n')
                f.write('class AuthService:\n')
                f.write('    @staticmethod\n')
                f.write('    def get_collection():\n')
                f.write('        return db.db["users"]\n')
                f.write('\n')
                f.write('    @staticmethod\n')
                f.write('    async def create_user(user_data: dict) -> dict:\n')
                f.write('        """Hash password and insert user into the database."""\n')
                f.write('        user_data["password"] = hash_password(user_data["password"])\n')
                f.write('        result = await AuthService.get_collection().insert_one(user_data)\n')
                f.write('        created_user = await AuthService.get_collection().find_one({"_id": result.inserted_id})\n')
                f.write('        return serialize_doc(created_user)\n')
                f.write('\n')
                f.write('    @staticmethod\n')
                f.write('    async def get_user_by_email(email: str):\n')
                f.write('        """Find a user document by email address."""\n')
                f.write('        user = await AuthService.get_collection().find_one({"email": email})\n')
                f.write('        return user\n')
            print(f"Created {auth_service}")
        else:
            print(f"{auth_service} already exists, skipping.")

        # =============================================
        # A4. src/auth/dependencies.py (JWT Logic)
        # =============================================
        auth_deps_file = auth_dir / "dependencies.py"
        if not auth_deps_file.exists():
            with open(auth_deps_file, "w", encoding="utf-8") as f:
                f.write('from datetime import datetime, timedelta\n')
                f.write('from jose import JWTError, jwt\n')
                f.write('from fastapi import Depends, HTTPException, status\n')
                f.write('from fastapi.security import OAuth2PasswordBearer\n')
                f.write('from src.config import settings\n')
                f.write('from src.auth.service import AuthService\n')
                f.write('from src.utils.helpers import serialize_doc\n')
                f.write('\n')
                f.write('oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")\n')
                f.write('\n')
                f.write('def create_access_token(data: dict) -> str:\n')
                f.write('    """Create a JWT access token with an expiration time."""\n')
                f.write('    to_encode = data.copy()\n')
                f.write('    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)\n')
                f.write('    to_encode.update({"exp": expire})\n')
                f.write('    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)\n')
                f.write('\n')
                f.write('async def get_current_user(token: str = Depends(oauth2_scheme)):\n')
                f.write('    """Decode the JWT token and return the current user from the database."""\n')
                f.write('    credentials_exception = HTTPException(\n')
                f.write('        status_code=status.HTTP_401_UNAUTHORIZED,\n')
                f.write('        detail="Could not validate credentials",\n')
                f.write('        headers={"WWW-Authenticate": "Bearer"},\n')
                f.write('    )\n')
                f.write('    try:\n')
                f.write('        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])\n')
                f.write('        email: str = payload.get("sub")\n')
                f.write('        if email is None:\n')
                f.write('            raise credentials_exception\n')
                f.write('    except JWTError:\n')
                f.write('        raise credentials_exception\n')
                f.write('    user = await AuthService.get_user_by_email(email)\n')
                f.write('    if user is None:\n')
                f.write('        raise credentials_exception\n')
                f.write('    return serialize_doc(user)\n')
            print(f"Created {auth_deps_file}")
        else:
            print(f"{auth_deps_file} already exists, skipping.")

        # =============================================
        # A5. src/auth/router.py (Auth Endpoints)
        # =============================================
        auth_router = auth_dir / "router.py"
        if not auth_router.exists():
            with open(auth_router, "w", encoding="utf-8") as f:
                f.write('from fastapi import APIRouter, HTTPException, Depends\n')
                f.write('from src.auth.schemas import UserCreate, UserLogin, UserResponse, Token\n')
                f.write('from src.auth.service import AuthService\n')
                f.write('from src.auth.dependencies import create_access_token, get_current_user\n')
                f.write('from src.auth.utils import verify_password\n')
                f.write('\n')
                f.write('router = APIRouter(prefix="/auth", tags=["Authentication"])\n')
                f.write('\n')
                f.write('@router.post("/register", response_model=UserResponse)\n')
                f.write('async def register(user: UserCreate):\n')
                f.write('    """Register a new user account."""\n')
                f.write('    existing_user = await AuthService.get_user_by_email(user.email)\n')
                f.write('    if existing_user:\n')
                f.write('        raise HTTPException(status_code=400, detail="Email already registered")\n')
                f.write('    created_user = await AuthService.create_user(user.model_dump())\n')
                f.write('    return created_user\n')
                f.write('\n')
                f.write('@router.post("/login", response_model=Token)\n')
                f.write('async def login(user: UserLogin):\n')
                f.write('    """Authenticate user and return a JWT access token."""\n')
                f.write('    db_user = await AuthService.get_user_by_email(user.email)\n')
                f.write('    if not db_user:\n')
                f.write('        raise HTTPException(status_code=401, detail="Invalid credentials")\n')
                f.write('    if not verify_password(user.password, db_user["password"]):\n')
                f.write('        raise HTTPException(status_code=401, detail="Invalid credentials")\n')
                f.write('    access_token = create_access_token(data={"sub": db_user["email"]})\n')
                f.write('    return {"access_token": access_token, "token_type": "bearer"}\n')
                f.write('\n')
                f.write('@router.get("/me", response_model=UserResponse)\n')
                f.write('async def get_me(current_user: dict = Depends(get_current_user)):\n')
                f.write('    """Get the profile of the currently authenticated user."""\n')
                f.write('    return current_user\n')
            print(f"Created {auth_router}")
        else:
            print(f"{auth_router} already exists, skipping.")

        print("\nJWT Authentication module setup complete!")

    # =============================================
    # DOCKER MODULE (only when --docker is passed)
    # =============================================
    if include_docker:
        print("\n--- Setting up Docker containerization ---")

        # =============================================
        # D1. Dockerfile
        # =============================================
        dockerfile = pathlib.Path("Dockerfile")
        if not dockerfile.exists():
            with open(dockerfile, "w", encoding="utf-8") as f:
                f.write('# ---- Base Python Image ----\n')
                f.write('FROM python:3.11-slim\n')
                f.write('\n')
                f.write('# Set environment variables\n')
                f.write('ENV PYTHONDONTWRITEBYTECODE=1\n')
                f.write('ENV PYTHONUNBUFFERED=1\n')
                f.write('\n')
                f.write('# Set work directory\n')
                f.write('WORKDIR /app\n')
                f.write('\n')
                f.write('# Install dependencies\n')
                f.write('COPY requirements.txt .\n')
                f.write('RUN pip install --no-cache-dir --upgrade pip && \\\n')
                f.write('    pip install --no-cache-dir -r requirements.txt\n')
                f.write('\n')
                f.write('# Copy project files\n')
                f.write('COPY . .\n')
                f.write('\n')
                f.write('# Expose the port\n')
                f.write('EXPOSE 8000\n')
                f.write('\n')
                f.write('# Run the application\n')
                f.write('CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]\n')
            print(f"Created {dockerfile}")
        else:
            print(f"{dockerfile} already exists, skipping.")

        # =============================================
        # D2. docker-compose.yml
        # =============================================
        compose_file = pathlib.Path("docker-compose.yml")
        if not compose_file.exists():
            with open(compose_file, "w", encoding="utf-8") as f:
                f.write('version: "3.8"\n')
                f.write('\n')
                f.write('services:\n')
                f.write('  app:\n')
                f.write('    build: .\n')
                f.write('    container_name: fastapi_app\n')
                f.write('    ports:\n')
                f.write('      - "8000:8000"\n')
                f.write('    depends_on:\n')
                f.write('      - mongo\n')
                f.write('    environment:\n')
                f.write('      - MONGODB_URL=mongodb://mongo:27017\n')
                f.write('      - DATABASE_NAME=fastapi_db\n')
                f.write('    volumes:\n')
                f.write('      - .:/app\n')
                f.write('    restart: always\n')
                f.write('\n')
                f.write('  mongo:\n')
                f.write('    image: mongo:7\n')
                f.write('    container_name: mongodb\n')
                f.write('    ports:\n')
                f.write('      - "27017:27017"\n')
                f.write('    volumes:\n')
                f.write('      - mongo_data:/data/db\n')
                f.write('    restart: always\n')
                f.write('\n')
                f.write('volumes:\n')
                f.write('  mongo_data:\n')
            print(f"Created {compose_file}")
        else:
            print(f"{compose_file} already exists, skipping.")

        # =============================================
        # D3. .dockerignore
        # =============================================
        dockerignore = pathlib.Path(".dockerignore")
        if not dockerignore.exists():
            with open(dockerignore, "w", encoding="utf-8") as f:
                f.write('__pycache__\n')
                f.write('*.pyc\n')
                f.write('*.pyo\n')
                f.write('.env\n')
                f.write('.git\n')
                f.write('.gitignore\n')
                f.write('venv\n')
                f.write('.venv\n')
                f.write('*.egg-info\n')
                f.write('dist\n')
                f.write('build\n')
                f.write('README.md\n')
            print(f"Created {dockerignore}")
        else:
            print(f"{dockerignore} already exists, skipping.")

        print("\nDocker setup complete!")

    # =============================================
    # FINAL SUMMARY
    # =============================================
    print("\n" + "=" * 50)
    print("  Project setup is complete!")
    print("=" * 50)
    print()

    if include_docker:
        print("  Start with Docker (recommended):")
        print("    docker-compose up --build")
        print()
        print("  Or run locally:")

    print("    pip install -r requirements.txt")
    print("    python main.py")
    print()

    if include_auth:
        print("  Auth endpoints:")
        print("    POST /auth/register")
        print("    POST /auth/login")
        print("    GET  /auth/me (protected)")
        print()

    print("  Swagger docs: http://localhost:8000/docs")
    print("=" * 50)


if __name__ == "__main__":
    init()
