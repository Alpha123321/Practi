
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import logging
import traceback
import sys

from app.database import init_db, shutdown_db, get_db
from app.crud import get_rates_by_date, save_rates
from app.schemas import CurrencyRateSchema
from app.utils import fetch_cbr_rates

#логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


#обработчик ошибок для отладки
@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(f"Unhandled exception: {tb}")
    return HTTPException(
        status_code=500,
        detail=f"Internal Server Error: {str(exc)}"
    )


@app.on_event("startup")
async def startup():
    try:
        await init_db()
        logger.info("Service started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown():
    try:
        await shutdown_db()
        logger.info("Service stopped gracefully")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")


@app.get("/exchange-rates", response_model=list[CurrencyRateSchema])
async def get_exchange_rates(db: AsyncSession = Depends(get_db)):
    today = date.today()
    logger.info(f"Request for exchange rates on {today}")

    try:
        # 1. Проверяем наличие данных в БД
        existing_rates = await get_rates_by_date(db, today)
        if existing_rates:
            logger.info(f"Returning {len(existing_rates)} rates from database")
            return existing_rates

        logger.info("No rates in DB, fetching from CBR")

        # 2. просим данные у цб
        new_rates = await fetch_cbr_rates(today)
        if not new_rates:
            logger.warning("No rates received from CBR")
            return []

        logger.info(f"Received {len(new_rates)} rates from CBR")

        # сохр в бд
        saved_count = await save_rates(db, new_rates)
        logger.info(f"Saved {saved_count} new rates to database")

        # выводим из бд
        db_rates = await get_rates_by_date(db, today)
        return db_rates if db_rates else []

    except Exception as e:
        logger.exception("Unhandled error in get_exchange_rates")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )

#BD - MyStrngPsswrd1
