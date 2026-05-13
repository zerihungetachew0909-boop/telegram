import os
import pdfplumber
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

TOKEN = os.getenv("TOKEN")

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "PDF ergaa fi maqaa barbaaddu ergi."
    )

# PDF RECEIVE
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()

    pdf_path = "passport.pdf"
    await file.download_to_drive(pdf_path)

    context.user_data["pdf"] = pdf_path

    await update.message.reply_text(
        "Amma maqaa keessan ergaa."
    )

# SEARCH NAME
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "pdf" not in context.user_data:
        await update.message.reply_text("Dura PDF ergaa.")
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

    # ✅ FOUND MESSAGE
    if found:
        keyboard = [
            [
                InlineKeyboardButton("Golloo Online Passport Solution", callback_data="Golloo Online Passport Solution")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "✅ Bagaa Gammadaan Passportiin Kessaan Bahe Jira",
            reply_markup=reply_markup
        )

    # ❌ NOT FOUND MESSAGE
    else:
        keyboard = [
            [
                InlineKeyboardButton("Golloo Online Passport Solution", callback_data="Golloo Online Passport Solution")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "❌ Maaloo Passportiin Kessan Hin baane Obsaan Eegadhaa",
            reply_markup=reply_markup
        )

# CLOSE BUTTON
async def close_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # message delete
    await query.message.delete()

# MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# X button handler
app.add_handler(CallbackQueryHandler(close_button, pattern="close"))

print("Bot Running...")
app.run_polling()