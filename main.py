from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7141362441:AAFm-ckIy2L51KHzgZ_w3USxMVW9Oo8NM3Q"

# Параметри RapidAPI
RAPIDAPI_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"
RAPIDAPI_HOST = "auto-download-all-in-one.p.rapidapi.com"
RAPIDAPI_URL = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

# Функція перевірки підписки
async def check_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Надсилає зображення і кнопки для перевірки підписок"""
    user_id = update.message.from_user.id
    keyboard = [
        [
            InlineKeyboardButton("Спонсорський бот", url="https://t.me/your_sponsor_bot"),
            InlineKeyboardButton("Спонсорський канал", url="https://t.me/your_sponsor_channel")
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

# Обробник натискання кнопки для перевірки підписок
async def handle_subscription_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє натискання на кнопку перевірки підписок"""
    query = update.callback_query
    await query.answer()

    # Перевірка підписки на канал (замість цього потрібно реалізувати вашу перевірку)
    user_id = query.from_user.id
    # Приклад перевірки підписки на канал:
    try:
        # Приклад перевірки підписки на канал
        # Використовуємо API для перевірки підписки
        is_subscribed = True  # Це має бути реальна перевірка через API Telegram
        if is_subscribed:
            await query.edit_message_text("Підписка підтверджена! Тепер ви можете завантажувати відео.")
            await query.message.reply_text("Надішліть посилання на відео, яке хочете завантажити.")
        else:
            await query.edit_message_text("Ви не підписались на канал. Будь ласка, підпишіться і спробуйте ще раз.")
    except Exception as e:
        await query.edit_message_text(f"Сталася помилка при перевірці підписки: {e}")

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
    app.add_handler(CommandHandler("start", check_subscriptions))  # Викликаємо функцію перевірки підписок
    app.add_handler(CallbackQueryHandler(handle_subscription_check, pattern="check_subscriptions"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Запуск бота
    print("Бот запущено...")
    app.run_polling()
