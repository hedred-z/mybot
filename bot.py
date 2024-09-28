import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Включаем логирование
logging.basicConfig(filename='admin_logs.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь для хранения аккаунтов
user_accounts = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Добавить аккаунт", callback_data='add_account')],
        [InlineKeyboardButton("Управлять аккаунтами", callback_data='manage_accounts')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажмите кнопку ниже.", reply_markup=reply_markup)

# Обработчик для кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_account':
        await query.message.reply_text("Введите номер телефона:")
        return
    elif query.data == 'manage_accounts':
        await manage_accounts(update, context)
        return

    # Обработка ввода номера телефона
    if query.message.text and query.message.text.isdigit():
        phone_number = query.message.text
        user_accounts[query.from_user.id] = {"phone": phone_number}
        logger.info(f"{query.from_user.username}: Добавил аккаунт: {phone_number}")
        await query.message.reply_text(f"Код был отправлен на номер: {phone_number}. Введите код:")
        return

    # Здесь добавьте логику для ввода кода и пароля

async def manage_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_accounts:
        accounts = user_accounts[user_id]
        await update.message.reply_text(f"Ваши аккаунты: {accounts['phone']}")
    else:
        await update.message.reply_text("У вас нет добавленных аккаунтов.")

def main():
    application = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

    # Обработчики команд и кнопок
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
    
