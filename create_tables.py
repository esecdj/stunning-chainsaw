import asyncio
import os
import importlib.util
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from models.base import Base  # A shared Base class for all models

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

# Dynamically import all .py files from models directory
def import_all_models_from_directory(directory: str):
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "base.py":
            module_name = filename[:-3]  # Strip .py extension
            module_path = os.path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(f"models.{module_name}", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

async def init_models():
    import_all_models_from_directory("models")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
