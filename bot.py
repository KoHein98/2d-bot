from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")


# reverse helper
def calc(text: str):
    total = 0
    import re

    items = text.split()

    i = 0
    while i < len(items):
        part = items[i]

        if "R" in part or (i + 1 < len(items) and items[i+1] == "R"):
            nums = re.findall(r"\d+", part)

            # handle cases like "52 R 20000"
            if len(nums) == 1 and i + 2 < len(items):
                num = nums[0]
                amount = int(items[i+2])

                # reverse pair
                total += 2 * amount
                i += 3
                continue

        else:
            nums = re.findall(r"\d+", part)
            if len(nums) == 1:
                total += int(nums[0])

        i += 1

    return total


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    total = calc(text)

    await update.message.reply_text(f"📊 Total = {total:,} MMK")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
