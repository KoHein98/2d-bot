from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import re

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 🧠 MEMORY STORE
# =========================
data_store = {}


# =========================
# 🧠 PARSER
# =========================
def parse_line(line):
    line = line.strip()
    line = re.sub(r"\.+", " ", line)
    line = re.sub(r"\s+", " ", line)

    nums = re.findall(r"\d+", line)
    if not nums:
        return None

    amount = int(nums[-1])

    clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1].strip()

    numbers = re.findall(r"\d+", clean)

    return {
        "text": line,
        "clean": clean,
        "amount": amount,
        "numbers": numbers
    }


# =========================
# 🧠 CALC SINGLE MESSAGE
# =========================
def calc_message(lines):
    cat = {
        "khwe": 0,
        "khwepue": 0,
        "apue": 0,
        "r": 0,
        "normal": 0
    }

    total = 0

    for b in lines:
        line = b["clean"]
        amount = b["amount"]

        if "အပူး" in line:
            val = 10 * amount
            cat["apue"] += val
            total += val
            continue

        if "ခွေပူး" in line:
            n = len(b["numbers"])
            val = (n * n) * amount
            cat["khwepue"] += val
            total += val
            continue

        if "ခွေ" in line and "ခွေပူး" not in line:
            n = len(b["numbers"])
            val = (n * (n - 1)) * amount
            cat["khwe"] += val
            total += val
            continue

        if "R" in line.upper():
            nums_r = re.findall(r"\d+", line)
            val = len(nums_r) * 2 * amount
            cat["r"] += val
            total += val
            continue

        val = len(b["numbers"]) * amount
        cat["normal"] += val
        total += val

    return cat, total


# =========================
# 🤖 MESSAGE HANDLER (LINE TOTAL)
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])

    parsed_lines = []

    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            data_store[chat_id].append(parsed)
            parsed_lines.append(parsed)

    cat, total = calc_message(parsed_lines)

    await update.message.reply_text(
        "📊 LINE RESULT\n\n"
        f"🟢 ခွေ = {cat['khwe']:,}\n"
        f"🟣 ခွေပူး = {cat['khwepue']:,}\n"
        f"🔴 အပူး = {cat['apue']:,}\n"
        f"🔵 R = {cat['r']:,}\n"
        f"🟡 NORMAL = {cat['normal']:,}\n\n"
        f"💰 Line Total = {total:,}\n"
        "👉 /total <number> for filter"
    )


# =========================
# 🔎 FILTER COMMAND
# =========================
async def smart_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bets = data_store.get(chat_id, [])

    # FULL TOTAL
    if not context.args:
        cat, total = calc_message(bets)
        await update.message.reply_text(f"💰 TOTAL = {total:,}")
        return

    query = context.args[0]

    filtered = []
    for b in bets:
        if query in b["numbers"]:
            filtered.append(b)

    if not filtered:
        await update.message.reply_text("❌ No match found")
        return

    cat, total = calc_message(filtered)

    msg = f"📊 Filter: {query}\n\n"

    for b in filtered:
        msg += f"{b['text']} → {b['amount']:,}\n"

    msg += f"\n💰 Total = {total:,}"

    await update.message.reply_text(msg)


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("total", smart_total))

print("🚀 FULL COMBINED 2D BOT RUNNING...")
app.run_polling()
