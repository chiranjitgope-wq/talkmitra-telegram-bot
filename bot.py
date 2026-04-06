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
# Render keep-alive server
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
# Bot Token
# =========================
TOKEN = "8299086246:AAHgf4rqQMvPiOPAHymOH475vEAeJ-bNspU"

# =========================
# Conversation States
# =========================
NAME, AGE, GENDER, CITY, EXPERIENCE, TIME, CONFIRM = range(7)

# =========================
# Start Command
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to TalkMitra Bot\n\n"
        "Yaha aapse kuch basic details alag alag puchi jayengi.\n"
        "Please sahi information dijiye.\n\n"
        "Sabse pehle,\n"
        "📝 Aapka naam kya hai?"
    )
    await update.message.reply_text(welcome_text)
    return NAME

# =========================
# Name
# =========================
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("🎂 Aapki age kya hai?")
    return AGE

# =========================
# Age
# =========================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text.strip()

    if not age.isdigit():
        await update.message.reply_text("⚠️ Please sirf number me age likhiye.\n\nExample: 21")
        return AGE

    context.user_data["age"] = age

    gender_keyboard = [["Male", "Female"], ["Other"]]
    await update.message.reply_text(
        "👤 Aapka gender select kijiye:",
        reply_markup=ReplyKeyboardMarkup(gender_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return GENDER

# =========================
# Gender
# =========================
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text.strip()
    await update.message.reply_text(
        "🏙️ Aap kis city se ho?",
        reply_markup=ReplyKeyboardRemove()
    )
    return CITY

# =========================
# City
# =========================
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text.strip()

    exp_keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        "💬 Kya aapko chatting ya calling ka experience hai?",
        reply_markup=ReplyKeyboardMarkup(exp_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return EXPERIENCE

# =========================
# Experience
# =========================
async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text.strip()

    time_keyboard = [["1 Hour", "2 Hours"], ["3 Hours", "4+ Hours"]]
    await update.message.reply_text(
        "⏰ Aap daily kitna time de sakte ho?",
        reply_markup=ReplyKeyboardMarkup(time_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return TIME

# =========================
# Time + Earning Details
# =========================
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text.strip()

    earning_text = (
        "💸 Earning Details\n\n"
        "💬 Chat earning: ₹5 per minute\n"
        "📞 Voice call earning: ₹10 per minute\n\n"
        "📌 Example 1:\n"
        "10 min chat = ₹50\n"
        "10 min voice call = ₹100\n"
        "Total = ₹150\n\n"
        "📌 Example 2:\n"
        "20 min chat = ₹100\n"
        "15 min voice call = ₹150\n"
        "Total = ₹250\n\n"
        "📌 Example 3:\n"
        "30 min chat = ₹150\n"
        "20 min voice call = ₹200\n"
        "Total = ₹350\n\n"
        "📅 Monthly Example:\n"
        "Daily ₹150 = ₹4500/month\n"
        "Daily ₹250 = ₹7500/month\n"
        "Daily ₹350 = ₹10500/month\n\n"
        "Note: Earnings depend on your activity, availability, and user engagement.\n\n"
        "✅ Kya aap process continue karna chahte ho?"
    )

    confirm_keyboard = [["Yes, Continue", "No"]]
    await update.message.reply_text(
        earning_text,
        reply_markup=ReplyKeyboardMarkup(confirm_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return CONFIRM

# =========================
# Final Confirm
# =========================
async def confirm_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.strip()
    context.user_data["confirm"] = answer

    if answer.lower() == "no":
        await update.message.reply_text(
            "ठीक hai 👍\nAgar future me interest ho to dubara /start bhej sakte ho.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    summary = (
        "✅ Thank you for submitting your details.\n\n"
        "📋 Your Details:\n"
        f"Name: {context.user_data.get('name', '')}\n"
        f"Age: {context.user_data.get('age', '')}\n"
        f"Gender: {context.user_data.get('gender', '')}\n"
        f"City: {context.user_data.get('city', '')}\n"
        f"Experience: {context.user_data.get('experience', '')}\n"
        f"Available Time: {context.user_data.get('time', '')}\n\n"
        "Our team will review your response.\n\n"
        "If you are selected for the next step, you will receive joining/process details soon.\n\n"
        "📩 Please stay active and reply properly during the process."
    )

    await update.message.reply_text(summary, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# =========================
# Cancel Command
# =========================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Process cancelled.\nAgar dubara start karna ho to /start bhejo.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# =========================
# Main Function
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
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

    app.add_handler(conv_handler)

    print("Bot started successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()