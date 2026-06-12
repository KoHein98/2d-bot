from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 🧠 MEMORY STORE
# =========================
data_store = {}


# =========================
# 🧠 PARSER
# =========================
def parse_line(line):
    line = line.strip()
    line = re.sub(r"\.+", " ", line)
    line = re.sub(r"\s+", " ", line)

    nums = re.findall(r"\d+", line)
    if not nums:
        return None

    amount = int(nums[-1])

    # remove last number only
    clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1].strip()

    # extract numbers inside text
    numbers = re.findall(r"\d+", clean)

    return {
        "text": line,
        "amount": amount,
        "numbers": numbers
    }


# =========================
# 🤖 STORE MESSAGES
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])

    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            data_store[chat_id].append(parsed)

    await update.message.reply_text("✔ Saved")


# =========================
# 🔎 FILTER + TOTAL
# =========================
async def smart_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bets = data_store.get(chat_id, [])

    # =========================
    # FULL TOTAL
    # =========================
    if not context.args:
        total = sum(b["amount"] for b in bets)
        await update.message.reply_text(f"💰 TOTAL = {total:,}")
        return

    query = context.args[0]

    filtered = []
    total = 0

    # =========================
    # EXACT MATCH FILTER
    # =========================
    for b in bets:
        if query in b["numbers"]:
            filtered.append(b)
            total += b["amount"]

    if not filtered:
        await update.message.reply_text("❌ No match found")
        return

    # =========================
    # OUTPUT
    # =========================
    msg = f"📊 Filter: {query}\n\n"

    for b in filtered:
        msg += f"{b['text']} → {b['amount']:,}\n"

    msg += f"\n💰 Total = {total:,}"

    await update.message.reply_text(msg)


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("total", smart_total))

print("🚀 CLEAN FILTER BOT RUNNING...")
app.run_polling()
