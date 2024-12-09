from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from yt_dlp import YoutubeDL
import os

# Папка для збереження файлів
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Токен вашого бота
BOT_TOKEN = "7924938712:AAEur9ZZSoZ5lLh3k8jId9a9YeLGcblxGSM"

async def start(update: Update, context):
    """Обробляє команду /start."""
    await update.message.reply_text("Привіт! Надішліть мені посилання на YouTube або TikTok відео.")

async def process_link(update: Update, context):
    """Обробляє посилання на відео."""
    url = update.message.text

    try:
        options = {"listformats": True}
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [
                {
                    "format_id": f["format_id"],
                    "resolution": f.get("resolution", "audio only"),
                    "ext": f["ext"],
                }
                for f in info.get("formats", [])
            ]

        # Генеруємо кнопки для вибору формату
        keyboard = [
            [InlineKeyboardButton(f"{f['resolution']} ({f['ext']})", callback_data=f['format_id'])]
            for f in formats
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Оберіть формат для завантаження:", reply_markup=reply_markup
        )
        context.user_data["url"] = url
    except Exception as e:
        await update.message.reply_text(f"Сталася помилка: {str(e)}")

async def download_video(update: Update, context):
    """Завантажує вибране відео."""
    query = update.callback_query
    await query.answer()
    format_id = query.data
    url = context.user_data.get("url")

    if not url or not format_id:
        await query.edit_message_text("Сталася помилка. Спробуйте знову.")
        return

    try:
        # Завантажуємо відео
        options = {
            "format": format_id,
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        }
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Відправляємо файл користувачу
        await query.edit_message_text("Завантаження завершено! Відправляю файл...")
        await query.message.reply_document(open(file_path, "rb"))
        os.remove(file_path)  # Видаляємо файл після відправки
    except Exception as e:
        await query.edit_message_text(f"Сталася помилка під час завантаження: {str(e)}")

def main():
    """Запуск бота."""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))
    app.add_handler(CallbackQueryHandler(download_video))

    print("Бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    main()
