from logging.config import fileConfig
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from alembic import context
from app.models import Base  # Импортируйте Base из вашего модуля models
from app.database import DATABASE_URL  # Импортируйте URL базы данных

# Конфигурация Alembic
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные моделей
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в офлайн-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме."""
    # Создаем асинхронный движок
    engine = create_async_engine(DATABASE_URL)

    # Подключаемся к базе данных
    async with engine.connect() as connection:
        # Настраиваем контекст Alembic
        await connection.run_sync(lambda sync_conn: context.configure(
            connection=sync_conn,
            target_metadata=target_metadata,
            compare_type=True,
        ))

        # Выполняем миграции
        await connection.run_sync(lambda sync_conn: context.run_migrations())

# Запуск миграций
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())



#В run_migrations_online создаётся асинхронный движок и подключается к базе данных.

#Используется connection.run_sync для выполнения синхронного кода Alembic.

#Синхронное соединение (sync_conn) передаётся в context.run_migrations через лямбду.