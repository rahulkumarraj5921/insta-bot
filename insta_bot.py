import os
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
RAPID_API_KEY = os.environ.get("RAPIDAPI_KEY") 
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot is live and fixed!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 **Insta Ninja Downloader (Final Version)** 🚀\n\n"
        "बस रील का लिंक भेजें और जादू देखें! ⚡\n\n"
        "👇 **Developer को सपोर्ट करने के लिए फॉलो करें:**"
    )
    keyboard = [[InlineKeyboardButton("💖 Follow Rahul Kumar Raj 💖", url=INSTA_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ दोस्त, कृपया सही Instagram लिंक भेजें!")
        return

    status_msg = await update.message.reply_text("⚙️ **वीडियो डाउनलोड किया जा रहा है...**")

    try:
        # instagram120 ka sahi endpoint for download
        api_url = "https://instagram120.p.rapidapi.com/api/instagram/links" 
        payload = {"url": url}
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": "instagram120.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        # Is API ka response aksar list me aata hai
        video_url = None
        if isinstance(data, list) and len(data) > 0:
            video_url = data[0].get("url") or data[0].get("video_url")
        elif isinstance(data, dict):
            video_url = data.get("url") or data.get("video_url")

        if not video_url:
            await status_msg.edit_text("❌ वीडियो लिंक नहीं मिला। कृपया सुनिश्चित करें कि रील पब्लिक है।")
            return

        file_path = f"reel_{chat_id}.mp4"
        video_data = requests.get(video_url).content
        with open(file_path, 'wb') as f:
            f.write(video_data)

        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption="🎬 **Reel Downloaded!** ✅",
                reply_markup=reply_markup
            )
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** सब्सक्राइब चेक करें या लिंक फिर से भेजें।")
        print(f"Detailed Error: {e}")

    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main():
    threading.Thread(target=run_web, daemon=True).start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
