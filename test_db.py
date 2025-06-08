import asyncio
from app.database import engine, async_session
from app.models import CurrencyRate
from sqlalchemy import select
from datetime import date
import logging

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_db():
    print("Testing database connection...")
    try:
        # Проверка подключения
        async with engine.connect() as conn:
            print("Database connection successful!")

        # Проверка работы с таблицей
        async with async_session() as session:
            # Создаем тестовую запись с корректными данными
            test_rate = CurrencyRate(
                date=date.today(),
                currency_code="TST",  # Используем 3 символа!
                name="Test Currency",
                rate=1.0,
                nominal=1
            )
            session.add(test_rate)
            await session.commit()
            print("Test record created")

            # Проверяем созданную запись
            result = await session.execute(
                select(CurrencyRate)
                .where(CurrencyRate.currency_code == "TST")
                .where(CurrencyRate.date == date.today())
            )
            saved_rate = result.scalar_one()
            print(f"Saved record: {saved_rate.currency_code} - {saved_rate.name}")

            # Удаляем тестовую запись
            await session.delete(saved_rate)
            await session.commit()
            print("Test record deleted")

        print("All database tests passed!")
        return True
    except Exception as e:
        logger.exception("Database test failed")
        return False


if __name__ == "__main__":
    asyncio.run(test_db())