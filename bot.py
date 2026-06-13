from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

data_store = {}


# =========================
# 🧹 CLEAN FUNCTION (IMPORTANT FIX)
# =========================
def clean(line):
    line = line.replace(".", " ")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


# =========================
# 🧠 CALCULATOR
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = clean(line)
        if not line:
            continue

        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])

        # remove last number
        main = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

        # =========================
        # 🔥 R LOGIC FIXED (STABLE)
        # =========================
        if "R" in line.upper():
            nums_r = re.findall(r"\d+", line)

            # TYPE 2: 15 10000 R 20000
            if len(nums_r) == 3:
                total += int(nums_r[1]) + int(nums_r[2])
                continue

            # TYPE 1: 50 57 R 10000
            if len(nums_r) >= 2:
                count = len(nums_r) - 1
                total += count * 2 * amount
                continue

        # =========================
        # DEFAULT RULE
        # =========================
        total += len(nums) * amount

    return total


# =========================
# 🤖 MESSAGE HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])
    data_store[chat_id].append(text)

    total = calc(text)

    await update.message.reply_text(
        f"📊 Batch Total = {total:,}\n✔ Saved"
    )


# =========================
# 💰 TOTAL
# =========================
async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    history = data_store.get(chat_id, [])

    total = calc("\n".join(history))

    await update.message.reply_text(f"💰 TOTAL = {total:,}")


# =========================
# ♻️ RESET
# =========================
async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data_store[chat_id] = []
    await update.message.reply_text("♻️ RESET DONE")


# =========================
# 🚀 RUN
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("total", total_cmd))
app.add_handler(CommandHandler("reset", reset_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("🚀 BOT RUNNING...")
app.run_polling()
