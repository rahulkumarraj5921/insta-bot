import os
import asyncio
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ Render se Token aayega
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")  
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

# 🌐 WEB SERVER
app = Flask(__name__)

@app.route('/')
def home():
    return "Rahul's Insta Bot is running with Cloud API!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 🤖 BOT CODE
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🔥 **Insta Ninja Downloader में आपका स्वागत है!** 🔥\n\n"
        "मैं Cloud API का इस्तेमाल करके किसी भी Instagram Reel को डाउनलोड कर सकता हूँ। ⚡\n\n"
        "🎯 *बस मुझे कोई भी Instagram लिंक भेजें और जादू देखें!*\n\n"
        "👇 **Developer को सपोर्ट करने के लिए Instagram पर फॉलो करें:**"
    )
    keyboard = [[InlineKeyboardButton("💖 Follow Me on Instagram 💖", url=INSTA_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ दोस्त, यह Instagram का लिंक नहीं लग रहा है। कृपया सही लिंक भेजें!")
        return

    status_msg = await update.message.reply_text("🔍 **Cloud API से लिंक बायपास किया जा रहा है...**")
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    file_path = f"reel_{chat_id}.mp4"

    try:
        # 🪄 JADUU YAHAN HAI: Cobalt Free API Call
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {"url": url}
        
        # API ko request bhejna
        api_response = requests.post("https://api.cobalt.tools/api/json", json=data, headers=headers)
        res_json = api_response.json()
        
        # Agar API ne error diya
        if "url" not in res_json:
            raise Exception("API block ho gayi ya link galat hai.")
            
        video_url = res_json["url"]
        await status_msg.edit_text("⚙️ **वीडियो मिल गया! सर्वर पर डाउनलोड हो रहा है... 🚀**")
        
        # Render server par video save karna
        video_data = requests.get(video_url).content
        with open(file_path, 'wb') as handler:
            handler.write(video_data)
            
        await status_msg.edit_text("📤 **टेलीग्राम पर अपलोड हो रहा है...**")
        
        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
            
        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id, 
                video=video_file, 
                supports_streaming=True,
                caption="🎬 **Download Successful!** ✅\n\n⚡ *Powered by Cloud API & Rahul Kumar Raj*",
                reply_markup=reply_markup
            )
        await status_msg.delete()

    except Exception as e:
        error_msg = f"❌ **Oops! कुछ गड़बड़ हो गई।**\nशायद लिंक प्राइवेट है या API सर्वर बिज़ी है।\n`Error: {e}`"
        await status_msg.edit_text(error_msg, parse_mode='Markdown')
        print(f"Error: {e}")
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Error: BOT_TOKEN nahi mila!")
        return

    threading.Thread(target=run_web, daemon=True).start()
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Ninja Insta Bot (API Version) is running 24/7!")
    application.run_polling()

if __name__ == '__main__':
    main()
