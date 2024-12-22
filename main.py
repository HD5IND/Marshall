import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import openpyxl

# Токен вашего бота
API_TOKEN = "8111798890:AAFdyuUCKEG-Z0eAznHIbPMVNKUJ07lLYgw"
TRACK24_API_KEY = "774f1dbcde7b02c7cfe41b797f4965b4"
EXCEL_FILE = "track_codes.xlsx"

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения языков пользователей
user_languages = {}

# ---------------- Функции ---------------- #
def main_menu(user_id):
    """Создает главное меню в зависимости от языка пользователя."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    current_language = user_languages.get(user_id, "ru")

    if current_language == "ru":
        btn1 = KeyboardButton("📍 Адреса складов")
        btn2 = KeyboardButton("💰 Цены")
        btn3 = KeyboardButton("🌐 Поменять язык")
        btn4 = KeyboardButton("💱 Обмен валют")
        btn5 = KeyboardButton("📦 Проверка трек-кода")
    else:
        btn1 = KeyboardButton("📍 Warehouse Addresses")
        btn2 = KeyboardButton("💰 Prices")
        btn3 = KeyboardButton("🌐 Change Language")
        btn4 = KeyboardButton("💱 Currency Exchange")
        btn5 = KeyboardButton("📦 Track Code Verification")

    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup


def find_in_excel(file_path, track_code):
    """Ищет трек-код в базе Excel."""
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] == track_code:
                return True
        return False
    except Exception as e:
        print(f"Ошибка чтения Excel: {e}")
        return False


def get_tracking_info(track_code):
    """Получает статус трек-кода через API Track24."""
    url = "https://api.track24.net/tracking/json/v2/"
    headers = {"Track24-API-Key": TRACK24_API_KEY}
    payload = {"trackCode": track_code}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                return data["data"][0]["status"]
        return None
    except Exception as e:
        print(f"Ошибка при запросе API: {e}")
        return None

# ---------------- Обработчики ---------------- #
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_languages[user_id] = "ru"  # Устанавливаем язык по умолчанию
    bot.send_message(
        user_id,
        "Добро пожаловать в MARKET!\nВыберите действие из меню ниже:",
        reply_markup=main_menu(user_id)
    )


@bot.message_handler(func=lambda message: message.text in ["🌐 Поменять язык", "🌐 Change Language"])
def change_language(message):
    """Переключение языка."""
    user_id = message.chat.id
    current_language = user_languages.get(user_id, "ru")

    # Меняем язык
    if current_language == "ru":
        user_languages[user_id] = "en"
        bot.send_message(
            user_id,
            "🌐 Language has been changed to English.\nPlease select an option from the menu below:",
            reply_markup=main_menu(user_id)
        )
    else:
        user_languages[user_id] = "ru"
        bot.send_message(
            user_id,
            "🌐 Язык изменен на русский.\nВыберите действие из меню ниже:",
            reply_markup=main_menu(user_id)
        )


@bot.message_handler(func=lambda message: message.text == "📦 Проверка трек-кода" or message.text == "📦 Track Code Verification")
def check_track_code(message):
    user_id = message.chat.id
    current_language = user_languages.get(user_id, "ru")

    if current_language == "ru":
        bot.send_message(user_id, "Пожалуйста, укажите номер вашего трек-кода для проверки:")
    else:
        bot.send_message(user_id, "Please provide your tracking code for verification:")
    bot.register_next_step_handler(message, process_track_code)


def process_track_code(message):
    user_id = message.chat.id
    current_language = user_languages.get(user_id, "ru")
    track_code = message.text.strip()

    # Проверяем трек-код в базе Excel
    is_in_base = find_in_excel(EXCEL_FILE, track_code)
    if not is_in_base:
        if current_language == "ru":
            bot.send_message(user_id, "❌ Трек-код не найден в базе.")
        else:
            bot.send_message(user_id, "❌ The tracking code was not found in the database.")
        return

    # Получаем статус через API Track24
    tracking_info = get_tracking_info(track_code)
    if tracking_info:
        if current_language == "ru":
            bot.send_message(user_id, f"📦 *Статус посылки:*\n{tracking_info}", parse_mode="Markdown")
        else:
            bot.send_message(user_id, f"📦 *Package Status:*\n{tracking_info}", parse_mode="Markdown")
    else:
        if current_language == "ru":
            bot.send_message(user_id, "❌ Не удалось получить информацию по трек-коду.")
        else:
            bot.send_message(user_id, "❌ Failed to retrieve information for the tracking code.")


@bot.message_handler(func=lambda message: message.text == "💰 Цены" or message.text == "💰 Prices")
def send_prices(message):
    user_id = message.chat.id
    current_language = user_languages.get(user_id, "ru")

    if current_language == "ru":
        text = (
            "📢 *Тариф на цены:*\n"
            "🔸 От 1кг до 5кг — 3$ за кг\n"
            "🔸 От 5кг до 50кг — 2.5$ за кг\n"
            "🔸 От 50кг и больше — 2$ за кг\n"
            "🔸 Куб — 270$\n"
        )
    else:
        text = (
            "📢 *Pricing rates:*\n"
            "🔸 of 1kg to 5kg — 3$ per kg\n"
            "🔸 of 5kg to 50kg — 2.5$ per kg\n"
            "🔸 of 50kg and more — 2$ per kg\n"
            "🔸 Cub — 270$\n"
        )
    bot.send_message(user_id, text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "📍 Адреса складов" or message.text == "📍 Warehouse Addresses")
def send_addresses(message):
    user_id = message.chat.id
    current_language = user_languages.get(user_id, "ru")

    if current_language == "ru":
        text = "📍 *Адреса складов:*\n1. Склад 1: ул. Примерная, д. 12\n2. Склад 2: ул. Логистическая, д. 5"
    else:
        text = "📍 *Warehouse addresses:*\n1. Warehouse 1: 12 Example St.\n2. Warehouse 2: 5 Logistics St."
    bot.send_message(user_id, text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "💱 Обмен валют" or message.text == "💱 Currency Exchange")
def exchange_rates(message):
    user_id = message.chat.id
    current_language = user_languages.get(user_id, "ru")

    if current_language == "ru":
        text = (
            "🍀 *Актуальный курс на юани:*\n"
            "✨ До 1000¥ — 1.58 смн\n"
            "✨ От 1000¥ до 5000¥ — 1.57 смн\n"
            "✨ От 5000¥ до 10000¥ — 1.55 смн\n"
            "✨ От 10000¥ — 1.54 смн\n"
        )
    else:
        text = (
            "🍀 *Current yuan exchange rates:*\n"
            "✨ Up to 1000¥ — 1.58 smn\n"
            "✨ 1000¥ to 5000¥ — 1.57 smn\n"
            "✨ 5000¥ to 10000¥ — 1.55 smn\n"
            "✨ Over 10000¥ — 1.54 smn\n"
        )
    bot.send_message(user_id, text, parse_mode="Markdown")


# ---------------- Запуск бота ---------------- #
if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling()