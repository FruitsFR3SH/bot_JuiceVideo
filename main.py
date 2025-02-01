from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import requests

# Вкажіть свій токен бота
BOT_TOKEN = "7141362441:AAFm-ckIy2L51KHzgZ_w3USxMVW9Oo8NM3Q"

# Параметри RapidAPI
RAPIDAPI_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"
RAPIDAPI_HOST = "auto-download-all-in-one.p.rapidapi.com"
RAPIDAPI_URL = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

# Словник для відстеження підписок користувачів
sponsor_choices = {}

# Дані про спонсорські ресурси
SPONSORS = {
    'bot': {
        'url': 'https://t.me/kittyverse_ai_bot/play?startapp=u1310633045',
        'chat_id': '@kittyverse_ai_bot'  # Замініть на username вашого бота
    },
    'channel': {
        'url': 'https://example.com/channel',
        'chat_id': '@save_download_bot'  # Замініть на username вашого каналу
    }
}

async def check_subscription(user_id: int, chat_id: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Перевіряє чи підписаний користувач на канал/бота"""
    try:
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Помилка перевірки підписки: {e}")  # Додаємо логування помилок
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Привітання користувача та показ кнопок спонсора"""
    keyboard = [
        [InlineKeyboardButton("Спонсорський бот", url=SPONSORS['bot']['url'])],
        [InlineKeyboardButton("Спонсорський канал", url=SPONSORS['channel']['url'])],
        [InlineKeyboardButton("✅ Перевірити підписки", callback_data='check_all')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Надсилаємо зображення та кнопки
    message = await update.message.reply_photo(
        photo="https://uainet.net/wp-content/uploads/2021/06/tekhnichni-roboty.jpg",
        caption="Перед тим як почати користуватись ботом ви повинні підписатись на наші спонсорські канали",
        reply_markup=reply_markup
    )
    
    # Зберігаємо message_id для подальшого видалення
    context.user_data['start_message_id'] = message.message_id

async def handle_sponsor_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка перевірки всіх підписок"""
    query = update.callback_query
    user_id = query.from_user.id
    
    print(f"Отримано callback від користувача {user_id}")  # Додаємо логування
    
    if query.data == 'check_all':
        print("Перевіряємо підписки...")  # Додаємо логування
        
        # Перевіряємо обидві підписки
        is_bot_subscribed = await check_subscription(user_id, SPONSORS['bot']['chat_id'], context)
        is_channel_subscribed = await check_subscription(user_id, SPONSORS['channel']['chat_id'], context)
        
        print(f"Результати перевірки: бот - {is_bot_subscribed}, канал - {is_channel_subscribed}")  # Додаємо логування

        if is_bot_subscribed and is_channel_subscribed:
            # Якщо користувач підписаний на обидва ресурси
            try:
                await query.message.delete()
                await context.bot.send_message(
                    chat_id=user_id,
                    text="✅ Дякуємо за підписку! Тепер ви можете надсилати посилання для завантаження відео."
                )
            except Exception as e:
                print(f"Помилка при видаленні повідомлення: {e}")  # Додаємо логування помилок
        else:
            # Формуємо повідомлення про відсутні підписки
            missing = []
            if not is_bot_subscribed:
                missing.append("бота")
            if not is_channel_subscribed:
                missing.append("канал")
            
            await query.answer(
                f"Ви не підписані на {' та '.join(missing)}! Спочатку підпишіться.",
                show_alert=True
            )
    
    await query.answer()  # Відповідаємо на callback query в будь-якому випадку

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє посилання на відео і завантажує його"""
    user_id = update.message.from_user.id

    # Перевірка підписок перед завантаженням
    is_bot_subscribed = await check_subscription(user_id, SPONSORS['bot']['chat_id'], context)
    is_channel_subscribed = await check_subscription(user_id, SPONSORS['channel']['chat_id'], context)

    if not (is_bot_subscribed and is_channel_subscribed):
        await update.message.reply_text(
            "Ви повинні підписатися на всі спонсорські канали перед завантаженням відео. Використайте /start щоб побачити кнопки підписки."
        )
        return

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
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_sponsor_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Запуск бота
    print("Бот запущено...")
    app.run_polling()
