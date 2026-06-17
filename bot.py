from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 💾 MEMORY
# =========================
data_store = {}

# =========================
# 🧹 CLEAN (STABLE INPUT FIX)
# =========================
def clean_text(text: str):
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\dA-Za-zခွေခွေပူးအပူးR ]+", " ", text)
    return text.strip()


# =========================
# 🧠 CORE ENGINE (FIXED)
# =========================
def calc(text: str, debug: bool = False):
    total = 0
    breakdown = []

    for line in text.splitlines():
        line = clean_text(line)
        if not line:
            continue

        line_total = 0

        # =========================
        # 🔥 R RULE (FIXED STABLE)
        # =========================
        if "R" in line.upper():
            nums = re.findall(r"\d+", line)

            if len(nums) < 2:
                continue

            amount = int(nums[-1])
            numbers = nums[:-1]

            line_total = len(numbers) * amount

        else:
            nums = re.findall(r"\d+", line)
            if not nums:
                continue

            amount = int(nums[-1])

            # =========================
            # 🔥 ခွေပူး
            # =========================
            if "ခွေပူး" in line:
                digits = re.findall(r"\d", line)
                line_total = (len(digits) ** 2) * amount

            # =========================
            # 🔥 ခွေ
            # =========================
            elif "ခွေ" in line:
                digits = re.findall(r"\d", line)
                line_total = len(digits) * (len(digits) - 1) * amount

            # =========================
            # 🔥 အပူး
            # =========================
            elif "အပူး" in line:
                line_total = 10 * amount

            # =========================
            # 🔥 DEFAULT
            # =========================
            else:
                nums_only = re.findall(r"\d+", line)
                count = len(nums_only) - 1
                line_total = amount if count <= 0 else count * amount

        total += line_total

        if debug:
            breakdown.append(f"{line} = {line_total}")

    return (total, breakdown) if debug else total


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
# 🔍 DEBUG
# =========================
async def debug_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    history = data_store.get(chat_id, [])

    total, breakdown = calc("\n".join(history), debug=True)

    msg = "🔍 BREAKDOWN:\n\n" + "\n".join(breakdown[-50:])
    msg += f"\n\n💰 TOTAL = {total:,}"

    await update.message.reply_text(msg)


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
    app.add_handler(CommandHandler("debug", debug_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

    print("🚀 V3 STABLE ENGINE RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
