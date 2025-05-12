import telebot
from bs4 import BeautifulSoup
import requests, random, re, time
from config import TELEGRAM_BOT_TOKEN


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_quote():
    url = 'https://башорг.рф'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        last_quote_number = int(str(soup.find('a', attrs={"class": "quote__header_permalink"}).getText())[1:])
        quote_check = False
        while not quote_check:
            num = random.randint(1, last_quote_number)
            url = f"https://башорг.рф/quote/{num}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                quote = soup.find('div', 'quote__body')
                quote_out = (str(quote).replace('<br/>', '\n')
                              .replace('<br>', '\n')
                              .replace(('<div class="quote__body">'), '')
                              .replace('</div>','')
                              .replace('&lt;', '<')
                              .replace('&gt;', '>'))
                quote_complete = re.sub('<div class="quote__strips" data-debug="1">\w+<\/div>', '', quote_out)
                if not quote_complete.strip() == '':
                    quote_check = True
        return str(quote_complete.strip())
    else:
        return "Сейчас Цитатник недоступен. Повторите попытку позже."

@bot.message_handler(commands=["start"])
def start(m, res=False):
        bot.send_message(m.chat.id, 'Чтобы получить случайную цитату с башорг.рф, введите команду /quote.')

@bot.message_handler(commands=["quote"])
def quote(m, res=False):
    q = get_quote()
    bot.send_message(m.chat.id, q)

bot.polling()
