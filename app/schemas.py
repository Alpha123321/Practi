from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date

class CurrencyRateSchema(BaseModel):
    # Исключаем id из схемы, так как он генерируется автоматически
    model_config = ConfigDict(from_attributes=True)

    date: date
    currency_code: str = Field(..., min_length=3, max_length=3)
    name: str
    rate: float
    nominal: int

    @field_validator("currency_code")
    def validate_currency_code(cls, value):
        if len(value) != 3 or not value.isalpha():
            raise ValueError("Currency code must be 3 alphabetic characters")
        return value.upper()
