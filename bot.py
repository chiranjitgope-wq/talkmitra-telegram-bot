from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# =========================
# Render Server (IMPORTANT)
# =========================
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# =========================
# BOT CONFIG
# =========================
TOKEN = "8299086246:AAHgf4rqQMvPiOPAHymOH475vEAeJ-bNspU"
ADMIN_ID = 8260499617

# =========================
# STATES
# =========================
NAME, AGE, GENDER, CITY, EXPERIENCE, TIME, CONFIRM = range(7)

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to TalkMitra\n\n"
        "Process start karne ke liye kuch details deni hogi.\n\n"
        "📝 Aapka naam kya hai?"
    )
    return NAME

# =========================
# NAME
# =========================
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🎂 Aapki age kya hai?")
    return AGE

# =========================
# AGE
# =========================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    keyboard = [["Male", "Female"], ["Other"]]
    await update.message.reply_text(
        "👤 Aapka gender select kare:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return GENDER

# =========================
# GENDER
# =========================
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("🏙️ Aap kis city se ho?", reply_markup=ReplyKeyboardRemove())
    return CITY

# =========================
# CITY
# =========================
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        "💬 Kya aapko chatting/calling ka experience hai?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return EXPERIENCE

# =========================
# EXPERIENCE
# =========================
async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text

    keyboard = [["1 Hour", "2 Hours"], ["3 Hours", "4+ Hours"]]
    await update.message.reply_text(
        "⏰ Aap daily kitna time de sakte ho?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return TIME

# =========================
# TIME + EARNING
# =========================
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text

    await update.message.reply_text(
        "💸 Earning Details\n\n"
        "💬 Chat: ₹5 per minute\n"
        "📞 Voice Call: ₹10 per minute\n\n"
        "📌 Example:\n"
        "10 min chat = ₹50\n"
        "10 min call = ₹100\n"
        "Total = ₹150\n\n"
        "📅 Monthly potential:\n"
        "₹150/day = ₹4500\n"
        "₹250/day = ₹7500\n"
        "₹350/day = ₹10500\n\n"
        "⚠️ Limited slots only\n\n"
        "✅ Continue karna chahte ho?"
    )

    keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        "Select option:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return CONFIRM

# =========================
# FINAL
# =========================
async def confirm_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "no":
        await update.message.reply_text("Thik hai 👍", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # USER SUMMARY
    await update.message.reply_text(
        "✅ Thank you! Aapka profile review me hai.\n\n"
        "Agar select hue to next step bheja jayega.",
        reply_markup=ReplyKeyboardRemove()
    )

    # ADMIN MESSAGE
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🚀 New Lead\n\n"
            f"Name: {context.user_data.get('name')}\n"
            f"Age: {context.user_data.get('age')}\n"
            f"Gender: {context.user_data.get('gender')}\n"
            f"City: {context.user_data.get('city')}\n"
            f"Experience: {context.user_data.get('experience')}\n"
            f"Time: {context.user_data.get('time')}\n"
            f"User ID: {update.effective_user.id}"
        )
    )

    return ConversationHandler.END

# =========================
# CANCEL
# =========================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled ❌", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_process)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()