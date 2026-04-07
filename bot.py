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

PAYMENT_LINK = "https://payments.cashfree.com/forms/join-talkmitra"
SUPPORT_TELEGRAM = "@talkmitra_support"

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =========================
# STATES
# =========================
NAME, AGE, GENDER, EXPERIENCE = range(4)

# =========================
# FILE HELPERS
# =========================
def load_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Error loading leads: {e}")
        return []

def save_leads(leads):
    try:
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving leads: {e}")

def add_lead(lead):
    leads = load_leads()
    leads.append(lead)
    save_leads(leads)

def find_lead(chat_id):
    leads = load_leads()
    for lead in leads:
        if str(lead.get("chat_id")) == str(chat_id):
            return lead
    return None

def update_lead_status(chat_id, status):
    leads = load_leads()
    updated = False
    for lead in leads:
        if str(lead.get("chat_id")) == str(chat_id):
            lead["status"] = status
            updated = True
            break
    if updated:
        save_leads(leads)
    return updated

def update_lead_field(chat_id, field_name, value):
    leads = load_leads()
    updated = False
    for lead in leads:
        if str(lead.get("chat_id")) == str(chat_id):
            lead[field_name] = value
            updated = True
            break
    if updated:
        save_leads(leads)
    return updated

# =========================
# HELPERS
# =========================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def username_text(user):
    return f"@{user.username}" if user.username else "No username"

def build_payment_message():
    return (
        "✅ Your profile has been reviewed\n\n"
        "🎉 You are selected for the next process\n\n"
        "To continue, complete your registration now.\n\n"
        "💰 Registration Amount: ₹499\n\n"
        f"🔗 Payment Link:\n{PAYMENT_LINK}\n\n"
        "📌 After payment, send screenshot here.\n\n"
        "OR\n\n"
        "💬 Only serious candidates can DM:\n"
        f"👉 {SUPPORT_TELEGRAM}\n\n"
        "⚠️ Limited slots available, complete your process today."
    )

def build_select_message():
    return (
        "🎉 Congratulations!\n\n"
        "Your profile has been shortlisted for the next step.\n\n"
        "Please stay active here. Further instructions will be shared shortly."
    )

def build_reminder_message():
    return (
        "⏳ Reminder\n\n"
        "We noticed you have not completed your next step yet.\n\n"
        "If you are still interested, complete your registration today.\n\n"
        f"🔗 Payment Link:\n{PAYMENT_LINK}\n\n"
        f"💬 Support: {SUPPORT_TELEGRAM}"
    )

# =========================
# USER FLOW
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Welcome to TalkMitra Application Bot\n\n"
        "Please fill your details step by step.\n\n"
        "First, enter your full name:"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data["name"] = name

    await update.message.reply_text("Please enter your age:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text.strip()
    context.user_data["age"] = age

    await update.message.reply_text(
        "Please select your gender:",
        reply_markup=ReplyKeyboardMarkup(
            [["Male", "Female"], ["Other"]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text.strip()
    context.user_data["gender"] = gender

    await update.message.reply_text(
        "Do you have any experience?",
        reply_markup=ReplyKeyboardMarkup(
            [["Fresher", "Experienced"]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return EXPERIENCE

async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    experience = update.message.text.strip()
    context.user_data["experience"] = experience

    user = update.effective_user
    chat_id = update.effective_chat.id

    lead = {
        "name": context.user_data.get("name", ""),
        "age": context.user_data.get("age", ""),
        "gender": context.user_data.get("gender", ""),
        "experience": context.user_data.get("experience", ""),
        "chat_id": chat_id,
        "username": user.username if user.username else "",
        "first_name": user.first_name if user.first_name else "",
        "last_name": user.last_name if user.last_name else "",
        "status": "new",
        "interested": "pending",
    }

    add_lead(lead)

    admin_msg = (
        "🔥 New Lead Received\n\n"
        f"Name: {lead['name']}\n"
        f"Age: {lead['age']}\n"
        f"Gender: {lead['gender']}\n"
        f"Experience: {lead['experience']}\n"
        f"Username: {username_text(user)}\n"
        f"Chat ID: {chat_id}\n"
        f"Status: {lead['status']}\n"
        f"Interested: {lead['interested']}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
    except Exception as e:
        logger.error(f"Error sending admin message: {e}")

    await update.message.reply_text(
        "✅ Thank you for submitting your details.\n\n"
        "Our team is reviewing your profile now.",
        reply_markup=ReplyKeyboardRemove(),
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "💸 Earning Details\n\n"
            "💬 Chat: ₹5 per minute\n"
            "📞 Voice Call: ₹10 per minute\n\n"
            "📊 Example:\n"
            "• 60 min chat = ₹300\n"
            "• 30 min voice call = ₹300\n"
            "• Total daily = ₹600+\n\n"
            "✅ Active and serious users can earn more."
        ),
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "⚠️ We are currently selecting limited candidates only.\n\n"
            "Your profile looks suitable for this opportunity."
        ),
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "👉 If you want to continue, reply with:\n\n"
            "YES"
        ),
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Application cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# =========================
# YES / SCREENSHOT / GENERAL USER REPLIES
# =========================
async def normal_user_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Ignore admin in this handler
    if is_admin(user.id):
        return

    lead = find_lead(chat_id)

    if text.upper() == "YES":
        if lead:
            update_lead_status(chat_id, "interested")
            update_lead_field(chat_id, "interested", "yes")

        await update.message.reply_text(
            "🔥 Great!\n\n"
            "You are now moved to the next step.\n\n"
            "Our team may send you the registration/payment process shortly.\n"
            "Please stay active here."
        )

        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "✅ Lead Replied YES\n\n"
                    f"Name: {lead.get('name', 'Unknown') if lead else 'Unknown'}\n"
                    f"Username: {username_text(user)}\n"
                    f"Chat ID: {chat_id}\n"
                    "Status updated: interested"
                ),
            )
        except Exception as e:
            logger.error(f"Error sending YES admin message: {e}")
        return

    lower_text = text.lower()

    if "screenshot" in lower_text or "paid" in lower_text or "payment done" in lower_text:
        if lead:
            update_lead_status(chat_id, "payment_claimed")

        await update.message.reply_text(
            "✅ Thank you.\n\n"
            "Our team will verify your payment and get back to you shortly."
        )

        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "💰 User Sent Payment-Related Message\n\n"
                    f"Name: {lead.get('name', 'Unknown') if lead else 'Unknown'}\n"
                    f"Username: {username_text(user)}\n"
                    f"Chat ID: {chat_id}\n"
                    f"Message: {text}"
                ),
            )
        except Exception as e:
            logger.error(f"Error notifying admin for payment claim: {e}")
        return

    # Generic user reply after form
    if lead:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "📩 User Message Received\n\n"
                    f"Name: {lead.get('name', 'Unknown')}\n"
                    f"Username: {username_text(user)}\n"
                    f"Chat ID: {chat_id}\n"
                    f"Message: {text}"
                ),
            )
        except Exception as e:
            logger.error(f"Error forwarding user message to admin: {e}")

        await update.message.reply_text(
            "Thanks for your message.\n\n"
            "Our team will guide you here shortly.\n"
            f"If urgent, you can also contact: {SUPPORT_TELEGRAM}"
        )
    else:
        await update.message.reply_text(
            "Please use /start to begin your application."
        )

# =========================
# PHOTO / SCREENSHOT HANDLER
# =========================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if is_admin(user.id):
        return

    lead = find_lead(chat_id)
    if lead:
        update_lead_status(chat_id, "screenshot_sent")

    await update.message.reply_text(
        "✅ Screenshot received.\n\n"
        "Our team will verify it and update you shortly."
    )

    try:
        caption_text = (
            "📸 Payment Screenshot Received\n\n"
            f"Name: {lead.get('name', 'Unknown') if lead else 'Unknown'}\n"
            f"Username: {username_text(user)}\n"
            f"Chat ID: {chat_id}\n"
            "Please review this screenshot."
        )

        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_id,
                caption=caption_text
            )
    except Exception as e:
        logger.error(f"Error forwarding screenshot to admin: {e}")

# =========================
# ADMIN COMMANDS
# =========================
async def leads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    all_leads = load_leads()

    if not all_leads:
        await update.message.reply_text("No leads found.")
        return

    messages = []
    current = "📋 Saved Leads\n\n"

    for i, lead in enumerate(all_leads, start=1):
        line = (
            f"{i}. {lead.get('name', '')} | "
            f"Age: {lead.get('age', '')} | "
            f"Gender: {lead.get('gender', '')} | "
            f"Chat ID: {lead.get('chat_id', '')} | "
            f"Status: {lead.get('status', 'new')}\n"
        )

        if len(current) + len(line) > 3500:
            messages.append(current)
            current = line
        else:
            current += line

    if current:
        messages.append(current)

    for msg in messages:
        await update.message.reply_text(msg)

async def sendselect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /sendselect chat_id")
        return

    try:
        chat_id = int(context.args[0])
        await context.bot.send_message(chat_id=chat_id, text=build_select_message())
        update_lead_status(chat_id, "selected")
        await update.message.reply_text("✅ Selection message sent.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def sendpayment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /sendpayment chat_id")
        return

    try:
        chat_id = int(context.args[0])
        await context.bot.send_message(chat_id=chat_id, text=build_payment_message())
        update_lead_status(chat_id, "payment_sent")
        await update.message.reply_text("✅ Payment message sent.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def sendreminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /sendreminder chat_id")
        return

    try:
        chat_id = int(context.args[0])
        await context.bot.send_message(chat_id=chat_id, text=build_reminder_message())
        update_lead_status(chat_id, "reminder_sent")
        await update.message.reply_text("✅ Reminder message sent.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def sendcustom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /sendcustom chat_id your message")
        return

    try:
        chat_id = int(context.args[0])
        msg = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=chat_id, text=msg)
        update_lead_status(chat_id, "custom_sent")
        await update.message.reply_text("✅ Custom message sent.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def helpadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    help_text = (
        "🛠 Admin Commands\n\n"
        "/leads - Show all leads\n"
        "/sendselect chat_id - Send shortlisted message\n"
        "/sendpayment chat_id - Send payment message\n"
        "/sendreminder chat_id - Send reminder\n"
        "/sendcustom chat_id your message - Send custom message\n"
        "/helpadmin - Show this menu\n\n"
        "Example:\n"
        "/sendpayment 123456789\n"
        "/sendcustom 123456789 Hello, complete payment and send screenshot."
    )
    await update.message.reply_text(help_text)

# =========================
# MAIN
# =========================
def main():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("ERROR: Please paste your real bot token in BOT_TOKEN.")
        return

    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    # Admin commands
    app.add_handler(CommandHandler("leads", leads_command))
    app.add_handler(CommandHandler("sendselect", sendselect_command))
    app.add_handler(CommandHandler("sendpayment", sendpayment_command))
    app.add_handler(CommandHandler("sendreminder", sendreminder_command))
    app.add_handler(CommandHandler("sendcustom", sendcustom_command))
    app.add_handler(CommandHandler("helpadmin", helpadmin_command))

    # User screenshot handler
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # General user replies like YES / payment done / others
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, normal_user_reply))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()