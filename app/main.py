from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import logging
import traceback

from app.database import init_db, shutdown_db, get_db
from app.crud import get_rates_by_date, save_rates
from app.schemas import CurrencyRateSchema
from app.utils import fetch_cbr_rates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await init_db()
        logger.info("Service started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

    yield

    # Shutdown
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


# Удаляем кастомный openapi.json endpoint - FastAPI создаст его автоматически

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
        # 1. Проверяем наличие данных в БД
        existing_rates = await get_rates_by_date(db, today)
        if existing_rates:
            logger.info(f"Returning {len(existing_rates)} rates from database")
            return existing_rates

        logger.info("No rates in DB, fetching from CBR")

        # 2. Запрашиваем данные у ЦБ
        new_rates = await fetch_cbr_rates(today)
        if not new_rates:
            logger.warning("No rates received from CBR")
            raise HTTPException(
                status_code=404,
                detail="Currency rates not available"
            )

        logger.info(f"Received {len(new_rates)} rates from CBR")

        # 3. Сохраняем в БД
        saved_count = await save_rates(db, new_rates)
        logger.info(f"Saved {saved_count} new rates to database")

        # 4. Возвращаем данные из БД
        db_rates = await get_rates_by_date(db, today)
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


@app.get("/")
async def root():
    return {"message": "Currency API is running"}

#BD - MyStrngPsswrd1
