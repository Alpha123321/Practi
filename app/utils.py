#import datetime
import datetime

import aiohttp
from lxml import etree
import logging

logger = logging.getLogger(__name__)

async def fetch_cbr_rates(target_date: datetime.date) -> list:
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={target_date.strftime('%d/%m/%Y')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                xml_bytes = await response.read()
                return parse_xml(xml_bytes, target_date)
    except aiohttp.ClientError as e:
        logger.error(f"CBR request failed: {str(e)}")
        raise


def parse_xml(xml_content: bytes, target_date: datetime.date) -> list:
    try:
        parser = etree.XMLParser(encoding='windows-1251')
        root = etree.fromstring(xml_content, parser=parser)
        rates = []

        date_str = root.get('Date')
        parsed_date = target_date
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            except ValueError:
                pass

        for valute in root.findall('Valute'):
            try:
                rates.append({
                    'date': parsed_date,
                    'currency_code': valute.find('CharCode').text.strip(),
                    'name': valute.find('Name').text.strip(),
                    'nominal': int(valute.find('Nominal').text),
                    'rate': float(valute.find('Value').text.replace(',', '.'))
                })
            except (AttributeError, ValueError) as e:
                logger.error(f"Error parsing Valute: {str(e)}")
                continue

        return rates
    except etree.XMLSyntaxError as e:
        logger.error(f"XML syntax error: {str(e)}")
        raise
