import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram import ChatMember

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found")

SPAM_KEYWORDS = [
    "assignment",
    "assigment",
    "visa",
    "visa slot",
    "consultancy",
    "consultant",
    "promotion",
    "promo",
    "ads",
    "advertise",
    "loan",
    "bet",
    "forex",
    "crypto",
    "bitcoin",
    "nude",
    "sex",
    "sexy",
    "xxx",
    "dm me",
    "contact me"
]

SAFE_WORDS = [
    "discussion",
    "student",
    "college",
    "genuine help"
]

async def is_admin(update):
    member = await update.effective_chat.get_member(update.effective_user.id)
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]

async def handle_message(update, context):
    text = (update.message.text or "").lower()

    if await is_admin(update):
        return

    for word in SAFE_WORDS:
        if word in text:
            return

    for bad in SPAM_KEYWORDS:
        if bad in text:
            await update.message.delete()
            return

async def start(update, context):
    await update.message.reply_text("Shield ProBot is active 🙂")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()

