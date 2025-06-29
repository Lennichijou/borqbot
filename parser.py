import random
import aiohttp
from bs4 import BeautifulSoup

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

async def get_quote(quote_id):
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
                return f'{str(quote_complete.strip())}\n\n#{quote_id}'
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
    else:
        url = f"{BASE_URL}/strip/{number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise NoConnectionError
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                strip = soup.find('img', class_='quote__img')['data-src']
                strip_url = f'https://xn--80abh7bk0c.xn--p1ai{str(strip)}'
                author = " ".join(soup.find('div', class_='quote__author').get_text().split())
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