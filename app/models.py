from sqlalchemy import Column, Date, String, Numeric, Integer, Index
from .database import Base


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    date = Column(Date, primary_key=True)
    currency_code = Column(String(3), primary_key=True)
    name = Column(String(100))
    rate = Column(Numeric(12, 6))
    nominal = Column(Integer)

    __table_args__ = (
        Index('idx_date_currency', 'date', 'currency_code', unique=True),
    )
