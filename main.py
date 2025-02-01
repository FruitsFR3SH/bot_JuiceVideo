import requests
import json
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder

# Токен вашого Telegram-бота
token = "token"
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
async def start(update: Update, context):
    await update.message.reply_text("Відправ мені посилання на відео, і я знайду його для тебе!")

# Обробник повідомлень із посиланнями
async def send_video(update: Update, context):
    video_url = update.message.text
    await update.message.reply_text("Зачекай, шукаю відео...")
    video_data = get_video_data(video_url)
    
    if video_data.get("error"):
        await update.message.reply_text("Не вдалося отримати відео. Спробуй інше посилання!")
        return
    
    title = video_data.get("title", "Без назви")
    author = video_data.get("author", "Невідомий автор")
    thumbnail = video_data.get("thumbnail")
    medias = video_data.get("medias", [])
    
    if not medias:
        await update.message.reply_text("Не вдалося знайти медіафайли для цього відео.")
        return
    
    video_url = medias[0].get("url")  # Беремо перше доступне відео
    quality = medias[0].get("quality", "Невідомо")
    
    response_text = f"🎬 *{title}*\n👤 {author}\n📺 Якість: {quality}\n\n[🔗 Завантажити відео]({video_url})"
    
    await bot.send_photo(update.message.chat.id, thumbnail, caption=response_text, parse_mode="Markdown")

# Налаштування бота
app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_video))

# Запуск бота
app.run_polling()
