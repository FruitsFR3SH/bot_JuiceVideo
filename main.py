import requests
import json
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

# Токен вашого Telegram-бота
token = "7696258601:AAFIOfaGiIU7_o6XFeqt1r6HmIIrY6goW6o"
bot = Bot(token)

# Дані API
API_HOST = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"
API_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"

# Функція для отримання відео
def get_video_data(video_url):
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "social-download-all-in-one.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    payload = json.dumps({"url": video_url})
    response = requests.post(API_HOST, data=payload, headers=headers)
    return response.json()

# Обробник команди /start
def start(update: Update, context):
    update.message.reply_text("Відправ мені посилання на відео, і я знайду його для тебе!")

# Обробник повідомлень із посиланнями
def send_video(update: Update, context):
    video_url = update.message.text
    update.message.reply_text("Зачекай, шукаю відео...")
    video_data = get_video_data(video_url)
    
    if video_data.get("error"):
        update.message.reply_text("Не вдалося отримати відео. Спробуй інше посилання!")
        return
    
    title = video_data.get("title", "Без назви")
    author = video_data.get("author", "Невідомий автор")
    thumbnail = video_data.get("thumbnail")
    medias = video_data.get("medias", [])
    
    if not medias:
        update.message.reply_text("Не вдалося знайти медіафайли для цього відео.")
        return
    
    video_url = medias[0].get("url")  # Беремо перше доступне відео
    quality = medias[0].get("quality", "Невідомо")
    
    response_text = f"🎬 *{title}*\n👤 {author}\n📺 Якість: {quality}\n\n[🔗 Завантажити відео]({video_url})"
    
    bot.send_photo(update.message.chat.id, thumbnail, caption=response_text, parse_mode="Markdown")

# Налаштування бота
updater = Updater(token, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, send_video))

# Запуск бота
updater.start_polling()
updater.idle()
