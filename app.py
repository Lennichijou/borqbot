import telebot
import logging
from bs4 import BeautifulSoup
import requests, random, re, time
#from aiogram import Bot, Dispatcher, executor, types
from config import TELEGRAM_BOT_TOKEN
from functions import *
from io import BytesIO

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
logging.basicConfig(level=logging.DEBUG)

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
                                          '/random_strip - получить случайный комикс.\n'
                                          '/abyss - случайная цитата из "Бездны".')


@bot.message_handler(commands=["strip"])
def strip(message):
    try:
        date = get_argument(message.text)
        strip_url, author = get_strip_url(date)
        if strip_url == ERROR_MESSAGE or strip_url == NO_STRIP_MESSAGE:
            bot.send_message(message.chat.id, strip_url)
        else:
            image_data = BytesIO(requests.get(strip_url).content)
            bot.send_photo(message.chat.id, image_data, caption=author)
    except IndexError:
        bot.send_message(message.chat.id, NO_NUM_MESSAGE)


@bot.message_handler(commands=["quote"])
def quote(message):
    try:
        number = get_argument(message.text)
        q = get_quote(number)
        bot.send_message(message.chat.id, q)
    except IndexError:
        bot.send_message(message.chat.id, 'Не хватает номера! Введите команду с номером нужной цитаты.')


@bot.message_handler(commands=["random_quote"])
def random_quote(message):
    q = get_random_quote()
    bot.send_message(message.chat.id, q)


@bot.message_handler(commands=["random_strip"])
def random_strip(message):
    strip_url, author = get_random_strip()
    if strip_url == ERROR_MESSAGE or strip_url == NO_STRIP_MESSAGE:
        bot.send_message(message.chat.id, strip_url)
    else:
        image_data = BytesIO(requests.get(strip_url).content)
        bot.send_photo(message.chat.id, image_data, caption=author)


@bot.message_handler(commands=['abyss'])
def abyss_q(message):
    q = get_abyss_quote()
    bot.send_message(message.chat.id, q)


bot.infinity_polling()
