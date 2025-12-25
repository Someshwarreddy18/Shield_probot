 import time
import re
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)

BOT_TOKEN = "8440794283:AAFMYpxCcQfGkz61hwK6IwTfrFOQDKkP1iA"

MAX_WARNINGS = 2
FLOOD_LIMIT = 6
FLOOD_TIME = 10

WARNINGS = {}
MESSAGE_LOG = {}

# ---------- normalize text ----------
def normalize(text: str):
    text = text.lower()
    conv = {
        "0": "o", "1": "i", "!": "i",
        "3": "e", "4": "a", "@": "a",
        "5": "s", "$": "s", "7": "t"
    }
    for k, v in conv.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-z0-9]", "", text)
    return text

# ---------- admin and owner check ----------
async def is_admin_or_owner(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    member = await context.bot.get_chat_member(chat_id, user_id)

    # creator = group owner
    if member.status == "creator":
        return True

    # admin
    if member.status == "administrator":
        return True

    return False

# ---------- safe normal student words ----------
SAFE_STUDENT_WORDS = [
    "how",
    "what",
    "when",
    "help",
    "info",
    "process",
    "status",
    "refusal",
    "reschedule",
    "anyone",
    "doubt",
    "suggest",
]

# ---------- high-risk scam selling indicators ----------
HIGH_RISK_SELLING_PATTERNS = [
    "paymentafterconfirmation",
    "lowcostcharges",
    "100genuine",
    "verygenuine",
    "slotavailable",
    "slotbooking",
    "earlyslo",
    "pingme",
    "dmme",
    "contactme",
    "charges",
    "service",
]

# ---------- instant ban scam types ----------
INSTANT_BAN_WORDS = [
    "usdt",
    "crypto",
    "trc20",
    "binance",
    "upworkaccount",
    "accountrent",
]

# ---------- commands ----------
async def start(update, context):
    await update.message.reply_text(
        "🛡️ Shield Bot active.\n"
        "Admins and owner have full freedom.\n"
        "Only spammers will be restricted."
    )

# ---------- spam filter ----------
async def spam_filter(update, context):
    msg = update.message or update.edited_message
    if not msg or not msg.text:
        return

    # 100 percent ignore ADMINS & OWNER
    if await is_admin_or_owner(update, context):
        return

    text = msg.text
    clean = normalize(text)

    # allow normal student talk
    for ok in SAFE_STUDENT_WORDS:
        if ok in clean:
            return

    # new users treated stricter
    member = await context.bot.get_chat_member(msg.chat.id, msg.from_user.id)
    is_new = False
    if member.joined_date:
        if datetime.utcnow() - member.joined_date < timedelta(days=3):
            is_new = True

    # instant-ban scam types
    for w in INSTANT_BAN_WORDS:
        if w in clean:
            await msg.delete()
            await context.bot.ban_chat_member(msg.chat.id, msg.from_user.id)
            return

    # selling pattern detection
    selling = False
    if "slot" in clean or "visaslot" in clean:
        for w in HIGH_RISK_SELLING_PATTERNS:
            if w in clean:
                selling = True

    if selling:

        # brand-new account selling → instant ban
        if is_new:
            await msg.delete()
            await context.bot.ban_chat_member(msg.chat.id, msg.from_user.id)
            return

        # otherwise warning then ban
        uid = str(msg.from_user.id)
        WARNINGS[uid] = WARNINGS.get(uid, 0) + 1

        await msg.delete()

        if WARNINGS[uid] >= MAX_WARNINGS:
            await context.bot.ban_chat_member(msg.chat.id, msg.from_user.id)
        else:
            await msg.chat.send_message(
                f"{msg.from_user.first_name}, promotions are not allowed. "
                "This is a warning. Repeating this will cause a ban."
            )

# ---------- flood control ----------
async def anti_flood(update, context):
    # admins and owner totally free
    if await is_admin_or_owner(update, context):
        return

    uid = update.message.from_user.id
    now = time.time()

    MESSAGE_LOG.setdefault(uid, [])
    MESSAGE_LOG[uid] = [t for t in MESSAGE_LOG[uid] if now - t < FLOOD_TIME]
    MESSAGE_LOG[uid].append(now)

    if len(MESSAGE_LOG[uid]) > FLOOD_LIMIT:
        await update.message.delete()
        await context.bot.restrict_chat_member(
            update.message.chat_id,
            uid,
            ChatPermissions(can_send_messages=False),
            until_date=int(now + 300)
        )

# ---------- main ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, spam_filter))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_flood))

    print("🛡️ Shield Bot running… Admins and owner fully free")
    app.run_polling()

if __name__ == "__main__":
    main()
