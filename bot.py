from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

def calc(text: str):
    import re

    total = 0

    # 1️⃣ normalize: convert multiple dots to single space safely
    text = re.sub(r"\.+", " ", text)

    # 2️⃣ keep only usable characters
    text = re.sub(r"[^\dR\s]", " ", text)

    # 3️⃣ R format ONLY strict
    r_items = re.findall(r"\b(\d+)\s*R\s*(\d+)\b", text)
    for nums, amt in r_items:
        total += int(nums) * int(amt)

    # 4️⃣ remove R parts before next parse
    text = re.sub(r"\b\d+\s*R\s*\d+\b", " ", text)

    # 5️⃣ STRICT normal format (must be clean pairs only)
    plain = re.findall(r"\b(\d{1,5})\s+(\d{3,})\b", text)
    for nums, amt in plain:
        total += int(nums) * int(amt)

    # 6️⃣ အပူး
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
