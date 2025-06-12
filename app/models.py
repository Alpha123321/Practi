from sqlalchemy import Column, Date, String, Numeric, Integer, Index
from app.database import Base

class CurrencyRate(Base):
    __tablename__ = "currency_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    currency_code = Column(String(3), nullable=False)
    name = Column(String(100))
    rate = Column(Numeric(12, 6))
    nominal = Column(Integer)
    __table_args__ = (
        Index('idx_date_currency', 'date', 'currency_code', unique=True),
    )