from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

# =========================
# 🔑 TOKEN
# =========================
TOKEN = os.getenv("BOT_TOKEN")


# =========================
# 🧠 MAIN CALCULATOR
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # 🧹 CLEAN INPUT
        line = line.replace(",", " ")
        line = re.sub(r"\.+", " ", line)

        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])

        expr = line.replace(nums[-1], "")
        expr = expr.replace("R", " R ")
        tokens = expr.split()

        # =========================
        # 🔴 အပူး
        # =========================
        if "အပူး" in line:
            total += 10 * amount
            continue

        # =========================
        # 🟣 ခွေပူး (n²)
        # =========================
        if "ခွေပူး" in line:
            digits = "".join(re.findall(r"\d", line.replace("ခွေပူး", "")))
            n = len(digits)

            total += (n * n) * amount
            continue

        # =========================
        # 🟢 ခွေ (n(n-1))
        # =========================
        if "ခွေ" in line and "ခွေပူး" not in line:
            digits = "".join(re.findall(r"\d", line.replace("ခွေ", "")))
            n = len(digits)

            total += (n * (n - 1)) * amount
            continue

        # =========================
        # 🔵 R CASE
        # =========================
        if "R" in line.upper():
            r_numbers = [t for t in tokens if t.isdigit()]
            total += len(r_numbers) * 2 * amount
            continue

        # =========================
        # 🟡 NORMAL
        # =========================
        nums_only = [t for t in tokens if t.isdigit()]
        total += len(nums_only) * amount

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

print("🚀 2D Bot Running (FINAL VERSION)")
app.run_polling()
