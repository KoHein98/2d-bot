from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

# 🔑 Bot Token (environment variable)
TOKEN = os.getenv("BOT_TOKEN")


# =========================
# 📊 2D CALCULATOR LOGIC
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # =========================
        # 🔴 အပူး (00-99 = 10 pairs)
        # =========================
        if "အပူး" in line:
            nums = re.findall(r"\d+", line)
            if nums:
                amount = int(nums[0])
                total += amount * 10
            continue

        # =========================
        # 🟡 ခွေ (e.g. 789 = 6 pairs)
        # =========================
        if "ခွေ" in line:
            nums = re.findall(r"\d+", line)
            if len(nums) >= 2:
                wheel = nums[0]
                amount = int(nums[1])

                pairs = len(set(
                    wheel[i] + wheel[j]
                    for i in range(len(wheel))
                    for j in range(len(wheel))
                    if i != j
                ))

                total += pairs * amount
            continue

        # =========================
        # 🔵 Reverse (R)
        # =========================
        if "R" in line.upper():
            nums = re.findall(r"\d+", line)
            if len(nums) >= 2:
                amount = int(nums[-1])
                total += amount * 2
            continue

        # =========================
        # ⚪ Normal (52 20000)
        # =========================
        nums = re.findall(r"\d+", line)
        if len(nums) >= 2:
            total += int(nums[-1])

    return total


# =========================
# 🤖 TELEGRAM HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    total = calc(text)

    await update.message.reply_text(
        f"📊 Total = {total:,} MMK"
    )


# =========================
# 🚀 START BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("Bot is running...")
app.run_polling()
