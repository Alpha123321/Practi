import asyncio
from datetime import date

from sqlalchemy import select

from app.database import async_session, init_db
from app.crud import save_rates
from app.models import CurrencyRate


async def test_save():
    await init_db()

    test_data = [
        {
            'date': date.today(),
            'currency_code': 'TST',
            'name': 'Test Currency',
            'rate': 1.23,
            'nominal': 1
        }
    ]

    async with async_session() as session:
        # Сохраняем тестовые данные
        await save_rates(session, test_data)

        # Проверяем сохранение
        result = await session.execute(
            seluvicorn app.main:app --reloadect(CurrencyRate)
            .where(CurrencyRate.currency_code == 'TST')
        )
        saved = result.scalar_one()
        print(f"Saved record: {saved.currency_code} - {saved.name}")

        # Очищаем тестовые данные
        await session.delete(saved)
        await session.commit()
        print("Test record deleted")


if __name__ == "__main__":
    asyncio.run(test_save())