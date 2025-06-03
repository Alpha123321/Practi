from fastapi import FastAPI, Depends, HTTPException
from datetime import date
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session, init_db
from app.crud import get_rates_by_date, save_rates
from app.utils import fetch_cbr_rates  # Исправлен импорт
from app.schemas import CurrencyRateSchema  # Исправлен импорт

from app.crud import get_rates_by_date


@app.on_event("startup")
async def startup_event():
    await update_currency_rates()  # или без await, если функция синхронная

# Современный подход к инициализации через lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при запуске
    await init_db()
    yield
    # Cleanup при завершении (если нужен)

app = FastAPI(lifespan=lifespan)

async def get_db() -> AsyncSession:
    """Генератор сессий для внедрения зависимостей"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Приложение работает!"}

@app.get("/exchange-rates", response_model=list[CurrencyRateSchema])
async def get_exchange_rates(db: AsyncSession = Depends(get_db)):
    """Основной эндпоинт для получения курсов валют"""
    today = date.today()

    # Проверка наличия данных в БД
    existing_rates = await get_rates_by_date(db, today)
    if existing_rates:
        return existing_rates

    try:
        # Получение данных из ЦБ РФ
        new_rates = await fetch_cbr_rates(today)
    except Exception as e:
        # Обработка ошибок при получении данных
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения данных: {str(e)}"
        )

    # Сохранение данных в БД
    await save_rates(db, new_rates)

    # Получаем сохраненные данные для возврата
    saved_rates = await get_rates_by_date(db, today)
    return saved_rates

#DB - 'MyStrngPsswrd1'