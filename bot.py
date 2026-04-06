from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_server).start()

TOKEN = "8299086246:AAHgf4rqQMvPiOPAHymOH475vEAeJ-bNspU"

keyboard = [
    ["Join as Host", "How it Works"],
    ["Earning Details", "Support"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to TalkMitra 💬\n\n"
        "TalkMitra ek chat & voice call based platform hai jahan aap host banne ke liye apply kar sakte ho.\n\n"
        "Yahan aap:\n"
        "• Host apply kar sakte ho\n"
        "• Process samajh sakte ho\n"
        "• Basic earning details dekh sakte ho\n"
        "• Support le sakte ho\n\n"
        "Neeche se option choose karo.",
        reply_markup=reply_markup
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text == "join as host":
        await update.message.reply_text(
            "Great choice 👍\n\n"
            "Host banne ke liye apni basic details is format me bhejo:\n\n"
            "Name:\n"
            "Age:\n"
            "City:\n"
            "Language:\n\n"
            "Example:\n"
            "Name: Rahul Das\n"
            "Age: 23\n"
            "City: Agartala\n"
            "Language: Hindi, Bengali\n\n"
            "Please genuine details hi share karein."
        )

    elif text == "how it works":
        await update.message.reply_text(
            "TalkMitra ka process simple hai:\n\n"
            "1. Aap host ke liye apply karte ho\n"
            "2. Hum aapka profile review karte hain\n"
            "3. Shortlisted users ko next step share kiya jata hai\n\n"
            "Work Type: Chat + Voice Call\n"
            "Timing: Flexible"
        )

    elif text == "earning details":
        await update.message.reply_text(
            "Earning depend karti hai:\n\n"
            "• Aapki activity par\n"
            "• Time spent par\n"
            "• User interaction par\n\n"
            "Detailed earning information shortlisted users ko next step me di jati hai."
        )

    elif text == "support":
        await update.message.reply_text(
            "Kisi bhi help ke liye contact kare:\n\n"
            "@talkmitra_support"
        )

    else:
        await update.message.reply_text(
            "Please neeche diye gaye buttons me se koi option choose karo."
        )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Host apply karne ke liye apni details bhejo:\n\n"
        "Name:\n"
        "Age:\n"
        "City:\n"
        "Language:"
    )

async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "TalkMitra ek chat & voice call based platform hai jahan interested users host banne ke liye apply kar sakte hain."
    )

async def earnings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Earning activity, time spent aur engagement par depend karti hai."
    )

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Support: @talkmitra_support"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("details", details))
    app.add_handler(CommandHandler("earnings", earnings))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    app.run_polling()

if __name__ == "__main__":
    main()