from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")


# =========================
# 🧠 EXACT 2D LOGIC (FIXED)
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # 💰 amount (last number)
        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])

        expr = line.replace(nums[-1], "")
        expr = expr.replace(".", " ").replace(",", " ")
        tokens = expr.split()

        # =========================
        # 🔵 R CASE
        # =========================
        if "R" in expr.upper():
            r_numbers = []

            for t in tokens:
                t = t.replace("R", "")
                if t.isdigit():
                    r_numbers.append(t)

            # each R number = 2 directions
            pairs = len(r_numbers) * 2
            total += pairs * amount
            continue

        # =========================
        # 🟡 NORMAL / APUE / CHOE
        # =========================
        nums_only = [t for t in tokens if t.isdigit()]

        n = len(nums_only)

        if n == 0:
            continue

        # IMPORTANT FIX:
        # 2 numbers → always 2 pairs (A↔B + B↔A)
        if n == 2:
            pairs = 2
        else:
            pairs = n * (n - 1)

        total += pairs * amount

    return total


# =========================
# 🤖 HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    total = calc(text)

    await update.message.reply_text(f"📊 Total = {total:,} MMK")


# =========================
# 🚀 RUN
# =========================
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("✅ 2D Bot Running...")
app.run_polling()
