from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")


def calc(text: str):
    total = 0

    # split lines only (NO guessing, NO messy parsing)
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # R format → 50 R 10000
        m = re.match(r"^(\d+)\s*R\s*(\d+)$", line)
        if m:
            total += int(m.group(1)) * int(m.group(2))
            continue

        # normal format → 2 10000
        m = re.match(r"^(\d+)\s+(\d+)$", line)
        if m:
            total += int(m.group(1)) * int(m.group(2))
            continue

        # အပူး → အပူး 5
        m = re.match(r"^အပူး\s*(\d+)$", line)
        if m:
            total += 10 * int(m.group(1))

    return total


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    total = calc(text)

    await update.message.reply_text(f"📊 Total = {total:,} MMK")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
