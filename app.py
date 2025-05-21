import telebot
from bs4 import BeautifulSoup
import requests, random, re, time
from config import TELEGRAM_BOT_TOKEN
from functions import *
from io import BytesIO

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def get_argument(arg):
    if len(arg) > 1:
        return arg.split()[1]
    else:
        pass


@bot.message_handler(commands=["start", "help"])
def start(message, res=False):
        bot.send_message(message.chat.id, '/quote + номер цитаты - получить цитату под этим номером.\n'
                                    '/random_quote - получить случайную цитату.\n'
                                    '/strip + YYYYMMDD - получить комикс, опубликованный в эту дату, если он есть.\n'
                                          '/random_strip - получить случайный комикс')


@bot.message_handler(commands=["strip"])
def strip(message):
    try:
        number = get_argument(message.text)
        strip_url, author = get_random_strip()
        image_data = BytesIO(requests.get(strip_url).content)
        bot.send_photo(message.chat.id, image_data, caption=author)
    except IndexError:
        bot.send_message(message.chat.id, 'Не хватает номера!')
    except NoStripError:
        bot.send_message(message.chat.id, NO_STRIP_MESSAGE)


@bot.message_handler(commands=["quote"])
def quote(message):
    try:
        number = get_argument(message.text)
        q = get_quote(number)
        bot.send_message(message.chat.id, q)
    except IndexError:
        bot.send_message(message.chat.id, 'Не хватает номера! Вместе с командой /quote вводится номер цитаты.')
    except NotAvailableError:
        bot.send_message(message.chat.id, ERROR_MESSAGE)


@bot.message_handler(commands=["random_quote"])
def random_quote(message):
    try:
        q = get_random_quote()
        bot.send_message(message.chat.id, q)
    except NotAvailableError:
        bot.send_message(message.chat.id, ERROR_MESSAGE)


@bot.message_handler(commands=["random_strip"])
def random_strip(message):
    try:
        strip_url, author = get_random_strip()
        image_data = BytesIO(requests.get(strip_url).content)
        bot.send_photo(message.chat.id, image_data, caption=author)
    except NotAvailableError:
        bot.send_message(message.chat.id, ERROR_MESSAGE)


bot.polling()
