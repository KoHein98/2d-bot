from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")


# =========================
# 🧠 CALCULATOR (NO MEMORY)
# =========================
def calc(text: str):
    cat = {
        "khwe": 0,
        "khwepue": 0,
        "apue": 0,
        "r": 0,
        "normal": 0
    }

    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"\.+", " ", line)
        line = re.sub(r"\s+", " ", line)

        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])
        line_clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

        # 🔴 အပူး
        if "အပူး" in line_clean:
            val = 10 * amount
            cat["apue"] += val
            total += val
            continue

        # 🟣 ခွေပူး
        if "ခွေပူး" in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            n = len(digits)
            val = (n * n) * amount
            cat["khwepue"] += val
            total += val
            continue

        # 🟢 ခွေ
        if "ခွေ" in line_clean and "ခွေပူး" not in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            n = len(digits)
            val = (n * (n - 1)) * amount
            cat["khwe"] += val
            total += val
            continue

        # 🔵 R
        if "R" in line_clean.upper():
            nums_r = re.findall(r"\d+", line_clean)
            val = len(nums_r) * 2 * amount
            cat["r"] += val
            total += val
            continue

        # 🟡 NORMAL
        nums_only = re.findall(r"\d+", line_clean)
        val = len(nums_only) * amount
        cat["normal"] += val
        total += val

    return cat, total


# =========================
# 🤖 MESSAGE HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat, total = calc(update.message.text)

    message = (
        "📊 *BREAKDOWN*\n\n"
        f"🟢 ခွေ = {cat['khwe']:,}\n"
        f"🟣 ခွေပူး = {cat['khwepue']:,}\n"
        f"🔴 အပူး = {cat['apue']:,}\n"
        f"🔵 R = {cat['r']:,}\n"
        f"🟡 NORMAL = {cat['normal']:,}\n"
        f"\n➕ *Batch Total = {total:,}*\n\n"
        "👉 ဒီ message တစ်ခါချင်းတွက်တာပဲ"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("🚀 NO MEMORY 2D BOT RUNNING...")
app.run_polling()
