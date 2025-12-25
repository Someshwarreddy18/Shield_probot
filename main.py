import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram import ChatMember

# get token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found")

# spam keyword list (you can add more)
SPAM_KEYWORDS = [
    "assignment",
    "visa slot",
    "consultancy",
    "promotion",
    "promo",
    "nude",
    "naked",
    "sexy",
    "xxx",
    "forex",
    "bet",
    "loan",
    "crypto",
    "bitcoin",
    "dm me",
    "contact me",
]

# whitelist words to avoid blocking genuine students
SAFE_WORDS = [
    "assignment help needed genuinely",
    "university assignment discussion",
    "college work",
]


async def is_admin(update):
    member = await update.effective_chat.get_member(update.effective_user.id)
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]


async def handle_message(update, context):
    text = (update.message.text or "").lower()

    # ignore admins completely
    if await is_admin(update):
        return

    # allow approved safe expressions
    for word in SAFE_WORDS:
        if word in text:
            return

    # spam detection
    for bad in SPAM_KEYWORDS:
        if bad in text:
            await update.message.delete()
            try:
                await update.message.reply_text(
                    "Message removed. Spam or promotional content is not allowed."
                )
            except:
                pass
            return  # stop further checks


async def start_message(update, context):
    await update.message.reply_text("Shield ProBot is active and protecting your group 🙂")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # handle normal messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # health ping support (for render uptime)
    app.add_handler(MessageHandler(filters.COMMAND, start_message))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()

