from sqlalchemy import Column, String, Date, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CurrencyRate(Base):
    __tablename__ = "currency_rates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    currency_code = Column(String(3), nullable=False)
    name = Column(String, nullable=False)
    rate = Column(Numeric, nullable=False)
    nominal = Column(Numeric, nullable=False)
