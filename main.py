from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7141362441:AAFm-ckIy2L51KHzgZ_w3USxMVW9Oo8NM3Q"

# Параметри RapidAPI
RAPIDAPI_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"
RAPIDAPI_HOST = "auto-download-all-in-one.p.rapidapi.com"
RAPIDAPI_URL = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

# Змінна для збереження стану натискання кнопок
user_subscription_status = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Надсилає зображення та кнопки для перевірки підписок"""
    user_id = update.message.from_user.id
    user_subscription_status[user_id] = {'bot': False, 'channel': False}

    keyboard = [
        [
            InlineKeyboardButton("Спонсорський бот", callback_data="bot"),
            InlineKeyboardButton("Спонсорський канал", callback_data="channel")
        ],
        [
            InlineKeyboardButton("Перевірити підписки", callback_data="check_subscriptions")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Надсилаємо зображення та текст перед кнопками
    photo_url = "https://uainet.net/wp-content/uploads/2021/06/tekhnichni-roboty.jpg"
    caption = "Перед тим як почати користуватись ботом, ви повинні підписатись на наші спонсорські канали."
    
    await update.message.reply_photo(photo=photo_url, caption=caption, reply_markup=reply_markup)

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє натискання кнопок спонсорського бота та каналу"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "bot":
        user_subscription_status[user_id]['bot'] = True
        await query.edit_message_text("Ви натиснули на спонсорський бот!")
    elif data == "channel":
        user_subscription_status[user_id]['channel'] = True
        await query.edit_message_text("Ви натиснули на спонсорський канал!")
    elif data == "check_subscriptions":
        if user_subscription_status[user_id]['bot'] and user_subscription_status[user_id]['channel']:
            await query.edit_message_text("Підписка підтверджена! Тепер ви можете завантажувати відео.")
            await query.message.reply_text("Надішліть посилання на відео, яке хочете завантажити.")
        else:
            await query.edit_message_text("Ви не натиснули на обидві спонсорські кнопки. Будь ласка, спробуйте ще раз.")

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
    app.add_handler(CallbackQueryHandler(handle_button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Запуск бота
    print("Бот запущено...")
    app.run_polling()
