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
# 🧠 CALCULATOR
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"\.+", " ", line)
        line = re.sub(r"\s+", " ", line)

        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])
        line_clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

        if "အပူး" in line_clean:
            total += 10 * amount
            continue

        if "ခွေပူး" in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            total += (len(digits) ** 2) * amount
            continue

        if "ခွေ" in line_clean and "ခွေပူး" not in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            total += (len(digits) * (len(digits) - 1)) * amount
            continue

        if "R" in line_clean.upper():
            nums_r = re.findall(r"\d+", line_clean)
            total += len(nums_r) * 2 * amount
            continue

        nums_only = re.findall(r"\d+", line_clean)
        total += len(nums_only) * amount

    return total


# =========================
# 🤖 MESSAGE HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    total = calc(text)

    data_store.setdefault(chat_id, 0)
    data_store[chat_id] += total

    await update.message.reply_text(
        f"📊 Batch Total = {total:,}\n👉 /total ရိုက်ပြီးစုကြည့်နိုင်ပါတယ်"
    )


# =========================
# 📌 TOTAL COMMAND
# =========================
async def show_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    total = data_store.get(chat_id, 0)

    await update.message.reply_text(f"💰 TOTAL = {total:,} MMK")


# =========================
# 🔄 RESET COMMAND
# =========================
async def reset_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data_store[chat_id] = 0

    await update.message.reply_text("♻️ TOTAL RESET DONE")


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("total", show_total))
app.add_handler(CommandHandler("reset", reset_total))

print("🚀 TOTAL COMMAND BOT RUNNING...")
app.run_polling()
