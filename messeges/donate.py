from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext

async def handle_donate(update: Update, context: CallbackContext):
    """Обробляє натискання кнопки 'Підтримати'"""
    query = update.callback_query
    await query.answer()

    donate_text = "Виберіть суму:"
    keyboard = [
        [InlineKeyboardButton("10⭐", callback_data="donate_10")],
        [InlineKeyboardButton("25⭐", callback_data="donate_25")],
        [InlineKeyboardButton("50⭐", callback_data="donate_50")],
        [InlineKeyboardButton("200⭐", callback_data="donate_200")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(donate_text, reply_markup=reply_markup)

async def process_donation(update: Update, context: CallbackContext):
    """Обробляє вибір суми і запускає оплату"""
    query = update.callback_query
    await query.answer()

    amount = int(query.data.split("_")[1])
    user_id = query.from_user.id

    title = "Підтримка JuiceSave"
    description = f"Дякуємо за підтримку на {amount}⭐!"
    payload = f"donation_{user_id}_{amount}"
    currency = "XTR"
    prices = [{"label": "Підтримка", "amount": amount}]

    await context.bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency=currency,
        prices=prices,
        start_parameter="donation"
    )
