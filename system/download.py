import requests
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
    url = update.message.text.strip()

    if not url:
        await update.message.reply_text("Будь ласка, надішліть дійсне посилання на відео.")
        return False

    try:
        api_url = f"https://videodownloadapi-production.up.railway.app/download?url={url}"
        response = requests.get(api_url, allow_redirects=True)

        if response.status_code == 200:
            video_url = response.url
            await update.message.reply_video(video_url, caption="Ось ваше відео!")
            # Оновлюємо статистику
            now = datetime.now()
            context.bot_data.setdefault("videos_downloaded", []).append(now)
            context.bot_data.setdefault("users", {})
            context.bot_data["users"][update.effective_user.id] = True
            context.bot_data.setdefault("messages", []).append(now)
            return True
        else:
            await update.message.reply_text(f"Помилка: сервер повернув статус {response.status_code}.")
            context.bot_data.setdefault("messages", []).append(datetime.now())
            return False
    except Exception as e:
        await update.message.reply_text(f"Сталася помилка при завантаженні відео: {e}")
        context.bot_data.setdefault("messages", []).append(datetime.now())
        return False