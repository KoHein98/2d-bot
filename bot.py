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
# 🧹 CLEAN
# =========================
def clean_text(text: str):
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# 🧠 CORE ENGINE (WITH DEBUG SUPPORT)
# =========================
def calc(text: str, debug=False):
    total = 0
    breakdown = []

    for raw_line in text.splitlines():
        line = clean_text(raw_line)
        if not line:
            continue

        upper_line = line.upper()

        line_result = 0

        # =========================
        # 🔥 R RULE (PRIORITY 1)
        # =========================
        if "R" in upper_line:
            fixed = re.sub(r'(\d)\s*R\s*(\d)', r'\1 R \2', line, flags=re.IGNORECASE)
            nums_r = re.findall(r"\d+", fixed)

            if len(nums_r) >= 3:
                line_result = int(nums_r[-2]) + int(nums_r[-1])
            elif len(nums_r) == 2:
                line_result = int(nums_r[-1]) * 2
            else:
                line_result = 0

            if debug:
                breakdown.append(f"{line} => R RULE => {line_result}")

            total += line_result
            continue


        # =========================
        # NORMAL PARSE
        # =========================
        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])
        main_part = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]


        # =========================
        # 🔥 RULE: အပူး
        # =========================
        if "အပူး" in main_part:
            line_result = 10 * amount
            total += line_result

            if debug:
                breakdown.append(f"{line} => အပူး => {line_result}")
            continue


        # =========================
        # 🔥 RULE: ခွေပူး
        # =========================
        if "ခွေပူး" in main_part:
            digits = re.findall(r"\d", main_part)
            line_result = (len(digits) ** 2) * amount
            total += line_result

            if debug:
                breakdown.append(f"{line} => ခွေပူး => {line_result}")
            continue


        # =========================
        # 🔥 RULE: ခွေ
        # =========================
        if "ခွေ" in main_part and "ခွေပူး" not in main_part:
            digits = re.findall(r"\d", main_part)
            line_result = (len(digits) * (len(digits) - 1)) * amount
            total += line_result

            if debug:
                breakdown.append(f"{line} => ခွေ => {line_result}")
            continue


        # =========================
        # 🔥 DEFAULT RULE
        # =========================
        count = len(nums) - 1

        line_result = amount if count <= 0 else count * amount
        total += line_result

        if debug:
            breakdown.append(f"{line} => DEFAULT => {line_result}")

    return total, breakdown


# =========================
# 🤖 MESSAGE HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])
    data_store[chat_id].append(text)

    total, _ = calc(text)

    await update.message.reply_text(
        f"📊 Batch Total = {total:,}\n✔ Saved"
    )


# =========================
# 💰 TOTAL
# =========================
async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    history = data_store.get(chat_id, [])

    total, _ = calc("\n".join(history))

    await update.message.reply_text(f"💰 TOTAL = {total:,}")


# =========================
# 🔍 DEBUG COMMAND (NEW)
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

    print("🚀 V2 BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
