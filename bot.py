from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

def calc(text: str):
    import re

    total = 0

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # 2D R format only (00-99 accepted)
        m = re.match(r"^(\d{1,2})\s*R\s*(\d+)$", line)
        if m:
            nums = int(m.group(1))
            amt = int(m.group(2))

            if 0 <= nums <= 99:
                total += nums * amt
            continue

        # normal 2D format (00-99)
        m = re.match(r"^(\d{1,2})\s+(\d+)$", line)
        if m:
            nums = int(m.group(1))
            amt = int(m.group(2))

            if 0 <= nums <= 99:
                total += nums * amt
            continue

        # အပူး
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
