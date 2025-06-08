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

    saved_count = 0
    for rate in rates:
        try:
            # Используем merge вместо insert для обработки конфликтов
            stmt = select(CurrencyRate).where(
                CurrencyRate.date == rate['date'],
                CurrencyRate.currency_code == rate['currency_code']
            )
            existing = await session.execute(stmt)
            if existing.scalar_one_or_none() is None:
                currency_rate = CurrencyRate(
                    date=rate['date'],
                    currency_code=rate['currency_code'],
                    name=rate['name'],
                    rate=rate['rate'],
                    nominal=rate['nominal']
                )
                session.add(currency_rate)
                saved_count += 1
        except Exception as e:
            logger.error(f"Error saving rate for {rate['currency_code']}: {str(e)}")
            continue

    if saved_count > 0:
        await session.commit()
        logger.info(f"Saved {saved_count} new currency rates")

    return saved_count