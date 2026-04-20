import os, re, requests, asyncio, threading
import telebot
import edge_tts
from flask import Flask
from moviepy.editor import *
from moviepy.config import change_settings
from urllib.parse import quote

# --- CONFIGURATION ---
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(8759756266:AAEYPEszDYC1x3Z1pfh-RH-j2bFgFY2XB84)

app = Flask(__name__)

@app.route('/')
def home(): return "Bot is Running!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

def setup_assets():
    if not os.path.exists("font.ttf"):
        font_url = "https://github.com"
        r = requests.get(font_url)
        with open("font.ttf", 'wb') as f: f.write(r.content)
    if not os.path.exists("bgm.mp3"):
        bgm_url = "https://bensound.com"
        r = requests.get(bgm_url)
        with open("bgm.mp3", 'wb') as f: f.write(r.content)

async def generate_voice(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

def get_image(text, i):
    encoded_prompt = quote(f"3d disney pixar style, cinematic lighting, {text}")
    url = f"https://pollinations.ai{encoded_prompt}?width=720&height=1280&seed={i}&model=flux&nologo=true"
    try:
        r = requests.get(url, timeout=30)
        with open(f"img_{i}.jpg", 'wb') as f: f.write(r.content)
        return f"img_{i}.jpg"
    except: return None

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "🎬 **AI Cinematic Bot Ready!**\nSend me a story in Hindi or English.")

@bot.message_handler(func=lambda m: True)
def process(m):
    cid = m.chat.id
    status = bot.reply_to(m, "⏳ **Step 1/2: Generating Voice & Visuals...**")
    sentences = [s.strip() for s in re.split(r'[।|?|!|\n]', m.text) if len(s.strip()) > 5][:5]
    clips = []
    temp_files = []
    
    try:
        for i, line in enumerate(sentences):
            v_path = f"v_{i}.mp3"
            img_path = f"img_{i}.jpg"
            temp_files.extend([v_path, img_path])
            asyncio.run(generate_voice(line, "hi-IN-SwaraNeural", v_path))
            img = get_image(line, i)
            if img:
                audio = AudioFileClip(v_path)
                txt = TextClip(line, font='font.ttf', fontsize=45, color='yellow', 
                               method='caption', size=(650, None), stroke_color='black', stroke_width=2)
                txt = txt.set_position(('center', 900)).set_duration(audio.duration)
                video = ImageClip(img).set_duration(audio.duration).resize(lambda t: 1 + 0.03*t)
                clips.append(CompositeVideoClip([video, txt]).set_audio(audio))

        if clips:
            bot.edit_message_text("🎞️ **Step 2/2: Rendering Video...**", cid, status.message_id)
            final = concatenate_videoclips(clips, method="compose")
            if os.path.exists("bgm.mp3"):
                bgm = AudioFileClip("bgm.mp3").volumex(0.12)
                final.audio = CompositeAudioClip([final.audio, afx.audio_loop(bgm, duration=final.duration)])
            out_file = f"vid_{cid}.mp4"
            final.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac", threads=4)
            with open(out_file, "rb") as v:
                bot.send_video(cid, v, caption="✅ **Your AI Video is Ready!**")
            temp_files.append(out_file)
    except Exception as e:
        bot.send_message(cid, f"❌ Error: {str(e)}")
    finally:
        for c in clips: c.close()
        for f in temp_files:
            if os.path.exists(f): os.remove(f)
        bot.delete_message(cid, status.message_id)

if __name__ == "__main__":
    setup_assets()
    keep_alive()
    bot.polling(none_stop=True)
  
