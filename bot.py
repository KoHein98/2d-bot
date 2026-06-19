from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 💾 MEMORY STORE
# =========================
data_store = {}

# =========================
# 🧠 CALC ENGINE (FIXED)
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # FIXED CLEAN (IMPORTANT)
        line = re.sub(r"\.+", " ", line)
        line = re.sub(r"\s+", " ", line)

        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])

        # remove last amount only
        line_clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

        # =========================
        # 🔥 အပူး
        # =========================
        if "အပူး" in line_clean:
            total += 10 * amount
            continue

        # =========================
        # 🔥 ခွေပူး
        # =========================
        if "ခွေပူး" in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            total += (len(digits) ** 2) * amount
            continue

        # =========================
        # 🔥 ခွေ
        # =========================
        if "ခွေ" in line_clean and "ခွေပူး" not in line_clean:
            digits = "".join(re.findall(r"\d", line_clean))
            total += (len(digits) * (len(digits) - 1)) * amount
            continue

        # =========================
        # 🔥 R RULE
        # =========================
        if "R" in line_clean.upper():

            nums_r = re.findall(r"\d+", line_clean)

            # Split Stake Mode
            # 74 25000R5000
            # 74 86 25000R5000
            if len(nums_r) >= 2 and int(nums_r[-1]) >= 1000:

                normal_amt = int(nums_r[-1])
                reverse_amt = amount

                pair_count = len(nums_r) - 1

                total += pair_count * (normal_amt + reverse_amt)
                continue

            # Normal Reverse
            # 43 R 5000
            # 42 52 R 10000
            pair_count = len(nums_r)

            total += pair_count * 2 * amount
            continue

        # =========================
        # 🔥 DEFAULT
        # =========================
        count = len(re.findall(r"\d+", line_clean))

        if count == 0:
            total += amount
        else:
            total += count * amount

    return total

# =========================
# 🤖 HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    total = calc(text)

    data_store.setdefault(chat_id, 0)
    data_store[chat_id] += total

    await update.message.reply_text(
        f"📊 Batch Total = {total:,}\n✔ Saved"
    )

# =========================
# 💰 TOTAL
# =========================
async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    total = data_store.get(chat_id, 0)

    await update.message.reply_text(f"💰 TOTAL = {total:,}")

# =========================
# ♻️ RESET
# =========================
async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data_store[chat_id] = 0

    await update.message.reply_text("♻️ RESET DONE")

# =========================
# 🚀 RUN BOT
# =========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("total", total_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

    print("🚀 BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
