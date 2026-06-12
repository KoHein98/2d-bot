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
# 🧠 PARSE BETS
# =========================
def parse_line(line):
    line = line.strip()
    line = re.sub(r"\.+", " ", line)
    line = re.sub(r"\s+", " ", line)

    nums = re.findall(r"\d+", line)
    if not nums:
        return None

    amount = int(nums[-1])
    clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

    numbers = re.findall(r"\d", clean)

    return {
        "text": line,
        "amount": amount,
        "clean": clean,
        "digits": numbers
    }


# =========================
# 🧠 CALC ALL
# =========================
def calc_all(bets):
    total = 0

    for b in bets:
        line = b["clean"]
        amount = b["amount"]

        if "အပူး" in line:
            total += 10 * amount
            continue

        if "ခွေပူး" in line:
            n = len(b["digits"])
            total += (n * n) * amount
            continue

        if "ခွေ" in line and "ခွေပူး" not in line:
            n = len(b["digits"])
            total += (n * (n - 1)) * amount
            continue

        if "R" in line.upper():
            nums_r = re.findall(r"\d+", line)
            total += len(nums_r) * 2 * amount
            continue

        total += len(b["digits"]) * amount

    return total


# =========================
# 🤖 MESSAGE HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])

    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            data_store[chat_id].append(parsed)

    total = calc_all(data_store[chat_id])

    await update.message.reply_text(
        f"📊 Added ✔\n💰 Current Total = {total:,}\n👉 /total <number> ရိုက်ပြီး search လုပ်နိုင်ပါတယ်"
    )


# =========================
# 📌 SMART TOTAL COMMAND
# =========================
async def smart_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    bets = data_store.get(chat_id, [])

    # no filter → full total
    if not context.args:
        total = calc_all(bets)
        await update.message.reply_text(f"💰 TOTAL = {total:,}")
        return

    query = context.args[0]

    filtered = []
    for b in bets:
        if query in b["clean"]:
            filtered.append(b)

    total = calc_all(filtered)

    # profit simulation (simple)
    p = total - (len(filtered) * 10000)

    await update.message.reply_text(
        f"📊 Number {query} Report\n"
        f"💰 Total = {total:,}\n"
        f"📈 P = {p:,}"
    )


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("total", smart_total))

print("🚀 SMART TOTAL BOT RUNNING...")
app.run_polling()
