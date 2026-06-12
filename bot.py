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
        if not line:
            continue

        # 1. R (အာ) format - ဥပမာ "57 R 10000" သို့မဟုတ် "57R10000"
        m = re.match(r"^(\d+)\s*[Rr]\s*(\d+)$", line)
        if m:
            # R ပါရင် ၂ ကွက်ဖြစ်သွားတဲ့အတွက် ထိုးကြေးကို ၂ နဲ့ မြှောက်ရပါမယ်
            bet_amount = int(m.group(2))
            total += bet_amount * 2
            continue

        # 2. Normal format (အာမပါ၊ အတည့်ပဲ) - ဥပမာ "57 10000"
        m = re.match(r"^(\d+)\s+(\d+)$", line)
        if m:
            # အာမပါရင် ၁ ကွက်စာပဲမို့လို့ ထိုးကြေးအတိုင်းပဲ ပေါင်းပါမယ်
            bet_amount = int(m.group(2))
            total += bet_amount

    return total

# စမ်းသပ်ကြည့်ခြင်း
print(calc("57 R 10000"))  # အဖြေမှန် 20000 ထွက်လာပါလိမ့်မယ်။
print(calc("57 10000"))    # အဖြေမှန် 10000 ထွက်လာပါလိမ့်မယ်။


    await update.message.reply_text(f"📊 Total = {total:,} MMK")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
