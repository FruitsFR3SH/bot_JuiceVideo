from telegram import Update
from telegram.ext import ContextTypes
from system.download import download_video
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from messeges.start import start
from datetime import datetime

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє текстові повідомлення"""
    # Додаємо повідомлення до статистики
    context.bot_data.setdefault("messages", []).append(datetime.now())
    
    if not context.user_data.get("subscription_checked", False):
        await start(update, context)
        return

    success = await download_video(update, context)

    if success:
        support_text = (
            "Нагадуємо, що ви можете нас підтримати з допомогою зірок Telegram, "
            "ми будемо вам дуже вдячні за внесок у наш розвиток ❤️"
        )
        keyboard = [
            [InlineKeyboardButton("Підтримати", callback_data="donate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open("messeges/banner1.png", "rb") as banner:
            await update.message.reply_photo(
                photo=banner,
                caption=support_text,
                reply_markup=reply_markup
            )