import os
import pathlib

def init():
    print("Initializing full-fledged MongoDB FastAPI project structure...")
    
    # Base directories
    src_dir = pathlib.Path("src")
    utils_dir = src_dir / "utils"
    tasks_dir = src_dir / "tasks"
    
    utils_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. src/config.py
    config_file = src_dir / "config.py"
    if not config_file.exists():
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("""from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "fastapi_db"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
""")
        print(f"Created {config_file}")
    else:
        print(f"{config_file} already exists, skipping.")
    
    # 2. src/utils/db.py
    db_file = utils_dir / "db.py"
    if not db_file.exists():
        with open(db_file, "w", encoding="utf-8") as f:
            f.write("""from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongodb():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.db = db.client[settings.database_name]
    await db.client.admin.command('ping')
    print("Connected to MongoDB!")

async def close_mongodb_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection.")
""")
        print(f"Created {db_file}")
    else:
        print(f"{db_file} already exists, skipping.")

    # 3. src/utils/helpers.py
    helpers_file = utils_dir / "helpers.py"
    if not helpers_file.exists():
        with open(helpers_file, "w", encoding="utf-8") as f:
            f.write("""def serialize_doc(doc):
    \"\"\"Convert MongoDB ObjectId to string\"\"\"
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

def serialize_docs(docs):
    return [serialize_doc(doc) for doc in docs]
""")
        print(f"Created {helpers_file}")
    else:
        print(f"{helpers_file} already exists, skipping.")

    # 4. src/tasks/schemas.py
    schemas_file = tasks_dir / "schemas.py"
    if not schemas_file.exists():
        with open(schemas_file, "w", encoding="utf-8") as f:
            f.write("""from pydantic import BaseModel, Field
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(..., example="Buy groceries")
    description: Optional[str] = Field(None, example="Milk, Eggs, Bread")
    completed: bool = False

class TaskResponse(TaskCreate):
    id: str
""")
        print(f"Created {schemas_file}")
    else:
        print(f"{schemas_file} already exists, skipping.")

    # 5. src/tasks/service.py
    service_file = tasks_dir / "service.py"
    if not service_file.exists():
        with open(service_file, "w", encoding="utf-8") as f:
            f.write("""from src.utils.db import db
from src.utils.helpers import serialize_doc, serialize_docs
from bson import ObjectId

class TaskService:
    @staticmethod
    def get_collection():
        return db.db["tasks"]

    @staticmethod
    async def create_task(task_data: dict) -> dict:
        result = await TaskService.get_collection().insert_one(task_data)
        created_task = await TaskService.get_collection().find_one({"_id": result.inserted_id})
        return serialize_doc(created_task)

    @staticmethod
    async def get_all_tasks() -> list:
        cursor = TaskService.get_collection().find()
        tasks = await cursor.to_list(length=100)
        return serialize_docs(tasks)

    @staticmethod
    async def delete_task(task_id: str) -> bool:
        result = await TaskService.get_collection().delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
""")
        print(f"Created {service_file}")
    else:
        print(f"{service_file} already exists, skipping.")

    # 6. src/tasks/router.py
    router_file = tasks_dir / "router.py"
    if not router_file.exists():
        with open(router_file, "w", encoding="utf-8") as f:
            f.write("""from fastapi import APIRouter, HTTPException
from typing import List
from src.tasks.schemas import TaskCreate, TaskResponse
from src.tasks.service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    created_task = await TaskService.create_task(task.model_dump())
    return created_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks():
    return await TaskService.get_all_tasks()

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    success = await TaskService.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
""")
        print(f"Created {router_file}")
    else:
        print(f"{router_file} already exists, skipping.")

    # 7. main.py
    main_file = pathlib.Path("main.py")
    if not main_file.exists():
        with open(main_file, "w", encoding="utf-8") as f:
            f.write("""from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from src.config import settings
from src.utils.db import connect_to_mongodb, close_mongodb_connection
from src.tasks.router import router as tasks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    await connect_to_mongodb()
    yield
    # Shutdown: Close DB
    await close_mongodb_connection()

app = FastAPI(lifespan=lifespan, title="FastAPI MongoDB App")

# Register routers
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI + MongoDB Boilerplate!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
""")
        print(f"Created {main_file}")
    else:
        print(f"{main_file} already exists, skipping.")

    # 8. .env
    env_file = pathlib.Path(".env")
    env_content = ""
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            env_content = f.read()

    with open(env_file, "a", encoding="utf-8") as f:
        if env_content and not env_content.endswith("\n"):
            f.write("\n")
        if "MONGODB_URL" not in env_content:
            f.write("MONGODB_URL=mongodb://localhost:27017\n")
        if "DATABASE_NAME" not in env_content:
            f.write("DATABASE_NAME=fastapi_db\n")
        if "PORT" not in env_content:
            f.write("PORT=8000\n")
            
    print("Updated .env file with MongoDB environment variables.")

    # 9. requirements.txt
    req_file = pathlib.Path("requirements.txt")
    if not req_file.exists():
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("""fastapi
uvicorn
motor
python-dotenv
pydantic
pydantic-settings
""")
        print(f"Created {req_file}")
    else:
        print(f"{req_file} already exists, skipping.")
        
    print("Full FastAPI + MongoDB structure setup is complete!")
    print("Run your server with: python main.py")

if __name__ == "__main__":
    init()
