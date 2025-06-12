from datetime import date, datetime
import aiohttp
from fastapi import HTTPException
from lxml import etree
import logging
import xml.etree.ElementTree as ET


logger = logging.getLogger(__name__)


async def fetch_cbr_rates(target_date: date) -> list[dict]:
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={target_date.strftime('%d/%m/%Y')}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return []

            text = await response.text()

    try:
        root = ET.fromstring(text)
        date_str = root.attrib.get('Date')
        cbr_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except Exception:
        return []

    rates = []
    for valute in root.findall('Valute'):
        try:
            char_code = valute.find('CharCode').text
            name = valute.find('Name').text
            nominal = int(valute.find('Nominal').text)
            rate_str = valute.find('Value').text.replace(',', '.')
            rate = float(rate_str)
        except Exception:
            continue

        rates.append({
            'date': cbr_date,
            'currency_code': char_code,
            'name': name,
            'rate': rate,
            'nominal': nominal,
        })

    return rates
def parse_xml(xml_content: str, fallback_date: date) -> list:
    try:
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
