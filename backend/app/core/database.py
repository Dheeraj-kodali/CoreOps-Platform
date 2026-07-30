from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

Base = declarative_base()

# Build Engine Arguments for Neon PostgreSQL or SQLite
db_url = settings.DATABASE_URL
engine_kwargs = {
    "echo": False,
    "future": True,
}

if "postgresql" in db_url or "postgres" in db_url:
    # Normalize query string parameters for asyncpg compatibility
    db_url = db_url.replace("sslmode=require", "ssl=require").replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    })

engine = create_async_engine(
    db_url,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
