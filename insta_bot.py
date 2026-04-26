import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# ⚠️ Yahan token nahi likhna hai, ye Render se aayega!
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")  
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

# 🌐 RENDER KE LIYE DUMMY WEB SERVER
app = Flask(__name__)

@app.route('/')
def home():
    return "Rahul's Insta Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 🤖 TELEGRAM BOT CODE
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🔥 **Insta Ninja Downloader में आपका स्वागत है!** 🔥\n\n"
        "मैं किसी भी Instagram Reel या Video को सेकंडों में डाउनलोड कर सकता हूँ। ⚡\n\n"
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

    status_msg = await update.message.reply_text("🔍 **लिंक स्कैन किया जा रहा है...**")
    await asyncio.sleep(1) 
    await status_msg.edit_text("⚙️ **सर्वर से वीडियो निकाला जा रहा है... 🚀**")
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    file_path = f"reel_{chat_id}.mp4"

    try:
        ydl_opts = {
            'outtmpl': file_path,
            'format': 'best', 
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        await status_msg.edit_text("📤 **टेलीग्राम पर अपलोड हो रहा है...**")
        
        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
            
        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id, 
                video=video_file, 
                supports_streaming=True,
                caption="🎬 **Download Successful!** ✅\n\n⚡ *Powered by Rahul Kumar Raj*",
                reply_markup=reply_markup
            )
        await status_msg.delete()

    except Exception as e:
        error_msg = f"❌ **Oops! कुछ गड़बड़ हो गई।**\nशायद लिंक प्राइवेट है। कृपया पब्लिक रील भेजें।"
        await status_msg.edit_text(error_msg, parse_mode='Markdown')
        print(f"Error: {e}")
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Error: BOT_TOKEN nahi mila! Kripya Render me Environment Variable set karein.")
        return

    # 🌐 Flask Server ko alag thread me start karna
    threading.Thread(target=run_web, daemon=True).start()
    
    # 🤖 Bot ko start karna
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Ninja Insta Bot is running 24/7! (Creator: Rahul Kumar Raj)")
    application.run_polling()

if __name__ == '__main__':
    main()
