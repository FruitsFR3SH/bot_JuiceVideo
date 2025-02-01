import http.client
import json
import telebot

# Токен вашого Telegram-бота
token = "7141362441:AAFm-ckIy2L51KHzgZ_w3USxMVW9Oo8NM3Q"
bot = telebot.TeleBot(token)

# Дані API
API_HOST = "social-download-all-in-one.p.rapidapi.com"
API_KEY = "bab1d69d47msh7571cc673e498c4p16f95djsn5bc443eeec97"

# Функція для отримання відео
def get_video_data(video_url):
    conn = http.client.HTTPSConnection(API_HOST)
    payload = json.dumps({"url": video_url})
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST,
        'Content-Type': "application/json"
    }
    conn.request("POST", "/v1/social/autolink", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Відправ мені посилання на відео, і я знайду його для тебе!")

# Обробник повідомлень із посиланнями
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def send_video(message):
    bot.reply_to(message, "Зачекай, шукаю відео...")
    video_data = get_video_data(message.text)
    
    if video_data.get("error"):
        bot.reply_to(message, "Не вдалося отримати відео. Спробуй інше посилання!")
        return
    
    title = video_data.get("title", "Без назви")
    author = video_data.get("author", "Невідомий автор")
    thumbnail = video_data.get("thumbnail")
    medias = video_data.get("medias", [])
    
    if not medias:
        bot.reply_to(message, "Не вдалося знайти медіафайли для цього відео.")
        return
    
    video_url = medias[0].get("url")  # Беремо перше доступне відео
    quality = medias[0].get("quality", "Невідомо")
    
    response_text = f"🎬 *{title}*\n👤 {author}\n📺 Якість: {quality}\n\n[🔗 Завантажити відео]({video_url})"
    
    bot.send_photo(message.chat.id, thumbnail, caption=response_text, parse_mode="Markdown")

# Запуск бота
bot.polling(none_stop=True)
