from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7801596549:AAGv39K8HhEOTN6jf5dEs74lBT3qkJ083IE"

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
    url = update.message.text.strip()

    # Перевірка на коректність посилання
    if not url:
        await update.message.reply_text("Будь ласка, надішліть дійсне посилання на відео.")
        return

    try:
        # Формуємо API-запит
        api_url = f"https://videodownloadapi-production.up.railway.app/download?url={url}"
        response = requests.get(api_url, allow_redirects=True)

        # Перевірка статусу відповіді
        if response.status_code == 200:
            video_url = response.url  # Після редіректу отримуємо URL відеофайлу
            await update.message.reply_video(video_url, caption="Ось ваше відео!")
        else:
            await update.message.reply_text(f"Помилка: сервер повернув статус {response.status_code}.")
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
