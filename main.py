from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7141362441:AAFm-ckIy2L51KHzgZ_w3USxMVW9Oo8NM3Q"

# Параметри RapidAPI
RAPIDAPI_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"
RAPIDAPI_HOST = "auto-download-all-in-one.p.rapidapi.com"
RAPIDAPI_URL = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

# Список користувачів, які натиснули на спонсорські кнопки
users_clicked_buttons = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відображає повідомлення з кнопками для спонсорських посилань"""
    keyboard = [
        [
            InlineKeyboardButton("Спонсорський бот", url="https://your-sponsor-bot-link.com", callback_data="sponsor_bot_clicked"),
            InlineKeyboardButton("Спонсорський канал", url="https://your-sponsor-channel-link.com", callback_data="sponsor_channel_clicked")
        ],
        [
            InlineKeyboardButton("Перевірити підписки", callback_data="check_subscription")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(
        photo="https://uainet.net/wp-content/uploads/2021/06/tekhnichni-roboty.jpg",
        caption="Перед тим як почати користуватись ботом ви повинні підписатись на наші спонсорські канали",
        reply_markup=reply_markup
    )

async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє натискання спонсорських кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    users_clicked_buttons.add(user_id)
    await query.edit_message_text(text="Дякуємо за натискання спонсорських кнопок! Тепер натисніть 'Перевірити підписки'.")

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перевіряє, чи натиснув користувач на спонсорські кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id in users_clicked_buttons:
        await query.edit_message_text(text="Дякуємо за підписку! Тепер ви можете завантажувати відео.")
    else:
        await query.edit_message_text(text="Ви повинні натиснути на спонсорські кнопки перед перевіркою. Використайте команду /start для початку.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
    user_id = update.message.from_user.id

    if user_id not in users_clicked_buttons:
        await update.message.reply_text("Ви повинні натиснути на спонсорські кнопки перед завантаженням відео. Використайте команду /start для початку.")
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
    app.add_handler(CallbackQueryHandler(button_click_handler, pattern="sponsor_bot_clicked"))
    app.add_handler(CallbackQueryHandler(button_click_handler, pattern="sponsor_channel_clicked"))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Запуск бота
    print("Бот запущено...")
    app.run_polling()
