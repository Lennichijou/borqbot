import random
import aiohttp
from bs4 import BeautifulSoup
from database import db_get_quote, db_add_quote, db_get_strip, db_add_strip
import logging

ERROR_MESSAGE = "Сейчас Цитатник недоступен. Повторите попытку позже."
NO_CONTENT_MESSAGE = "Такой цитаты/стрипа здесь нет."
NO_NUM_MESSAGE = 'Отсутствует номер цитаты/стрипа.'
BASE_URL = "https://xn--80abh7bk0c.xn--p1ai"

class NoConnectionError(Exception):
    def __init__(self, message=ERROR_MESSAGE):
        self.message = message
        super().__init__(self.message)

class NoNumberError(Exception):
    def __init__(self, message=NO_NUM_MESSAGE):
        self.message = message
        super().__init__(self.message)

class NoContentError(Exception):
    def __init__(self, message=NO_CONTENT_MESSAGE):
        self.message = message
        super().__init__(self.message)

def get_argument(message):
    if len(message.split()) > 1:
        return message.split()[1]
    else:
        raise NoNumberError

async def get_quote(quote_id):
    answer = await db_get_quote(quote_id)
    if answer:
        logging.getLogger(__name__).info(f"Called a quote from database: {quote_id}")
        return answer
    else:
        url =  f"{BASE_URL}/quote/{quote_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise NoConnectionError
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                quote = soup.find('div', class_='quote__body')
                for tag in quote.find_all('div'):
                    tag.decompose()
                for tag in quote.find_all('br'):
                    tag.replace_with("\n")
                quote_complete = quote.get_text()
                if not quote_complete.strip() == '':
                    result = f'{str(quote_complete.strip())}\n\n#{quote_id}'
                    await db_add_quote(quote_id, result)
                    return result
                else:
                    raise NoContentError

async def get_abyss_quote():
    url = f"{BASE_URL}/abyss"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise NoConnectionError
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            quote = soup.find('div', class_='quote__body')
            for tag in quote.find_all('div'):
                tag.decompose()
            for tag in quote.find_all('br'):
                tag.replace_with("\n")
            quote_complete = quote.get_text()
            return str(quote_complete.strip())

async def get_strip_info(number):
    with open('src/strip_ids.txt', 'r') as file:
        strip_ids = file.read().split()
        file.close()
    if number not in strip_ids:
        raise NoContentError
    answer = await db_get_strip(number)
    if answer:
        logging.getLogger(__name__).info(f"Called a strip from database: {number}")
        strip_url, author = answer
        return strip_url, author
    else:
        url = f"{BASE_URL}/strip/{number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise NoConnectionError
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                strip = soup.find('img', class_='quote__img')['data-src']
                strip_url = f'{BASE_URL}{str(strip)}'
                author = " ".join(soup.find('div', class_='quote__author').get_text().split())
                await db_add_strip(number, strip_url, author)
                return strip_url, author

async def get_random_quote():
    url = BASE_URL
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise NoConnectionError
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            last_quote_number = int(str(soup.find('a', class_="quote__header_permalink").get_text())[1:])
            while True:
                try:
                    q = await get_quote(random.randint(1, last_quote_number))
                except NoContentError:
                    continue
                else:
                    return q

async def get_random_strip():
    with open('src/strip_ids.txt', 'r') as file:
        strip_ids = file.read().split()
        file.close()
    number = random.choice(strip_ids)
    strip_url, author = await get_strip_info(number)
    return strip_url, author