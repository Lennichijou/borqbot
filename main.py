import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, URLInputFile
import asyncio
import aiohttp
import random
import sqlite3
from bs4 import BeautifulSoup
import logging
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(filename='main.log', level=logging.INFO)

bot: Bot
conn: aiosqlite.Connection
session: aiohttp.ClientSession
dp: Dispatcher

ERROR_MESSAGE = "Сейчас Цитатник недоступен. Повторите попытку позже."
NO_CONTENT_MESSAGE = "Такой цитаты/стрипа здесь нет."
NO_NUM_MESSAGE = 'Отсутствует номер цитаты/стрипа.'
BASE_URL = "https://xn--80abh7bk0c.xn--p1ai"
STRIPS_ID_LIST = "strip_ids.txt"
DB_PATH = "quotes.db"
logger = logging.getLogger(__name__)

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

async def init_db():
    await conn.execute("PRAGMA journal_mode = WAL")
    await conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id TEXT NOT NULL,
                text TEXT NOT NULL,
                UNIQUE(quote_id, text)
            )
        """)
    await conn.execute("""
            CREATE TABLE IF NOT EXISTS strips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strip_id TEXT NOT NULL,
                link TEXT NOT NULL,
                description TEXT NOT NULL,
                UNIQUE(strip_id, link, description)
                    )
                """)
    logger.info(f"Called/created a database.")
    await conn.commit()


async def db_add_quote(quote_id, text):
    try:
        await conn.execute(
            "INSERT INTO quotes (quote_id, text) VALUES (?, ?)",
            (quote_id, text)
        )
        await conn.commit()
        logger.info(f"Added a quote: {quote_id}.")
    except sqlite3.IntegrityError:
        pass


async def db_get_quote(quote_id):
    cursor = await conn.execute("""
        SELECT text FROM quotes
            WHERE quote_id = ?
    """, (quote_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    logger.info(f"Called a quote: {quote_id}.")
    return row[0]


async def db_add_strip(strip_id, link, desc):
    try:
        await conn.execute(
            "INSERT INTO strips (strip_id, link, description) VALUES (?, ?, ?)",
            (strip_id, link, desc)
        )
        await conn.commit()
        logger.info(f"Added a strip: {strip_id}.")
    except sqlite3.IntegrityError:
        pass

async def db_get_strip(strip_id):
    cursor = await conn.execute("""
        SELECT link, description FROM strips
        WHERE strip_id = ?
    """, (strip_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    link, desc = row
    logger.info(f"Called a strip: {strip_id}.")
    return link, desc

async def get_quote(quote_id):
    answer = await db_get_quote(quote_id)
    if answer:
        logger.info(f"Called a quote from database: {quote_id}")
        return answer
    url =  f"{BASE_URL}/quote/{quote_id}"
    async with session.get(url) as response:
        if response.status != 200:
            raise NoConnectionError
        html = await response.text()
        response.close()
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
    async with session.get(url) as response:
        if response.status != 200:
            raise NoConnectionError
        html = await response.text()
        response.close()
    soup = BeautifulSoup(html, 'html.parser')
    quote = soup.find('div', class_='quote__body')
    for tag in quote.find_all('div'):
        tag.decompose()
    for tag in quote.find_all('br'):
        tag.replace_with("\n")
    quote_complete = quote.get_text()
    return str(quote_complete.strip())

async def get_strip_info(number):
    with open(STRIPS_ID_LIST, 'r') as file:
        strip_ids = file.read().split()
        file.close()
    if number not in strip_ids:
        raise NoContentError
    answer = await db_get_strip(number)
    if answer:
        logger.info(f"Called a strip from database: {number}")
        strip_url, author = answer
        return strip_url, author
    url = f"{BASE_URL}/strip/{number}"
    async with session.get(url) as response:
        if response.status != 200:
            raise NoConnectionError
        html = await response.text()
        response.close()
    soup = BeautifulSoup(html, 'html.parser')
    s = soup.find('img', class_='quote__img')['data-src']
    strip_url = f'{BASE_URL}{str(s)}'
    author = " ".join(soup.find('div', class_='quote__author').get_text().split())
    await db_add_strip(number, strip_url, author)
    return strip_url, author

async def get_random_quote():
    url = BASE_URL
    async with session.get(url) as response:
        if response.status != 200:
            raise NoConnectionError
        html = await response.text()
        response.close()
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
    with open(STRIPS_ID_LIST, 'r') as file:
        strip_ids = file.read().split()
        file.close()
    number = random.choice(strip_ids)
    strip_url, author = await get_strip_info(number)
    return strip_url, author


async def main():
    global conn, session, bot, dp

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    session = aiohttp.ClientSession(timeout=timeout)
    conn = await aiosqlite.connect(DB_PATH)

    @dp.startup()
    async def on_startup():
        await init_db()

    @dp.message(Command("start", "help"))
    async def start(message: Message):
        await message.answer('/quote + номер цитаты - получить цитату под этим номером.\n'
                             '/random_quote - получить случайную цитату.\n'
                             '/strip + YYYYMMDD - получить комикс, опубликованный в эту дату, если он есть.\n'
                             '/random_strip - получить случайный комикс.\n'
                             '/abyss - случайная цитата из "Бездны".')

    @dp.message(Command("quote"))
    async def quote(message: Message):
        try:
            quote_id = get_argument(message.text)
            quote_data = await get_quote(quote_id)
            await message.answer(quote_data)
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

    @dp.message(Command("abyss"))
    async def abyss(message: Message):
        try:
            abyss_quote = await get_abyss_quote()
            await message.answer(abyss_quote)
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

    @dp.message(Command("strip"))
    async def strip(message: Message):
        try:
            strip_id = get_argument(message.text)
            strip_url, author = await get_strip_info(strip_id)
            image = URLInputFile(strip_url)
            await message.answer_photo(image, caption=author)
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

    @dp.message(Command("random_quote"))
    async def random_quote(message: Message):
        try:
            result = await get_random_quote()
            await message.answer(result)
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

    @dp.message(Command("random_strip"))
    async def random_strip(message: Message):
        try:
            strip_url, author = await get_random_strip()
            image = URLInputFile(strip_url)
            await message.answer_photo(image, caption=author)
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())