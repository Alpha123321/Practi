from datetime import date, datetime
import aiohttp
from fastapi import HTTPException
from lxml import etree
import logging

logger = logging.getLogger(__name__)

async def fetch_cbr_rates(target_date: date) -> list:
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={target_date.strftime('%d/%m/%Y')}"
    headers = {"User-Agent": "FastAPI Currency Service"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                # Упрощенная обработка кодировки
                xml_content = await response.text(encoding='windows-1251')
                return parse_xml(xml_content, target_date)
    except aiohttp.ClientError as e:
        logger.error(f"CBR request failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="CBR service unavailable"
        ) from e
    except Exception as e:
        logger.error(f"Error fetching rates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch currency rates"
        ) from e

def parse_xml(xml_content: str, fallback_date: date) -> list:
    try:
        # Упрощенный парсинг без двойного кодирования
        root = etree.fromstring(xml_content.encode('windows-1251'))
        rates = []

        date_str = root.get('Date')
        parsed_date = fallback_date
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}, using fallback")

        for valute in root.findall('Valute'):
            try:
                char_code = valute.find('CharCode').text
                name = valute.find('Name').text
                nominal = valute.find('Nominal').text
                value = valute.find('Value').text

                if not char_code or not value:
                    continue

                rates.append({
                    'date': parsed_date,
                    'currency_code': char_code.strip(),
                    'name': name.strip() if name else "",
                    'nominal': int(nominal) if nominal else 1,
                    'rate': float(value.replace(',', '.'))
                })
            except (AttributeError, ValueError, TypeError) as e:
                logger.error(f"Error parsing Valute: {str(e)}")
                continue

        logger.info(f"Parsed {len(rates)} currency rates")
        return rates
    except etree.XMLSyntaxError as e:
        logger.error(f"XML syntax error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Invalid XML response from CBR"
        ) from e
    except Exception as e:
        logger.error(f"XML parsing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to parse currency data"
        ) from e
