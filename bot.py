from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

def calc(text: str):
    total = 0

    # R format (17 R 20000)
    r_items = re.findall(r"(\d{2})\s*R\s*(\d+)", text)
    for num, amt in r_items:
        total += 2 * int(amt)

    # normal format (77 30000)
    plain = re.findall(r"(\d{2})\s+(\d+)", text)
    for num, amt in plain:
        total += int(amt)

    # အပူး
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
