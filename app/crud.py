from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CurrencyRate
from datetime import date
import logging
from decimal import Decimal
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

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

    count = 0
    try:
        for rate in rates:
            logger.debug(f"Saving rate: {rate}")  # Логируем каждый курс перед сохранением
            stmt = insert(CurrencyRate).values(
                date=rate['date'],
                currency_code=rate['currency_code'],
                name=rate['name'],
                rate=Decimal(str(rate['rate'])),
                nominal=rate['nominal']
            ).on_conflict_do_update(
                index_elements=['date', 'currency_code'],
                set_={
                    'name': rate['name'],
                    'rate': Decimal(str(rate['rate'])),
                    'nominal': rate['nominal']
                }
            )
            await session.execute(stmt)
            count += 1
        await session.commit()
        logger.info(f"Upserted {count} currency rates")
    except Exception as e:
        logger.error(f"Error saving rates: {e}", exc_info=True)
        await session.rollback()
        return 0

    return count
