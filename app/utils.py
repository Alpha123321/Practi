from datetime import date
import aiohttp
from lxml import etree


async def fetch_cbr_rates(target_date: date) -> list:
    """Получение данных с сайта ЦБ РФ"""
    # Форматируем URL с указанием даты
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={target_date.strftime('%d/%m/%Y')}"

    # Асинхронный HTTP-запрос с правильной обработкой кодировки
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Получаем сырые байты для правильной обработки кодировки
            xml_bytes = await response.read()
            return parse_xml(xml_bytes, target_date)


def parse_xml(xml_content: bytes, target_date: date) -> list:
    """Парсинг XML-ответа от ЦБ РФ"""
    try:
        # Попытка парсинга с указанием кодировки windows-1251
        xml_str = xml_content.decode('windows-1251')
        root = etree.fromstring(xml_str.encode('utf-8'))
    except UnicodeDecodeError:
        # Fallback на utf-8 если windows-1251 не работает
        root = etree.fromstring(xml_content)

    rates = []
    for valute in root.findall('Valute'):
        # Извлечение данных о валюте с проверкой наличия элементов
        char_code = valute.find('CharCode')
        name = valute.find('Name')
        nominal = valute.find('Nominal')
        value = valute.find('Value')

        if all([char_code is not None, name is not None, nominal is not None, value is not None]):
            rates.append({
                'date': target_date,
                'currency_code': char_code.text,
                'name': name.text,
                'nominal': int(nominal.text),
                # Преобразование разделителя дробей из запятой в точку
                'rate': float(value.text.replace(',', '.'))
            })

    return rates
