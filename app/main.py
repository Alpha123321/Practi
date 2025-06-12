from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import CurrencyRate
from app.database import get_db
from app.schemas import CurrencyRateSchema

app = FastAPI()

# Получить все курсы
@app.get("/currency-rates/", response_model=List[CurrencyRateSchema])
async def get_all_rates(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CurrencyRate).order_by(CurrencyRate.date.desc()))
        rates = result.scalars().all()
        return rates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Получить курс по id
@app.get("/currency-rates/{rate_id}", response_model=CurrencyRateSchema)
async def get_rate_by_id(rate_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CurrencyRate).where(CurrencyRate.id == rate_id))
        rate = result.scalars().first()
        if not rate:
            raise HTTPException(status_code=404, detail="Rate not found")
        return rate
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Получить последние 10 курсов
@app.get("/currency-rates/latest/", response_model=List[CurrencyRateSchema])
async def get_latest_rates(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CurrencyRate).order_by(CurrencyRate.date.desc()).limit(10))
        rates = result.scalars().all()
        return rates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Получить курсы по коду валюты
@app.get("/currency-rates/currency/{currency_code}", response_model=List[CurrencyRateSchema])
async def get_rates_by_code(currency_code: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(CurrencyRate)
            .where(CurrencyRate.currency_code == currency_code.upper())
            .order_by(CurrencyRate.date.desc())
        )
        rates = result.scalars().all()
        if not rates:
            raise HTTPException(status_code=404, detail="No rates found for this currency code")
        return rates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Добавить новый курс
@app.post("/currency-rates/", response_model=CurrencyRateSchema)
async def create_currency_rate(rate: CurrencyRateSchema, db: AsyncSession = Depends(get_db)):
    try:
        new_rate = CurrencyRate(**rate.model_dump())
        db.add(new_rate)
        await db.commit()
        await db.refresh(new_rate)
        return new_rate
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Удалить курс по id
@app.delete("/currency-rates/{rate_id}")
async def delete_currency_rate(rate_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CurrencyRate).where(CurrencyRate.id == rate_id))
        rate = result.scalars().first()
        if not rate:
            raise HTTPException(status_code=404, detail="Rate not found")
        await db.delete(rate)
        await db.commit()
        return {"message": "Rate deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#BD - MyStrngPsswrd1
