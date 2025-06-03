from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class CurrencyRateSchema(BaseModel):
    """Схема для валидации и сериализации данных"""
    date: date
    currency_code: str
    name: str
    rate: float
    nominal: int

    class Config:
        # Новый параметр вместо orm_mode
        from_attributes = True
