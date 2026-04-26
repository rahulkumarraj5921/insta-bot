import os
import asyncio
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Render se aane wale Tokens
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
RAPID_API_KEY = os.environ.get("RAPIDAPI_KEY") 
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot is live with RapidAPI!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 **Insta Ninja Downloader (Pro Version)** 🚀\n\n"
        "Professional API के साथ अब रील्स डाउनलोड करना और भी आसान। ⚡\n\n"
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

    status_msg = await update.message.reply_text("⚙️ **RapidAPI सर्वर से वीडियो निकाला जा रहा है...**")
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    file_path = f"reel_{chat_id}.mp4"

    try:
        # 🪄 RAPIDAPI CALL (Aapke diye gaye cURL ke hisab se)
        # Note: Maine URL ko assume kiya hai, agar error aaye to RapidAPI dashboard check karein
        api_url = "https://instagram120.p.rapidapi.com/api/instagram/links" 
        
        # Payload (Data) - Username ki jagah hum URL bhejenge
        payload = {
            "url": url
        }
        
        # Headers (Aapke diye gaye host aur key ke sath)
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": "instagram120.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        # POST Request bhej rahe hain
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        # Video link nikalna (Yeh API ke response par depend karta hai)
        # Agar JSON alag hua, to is line me error aa sakta hai
        video_url = data[0].get("video_url") if isinstance(data, list) else data.get("video_url") or data.get("url")

        if not video_url:
            raise Exception("API ne video link nahi diya. Shayad endpoint galat hai.")

        await status_msg.edit_text("📥 **वीडियो मिल गया! टेलीग्राम पर भेजा जा रहा है...**")

        video_data = requests.get(video_url).content
        with open(file_path, 'wb') as f:
            f.write(video_data)

        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                supports_streaming=True,
                caption="✅ **Reel Downloaded!**\n\n⚡ *Powered by Ninja API*",
                reply_markup=reply_markup
            )
        await status_msg.delete()

    except Exception as e:
        error_text = f"❌ **Error:** API में दिक्कत है या लिंक गलत है।\n`{str(e)[:100]}`"
        await status_msg.edit_text(error_text, parse_mode='Markdown')
        print(f"Error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    threading.Thread(target=run_web, daemon=True).start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()

