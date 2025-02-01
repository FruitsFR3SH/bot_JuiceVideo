from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7141362441:AAFm-ckIy2L51KHzgZ_w3USxMVW9Oo8NM3Q"

# Параметри RapidAPI
RAPIDAPI_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"
RAPIDAPI_HOST = "auto-download-all-in-one.p.rapidapi.com"
RAPIDAPI_URL = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

# Словник для відстеження підписок користувачів
sponsor_choices = {}

# Дані про спонсорські ресурси
SPONSORS = {
    'bot': {
        'url': 'https://example.com/bot'
    },
    'channel': {
        'url': 'https://example.com/channel'
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Привітання користувача та показ кнопок спонсора"""
    keyboard = [
        [InlineKeyboardButton("Спонсорський бот", url=SPONSORS['bot']['url'])],
        [InlineKeyboardButton("Спонсорський канал", url=SPONSORS['channel']['url'])],
        [InlineKeyboardButton("✅ Перевірити підписки", callback_data='check_all')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo="https://uainet.net/wp-content/uploads/2021/06/tekhnichni-roboty.jpg",
        caption="Перед тим як почати користуватись ботом ви повинні підписатись на наші спонсорські канали",
        reply_markup=reply_markup
    )

async def handle_sponsor_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка перевірки підписок"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == 'check_all':
        # Видаляємо повідомлення з кнопками і надсилаємо підтвердження
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Дякуємо за підписку! Тепер ви можете надсилати посилання для завантаження відео."
        )
    
    await query.answer()

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
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
