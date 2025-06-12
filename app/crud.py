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
    if not rates:
        logger.warning("No rates to save")
        return 0

    # Получаем все существующие коды валют за эту дату
    target_date = rates[0]['date']
    existing = await session.execute(
        select(CurrencyRate.currency_code)
        .where(CurrencyRate.date == target_date)
    )
    existing_codes = {code[0] for code in existing}

    # Фильтруем только новые записи
    new_rates = [
        CurrencyRate(
            date=rate['date'],
            currency_code=rate['currency_code'],
            name=rate['name'],
            rate=rate['rate'],
            nominal=rate['nominal']
        )
        for rate in rates
        if rate['currency_code'] not in existing_codes
    ]

    if not new_rates:
        logger.info("All rates already exist in database")
        return 0

    session.add_all(new_rates)
    await session.commit()
    logger.info(f"Saved {len(new_rates)} new currency rates")
    return len(new_rates)