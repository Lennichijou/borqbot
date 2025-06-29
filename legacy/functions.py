from bs4 import BeautifulSoup
import requests, random, re, time


with open('src/strip_ids.txt', 'r') as file:
    strip_ids = file.read().split()
    file.close()


ERROR_MESSAGE = "Сейчас Цитатник недоступен. Повторите попытку позже."
NO_STRIP_MESSAGE = "Такого стрипа здесь нет."
NO_QUOTE_MESSAGE = "Такой цитаты здесь нет. Попробуйте другой номер."
NO_NUM_MESSAGE = 'Не хватает номера!'


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


def get_quote(number):
    url = f"https://xn--80abh7bk0c.xn--p1ai/quote/{number}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        quote = soup.find('div', class_='quote__body')
        for tag in quote.find_all('div'):
            tag.decompose()
        for tag in quote.find_all('br'):
            tag.replace_with("\n")
        quote_complete = quote.get_text()
        if not quote_complete.strip() == '':
            return f'{str(quote_complete.strip())}\n\n#{number}'
        else:
            return NO_QUOTE_MESSAGE
    else:
        return ERROR_MESSAGE


def get_random_quote():
    url = 'https://xn--80abh7bk0c.xn--p1ai/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        last_quote_number = int(str(soup.find('a', attrs={"class": "quote__header_permalink"}).getText())[1:])
        while True:
            num = random.randint(1, last_quote_number)
            quote = get_quote(num)
            if quote != NO_QUOTE_MESSAGE:
                return quote
    else:
        return ERROR_MESSAGE


def get_abyss_quote():
    url = "https://xn--80abh7bk0c.xn--p1ai/abyss"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        quote = soup.find('div', class_='quote__body')
        for tag in quote.find_all('div'):
            tag.decompose()
        for tag in quote.find_all('br'):
            tag.replace_with("\n")
        quote_complete = quote.get_text()
        return f'{str(quote_complete.strip())}'
    else:
        return ERROR_MESSAGE


def get_strip_url(date):
    if date in strip_ids:
        url = "https://xn--80abh7bk0c.xn--p1ai/strip/" + date
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            strip = soup.find('img', 'quote__img')['data-src']
            strip_url = f'https://xn--80abh7bk0c.xn--p1ai{str(strip)}'
            author = " ".join(soup.find('div', 'quote__author').get_text().split())
            return strip_url, author
        else:
            return ERROR_MESSAGE, None
    else:
        return NO_STRIP_MESSAGE, None


def get_random_strip():
    number = random.choice(strip_ids)
    strip_url, author = get_strip_url(number)
    return strip_url, author

