from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")


# =========================
# 🧠 SMART PARSER ENGINE
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # =========================
        # 💰 extract amount (last number in line)
        # =========================
        amounts = re.findall(r"\d+", line)
        if not amounts:
            continue

        amount = int(amounts[-1])

        # remove amount from line
        expr = line.replace(amounts[-1], "").strip()

        # normalize separators
        expr = expr.replace(",", " ").replace(".", " ")
        tokens = expr.split()

        # =========================
        # 🔵 CASE 1: R MODE
        # =========================
        if "R" in expr.upper():
            pairs = 0

            for t in tokens:
                t = t.replace("R", "").strip()

                if t.isdigit():
                    # each R number gives reverse pair = 2
                    pairs += 2

            total += pairs * amount
            continue

        # =========================
        # 🟡 CASE 2: NORMAL / APUE / CHOE
        # =========================
        nums = [t for t in tokens if t.isdigit()]

        n = len(nums)

        if n == 0:
            continue

        # 2-digit combinations logic
        if n == 1:
            pairs = 1
        else:
            pairs = n * (n - 1)

        total += pairs * amount

    return total


# =========================
# 🤖 TELEGRAM HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    total = calc(text)

    await update.message.reply_text(f"📊 Total = {total:,} MMK")


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("🚀 Smart 2D Bot Running...")
app.run_polling()
