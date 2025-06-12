from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
import logging
import traceback

from app.database import init_db, shutdown_db, get_db
from app.crud import get_rates_by_date, save_rates
from app.schemas import CurrencyRateSchema
from app.utils import fetch_cbr_rates
from app.models import CurrencyRate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("Service started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

    yield

    try:
        await shutdown_db()
        logger.info("Service stopped gracefully")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

app = FastAPI(
    title="Currency API",
    description="Сервис для получения курсов валют ЦБ РФ",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

@app.get("/exchange-rates", response_model=list[CurrencyRateSchema])
async def get_exchange_rates(db: AsyncSession = Depends(get_db)):
    today = date.today()
    logger.info(f"Request for exchange rates on {today}")

    try:
        # Сначала пытаемся получить курсы из базы по сегодняшней дате
        existing_rates = await get_rates_by_date(db, today)
        if existing_rates:
            logger.info(f"Returning {len(existing_rates)} rates from database for date {today}")
            return existing_rates

        logger.info("No rates found in DB, fetching from CBR")

        new_rates = await fetch_cbr_rates(today)
        logger.info(f"Received {len(new_rates)} rates from CBR")

        if not new_rates:
            logger.warning("No rates received from CBR")
            raise HTTPException(
                status_code=404,
                detail="Currency rates not available"
            )

        # Логируем дату из данных ЦБР
        first_date = new_rates[0]['date']
        logger.info(f"Date in fetched rates: {first_date}")

        # Сохраняем курсы в базе
        saved_count = await save_rates(db, new_rates)
        logger.info(f"Upserted {saved_count} currency rates")

        # Используем дату из данных для чтения из базы
        db_rates = await get_rates_by_date(db, first_date)
        logger.info(f"Rates fetched after save: {len(db_rates)} for date {first_date}")

        if not db_rates:
            logger.error("Saved rates not found in database")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve saved rates"
            )

        return db_rates

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error in get_exchange_rates")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/exchange-rates/{currency_code}", response_model=CurrencyRateSchema)
async def get_exchange_rate(
    currency_code: str,
    date: date = Query(default=date.today()),
    db: AsyncSession = Depends(get_db)
):
    currency_code = currency_code.upper()
    logger.info(f"Request for rate of {currency_code} on {date}")

    try:
        result = await db.execute(
            select(CurrencyRate).where(
                CurrencyRate.currency_code == currency_code,
                CurrencyRate.date == date
            )
        )
        rate = result.scalars().first()
        if not rate:
            raise HTTPException(status_code=404, detail="Currency rate not found")

        return rate

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching currency rate")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    return {"message": "Currency API is running"}

#BD - MyStrngPsswrd1
