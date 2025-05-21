from bs4 import BeautifulSoup
import requests, random, re, time


with open('src/strip_ids.txt', 'r') as file:
    strip_ids = file.read().split()
    file.close()


ERROR_MESSAGE = "Сейчас Цитатник недоступен. Повторите попытку позже."
NO_STRIP_MESSAGE = "Такого стрипа здесь нет."


class NoStripError(Exception):
    pass


class NotAvailableError(Exception):
    pass


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


def get_quote(number):
    url = f"https://башорг.рф/quote/{number}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        quote = soup.find('div', 'quote__body')
        quote_out = (str(quote).replace('<br/>', '\n')
                     .replace('<br>', '\n')
                     .replace(('<div class="quote__body">'), '')
                     .replace('</div>', '')
                     .replace('&lt;', '<')
                     .replace('&gt;', '>'))
        soup = BeautifulSoup(quote_out, 'html.parser')
        for tag in soup.find_all('div', class_='quote__strips'):
            tag.decompose()
        quote_complete = soup.get_text()
        if not quote_complete.strip() == '':
            return str(quote_complete.strip())
        else:
            return "Такой цитаты здесь нет. Попробуйте другой номер."
    else:
        raise NotAvailableError


def get_random_quote():
    url = 'https://башорг.рф'
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
                             .replace('</div>', '')
                             .replace('&lt;', '<')
                             .replace('&gt;', '>'))
                soup = BeautifulSoup(quote_out, 'html.parser')
                for tag in soup.find_all('div', class_='quote__strips'):
                    tag.decompose()
                quote_complete = soup.get_text()
                if not quote_complete.strip() == '':
                    quote_check = True
        return f'{str(quote_complete.strip())}\n\n#{num}'
    else:
        raise NotAvailableError


def get_strip_url(date):
    if date in strip_ids:
        url = "https://башорг.рф/strip/" + date
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            strip = soup.find('img', 'quote__img')['data-src']
            strip_url = f'https://башорг.рф{str(strip)}'
            author = " ".join(soup.find('div', 'quote__author').get_text().split())
            return strip_url, author
        else:
            raise NotAvailableError
    else:
        raise NoStripError


def get_random_strip():
    number = random.choice(strip_ids)
    strip_url, author = get_strip_url(number)
    return strip_url, author

