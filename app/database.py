from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# DATABASE_URL = "postgresql+asyncpg://postgres:Pato1234@localhost:5432/postgres" # local
DATABASE_URL = "postgresql+asyncpg://postgres:secret123@db:5432/fastapi_db"
DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL)

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()
