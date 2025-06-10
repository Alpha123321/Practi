from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CurrencyRate
from datetime import date
import logging

logger = logging.getLogger(__name__)


async def get_rates_by_date(session: AsyncSession, target_date: date):
    result = await session.execute(
        select(CurrencyRate).where(CurrencyRate.date == target_date)
    )
    return result.scalars().all()


async def save_rates(session: AsyncSession, rates: list):
    """Сохраняет курсы валют в базу данных"""
    if not rates:
        return 0

    # Привести данные к нужному формату
    currency_data = []
    for rate in rates:
        # Проверить, существует ли запись
        stmt = select(CurrencyRate).where(
            CurrencyRate.date == rate['date'],
            CurrencyRate.currency_code == rate['currency_code']
        )
        result = await session.execute(stmt)
        existing = result.scalar()

        if not existing:
            # Добавить новую запись
            currency_data.append(
                CurrencyRate(
                    date=rate['date'],
                    currency_code=rate['currency_code'],
                    name=rate['name'],
                    rate=rate['rate'],
                    nominal=rate['nominal']
                )
            )

    # Вставляем все новые записи
    if currency_data:
        session.add_all(currency_data)
        await session.commit()

    return len(currency_data)