import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import logging

# Загрузка переменных из .env
load_dotenv()

# Логгер
logger = logging.getLogger("database")

# Получение DATABASE_URL из .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Создание движка базы данных
engine = create_async_engine(DATABASE_URL)

# Создание фабрики сессий
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Базовый класс для моделей
Base = declarative_base()

async def get_db():
    """Генератор сессий для работы с базой данных."""
    async with AsyncSessionLocal() as db:
        try:
            logger.debug("Создана новая сессия базы данных")
            yield db
        except Exception as e:
            logger.error(f"Ошибка при работе с базой данных: {e}")
            raise

async def init_db():
    """Инициализация базы данных: создание всех таблиц."""
    try:
        async with engine.begin() as conn:
            logger.info("Создание таблиц в базе данных")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Таблицы успешно созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise

async def close_db():
    """Закрытие соединения с базой данных."""
    try:
        await engine.dispose()
        logger.info("Соединение с базой данных закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии соединения: {e}")
        raise
