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
# 🧹 CLEAN FUNCTION
# =========================
def clean_text(text: str):
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# =========================
# 🧠 CALC ENGINE (SAFE)
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
        main_part = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

        # =========================
        # 🔥 R RULE (SAFE)
        # =========================
        if "R" in line.upper():
            fixed = re.sub(r'(\d)R(\d)', r'\1 R \2', line, flags=re.IGNORECASE)
            nums_r = re.findall(r'\d+', fixed)

            if len(nums_r) >= 3:
                # special mode (47.25.15000R15000 style)
                total += int(nums_r[-2]) + int(nums_r[-1])
            else:
                # normal R mode
                total += int(nums_r[-1]) * 2

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
        # 🧠 DEFAULT RULE (FIXED)
        # =========================
        nums_only = re.findall(r"\d+", line)
        count = max(len(nums_only) - 1, 0)

        total += amount if count == 0 else count * amount

    return total

# =========================
# 🤖 HANDLER
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
# 💰 TOTAL
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
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("total", total_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

    print("🚀 BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
