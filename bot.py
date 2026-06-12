from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 🧠 STORE RAW TEXT ONLY
# =========================
data_store = {}


# =========================
# 🧹 CLEAN LINE
# =========================
def clean_text(text):
    text = text.replace("..", " ")
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# 🧠 PARSE MESSAGE
# =========================
def parse_line(line):
    line = clean_text(line)

    nums = re.findall(r"\d+", line)
    if not nums:
        return None

    amount = int(nums[-1])

    # remove last number (stake)
    main_part = line[::-1].replace(nums[-1][::-1], "", 1)[::-1].strip()

    numbers = re.findall(r"\d+", main_part)

    return {
        "numbers": numbers,
        "amount": amount
    }


# =========================
# 🤖 MESSAGE HANDLER
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

    await update.message.reply_text("✔ Saved")


# =========================
# 🔎 FILTER: NUMBER → AMOUNT
# =========================
def map_number(data, query):
    results = []
    total = 0

    for item in data:
        if query in item["numbers"]:
            results.append(f"{query} → {item['amount']:,}")
            total += item["amount"]

    return results, total


# =========================
# 📌 /total COMMAND
# =========================
async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = data_store.get(chat_id, [])

    if not context.args:
        await update.message.reply_text("❌ Please enter number (/total 11)")
        return

    query = context.args[0]

    results, total = map_number(data, query)

    if not results:
        await update.message.reply_text("❌ No match found")
        return

    msg = "📊 RESULT\n\n"
    msg += "\n".join(results)
    msg += f"\n\n💰 Total = {total:,}"

    await update.message.reply_text(msg)


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("total", total_cmd))

print("🚀 FINAL NUMBER MAPPING BOT RUNNING...")
app.run_polling()
