import re
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import logging

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = '8006041676:AAHz6ce50eCX6yxsN67ezHG3Z0QRSqCH5Zc'

# ID администраторов (можно добавлять несколько ID)
ADMIN_IDS = ['1668134488', '670358613']  # Замените на Telegram ID ваших администраторов

# Состояния разговора
ORDER, NAME, PHONE, PICKUP_DATETIME, CONFIRM, DISK_CHOICE = range(6)

# Список характеристик дисков
disk_choices = [
    "5x100R14", "5x100R15", "5x100R16", "5x114.3R14", "5x114.3R15", "5x114.3R16", "5x114.3R17",
    "4x100R14", "4x100R15", "4x100R16", "4x100R17"
]

# Восстановленный список товаров
catalog = [
    {"name": "Лот #0002", "price": 20000},
    {"name": "Лот #0003", "price": 20000},
    {"name": "Лот #0004", "price": 20000},
    {"name": "Лот #0005", "price": 20000},
    {"name": "Лот #0006", "price": 20000},
    {"name": "Лот #0007", "price": 20000},
    {"name": "Лот #0008", "price": 20000},
    {"name": "Лот #0009", "price": 22000},
    {"name": "Лот #0011", "price": 22000},
    {"name": "Лот #0012", "price": 22000},
    {"name": "Лот #0013", "price": 22000},
    {"name": "Лот #0014", "price": 22000},
    {"name": "Лот #0015", "price": 22000},
    {"name": "Лот #0016", "price": 24000},
    {"name": "Лот #0017", "price": 24000},
    {"name": "Лот #0018", "price": 18000},
    {"name": "Лот #0019", "price": 20000},
    {"name": "Лот #0020", "price": 18000},
    {"name": "Лот #0021", "price": 26000},
    {"name": "Лот #0022", "price": 26000},
    {"name": "Лот #0023", "price": 25000},
    {"name": "Лот #0024", "price": 26000},
    {"name": "Лот #0025", "price": 25000},
    {"name": "Лот #0026", "price": 25000},
    {"name": "Лот #0027", "price": 25000},
    {"name": "Лот #0028", "price": 20000},
    {"name": "Лот #0029", "price": 20000},
    {"name": "Лот #0030", "price": 25000},
    {"name": "Лот #0031", "price": 25000},
    {"name": "Лот #0032", "price": 30000},
    {"name": "Лот #0033", "price": 32000},
    {"name": "Лот #0034", "price": 30000},
    {"name": "Лот #0035", "price": 30000},
    {"name": "Лот #0036", "price": 30000},
    {"name": "Лот #0037", "price": 43000},
    {"name": "Лот #0038", "price": 43000},
    {"name": "Лот #0039", "price": 43000},
    {"name": "Лот #0040", "price": 40000},
    {"name": "Лот #0041", "price": 45000},
    {"name": "Лот #0042", "price": 32000},
    {"name": "Лот #0043", "price": 28000},
    {"name": "Лот #0044", "price": 28000},
    {"name": "Лот #0045", "price": 28000},
    {"name": "Лот #0046", "price": 28000},
    {"name": "Лот #0047", "price": 28000},
    {"name": "Лот #0048", "price": 28000},
    {"name": "Лот #0049", "price": 16000},
    {"name": "Лот #0050", "price": 28000},
    {"name": "Лот #0051", "price": 28000},
    {"name": "Лот #0052", "price": 20000},
    {"name": "Лот #0053", "price": 28000},
    {"name": "Лот #0054", "price": 28000},
    {"name": "Лот #0055", "price": 20000},
    {"name": "Лот #0056", "price": 28000},
    {"name": "Лот #0057", "price": 26000},
    {"name": "Лот #0058", "price": 28000},
    {"name": "Лот #0059", "price": 28000},
    {"name": "Лот #0060", "price": 28000},
    {"name": "Лот #0061", "price": 20000},
    {"name": "Лот #0062", "price": 20000},
    {"name": "Лот #0063", "price": 20000},
    {"name": "Лот #0064", "price": 20000},
    {"name": "Лот #0065", "price": 48000},
    {"name": "Лот #0066", "price": 18000},
    {"name": "Лот #0067", "price": 35000},
    {"name": "Лот #0068", "price": 18000},
    {"name": "Лот #0069", "price": 20000},
    {"name": "Лот #0070", "price": 35000},
    {"name": "Лот #0071", "price": 35000},
    {"name": "Лот #0072", "price": 36000},
    {"name": "Лот #0073", "price": 28000},
    {"name": "Лот #0074", "price": 20000},
    {"name": "Лот #0075", "price": 18000},
    {"name": "Лот #0076", "price": 42000},
    {"name": "Лот #0078", "price": 28000},
    {"name": "Лот #0079", "price": 40000},
    {"name": "Лот #0080", "price": 38000},
    {"name": "Лот #0081", "price": 18000},
    {"name": "Лот #0082", "price": 35000},
    {"name": "Лот #0083", "price": 30000},
    {"name": "Лот #0084", "price": 35000},
    {"name": "Лот #0085", "price": 25000},
    {"name": "Лот #0086", "price": 20000},
    {"name": "Лот #0087", "price": 35000},
    {"name": "Лот #0088", "price": 28000},
    {"name": "Лот #0089", "price": 25000},
    {"name": "Лот #0090", "price": 16000},
    {"name": "Лот #0091", "price": 32000},
    {"name": "Лот #0092", "price": 20000},
    {"name": "Лот #0093", "price": 55000},
    {"name": "Лот #0094", "price": 20000},
    {"name": "Лот #0095", "price": 35000},
    {"name": "Лот #0096", "price": 45000},
    {"name": "Лот #0097", "price": 35000},
    {"name": "Лот #0099", "price": 35000},
    {"name": "Лот #0100", "price": 35000},
    {"name": "Лот #0101", "price": 45000},
    {"name": "Лот #0102", "price": 45000},
    {"name": "Лот #0103", "price": 20000},
    {"name": "Лот #0104", "price": 25000},
    {"name": "Лот #0105", "price": 40000},
    {"name": "Лот #0106", "price": 40000},
    {"name": "Лот #0107", "price": 40000},
    {"name": "Лот #0108", "price": 40000},
    {"name": "Лот #0109", "price": 40000},
    {"name": "Лот #0110", "price": 40000},
    {"name": "Лот #0111", "price": 40000},
    {"name": "Лот #0112", "price": 40000},
    {"name": "Лот #0113", "price": 35000},
    {"name": "Лот #0114", "price": 20000},
    {"name": "Лот #0115", "price": 35000},
    {"name": "Лот #0116", "price": 35000},
    {"name": "Лот #0117", "price": 35000},
    {"name": "Лот #0118", "price": 35000},
    {"name": "Лот #0119", "price": 40000},
    {"name": "Лот #0120", "price": 35000},
    {"name": "Лот #0121", "price": 35000},
    {"name": "Лот #0122", "price": 35000},
    {"name": "Лот #0123", "price": 35000},
    {"name": "Лот #0124", "price": 20000},
    {"name": "Лот #0125", "price": 35000},
    {"name": "Лот #0126", "price": 35000},
    {"name": "Лот #0127", "price": 32000},
]


# Функция начала общения с ботом (обновлено с эмодзи)
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    first_name = user.first_name if user.first_name else 'пользователь'

    # Персонализированное приветствие с эмодзи
    message = f"Привет, {first_name}! 👋\nДобро пожаловать в наш магазин! 🛒\nВот наш каталог товаров:\n\n"

    # Отображаем все товары с эмодзи
    for i, item in enumerate(catalog, 1):
        message += f"➡️ <b>{i}</b>. {item['name']} - {item['price']} руб. 💰\n"

    message += "\nЧтобы оформить заказ, используйте команду /zakaz. 📝"

    await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([['/zakaz']], one_time_keyboard=True),
                                    parse_mode='HTML')


# Начало оформления заказа
async def zakaz(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Выберите товар из нашего каталога, который хотите заказать. Просто отправьте номер строки товара. 🔢"
    )
    return ORDER


# Обработка выбора товара
async def handle_order(update: Update, context: CallbackContext):
    try:
        item_index = int(update.message.text) - 1
        if 0 <= item_index < len(catalog):
            context.user_data['order'] = catalog[item_index]
            await update.message.reply_text(
                f"🎉 Вы выбрали {catalog[item_index]['name']} за {catalog[item_index]['price']} руб. 💸\n\nНапишите ваше имя и фамилию через пробел. 🧑‍💼"
            )
            return NAME
        else:
            await update.message.reply_text("❌ Неверный номер. Пожалуйста, выберите товар из списка.")
            return ORDER
    except ValueError:
        await update.message.reply_text("❗ Пожалуйста, отправьте номер товара.")
        return ORDER


# Запрос имени и фамилии
async def get_name(update: Update, context: CallbackContext):
    full_name = update.message.text.split()

    if len(full_name) == 2:
        first_name, last_name = full_name
        context.user_data['first_name'] = first_name
        context.user_data['last_name'] = last_name
        await update.message.reply_text("📞 Теперь напишите ваш контактный номер.")
        return PHONE
    else:
        await update.message.reply_text("❗ Пожалуйста, введите ваше имя и фамилию через пробел.")
        return NAME


# Валидация номера телефона
def validate_phone(phone: str) -> bool:
    phone_pattern = r'^\+?\d{10,12}$'
    return bool(re.match(phone_pattern, phone))


# Запрос телефона с валидацией
async def get_phone(update: Update, context: CallbackContext):
    phone = update.message.text
    if validate_phone(phone):
        context.user_data['phone'] = phone
        await update.message.reply_text(
            "⏰ Пожалуйста, укажите время, когда вы приедете за заказом (Образец: '01.01.2025 9:35')."
        )
        return PICKUP_DATETIME
    else:
        await update.message.reply_text("❗ Пожалуйста, введите корректный номер телефона.")
        return PHONE


# Валидация даты и времени
def validate_datetime(datetime_str: str) -> bool:
    datetime_pattern = r'^\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}$'
    return bool(re.match(datetime_pattern, datetime_str))


# Запрос даты и времени самовывоза
async def get_pickup_datetime(update: Update, context: CallbackContext):
    pickup_datetime = update.message.text
    if validate_datetime(pickup_datetime):
        context.user_data['pickup_datetime'] = pickup_datetime
        order = context.user_data['order']
        first_name = context.user_data['first_name']
        last_name = context.user_data['last_name']
        phone = context.user_data['phone']
        pickup_time = context.user_data['pickup_datetime']

        confirmation_message = f"✅ Ваш заказ:\n{order['name']} - {order['price']} руб. 💸\n\nИмя: {first_name} {last_name} 🧑‍💼\nТелефон: {phone} 📱\nВремя самовывоза: {pickup_time} ⏳\n\nПодтвердите заказ, отправив 'Да' ✅ или отмените его, отправив 'Отменить' ❌."

        await update.message.reply_text(confirmation_message,
                                        reply_markup=ReplyKeyboardMarkup([['Да', 'Отменить']], one_time_keyboard=True))
        return CONFIRM
    else:
        await update.message.reply_text("❗ Пожалуйста, введите дату и время самовывоза в формате: '01.01.2025 9:35'.")
        return PICKUP_DATETIME


# Подтверждение или отмена заказа
async def confirm_order(update: Update, context: CallbackContext):
    if update.message.text.lower() == 'да':
        order = context.user_data['order']
        first_name = context.user_data['first_name']
        last_name = context.user_data['last_name']
        phone = context.user_data['phone']
        pickup_time = context.user_data['pickup_datetime']

        user = update.message.from_user
        telegram_username = user.username if user.username else f"{user.first_name} {user.last_name}"

        # Ссылка на профиль клиента
        profile_link = f"https://t.me/{user.username}" if user.username else f"Профиль не установлен"

        # Логирование с дополнительной информацией
        logger.info(
            f"Заказ подтвержден. Информация о заказе: {order['name']} - {order['price']} руб., {first_name} {last_name}, {phone}, {pickup_time}, {telegram_username}, Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        admin_message = f"🎉 Новый заказ:\nТовар: {order['name']} - {order['price']} руб. 💰\nИмя: {first_name} {last_name} 🧑‍💼\nТелефон: {phone} 📱\nВремя самовывоза: {pickup_time} ⏳\nКлиент: {telegram_username} 👤\nСсылка на профиль: {profile_link} 🔗\nДата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        try:
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(admin_id, admin_message)
                logger.info(f"Сообщение отправлено админу {admin_id}.")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения админу: {e}")

        await update.message.reply_text(
            f"✅ Спасибо за заказ! Ваш товар: {order['name']} - {order['price']} руб. 💰\nМы свяжемся с вами по телефону: {phone} 📱 для уточнения времени самовывоза ⏳.")
        return ConversationHandler.END

    elif update.message.text.lower() == 'отменить':
        await update.message.reply_text(
            "❌ Заказ отменен. Вы можете начать оформление заказа заново.",
            reply_markup=ReplyKeyboardMarkup([['/start']], one_time_keyboard=True)
        )
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "❓ Неверная команда. Пожалуйста, отправьте 'Да' ✅ для подтверждения или 'Отменить' ❌ для отмены заказа.")
        return CONFIRM


# Функция для выхода
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("❌ Заказ отменен.")
    return ConversationHandler.END


# Основная функция
def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчик команд
    application.add_handler(CommandHandler("start", start))

    # Обработчик разговоров
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('zakaz', zakaz)],
        states={
            ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PICKUP_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pickup_datetime)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
