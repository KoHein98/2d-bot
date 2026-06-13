from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 🧠 STORAGE (RAW TEXT)
# =========================
data_store = {}


# =========================
# 🧹 CLEAN TEXT
# =========================
def clean_text(text):
    text = text.replace("..", " ")
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# 🧠 CALC ENGINE (YOUR RULES)
# =========================
def calc(text: str):
    total = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        line = clean_text(line)

        nums = re.findall(r"\d+", line)
        if not nums:
            continue

        amount = int(nums[-1])

        # remove last number (stake)
        main_part = line[::-1].replace(nums[-1][::-1], "", 1)[::-1]

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
        # 🔥 R LOGIC (FINAL FIXED)
        # =========================
        if "R" in line.upper():
            nums_r = re.findall(r"\d+", line)

            # TYPE 2: 15 10000 R 20000
            if len(nums_r) == 3:
                total += int(nums_r[1]) + int(nums_r[2])
                continue

            # TYPE 1: 50 57 R 10000
            count = len(nums_r) - 1
            total += count * 2 * amount
            continue

        # =========================
        # DEFAULT
        # =========================
        total += len(nums) * amount

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
# 💰 /TOTAL COMMAND
# =========================
async def total_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    history = data_store.get(chat_id, [])

    # =========================
    # GRAND TOTAL
    # =========================
    if not context.args:
        total = calc("\n".join(history))
        await update.message.reply_text(f"💰 GRAND TOTAL = {total:,}")
        return

    # =========================
    # FILTER MODE (/total 11)
    # =========================
    query = context.args[0]

    results = []
    total = 0

    for text in history:
        for line in text.splitlines():
            clean = clean_text(line)
            nums = re.findall(r"\d+", clean)

            if len(nums) < 2:
                continue

            amount = int(nums[-1])
            main = clean[::-1].replace(nums[-1][::-1], "", 1)[::-1]

            if query in nums[:-1]:
                results.append(f"{query} → {amount:,}")
                total += amount

    if not results:
        await update.message.reply_text("❌ No match found")
        return

    msg = f"📊 Number {query}\n\n"
    msg += "\n".join(results)
    msg += f"\n\n💰 Total = {total:,}"

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
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("total", total_cmd))
app.add_handler(CommandHandler("reset", reset_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("🚀 FINAL 2D BOT RUNNING...")
app.run_polling()
