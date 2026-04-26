import os
import threading
import requests
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Render Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
RAPID_API_KEY = os.environ.get("RAPIDAPI_KEY") 
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

# 🌐 WEB SERVER FOR RENDER
app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot is Live and Working! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 🤖 BOT LOGIC
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🔥 **Insta Ninja Downloader v2.0** 🔥\n\n"
        "नमस्ते! मैं किसी भी Instagram Reel को हाई क्वालिटी में डाउनलोड कर सकता हूँ। ⚡\n\n"
        "🎯 *बस मुझे रील का लिंक भेजें!*\n\n"
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

    status_msg = await update.message.reply_text("🔍 **वीडियो प्रोसेस किया जा रहा है...**")
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    try:
        # RapidAPI Configuration
        api_url = "https://instagram120.p.rapidapi.com/api/instagram/links" 
        payload = {"url": url}
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": "instagram120.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        # API Call
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        # 🎯 LINK EXTRACTION (Based on your Debug JSON)
        # Structure: data[0]['urls'][0]['url']
        video_url = None
        video_title = "✅ Reel Downloaded!"
        
        if isinstance(data, list) and len(data) > 0:
            video_url = data[0]['urls'][0]['url']
            video_title = data[0].get('meta', {}).get('title', "🎬 Downloaded successfully!")[:1000]

        if not video_url:
            await status_msg.edit_text("❌ वीडियो लिंक नहीं मिल पाया। शायद रील प्राइवेट है।")
            return

        await status_msg.edit_text("📥 **सर्वर पर डाउनलोड हो रहा है... बस कुछ ही पल!**")

        # Downloading File
        file_path = f"reel_{chat_id}.mp4"
        video_response = requests.get(video_url)
        with open(file_path, 'wb') as f:
            f.write(video_response.content)

        await status_msg.edit_text("📤 **टेलीग्राम पर भेजा जा रहा है... 🚀**")

        # Sending to Telegram
        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=f"🎬 **{video_title}**\n\n⚡ *Powered by Rahul Kumar Raj*",
                reply_markup=reply_markup
            )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** कुछ गड़बड़ हो गई। कृपया थोड़ी देर बाद प्रयास करें।")
        print(f"Final Error: {e}")

    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main():
    threading.Thread(target=run_web, daemon=True).start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Ninja Bot (Final) is Running 24/7!")
    application.run_polling()

if __name__ == '__main__':
    main()
