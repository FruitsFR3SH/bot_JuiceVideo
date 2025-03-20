from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from messeges.start import start, button_handler
from messeges.classic import handle_text
from messeges.tech_works import tech_works
from messeges.donate import handle_donate, process_donation

with open("system/token.txt", "r") as token_file:
    BOT_TOKEN = token_file.read().strip()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="check_subscriptions"))
    app.add_handler(CallbackQueryHandler(process_donation, pattern=r"donate_\d+"))
    app.add_handler(CallbackQueryHandler(handle_donate, pattern="donate"))
    print("Бот запущено...")
    app.run_polling()
