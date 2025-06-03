from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CurrencyRate


async def get_rates_by_date(session: AsyncSession, target_date: date):
    """Получение курсов валют за указанную дату"""
    result = await session.execute(
        select(CurrencyRate)
        .where(CurrencyRate.date == target_date)
    )
    return result.scalars().all()


async def save_rates(session: AsyncSession, rates: list[dict]):
    """Сохранение списка курсов в БД с правильной обработкой транзакций"""
    try:
        for rate_data in rates:
            # Создание объекта модели из словаря данных
            rate_obj = CurrencyRate(
                date=rate_data['date'],
                currency_code=rate_data['currency_code'],
                name=rate_data['name'],
                rate=rate_data['rate'],
                nominal=rate_data['nominal']
            )
            session.add(rate_obj)

        # Атомарное сохранение всех изменений
        await session.commit()
    except Exception as e:
        # Откат транзакции при ошибке
        await session.rollback()
        raise e
