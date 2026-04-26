import os
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
    return "Ninja Bot is live with RapidAPI (Debug Mode)!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 **Insta Ninja Downloader (Debug Mode)** 🚀\n\n"
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

    status_msg = await update.message.reply_text("⚙️ **RapidAPI को रिक्वेस्ट भेजी जा रही है...**")

    try:
        api_url = "https://instagram120.p.rapidapi.com/api/instagram/links" 
        payload = {"url": url}
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": "instagram120.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        
        # API kya bhej rahi hai usko nikalna
        try:
            data = response.json()
        except:
            data = response.text

        # 🛠 DEBUG MODE: Yahan hum API ka asli kachha data Telegram par dikhayenge
        debug_text = f"🛠 **API Response (Debug):**\n`{str(data)[:3000]}`"
        await status_msg.edit_text(debug_text, parse_mode='Markdown')

    except Exception as e:
        await status_msg.edit_text(f"❌ **System Error:** `{str(e)}`", parse_mode='Markdown')

def main():
    if not TELEGRAM_BOT_TOKEN or not RAPID_API_KEY:
        print("⚠️ Error: BOT_TOKEN ya RAPIDAPI_KEY nahi mila!")
        return

    threading.Thread(target=run_web, daemon=True).start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Ninja Insta Bot (Debug Mode) is running!")
    application.run_polling()

if __name__ == '__main__':
    main()

