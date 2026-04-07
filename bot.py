import json
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# =========================
# SETTINGS
# =========================
BOT_TOKEN = "8299086246:AAHgf4rqQMvPiOPAHymOH475vEAeJ-bNspU"
ADMIN_ID = 8260499617
LEADS_FILE = "leads.json"

# =========================
# MESSAGES
# =========================
PAYMENT_MESSAGE = (
    "✅ Your profile has been reviewed\n\n"
    "🎉 You are selected for the next process\n\n"
    "To continue, complete your registration now.\n\n"
    "💰 Registration Amount: ₹499\n\n"
    "🔗 Payment Link:\n"
    "https://payments.cashfree.com/forms/join-talkmitra\n\n"
    "📌 After payment, send screenshot here\n\n"
    "OR\n\n"
    "💬 Only serious candidates can DM:\n"
    "👉 @talkmitra_support\n\n"
    "⚠️ Limited slots available, complete your process today."
)

SELECT_MESSAGE = (
    "🎉 Congratulations!\n\n"
    "Your profile has been selected for the next step.\n"
    "Please stay active, further instructions coming soon."
)

REMINDER_MESSAGE = (
    "⏳ Reminder:\n\n"
    "We noticed you haven't completed your registration.\n\n"
    "If you are still interested, complete your payment today.\n\n"
    "Limited slots available."
)

AFTER_FORM_MESSAGE = (
    "✅ Thank you for submitting your details\n\n"
    "💸 Earning Details:\n"
    "Chat ₹5/min | Call ₹10/min\n\n"
    "📊 Daily Example:\n"
    "Earn ₹500–₹1000/day\n\n"
    "We will review your profile shortly."
)

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# STATES
# =========================
NAME, AGE, GENDER, EXPERIENCE = range(4)

# =========================
# FILE FUNCTIONS
# =========================
def load_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_leads(data):
    with open(LEADS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_lead(lead):
    data = load_leads()
    data.append(lead)
    save_leads(data)

def update_status(chat_id, status):
    data = load_leads()
    for lead in data:
        if str(lead["chat_id"]) == str(chat_id):
            lead["status"] = status
    save_leads(data)

# =========================
# USER FLOW
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your full name:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your age:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text(
        "Select gender:",
        reply_markup=ReplyKeyboardMarkup(
            [["Male", "Female"], ["Other"]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text(
        "Experience?",
        reply_markup=ReplyKeyboardMarkup(
            [["Fresher", "Experienced"]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return EXPERIENCE

async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text

    chat_id = update.effective_chat.id
    user = update.effective_user

    lead = {
        "name": context.user_data["name"],
        "age": context.user_data["age"],
        "gender": context.user_data["gender"],
        "experience": context.user_data["experience"],
        "chat_id": chat_id,
        "username": user.username,
        "status": "new",
    }

    add_lead(lead)

    admin_msg = f"""
🔥 New Lead

Name: {lead['name']}
Age: {lead['age']}
Gender: {lead['gender']}
Chat ID: {chat_id}
Status: new
"""

    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
    await update.message.reply_text(AFTER_FORM_MESSAGE, reply_markup=ReplyKeyboardRemove())

    context.user_data.clear()
    return ConversationHandler.END

# =========================
# ADMIN COMMANDS
# =========================
def is_admin(user_id):
    return user_id == ADMIN_ID

async def leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    data = load_leads()
    if not data:
        await update.message.reply_text("No leads.")
        return

    text = "Leads:\n\n"
    for l in data:
        text += f"{l['name']} | {l['chat_id']} | {l['status']}\n"

    await update.message.reply_text(text)

async def sendpayment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    chat_id = int(context.args[0])
    await context.bot.send_message(chat_id=chat_id, text=PAYMENT_MESSAGE)
    update_status(chat_id, "payment_sent")
    await update.message.reply_text("Payment sent")

async def sendselect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    chat_id = int(context.args[0])
    await context.bot.send_message(chat_id=chat_id, text=SELECT_MESSAGE)
    update_status(chat_id, "selected")
    await update.message.reply_text("Selected msg sent")

async def sendreminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    chat_id = int(context.args[0])
    await context.bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)
    await update.message.reply_text("Reminder sent")

async def sendcustom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    chat_id = int(context.args[0])
    msg = " ".join(context.args[1:])
    await context.bot.send_message(chat_id=chat_id, text=msg)
    await update.message.reply_text("Custom sent")

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)

    app.add_handler(CommandHandler("leads", leads))
    app.add_handler(CommandHandler("sendpayment", sendpayment))
    app.add_handler(CommandHandler("sendselect", sendselect))
    app.add_handler(CommandHandler("sendreminder", sendreminder))
    app.add_handler(CommandHandler("sendcustom", sendcustom))

    app.run_polling()

if __name__ == "__main__":
    main()