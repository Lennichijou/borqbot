from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, URLInputFile
import asyncio
import logging
from parser import get_quote, get_abyss_quote, get_strip_info, get_random_quote, get_random_strip, NoNumberError
from config import TELEGRAM_BOT_TOKEN


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.DEBUG)


def get_argument(message):
    if len(message.split()) > 1:
        return message.split()[1]
    else:
        raise NoNumberError


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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())