from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

def calc(text: str):
    import re

    total = 0

    # 1️⃣ keep only digits, R, spaces
    text = re.sub(r"[^\dR\s]", " ", text)

    # 2️⃣ R format (50 R 10000)
    r_items = re.findall(r"(\d+)\s*R\s*(\d+)", text)
    for nums, amt in r_items:
        total += int(nums) * int(amt)

    # 3️⃣ remove R parts to avoid double count
    text = re.sub(r"\d+\s*R\s*\d+", " ", text)

    # 4️⃣ normal format (11 10000)
    plain = re.findall(r"(\d+)\s+(\d+)", text)
    for nums, amt in plain:
        total += int(nums) * int(amt)

    # 5️⃣ အပူး
    apu = re.findall(r"အပူး\s*(\d+)", text)
    for a in apu:
        total += 10 * int(a)

    return total



async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    total = calc(text)

    await update.message.reply_text(f"📊 Total = {total:,} MMK")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
