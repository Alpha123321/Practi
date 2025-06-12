from pydantic import BaseModel, field_validator
from datetime import date as DateType
import re

class CurrencyRateSchema(BaseModel):
    date: DateType
    currency_code: str
    name: str
    rate: float
    nominal: int

    @field_validator('currency_code')
    def validate_currency_code(cls, v):
        v = v.strip().upper()
        if not re.match(r'^[A-Z]{3}$', v):
            raise ValueError('Currency code must be 3 uppercase letters')
        return v

    class Config:
        from_attributes = True