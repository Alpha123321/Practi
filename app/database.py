import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Добавляем настройки для лучшей обработки соединений
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    pool_timeout=30,
    pool_recycle=3600
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Явный импорт ВСЕХ моделей здесь!
from app.models import CurrencyRate  # Важно!

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

async def shutdown_db():
    await engine.dispose()
    logger.info("Database engine disposed")
