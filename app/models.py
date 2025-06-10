from sqlalchemy import Column, Integer, Date, String, Numeric
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import Base


class CurrencyRate(Base):
    __tablename__ = 'currency_rates'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    currency_code = Column(String(3), nullable=False)
    name = Column(String, nullable=False)
    rate = Column(Numeric(precision=12, scale=6), nullable=False)
    nominal = Column(Integer, nullable=False)

    @classmethod
    async def create_currency_rate(cls, db: AsyncSession, currency_rate: 'CurrencyRateSchema'):
        """Добавляет новую запись в таблицу currency_rates."""
        currency_rate_dict = currency_rate.model_dump()

        stmt = (
            insert(cls)
            .values(**currency_rate_dict)
            .on_conflict_do_nothing(index_elements=['date', 'currency_code'])
        )

        await db.execute(stmt)
        await db.commit()

        result = await db.execute(
            select(cls)
            .where(cls.date == currency_rate_dict['date'])
            .where(cls.currency_code == currency_rate_dict['currency_code'])
        )
        return result.scalar_one_or_none()
