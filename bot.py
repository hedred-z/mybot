import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import os

API_TOKEN = '6760012279:AAGfY1w2LR7TuY1r_mbMXIyLlscrai2oT28'  # Твой API токен

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ID администратора
ADMIN_ID = 954053674  # Твой ID

# Логи
LOG_FILE = 'logs.txt'

# Запись логов
def log_action(action):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(action + '\n')

# Проверка админа
def is_admin(user_id):
    return user_id == ADMIN_ID

# Подключение к базе данных
conn = sqlite3.connect('accounts.db')
cursor = conn.cursor()

# Создание таблиц, если их нет
cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    password TEXT,
    status TEXT DEFAULT 'active'
)''')
conn.commit()

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    add_account_btn = KeyboardButton("➕ Добавить аккаунт")
    
    if is_admin(message.from_user.id):
        download_logs_btn = KeyboardButton("📄 Скачать логи")
        markup.add(download_logs_btn)

    markup.add(add_account_btn)
    await message.answer("Выберите действие:", reply_markup=markup)

# Добавление аккаунта
@dp.message_handler(lambda message: message.text == "➕ Добавить аккаунт")
async def add_account(message: types.Message):
    await message.answer("Введите номер телефона:")

    @dp.message_handler()
    async def get_phone(message: types.Message):
        phone = message.text
        cursor.execute("INSERT INTO accounts (phone) VALUES (?)", (phone,))
        conn.commit()
        log_action(f"{message.from_user.username}: Добавил аккаунт: {phone}")
        await message.answer("Аккаунт добавлен")

# Скачивание логов (только администратор)
@dp.message_handler(lambda message: message.text == "📄 Скачать логи")
async def send_logs(message: types.Message):
    if is_admin(message.from_user.id):
        with open(LOG_FILE, 'rb') as log_file:
            await bot.send_document(message.chat.id, log_file)
    else:
        await message.answer("У вас нет доступа.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
