
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("DATABASE_URL")
print(password)
engine = create_async_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency for FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session
