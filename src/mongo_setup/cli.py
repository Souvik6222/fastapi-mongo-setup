import os
import pathlib
import argparse
import json
import urllib.request
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

__version__ = "0.8.0"


def check_for_updates():
    """Check PyPI for a newer version of the package."""
    try:
        url = "https://pypi.org/pypi/fastapi-mongo-setup/json"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            latest = data["info"]["version"]
            if latest != __version__:
                console.print(
                    f"  [yellow]â¬† Update available:[/yellow] {__version__} â†’ "
                    f"[green]{latest}[/green]  "
                    f"Run: [cyan]pip install --upgrade fastapi-mongo-setup[/cyan]\n"
                )
    except Exception:
        pass


def to_pascal_case(snake_str):
    """Convert snake_case to PascalCase. e.g. blog_posts -> BlogPosts"""
    return "".join(word.capitalize() for word in snake_str.split("_"))


def generate_resource(name):
    """Generate a new API resource module with router, schemas, and service."""
    src_dir = pathlib.Path("src")
    resource_dir = src_dir / name
    class_name = to_pascal_case(name)

    if resource_dir.exists():
        console.print(f"  [red]âœ—[/red] Error: src/{name}/ already exists. Choose a different name.")
        return

    resource_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"\n  [bold cyan]â–¸ Generating '{name}' resource module...[/bold cyan]")

    # __init__.py
    with open(resource_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")

    # schemas.py
    schemas_file = resource_dir / "schemas.py"
    with open(schemas_file, "w", encoding="utf-8") as f:
        f.write('from pydantic import BaseModel, Field\n')
        f.write('from typing import Optional\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'class {class_name}Create(BaseModel):\n')
        f.write(f'    name: str = Field(..., example="Sample {class_name}")\n')
        f.write(f'    description: Optional[str] = Field(None, example="A sample description")\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'class {class_name}Update(BaseModel):\n')
        f.write(f'    name: Optional[str] = None\n')
        f.write(f'    description: Optional[str] = None\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'class {class_name}Response({class_name}Create):\n')
        f.write('    id: str\n')
    console.print(f"  [green]âœ“[/green] Created {schemas_file}")

    # service.py
    service_file = resource_dir / "service.py"
    with open(service_file, "w", encoding="utf-8") as f:
        f.write('from src.utils.db import db\n')
        f.write('from src.utils.helpers import serialize_doc, serialize_docs\n')
        f.write('from bson import ObjectId\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'class {class_name}Service:\n')
        f.write('    @staticmethod\n')
        f.write('    def get_collection():\n')
        f.write(f'        return db.db["{name}"]\n')
        f.write('\n')
        f.write('    @staticmethod\n')
        f.write(f'    async def create(data: dict) -> dict:\n')
        f.write(f'        result = await {class_name}Service.get_collection().insert_one(data)\n')
        f.write(f'        created = await {class_name}Service.get_collection().find_one({{"_id": result.inserted_id}})\n')
        f.write('        return serialize_doc(created)\n')
        f.write('\n')
        f.write('    @staticmethod\n')
        f.write(f'    async def get_all() -> list:\n')
        f.write(f'        cursor = {class_name}Service.get_collection().find()\n')
        f.write('        items = await cursor.to_list(length=100)\n')
        f.write('        return serialize_docs(items)\n')
        f.write('\n')
        f.write('    @staticmethod\n')
        f.write(f'    async def get_by_id(item_id: str):\n')
        f.write(f'        item = await {class_name}Service.get_collection().find_one({{"_id": ObjectId(item_id)}})\n')
        f.write('        return serialize_doc(item) if item else None\n')
        f.write('\n')
        f.write('    @staticmethod\n')
        f.write(f'    async def update(item_id: str, data: dict) -> dict:\n')
        f.write('        update_data = {k: v for k, v in data.items() if v is not None}\n')
        f.write('        if not update_data:\n')
        f.write('            return await {class_name}Service.get_by_id(item_id)\n'.format(class_name=class_name))
        f.write(f'        await {class_name}Service.get_collection().update_one(\n')
        f.write('            {"_id": ObjectId(item_id)}, {"$set": update_data}\n')
        f.write('        )\n')
        f.write(f'        return await {class_name}Service.get_by_id(item_id)\n')
        f.write('\n')
        f.write('    @staticmethod\n')
        f.write(f'    async def delete(item_id: str) -> bool:\n')
        f.write(f'        result = await {class_name}Service.get_collection().delete_one({{"_id": ObjectId(item_id)}})\n')
        f.write('        return result.deleted_count > 0\n')
    console.print(f"  [green]âœ“[/green] Created {service_file}")

    # router.py
    router_file = resource_dir / "router.py"
    with open(router_file, "w", encoding="utf-8") as f:
        f.write('from fastapi import APIRouter, HTTPException\n')
        f.write('from typing import List\n')
        f.write(f'from src.{name}.schemas import {class_name}Create, {class_name}Update, {class_name}Response\n')
        f.write(f'from src.{name}.service import {class_name}Service\n')
        f.write('\n')
        f.write(f'router = APIRouter(prefix="/{name}", tags=["{class_name}"])\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'@router.post("/", response_model={class_name}Response)\n')
        f.write(f'async def create_{name}_item(item: {class_name}Create):\n')
        f.write(f'    """Create a new {name} item."""\n')
        f.write(f'    return await {class_name}Service.create(item.model_dump())\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'@router.get("/", response_model=List[{class_name}Response])\n')
        f.write(f'async def get_all_{name}():\n')
        f.write(f'    """Get all {name} items."""\n')
        f.write(f'    return await {class_name}Service.get_all()\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'@router.get("/{{item_id}}", response_model={class_name}Response)\n')
        f.write(f'async def get_{name}_by_id(item_id: str):\n')
        f.write(f'    """Get a single {name} item by ID."""\n')
        f.write(f'    item = await {class_name}Service.get_by_id(item_id)\n')
        f.write('    if not item:\n')
        f.write(f'        raise HTTPException(status_code=404, detail="{class_name} not found")\n')
        f.write('    return item\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'@router.put("/{{item_id}}", response_model={class_name}Response)\n')
        f.write(f'async def update_{name}_item(item_id: str, item: {class_name}Update):\n')
        f.write(f'    """Update an existing {name} item."""\n')
        f.write(f'    existing = await {class_name}Service.get_by_id(item_id)\n')
        f.write('    if not existing:\n')
        f.write(f'        raise HTTPException(status_code=404, detail="{class_name} not found")\n')
        f.write(f'    return await {class_name}Service.update(item_id, item.model_dump())\n')
        f.write('\n')
        f.write(f'\n')
        f.write(f'@router.delete("/{{item_id}}")\n')
        f.write(f'async def delete_{name}_item(item_id: str):\n')
        f.write(f'    """Delete a {name} item."""\n')
        f.write(f'    success = await {class_name}Service.delete(item_id)\n')
        f.write('    if not success:\n')
        f.write(f'        raise HTTPException(status_code=404, detail="{class_name} not found")\n')
        f.write(f'    return {{"message": "{class_name} deleted successfully"}}\n')
    console.print(f"  [green]âœ“[/green] Created {router_file}")

    # Final instructions
    table = Table(title=f"ðŸ§© Endpoints for /{name}", show_header=True, header_style="bold cyan")
    table.add_column("Method", style="green", width=8)
    table.add_column("Endpoint", style="white")
    table.add_column("Action", style="dim")
    table.add_row("POST", f"/{name}/", "Create")
    table.add_row("GET", f"/{name}/", "List all")
    table.add_row("GET", f"/{name}/{{id}}", "Get by ID")
    table.add_row("PUT", f"/{name}/{{id}}", "Update")
    table.add_row("DELETE", f"/{name}/{{id}}", "Delete")
    console.print()
    console.print(table)

    add_code = f"from src.{name}.router import router as {name}_router\napp.include_router({name}_router)"
    console.print(Panel(add_code, title="[yellow]Add to main.py[/yellow]", border_style="yellow"))


def init():
    parser = argparse.ArgumentParser(
        description="Scaffold a production-ready FastAPI + MongoDB project"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="setup",
        help="Command to run: 'setup' (default) or 'resource <name>'"
    )
    parser.add_argument(
        "resource_name",
        nargs="?",
        default=None,
        help="Name of the resource to generate (used with 'resource' command)"
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
        "--test",
        action="store_true",
        help="Include pytest test scaffolding and ruff linter config"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include all optional features (auth + docker + test)"
    )
    args = parser.parse_args()

    # Check for updates
    check_for_updates()

    # =============================================
    # RESOURCE GENERATOR: mongo-setup resource posts
    # =============================================
    if args.command == "resource":
        if not args.resource_name:
            console.print("  [red]âœ—[/red] Please provide a resource name.")
            console.print("  Usage: [cyan]mongo-setup resource <name>[/cyan]")
            console.print("  Example: [cyan]mongo-setup resource products[/cyan]")
            return
        generate_resource(args.resource_name)
        return

    # --all shortcut enables everything
    if args.all:
        args.auth = True
        args.docker = True
        args.test = True

    # =============================================
    # INTERACTIVE MODE: If no flags passed, ask user
    # =============================================
    if args.command != "setup" and args.command != "resource":
        # Treat unknown command as a flag-only run
        pass

    if not args.auth and not args.docker and not args.test:
        console.print(Panel(
            "[bold white]Let's configure your project.[/bold white]",
            title="[bold cyan]ðŸš€ fastapi-mongo-setup[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))
        console.print()

        auth_answer = console.input("  ðŸ” Include JWT Authentication? [dim](y/N)[/dim]: ").strip().lower()
        args.auth = auth_answer in ("y", "yes")

        docker_answer = console.input("  ðŸ³ Include Docker setup? [dim](y/N)[/dim]: ").strip().lower()
        args.docker = docker_answer in ("y", "yes")

        test_answer = console.input("  ðŸ§ª Include Test scaffolding? [dim](y/N)[/dim]: ").strip().lower()
        args.test = test_answer in ("y", "yes")
        console.print()

    include_auth = args.auth
    include_docker = args.docker
    include_test = args.test

    features = []
    if include_auth:
        features.append("[green]âœ“[/green] JWT Authentication")
    if include_docker:
        features.append("[green]âœ“[/green] Docker containerization")
    if include_test:
        features.append("[green]âœ“[/green] Pytest & Ruff linter")
    features.append("[green]âœ“[/green] Base project (DB + CRUD)")

    console.print(Panel(
        "\n".join(features),
        title="[bold cyan]ðŸ“¦ Building your project[/bold cyan]",
        border_style="cyan",
    ))

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
        console.print(f"  [green]✓[/green] Created {config_file}")
    else:
        console.print(f"  [yellow]→[/yellow] {config_file} already exists, skipping.")
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
        console.print(f"  [green]✓[/green] Created {db_file}")
    else:
        console.print(f"  [yellow]→[/yellow] {db_file} already exists, skipping.")

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
        console.print(f"  [green]✓[/green] Created {helpers_file}")
    else:
        console.print(f"  [yellow]→[/yellow] {helpers_file} already exists, skipping.")

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
        console.print(f"  [green]✓[/green] Created {schemas_file}")
    else:
        console.print(f"  [yellow]→[/yellow] {schemas_file} already exists, skipping.")

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
        console.print(f"  [green]✓[/green] Created {service_file}")
    else:
        console.print(f"  [yellow]→[/yellow] {service_file} already exists, skipping.")

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
        console.print(f"  [green]✓[/green] Created {router_file}")
    else:
        console.print(f"  [yellow]→[/yellow] {router_file} already exists, skipping.")

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
        console.print(f"  [green]✓[/green] Created {main_file}")
    else:
        console.print(f"  [yellow]→[/yellow] {main_file} already exists, skipping.")
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

    console.print("  [green]✓[/green] Updated .env file with environment variables.")

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
        console.print(f"  [green]✓[/green] Updated {req_file} with dependencies.")
    else:
        print(f"{req_file} already has all required dependencies.")

    # =============================================
    # AUTH MODULE (only when --auth is passed)
    # =============================================
    if include_auth:
        console.print("\n  [bold cyan]▸ Setting up JWT Authentication module[/bold cyan]")
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
            console.print(f"  [green]✓[/green] Created {auth_utils}")
        else:
            console.print(f"  [yellow]→[/yellow] {auth_utils} already exists, skipping.")

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
            console.print(f"  [green]✓[/green] Created {auth_schemas}")
        else:
            console.print(f"  [yellow]→[/yellow] {auth_schemas} already exists, skipping.")

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
            console.print(f"  [green]✓[/green] Created {auth_service}")
        else:
            console.print(f"  [yellow]→[/yellow] {auth_service} already exists, skipping.")

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
            console.print(f"  [green]✓[/green] Created {auth_deps_file}")
        else:
            console.print(f"  [yellow]→[/yellow] {auth_deps_file} already exists, skipping.")

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
            console.print(f"  [green]✓[/green] Created {auth_router}")
        else:
            console.print(f"  [yellow]→[/yellow] {auth_router} already exists, skipping.")

        console.print("\n  [green]✓ JWT Authentication module ready![/green]")

    # =============================================
    # DOCKER MODULE (only when --docker is passed)
    # =============================================
    if include_docker:
        console.print("\n  [bold cyan]▸ Setting up Docker containerization[/bold cyan]")

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
            console.print(f"  [green]✓[/green] Created {dockerfile}")
        else:
            console.print(f"  [yellow]→[/yellow] {dockerfile} already exists, skipping.")

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
            console.print(f"  [green]✓[/green] Created {compose_file}")
        else:
            console.print(f"  [yellow]→[/yellow] {compose_file} already exists, skipping.")

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
            console.print(f"  [green]✓[/green] Created {dockerignore}")
        else:
            console.print(f"  [yellow]→[/yellow] {dockerignore} already exists, skipping.")

        console.print("\n  [green]✓ Docker setup ready![/green]")

    # =============================================
    # TEST MODULE (only when --test is passed)
    # =============================================
    if include_test:
        console.print("\n  [bold cyan]▸ Setting up Test scaffolding & Linter[/bold cyan]")
        tests_dir = pathlib.Path("tests")
        tests_dir.mkdir(parents=True, exist_ok=True)

        # =============================================
        # T1. pytest.ini
        # =============================================
        pytest_ini = pathlib.Path("pytest.ini")
        if not pytest_ini.exists():
            with open(pytest_ini, "w", encoding="utf-8") as f:
                f.write('[pytest]\n')
                f.write('asyncio_mode = auto\n')
            console.print(f"  [green]✓[/green] Created {pytest_ini}")
        else:
            console.print(f"  [yellow]→[/yellow] {pytest_ini} already exists, skipping.")

        # =============================================
        # T2. tests/__init__.py
        # =============================================
        tests_init = tests_dir / "__init__.py"
        if not tests_init.exists():
            with open(tests_init, "w", encoding="utf-8") as f:
                f.write("")

        # =============================================
        # T3. tests/conftest.py (Test Client Setup)
        # =============================================
        conftest_file = tests_dir / "conftest.py"
        if not conftest_file.exists():
            with open(conftest_file, "w", encoding="utf-8") as f:
                f.write('import pytest\n')
                f.write('from httpx import AsyncClient, ASGITransport\n')
                f.write('from main import app\n')
                f.write('\n')
                f.write('\n')
                f.write('@pytest.fixture\n')
                f.write('async def client():\n')
                f.write('    """Create an async test client for the FastAPI app."""\n')
                f.write('    transport = ASGITransport(app=app)\n')
                f.write('    async with AsyncClient(transport=transport, base_url="http://test") as ac:\n')
                f.write('        yield ac\n')
            console.print(f"  [green]✓[/green] Created {conftest_file}")
        else:
            console.print(f"  [yellow]→[/yellow] {conftest_file} already exists, skipping.")

        # =============================================
        # T4. tests/test_tasks.py
        # =============================================
        test_tasks = tests_dir / "test_tasks.py"
        if not test_tasks.exists():
            with open(test_tasks, "w", encoding="utf-8") as f:
                f.write('import pytest\n')
                f.write('\n')
                f.write('\n')
                f.write('async def test_root(client):\n')
                f.write('    """Test that the root endpoint returns a welcome message."""\n')
                f.write('    response = await client.get("/")\n')
                f.write('    assert response.status_code == 200\n')
                f.write('    data = response.json()\n')
                f.write('    assert "message" in data\n')
                f.write('\n')
                f.write('\n')
                f.write('async def test_get_tasks(client):\n')
                f.write('    """Test that GET /tasks/ returns a list."""\n')
                f.write('    response = await client.get("/tasks/")\n')
                f.write('    assert response.status_code == 200\n')
                f.write('    assert isinstance(response.json(), list)\n')
                f.write('\n')
                f.write('\n')
                f.write('async def test_create_task(client):\n')
                f.write('    """Test creating a new task via POST /tasks/."""\n')
                f.write('    task_data = {"title": "Test Task", "description": "A test task", "completed": False}\n')
                f.write('    response = await client.post("/tasks/", json=task_data)\n')
                f.write('    assert response.status_code == 200\n')
                f.write('    data = response.json()\n')
                f.write('    assert data["title"] == "Test Task"\n')
                f.write('    assert "id" in data\n')
                f.write('\n')
                f.write('\n')
                f.write('async def test_delete_task_not_found(client):\n')
                f.write('    """Test deleting a task that does not exist returns 404."""\n')
                f.write('    response = await client.delete("/tasks/000000000000000000000000")\n')
                f.write('    assert response.status_code == 404\n')
            console.print(f"  [green]✓[/green] Created {test_tasks}")
        else:
            console.print(f"  [yellow]→[/yellow] {test_tasks} already exists, skipping.")

        # =============================================
        # T5. tests/test_auth.py (only with --auth)
        # =============================================
        if include_auth:
            test_auth = tests_dir / "test_auth.py"
            if not test_auth.exists():
                with open(test_auth, "w", encoding="utf-8") as f:
                    f.write('import pytest\n')
                    f.write('\n')
                    f.write('\n')
                    f.write('async def test_register(client):\n')
                    f.write('    """Test registering a new user account."""\n')
                    f.write('    user_data = {"name": "Test User", "email": "test@example.com", "password": "secret123"}\n')
                    f.write('    response = await client.post("/auth/register", json=user_data)\n')
                    f.write('    assert response.status_code == 200\n')
                    f.write('    data = response.json()\n')
                    f.write('    assert data["email"] == "test@example.com"\n')
                    f.write('    assert "id" in data\n')
                    f.write('\n')
                    f.write('\n')
                    f.write('async def test_register_duplicate_email(client):\n')
                    f.write('    """Test that registering with an existing email fails."""\n')
                    f.write('    user_data = {"name": "Test User", "email": "test@example.com", "password": "secret123"}\n')
                    f.write('    response = await client.post("/auth/register", json=user_data)\n')
                    f.write('    assert response.status_code == 400\n')
                    f.write('\n')
                    f.write('\n')
                    f.write('async def test_login(client):\n')
                    f.write('    """Test logging in with valid credentials."""\n')
                    f.write('    user_data = {"email": "test@example.com", "password": "secret123"}\n')
                    f.write('    response = await client.post("/auth/login", json=user_data)\n')
                    f.write('    assert response.status_code == 200\n')
                    f.write('    data = response.json()\n')
                    f.write('    assert "access_token" in data\n')
                    f.write('    assert data["token_type"] == "bearer"\n')
                    f.write('\n')
                    f.write('\n')
                    f.write('async def test_login_wrong_password(client):\n')
                    f.write('    """Test that login fails with wrong password."""\n')
                    f.write('    user_data = {"email": "test@example.com", "password": "wrongpassword"}\n')
                    f.write('    response = await client.post("/auth/login", json=user_data)\n')
                    f.write('    assert response.status_code == 401\n')
                    f.write('\n')
                    f.write('\n')
                    f.write('async def test_me_unauthorized(client):\n')
                    f.write('    """Test that /auth/me returns 401 without a token."""\n')
                    f.write('    response = await client.get("/auth/me")\n')
                    f.write('    assert response.status_code == 401\n')
                console.print(f"  [green]✓[/green] Created {test_auth}")
            else:
                console.print(f"  [yellow]→[/yellow] {test_auth} already exists, skipping.")

        # =============================================
        # T6. .ruff.toml (Linter Configuration)
        # =============================================
        ruff_config = pathlib.Path(".ruff.toml")
        if not ruff_config.exists():
            with open(ruff_config, "w", encoding="utf-8") as f:
                f.write('# Ruff linter configuration\n')
                f.write('# Run: pip install ruff && ruff check .\n')
                f.write('\n')
                f.write('[lint]\n')
                f.write('select = ["E", "F", "W", "I"]\n')
                f.write('ignore = ["E501"]\n')
                f.write('\n')
                f.write('[format]\n')
                f.write('quote-style = "double"\n')
                f.write('indent-style = "space"\n')
            console.print(f"  [green]✓[/green] Created {ruff_config}")
        else:
            console.print(f"  [yellow]→[/yellow] {ruff_config} already exists, skipping.")

        # Add test deps to requirements.txt
        req_file = pathlib.Path("requirements.txt")
        req_content = ""
        if req_file.exists():
            with open(req_file, "r", encoding="utf-8") as f:
                req_content = f.read()

        test_deps = ["pytest", "pytest-asyncio", "httpx", "ruff"]
        test_deps_to_add = []
        for dep in test_deps:
            if dep not in req_content:
                test_deps_to_add.append(dep)

        if test_deps_to_add:
            with open(req_file, "a", encoding="utf-8") as f:
                if req_content and not req_content.endswith("\n"):
                    f.write("\n")
                f.write("# Testing & Linting\n")
                for dep in test_deps_to_add:
                    f.write(dep + "\n")
            console.print(f"  [green]✓[/green] Updated {req_file} with test dependencies.")

        console.print("\n  [green]✓ Test scaffolding & linter ready![/green]")

    # =============================================
    # FINAL SUMMARY
    # =============================================
    summary_lines = []

    if include_docker:
        summary_lines.append("[bold]Start with Docker (recommended):[/bold]")
        summary_lines.append("  [cyan]docker-compose up --build[/cyan]")
        summary_lines.append("")
        summary_lines.append("[bold]Or run locally:[/bold]")
    else:
        summary_lines.append("[bold]Get started:[/bold]")

    summary_lines.append("  [cyan]pip install -r requirements.txt[/cyan]")
    summary_lines.append("  [cyan]python main.py[/cyan]")

    if include_auth:
        summary_lines.append("")
        summary_lines.append("[bold]Auth endpoints:[/bold]")
        summary_lines.append("  POST [green]/auth/register[/green]")
        summary_lines.append("  POST [green]/auth/login[/green]")
        summary_lines.append("  GET  [green]/auth/me[/green] [dim](protected)[/dim]")

    if include_test:
        summary_lines.append("")
        summary_lines.append("[bold]Quality tools:[/bold]")
        summary_lines.append("  [cyan]pytest[/cyan]          Run tests")
        summary_lines.append("  [cyan]ruff check .[/cyan]    Lint code")

    summary_lines.append("")
    summary_lines.append("[bold]Swagger docs:[/bold] [link=http://localhost:8000/docs]http://localhost:8000/docs[/link]")

    console.print()
    console.print(Panel(
        "\n".join(summary_lines),
        title="[bold green]âœ… Project setup complete![/bold green]",
        border_style="green",
        padding=(1, 2)
    ))


if __name__ == "__main__":
    init()
