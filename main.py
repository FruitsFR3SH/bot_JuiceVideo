from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7801596549:AAGv39K8HhEOTN6jf5dEs74lBT3qkJ083IE"

# Параметри RapidAPI
RAPIDAPI_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"
RAPIDAPI_HOST = "auto-download-all-in-one.p.rapidapi.com"
RAPIDAPI_URL = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Привітання користувача та показ кнопок спонсора"""
    keyboard = [
        [InlineKeyboardButton("Спонсорський бот", url="https://exemple.com")],
        [InlineKeyboardButton("Спонсорський канал", url="https://exemple.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Надсилаємо зображення та кнопки
    await update.message.reply_photo(
        photo="https://uainet.net/wp-content/uploads/2021/06/tekhnichni-roboty.jpg",
        caption="Перед тим як почати користуватись ботом ви повинні підписатись на наші спонсорські канали",
        reply_markup=reply_markup
    )

    # Встановлюємо "sponsor_choice" для користувача
    user_data = context.user_data
    user_data["sponsor_choice"] = set()

async def handle_sponsor_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка вибору спонсора"""
    query = update.callback_query
    await query.answer()

    # Збереження натискання користувача в user_data
    user_data = context.user_data
    choice = query.data

    # Додаємо вибір до списку
    if "sponsor_choice" not in user_data:
        user_data["sponsor_choice"] = set()

    user_data["sponsor_choice"].add(choice)

    # Логування для перевірки, що зберігається в user_data
    print("User sponsor choices:", user_data["sponsor_choice"])

    # Перевірка, чи натиснуті обидві кнопки
    if len(user_data["sponsor_choice"]) == 2:
        # Обидві кнопки натиснуті, дозволяємо завантаження відео
        await query.edit_message_text("Ви підписалися на всі спонсорські канали! Тепер ви можете надсилати посилання для завантаження відео.")
    else:
        # Якщо не всі кнопки натиснуті, чекаємо
        await query.edit_message_text("Будь ласка, підпишіться на всі спонсорські канали, щоб почати користуватися ботом.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
    # Перевірка, чи користувач вибрав обидві кнопки
    user_data = context.user_data
    print("User sponsor choices at video download:", user_data.get("sponsor_choice", set()))

    if "sponsor_choice" not in user_data or len(user_data["sponsor_choice"]) != 2:
        await update.message.reply_text("Ви повинні підписатися на всі спонсорські канали перед завантаженням відео.")
        return

    url = update.message.text.strip()

    # Перевірка на коректність посилання
    if not (url.startswith("https://www.tiktok.com/") or url.startswith("https://vm.tiktok.com/")):
        await update.message.reply_text("Будь ласка, надішліть дійсне посилання на TikTok.")
        return

    try:
        # Дані для запиту
        payload = {"url": url}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST,
            "Content-Type": "application/json",
        }

        # Виконання запиту до RapidAPI
        response = requests.post(RAPIDAPI_URL, json=payload, headers=headers)
        response_data = response.json()

        # Логування відповіді для діагностики
        print("API Response:", response_data)

        # Перевірка на успішність запиту
        if response.status_code == 200 and "medias" in response_data:
            medias = response_data["medias"]
            video_url = next((media["url"] for media in medias if media["extension"] == "mp4"), None)

            if video_url:
                await update.message.reply_video(video_url, caption="Ось ваше відео з TikTok!")
            else:
                await update.message.reply_text("На жаль, не вдалося знайти відео.")
        else:
            error_message = response_data.get("message", "Не вдалося завантажити відео.")
            await update.message.reply_text(f"Помилка: {error_message}")
    except Exception as e:
        await update.message.reply_text(
            f"Сталася помилка при завантаженні відео: {e}"
        )

if __name__ == "__main__":
    # Створення додатку
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обробники команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_sponsor_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Запуск бота
    print("Бот запущено...")
    app.run_polling()
