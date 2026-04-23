import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send: video <your topic>")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("video"):
        topic = text.replace("video", "").strip()

        # 1. Fake script (later replace with OpenAI)
        script = f"{topic} ki ek bhakti kahani..."

        # 2. Fake voice (placeholder)
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

        # 3. Fake image
        image_url = "https://picsum.photos/720/1280"

        # Send response
        await update.message.reply_text(script)
        await update.message.reply_audio(audio_url)
        await update.message.reply_photo(image_url)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
