
from sqlalchemy import Column, Date, String, Numeric, Index
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class CurrencyRate(Base):
    """Модель для хранения курсов валют"""
    __tablename__ = "currency_rates"

    # Составной первичный ключ: дата + код валюты
    date = Column(Date, primary_key=True)
    currency_code = Column(String(3), primary_key=True)

    # Дополнительные поля
    name = Column(String(100))
    rate = Column(Numeric(10, 4))
    nominal = Column(Numeric(10, 0))

    # Индекс для ускорения поиска по дате
    __table_args__ = (Index('ix_currency_date', 'date'),)