from telegram import Update
from telegram.ext import ContextTypes

async def tech_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Повідомлення про технічні роботи"""
    await update.message.reply_text("Вибачте, бот тимчасово на технічних роботах.")