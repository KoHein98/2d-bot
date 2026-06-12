from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")


# reverse helper
def reverse_num(n: str):
    return n[::-1]


def calc(text: str):
    total = 0

    # split lines first
    lines = text.split()

    i = 0
    while i < len(lines):
        part = lines[i]

        # clean dots
        part = part.replace(".", " ")

        # R case
        if "R" in part:
            # handle cases like 52R20000 or 52 R 20000
            match = re.findall(r"(\d+)", part)
            if len(match) >= 2:
                nums_part = match[:-1]
                amount = int(match[-1])

                count = 0

                for num in nums_part:
                    count += 1  # original
                    count += 1  # reverse

                total += count * amount

        else:
            # normal number case (flat)
            match = re.findall(r"\d+", part)
            if len(match) == 1:
                total += int(match[0])

        i += 1

    return total


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    total = calc(text)

    await update.message.reply_text(f"📊 Total = {total:,} MMK")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
