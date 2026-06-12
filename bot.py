from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

# =========================
# 🔑 BOT TOKEN
# =========================
TOKEN = os.getenv("BOT_TOKEN")


# =========================
# 🧠 CLEAN CALCULATOR ENGINE
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # =========================
        # 🧹 NORMALIZE INPUT
        # =========================
        line = line.replace(",", " ")
        line = re.sub(r"\.+", " ", line)
        line = re.sub(r"\s+", " ", line)

        # 💰 extract numbers
        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])

        # remove ONLY last amount safely
        line_clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

        # =========================
        # 🔴 အပူး (00–99)
        # =========================
        if "အပူး" in line_clean:
            total += 10 * amount
            continue

        # =========================
        # 🟣 ခွေပူး (n² rule)
        # =========================
        if "ခွေပူး" in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            n = len(digits)

            total += (n * n) * amount
            continue

        # =========================
        # 🟢 ခွေ (n(n-1) rule)
        # =========================
        if "ခွေ" in line_clean and "ခွေပူး" not in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            n = len(digits)

            if n >= 2:
                total += (n * (n - 1)) * amount

            continue

        # =========================
        # 🔵 R CASE
        # =========================
        if "R" in line_clean.upper():
            r_numbers = re.findall(r"\d+", line_clean)
            total += len(r_numbers) * 2 * amount
            continue

        # =========================
        # 🟡 NORMAL CASE
        # =========================
        nums_only = re.findall(r"\d+", line_clean)
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

print("🚀 2D Bot Running (FINAL STABLE VERSION)")
app.run_polling()
