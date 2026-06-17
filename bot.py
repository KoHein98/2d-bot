from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

data_store = {}


# =========================
# 🧹 CLEAN FUNCTION
# =========================
def clean_text(text: str):
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# 🧠 CALC ENGINE
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = clean_text(line)
        if not line:
            continue

        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])

        # remove last number
        main_part = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]
        # =========================
        # 🔥 R RULE
        # =========================
        if "R" in line.upper():

            fixed = re.sub(r'(\d)R(\d)', r'\1 R \2', line, flags=re.IGNORECASE)
            fixed = re.sub(r'\s+', ' ', fixed)

            nums_r = re.findall(r'\d+', fixed)

            # Split Stake Mode
            # 74 25000R5000
            # 74 86 25000R5000
            if len(nums_r) >= 3 and int(nums_r[-2]) >= 1000:

                normal_amt = int(nums_r[-2])
                reverse_amt = int(nums_r[-1])

                pair_count = len(nums_r) - 2

                total += pair_count * (normal_amt + reverse_amt)
                continue

            # Pair × 2 Mode
            amount = int(nums_r[-1])
            pair_count = len(nums_r) - 1

            total += pair_count * 2 * amount
            continue
        # =========================
        # 🔥 အပူး
        # =========================
        if "အပူး" in main_part:
            total += 10 * amount
            continue

        # =========================
        # 🔥 ခွေပူး
        # =========================
        if "ခွေပူး" in main_part:
            digits = re.findall(r"\d", main_part)
            total += (len(digits) ** 2) * amount
            continue

        # =========================
        # 🔥 ခွေ
        # =========================
        if "ခွေ" in main_part and "ခွေပူး" not in main_part:
            digits = re.findall(r"\d", main_part)
            total += (len(digits) * (len(digits) - 1)) * amount
            continue

        # =========================
        # DEFAULT RULE
        # =========================
        total += amount

    return total


# =========================
# 🤖 MESSAGE HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])
    data_store[chat_id].append(text)

    total = calc(text)

    await update.message.reply_text(
        f"📊 Batch Total = {total:,}\n✔ Saved"
    )


# =========================
# 💰 /TOTAL
# =========================
async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    history = data_store.get(chat_id, [])

    total = calc("\n".join(history))

    await update.message.reply_text(f"💰 TOTAL = {total:,}")


# =========================
# ♻️ RESET
# =========================
async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data_store[chat_id] = []
    await update.message.reply_text("♻️ RESET DONE")


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("total", total_cmd))
app.add_handler(CommandHandler("reset", reset_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("🚀 FINAL BOT RUNNING...")
app.run_polling()
