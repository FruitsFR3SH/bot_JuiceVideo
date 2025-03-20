from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє команду /start"""
    welcome_text = (
        "❗️Перед тим як почати користуватись ботом ви повинні підписатись на спонсорський контент"
    )
    keyboard = [
        [InlineKeyboardButton("Спонсор 1", url="https://t.me/sponsor1")],
        [InlineKeyboardButton("Спонсор 2", url="https://t.me/sponsor2")],
        [InlineKeyboardButton("Спонсор 3", url="https://t.me/sponsor3")],
        [InlineKeyboardButton("Перевірити підписки", callback_data="check_subscriptions")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("messeges/banner.png", "rb") as banner:
        await update.message.reply_photo(
            photo=banner,
            caption=welcome_text,
            reply_markup=reply_markup
        )
    context.user_data["subscription_checked"] = False

async def button_handler(update: Update, context: CallbackContext):
    """Обробляє натискання кнопки 'Перевірити підписки'"""
    query = update.callback_query
    await query.answer()

    if context.user_data.get("subscription_checked", False):
        user_name = query.from_user.first_name
        success_text = (
            f"Привіт {user_name} 👋\n"
            "Я JuiceSave, просто надішли мені посилання на TikTok відео "
            "і я завантажу його для тебе у найкращій якості"
        )
        with open("messeges/banner.png", "rb") as banner:
            await query.message.reply_photo(
                photo=banner,
                caption=success_text
            )
    else:
        fail_text = "🚫 Перевірка не успішна, перевірте підписки на спонсорський контент"
        await query.message.reply_text(fail_text)

        welcome_text = (
            "❗️Перед тим як почати користуватись ботом ви повинні підписатись на спонсорський контент"
        )
        keyboard = [
            [InlineKeyboardButton("Спонсор 1", url="https://t.me/sponsor1")],
            [InlineKeyboardButton("Спонсор 2", url="https://t.me/sponsor2")],
            [InlineKeyboardButton("Спонсор 3", url="https://t.me/sponsor3")],
            [InlineKeyboardButton("Перевірити підписки", callback_data="check_subscriptions")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open("messeges/banner.png", "rb") as banner:
            await query.message.reply_photo(
                photo=banner,
                caption=welcome_text,
                reply_markup=reply_markup
            )
        context.user_data["subscription_checked"] = True
