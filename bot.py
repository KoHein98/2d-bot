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
# 🧠 PARSER (STRICT)
# =========================
def parse_line(line):
    line = line.strip()
    line = re.sub(r"\.+", " ", line)
    line = re.sub(r"\s+", " ", line)

    nums = re.findall(r"\d+", line)
    if not nums:
        return None

    amount = int(nums[-1])

    # remove ONLY last number
    clean = line[::-1].replace(nums[-1][::-1], "", 1)[::-1].strip()

    numbers = re.findall(r"\d+", clean)

    return {
        "clean": clean,
        "amount": amount,
        "numbers": numbers
    }


# =========================
# 🧠 CALCULATOR (FULL RULES)
# =========================
def calc(bets):
    cat = {
        "khwe": 0,
        "khwepue": 0,
        "apue": 0,
        "r": 0,
        "normal": 0
    }

    total = 0

    for b in bets:
        line = b["clean"]
        amount = b["amount"]

        # 🔴 အပူး
        if "အပူး" in line:
            val = 10 * amount
            cat["apue"] += val
            total += val
            continue

        # 🟣 ခွေပူး (n²)
        if "ခွေပူး" in line:
            n = len(b["numbers"])
            val = (n * n) * amount
            cat["khwepue"] += val
            total += val
            continue

        # 🟢 ခွေ (n(n-1))
        if "ခွေ" in line and "ခွေပူး" not in line:
            n = len(b["numbers"])
            val = (n * (n - 1)) * amount
            cat["khwe"] += val
            total += val
            continue

        # 🔵 R
        if "R" in line.upper():
            nums_r = re.findall(r"\d+", line)
            val = len(nums_r) * 2 * amount
            cat["r"] += val
            total += val
            continue

        # 🟡 NORMAL
        val = len(b["numbers"]) * amount
        cat["normal"] += val
        total += val

    return cat, total


# =========================
# 🤖 MESSAGE HANDLER
# =========================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    data_store.setdefault(chat_id, [])

    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            data_store[chat_id].append(parsed)

    cat, total = calc(data_store[chat_id])

    await update.message.reply_text(
        "📊 Added ✔\n"
        f"💰 Current Total = {total:,}\n"
        "👉 /total <number> ရိုက်ပြီးရှာနိုင်ပါတယ်"
    )


# =========================
# 🔎 SMART FILTER TOTAL (EXACT MATCH FIXED)
# =========================
async def smart_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bets = data_store.get(chat_id, [])

    # 👉 FULL TOTAL
    if not context.args:
        cat, total = calc(bets)
        await update.message.reply_text(f"💰 TOTAL = {total:,}")
        return

    query = context.args[0]

    filtered = []
    for b in bets:
        # ✅ EXACT MATCH ONLY (FIXED BUG)
        if query in b["numbers"]:
            filtered.append(b)

    cat, total = calc(filtered)

    # 💸 stake (optional simple calc)
    stake = sum(b["amount"] * len(b["numbers"]) for b in filtered)

    p = total - stake

    await update.message.reply_text(
        f"📊 Number {query} Report\n\n"
        f"🟢 ခွေ = {cat['khwe']:,}\n"
        f"🟣 ခွေပူး = {cat['khwepue']:,}\n"
        f"🔴 အပူး = {cat['apue']:,}\n"
        f"🔵 R = {cat['r']:,}\n"
        f"🟡 NORMAL = {cat['normal']:,}\n\n"
        f"💰 Total = {total:,}\n"
        f"💸 Stake = {stake:,}\n"
        f"📈 P = {p:,}"
    )


# =========================
# 🚀 RUN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(CommandHandler("total", smart_total))

print("🚀 FINAL SMART 2D BOT RUNNING...")
app.run_polling()
