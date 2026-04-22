import os
import telebot
from flask import Flask
from threading import Thread
from huggingface_hub import InferenceClient
import io

# 1. Render को 'जिंदा' रखने के लिए वेब सर्वर सेटअप
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run():
    # Render स्वचालित रूप से PORT प्रदान करता है
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. बॉट और AI क्लाइंट सेटअप
# टोकन सीधा कोड में न डालें, Render के 'Environment Variables' में सेट करें
TOKEN = os.environ.get('TELEGRAM_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

bot = telebot.TeleBot(TOKEN)
client = InferenceClient(token=HF_TOKEN)

# 3. बॉट कमांड्स
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "नमस्ते! मुझे अपनी कहानी भेजें, मैं उसकी AI इमेज बनाऊंगा।")

@bot.message_handler(func=lambda message: True)
def handle_story(message):
    msg = bot.reply_to(message, "🎨 आपकी कहानी से इमेज तैयार की जा रही है...")
    
    try:
        # AI मॉडल का उपयोग करके इमेज जनरेट करना
        prompt = f"Cinematic masterpiece, 4k, high detail: {message.text}"
        image = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")

        # इमेज को टेलीग्राम पर भेजने के लिए फॉर्मेट करना
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        bot.send_photo(message.chat.id, photo=img_byte_arr, caption="✨ आपका सीन तैयार है!")
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ एरर आया: {str(e)}")

# 4. बॉट शुरू करना
if __name__ == "__main__":
    keep_alive()  # वेब सर्वर शुरू करें
    print("Bot is starting...")
    bot.infinity_polling() # बॉट चालू करें
    
