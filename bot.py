from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

data_store = {}


# =========================
# 🧹 CLEAN
# =========================
def clean_text(text):
    text = text.replace("..", " ")
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# 🧠 PARSE
# =========================
def parse_line(line):
    line = clean_text(line)

    nums = re.findall(r"\d+", line)
    if not nums:
        return None

    amount = int(nums[-1])

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

    batch = []

    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            batch.append(parsed)
            data_store[chat_id].append(parsed)

    batch_total = sum(b["amount"] for b in batch)

    await update.message.reply_text(
        f"📊 Batch Total = {batch_total:,}\n✔ Saved"
    )


# =========================
# 🔎 TOTAL COMMAND
# =========================
async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = data_store.get(chat_id, [])

    # =========================
    # 🟢 GRAND TOTAL
    # =========================
    if not context.args:
        grand_total = sum(b["amount"] for b in data)
        await update.message.reply_text(f"💰 GRAND TOTAL = {grand_total:,}")
        return

    # =========================
    # 🟡 FILTER MODE
    # =========================
    query = context.args[0]

    results = []
    total = 0

    for item in data:
        if query in item["numbers"]:
            results.append(f"{query} → {item['amount']:,}")
            total += item["amount"]

    if not results:
        await update.message.reply_text("❌ No match found")
        return

    msg = "📊 RESULT\n\n"
    msg += "\n".join(results)
    msg += f"\n\n💰 Total = {total:,}"

    await update.message.reply_text(msg)


# =========================
# 🚀 RUN
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("total", total_cmd))

print("🚀 BOT RUNNING WITH GRAND TOTAL + FILTER")
app.run_polling()
