from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 🧠 MEMORY
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
    clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1].strip()

    numbers = re.findall(r"\d+", clean)

    return {
        "text": line,
        "amount": amount,
        "numbers": numbers
    }


# =========================
# 🤖 STORE + MESSAGE TOTAL
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])

    parsed_lines = []

    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            parsed_lines.append(parsed)
            data_store[chat_id].append(parsed)

    # message total
    msg_total = sum(b["amount"] for b in parsed_lines)

    await update.message.reply_text(
        f"📊 Message Total = {msg_total:,}\n✔ Saved"
    )


# =========================
# 🔎 TOTAL COMMAND (ALL + FILTER)
# =========================
async def smart_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bets = data_store.get(chat_id, [])

    # =========================
    # 🟢 ALL TOTAL
    # =========================
    if not context.args:
        total = sum(b["amount"] for b in bets)
        await update.message.reply_text(f"💰 ALL TOTAL = {total:,}")
        return

    # =========================
    # 🟡 FILTER TOTAL
    # =========================
    query = context.args[0]

    filtered = []
    total = 0

    for b in bets:
        if query in b["numbers"]:
            filtered.append(b)
            total += b["amount"]

    if not filtered:
        await update.message.reply_text("❌ No match found")
        return

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

print("🚀 FINAL ALL-TOTAL BOT RUNNING...")
app.run_polling()
