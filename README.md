# borqbot
Простенький Telegram-бот, выдающий по команде цитату/комикс из Цитатника Рунета (https://башорг.рф/)

# Установка
Для запуска требуется Python 3.11/3.12.

Клонируйте репозиторий:
```
git clone https://github.com/Lennichijou/borqbot.git
```
Установите библиотеки из файла ```requirements.txt```:
```
pip install -r requirements.txt
```
Создайте файл ```.env``` и в нём пропишите токен аутентификации, полученный в BotFather:
```
TELEGRAM_BOT_TOKEN=<YOUR_TOKEN>
```

Запустите в терминале:
```
python app.py
```
