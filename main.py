from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7801596549:AAGv39K8HhEOTN6jf5dEs74lBT3qkJ083IE"

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
    url = update.message.text.strip()

    # Перевірка на коректність посилання
    if not (url.startswith("https://www.tiktok.com/") or url.startswith("https://vm.tiktok.com/")):
        await update.message.reply_text("Будь ласка, надішліть дійсне посилання на TikTok.")
        return

    try:
        # Формуємо API-запит
        api_url = f"https://videodownloadapi-production.up.railway.app/download?url={url}"
        response = requests.get(api_url)
        response_data = response.json()

        # Логування відповіді для діагностики
        print("API Response:", response_data)

        # Перевірка на успішність запиту
        if response.status_code == 200 and "url" in response_data:
            video_url = response_data["url"]
            await update.message.reply_video(video_url, caption="Ось ваше відео з TikTok!")
        else:
            error_message = response_data.get("message", "Не вдалося завантажити відео.")
            await update.message.reply_text(f"Помилка: {error_message}")
    except Exception as e:
        await update.message.reply_text(f"Сталася помилка при завантаженні відео: {e}")

if __name__ == "__main__":
    # Створення додатку
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обробник повідомлень
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Запуск бота
    print("Бот запущено...")
    app.run_polling()
