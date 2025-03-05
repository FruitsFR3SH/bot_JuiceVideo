from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, filters
from messeges.start import start, button_handler
from messeges.classic import handle_text
from messeges.tech_works import tech_works
from messeges.donate import handle_donate, process_donation, precheckout_callback
from website.stats import stats_bp  # Змінено з 'site' на 'website'
from flask import Flask, session
import threading

flask_app = Flask(__name__, static_folder="website/static", template_folder="website/templates")
flask_app.secret_key = "your_secret_key_here"
flask_app.register_blueprint(stats_bp)

with open("system/token.txt", "r") as token_file:
    BOT_TOKEN = token_file.read().strip()

def run_flask(bot_context):
    flask_app.bot_context = bot_context
    flask_app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="check_subscriptions"))
    app.add_handler(CallbackQueryHandler(process_donation, pattern=r"donate_\d+"))  # Спочатку обробка сум
    app.add_handler(CallbackQueryHandler(handle_donate, pattern="donate"))         # Потім "donate"
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    flask_thread = threading.Thread(target=run_flask, args=(app,))
    flask_thread.daemon = True
    flask_thread.start()

    print("Бот запущено...")
    app.run_polling()