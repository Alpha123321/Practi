from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv  # Импортируем функцию загрузки

# Загружаем переменные из .env
load_dotenv()

# Получаем строку подключения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем асинхронный движок для работы с PostgreSQL
engine = create_async_engine(DATABASE_URL)

# Настраиваем фабрику сессий
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Инициализация базы данных - создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)