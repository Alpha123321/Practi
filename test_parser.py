import asyncio
import sys
import os
from datetime import date

# Добавляем путь к проекту в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Теперь импортируем функцию из app
from app.utils import fetch_cbr_rates


async def test_parser():
    try:
        print("Testing CBR parser...")
        rates = await fetch_cbr_rates(date.today())
        print(f"Success! Got {len(rates)} currency rates")

        # Проверяем несколько валют
        currencies_to_check = ["USD", "EUR", "CNY", "JPY"]
        for currency in currencies_to_check:
            currency_data = next((r for r in rates if r['currency_code'] == currency), None)
            if currency_data:
                print(f"{currency}: {currency_data['rate']} (nominal: {currency_data['nominal']})")
            else:
                print(f"{currency} not found in results")

        # Проверяем типы данных
        sample = next(iter(rates), None)
        if sample:
            print("\nSample rate structure:")
            print(f"Date: {type(sample['date']).__name__}, value: {sample['date']}")
            print(f"Currency code: {type(sample['currency_code']).__name__}, value: {sample['currency_code']}")
            print(f"Nominal: {type(sample['nominal']).__name__}, value: {sample['nominal']}")
            print(f"Rate: {type(sample['rate']).__name__}, value: {sample['rate']}")

        return True
    except Exception as e:
        print(f"Parser test failed: {str(e)}")
        return False


if __name__ == "__main__":
    asyncio.run(test_parser())