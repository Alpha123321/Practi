from sqlalchemy import Column, Date, String, Numeric, Integer, PrimaryKeyConstraint
from app.database import Base

class CurrencyRate(Base):
    __tablename__ = "currency_rates"
    date = Column(Date, nullable=False)
    currency_code = Column(String(3), nullable=False)
    name = Column(String(100))
    rate = Column(Numeric(12, 6))
    nominal = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint("date", "currency_code"),
    )
