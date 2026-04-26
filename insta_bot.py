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
    return "Ninja Bot: Debugging JSON structure..."

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "🚀 **Debug Mode ON** 🚀\nलिंक भेजें और JSON चेक करें।"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text
    status_msg = await update.message.reply_text("⚙️ **API Response स्कैन किया जा रहा है...**")

    try:
        api_url = "https://instagram120.p.rapidapi.com/api/instagram/links" 
        payload = {"url": url}
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": "instagram120.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        # 🛠️ Yahan hum pura JSON dikhayenge taaki hume sahi field mil sake
        import json
        clean_json = json.dumps(data, indent=2)
        debug_text = f"✅ **API ne ye data bheja hai:**\n\n`{clean_json[:3500]}`"
        
        await status_msg.edit_text(debug_text, parse_mode='Markdown')

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** `{str(e)}`")

def main():
    threading.Thread(target=run_web, daemon=True).start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
