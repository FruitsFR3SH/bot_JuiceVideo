import requests
from telegram import Update
from telegram.ext import ContextTypes

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
    url = update.message.text.strip()

    if not url:
        await update.message.reply_text("Будь ласка, надішліть дійсне посилання на відео.")
        return False

    try:
        api_url = f"videodownloadapi-production.up.railway.app/download?url={url}"
        response = requests.get(api_url, allow_redirects=True)

        if response.status_code == 200:
            video_url = response.url
            await update.message.reply_video(video_url, caption="Ось ваше відео!")
            return True
        else:
            await update.message.reply_text(f"Помилка: сервер повернув статус {response.status_code}.")
            return False
    except Exception as e:
        await update.message.reply_text(f"Сталася помилка при завантаженні відео: {e}")
        return False
