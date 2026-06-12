from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

def calc(text: str):
    total = 0

    text = text.replace(".", " ")

    r_items = re.findall(r"(\d+)\s*R\s*(\d+)", text)
    for nums, amt in r_items:
        total += int(nums) * int(amt)

    plain = re.findall(r"(\d+)\s+(\d+)", text)
    for nums, amt in plain:
        total += int(nums) * int(amt)

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
