from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")

user_data = {}


# ---------------- START MENU ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Add 2D Entry", callback_data="add")],
        [InlineKeyboardButton("📊 Calculate Total", callback_data="calc")],
        [InlineKeyboardButton("🧹 Reset", callback_data="reset")]
    ]

    await update.message.reply_text(
        "🎰 2D Betting Bot\nChoose option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- BUTTON HANDLER ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = []

    if query.data == "add":
        await query.message.reply_text(
            "Send format:\n👉 17 10000\n👉 17 R 10000"
        )

    elif query.data == "calc":
        total = 0

        for item in user_data.get(user_id, []):
            parts = item.split()

            if "R" in parts:
                nums = int(parts[0])
                amt = int(parts[2])
            else:
                nums = int(parts[0])
                amt = int(parts[1])

            if 0 <= nums <= 99:
                total += nums * amt

        await query.message.reply_text(f"📊 Total = {total:,} MMK")

    elif query.data == "reset":
        user_data[user_id] = []
        await query.message.reply_text("🧹 Reset done!")


# ---------------- TEXT INPUT ----------------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = []

    user_data[user_id].append(text)

    await update.message.reply_text("✅ Added!")


# ---------------- MAIN ----------------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
