import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests  # Для HTTP-запросов
from googletrans import Translator
import openpyxl  # Для работы с Excel

# Токен вашего бота
API_TOKEN = "8111798890:AAFdyuUCKEG-Z0eAznHIbPMVNKUJ07lLYgw"
TRACK24_API_KEY = "774f1dbcde7b02c7cfe41b797f4965b4" 
# Замените на ваш ключ API Track24
EXCEL_FILE = "track_codes.xlsx"  
# Укажите путь к вашему Excel-файлу

bot = telebot.TeleBot(API_TOKEN)
translator = Translator()

# Глобальная переменная для текущего языка
current_language = "ru"

# ---------------- Клавиатура ---------------- #
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("📍 Адреса складов")
    btn2 = KeyboardButton("💰 Цены")
    btn3 = KeyboardButton("🌐 Поменять язык")
    btn4 = KeyboardButton("💱 Обмен валют")
    btn5 = KeyboardButton("📦 Проверка трек-кода")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# ---------------- Проверка трек-кода ---------------- #
def find_in_excel(file_path, track_code):
    """Ищет трек-код в базе Excel."""
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] == track_code:
                return True  # Если трек-код найден
        return False  # Если трек-код не найден
    except Exception as e:
        print(f"Ошибка чтения Excel: {e}")
        return False

def get_tracking_info(track_code):
    """Получает статус трек-кода через API Track24."""
    url = "https://api.track24.net/tracking/json/v2/"  # URL API Track24
    headers = {"Track24-API-Key": TRACK24_API_KEY}
    payload = {"trackCode": track_code}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                status = data["data"][0]["status"]
                return status
        return None
    except Exception as e:
        print(f"Ошибка при запросе API: {e}")
        return None

@bot.message_handler(func=lambda message: message.text == "📦 Проверка трек-кода")
def check_track_code(message):
    if current_language == "ru":
        bot.send_message(message.chat.id, "Пожалуйста, укажите номер вашего трек-кода для проверки:")
    else:
        bot.send_message(message.chat.id, "Please provide your tracking code for verification:")
    bot.register_next_step_handler(message, process_track_code)

def process_track_code(message):
    track_code = message.text.strip()

    # Проверяем трек-код в базе Excel
    is_in_base = find_in_excel(EXCEL_FILE, track_code)
    if not is_in_base:
        if current_language == "ru":
            bot.send_message(message.chat.id, "❌ Трек-код не найден в базе.")
        else:
            bot.send_message(message.chat.id, "❌ The tracking code was not found in the database.")
        return

    # Получаем статус через API Track24
    tracking_info = get_tracking_info(track_code)
    if tracking_info:
        if current_language == "ru":
            bot.send_message(message.chat.id, f"📦 *Статус посылки:*\n{tracking_info}", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"📦 *Package Status:*\n{tracking_info}", parse_mode="Markdown")
    else:
        if current_language == "ru":
            bot.send_message(message.chat.id, "❌ Не удалось получить информацию по трек-коду.")
        else:
            bot.send_message(message.chat.id, "❌ Failed to retrieve information for the tracking code.")

# ---------------- Остальной функционал ---------------- #
# Остальные обработчики остались без изменений.

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в MARKET!\nВыберите действие из меню ниже:",
        reply_markup=main_menu()
    )

# ---------------- Запуск бота ---------------- #
if __name__ == "__main__":
    bot.remove_webhook()  # Удалить активный вебхук
    bot.polling()