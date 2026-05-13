import os
import pdfplumber
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# 🔐 TOKEN (Render ENV variable)
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN is missing! Please set it in Render environment variables.")

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 PDF ergi, achin maqaa kee ergi."
    )

# PDF RECEIVE
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()

    pdf_path = "file.pdf"
    await file.download_to_drive(pdf_path)

    context.user_data["pdf"] = pdf_path

    await update.message.reply_text("✍️ Amma maqaa keessan barreessaa.")

# TEXT CHECK
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "pdf" not in context.user_data:
        await update.message.reply_text("⚠️ Dura PDF ergaa.")
        return

    name = update.message.text.lower()
    pdf_path = context.user_data["pdf"]

    found = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text and name in text.lower():
                found = True
                break

    # BUTTON
    keyboard = [[InlineKeyboardButton("❌ Close", callback_data="close")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if found:
        await update.message.reply_text(
            "✅ Bagaa Gammadaan Passportiin Kessan Bahe Jira",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "❌ Maaloo Passportiin Kessan Hin baane Obsaan Eegadhaa",
            reply_markup=reply_markup
        )

# CLOSE BUTTON
async def close_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()

# MAIN APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(close_btn, pattern="close"))

print("Bot Running...")
app.run_polling()
