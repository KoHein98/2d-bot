from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

data_store = {}

# =========================
# 🧹 CLEAN (STRICT NORMALIZER)
# =========================
def clean_text(text: str):
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\dA-Za-zခွေခွေပူးအပူးR ]+", " ", text)
    return text.strip()


# =========================
# 🧠 LOCKED ENGINE (NO AMBIGUITY)
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = clean_text(line)
        if not line:
            continue

        nums = re.findall(r"\d+", line)

        # =========================
        # 🔥 RULE 1: R MODE (LOCKED)
        # =========================
        if "R" in line.upper():
            if len(nums) < 2:
                continue

            amount = int(nums[-1])
            selections = nums[:-1]

            # ✔ each selection = 1 unit
            total += len(selections) * amount
            continue

        if not nums:
            continue

        amount = int(nums[-1])

        # =========================
        # 🔥 RULE 2: SPECIAL WORDS
        # =========================
        if "ခွေပူး" in line:
            digits = re.findall(r"\d", line)
            total += (len(digits) ** 2) * amount
            continue

        if "ခွေ" in line:
            digits = re.findall(r"\d", line)
            total += len(digits) * (len(digits) - 1) * amount
            continue

        if "အပူး" in line:
            total += 10 * amount
            continue

        # =========================
        # 🔥 RULE 3: DEFAULT MODE (LOCKED)
        # =========================
        count = len(nums) - 1

        if count <= 0:
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

    print("🚀 FINAL V5 LOCK ENGINE RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
