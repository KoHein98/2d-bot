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
        if not line:  # လိုင်းက အလွတ်ဖြစ်နေရင် ကျော်မယ်
            continue

        # 1. R format ကို အရင်စစ်မယ် (ဥပမာ - "5 R 10" သို့မဟုတ် "5R10")
        m = re.search(r"(\d+)\s*R\s*(\d+)", line)
        if m:
            total += int(m.group(1)) * int(m.group(2))
            continue  # ကိုက်ညီမှုရှိသွားရင် အောက်က normal format ကို ထပ်မစစ်တော့ဘဲ ကျော်မယ်

        # 2. Normal format ကို စစ်မယ် (ဥပမာ - "5 10")
        m = re.search(r"(\d+)\s+(\d+)", line)
        if m:
            total += int(m.group(1)) * int(m.group(2))

    return total


    await update.message.reply_text(f"📊 Total = {total:,} MMK")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
