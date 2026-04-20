import os, re, requests, asyncio, threading, subprocess
import telebot
import edge_tts
from flask import Flask
from urllib.parse import quote

# --- CONFIGURATION ---
API_TOKEN = "8759756266:AAFVCXuYGFQxPuPYr1q6_TQUEGyjjRGEA_Q" # <-- अपना नया टोकन यहाँ डालें
bot = telebot.TeleBot(API_TOKEN)

ALLOWED_USER_ID = 5177831693 

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"

def run_server():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# यहाँ आवाज़ें (Voices) अपडेट की गई हैं
VOICES = {"B": "hi-IN-MadhurNeural", "G": "hi-IN-AnanyaNeural", "E": "hi-IN-AnanyaNeural"}

def auto_voice(text):
    t = text.lower()
    if any(w in t for w in ["lalla", "kanha", "beta", "boy", "he"]): return "B"
    return "G"

def get_image(text, i):
    try:
        encoded_prompt = quote(f"3d disney pixar style, {text}, cinematic lighting, 9:16 aspect ratio")
        url = f"https://pollinations.ai{encoded_prompt}?width=720&height=1280&seed={i}&model=flux&nologo=true"
        r = requests.get(url, timeout=30)
        path = f"img_{i}.jpg"
        with open(path, 'wb') as f: f.write(r.content)
        return path
    except: return None

@bot.message_handler(commands=['start'])
def welcome(m):
    if m.chat.id != ALLOWED_USER_ID:
        bot.reply_to(m, "❌ Access Denied!")
        return
    bot.reply_to(m, "🎬 **नमस्ते मालिक!** कहानी भेजें, मैं वीडियो बनाता हूँ।")

async def make_audio(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

@bot.message_handler(func=lambda m: True)
def process_video(m):
    cid = m.chat.id
    if cid != ALLOWED_USER_ID: return

    msg = bot.reply_to(m, "⏳ **ऑडियो और वीडियो बन रहा है...**")
    sentences = [s.strip() for s in re.split(r'[।|?|!|\n]', m.text) if len(s.strip()) > 3][:6]
    clips = []
    temp_files = []

    try:
        for i, line in enumerate(sentences):
            vtype = auto_voice(line)
            v_path = f"v_{i}.mp3"; out = f"p_{i}.mp4"
            temp_files.extend([v_path, out])
            
            # ऑडियो बनाने का नया तरीका (More Stable)
            asyncio.run(make_audio(line, VOICES[vtype], v_path))
            
            img_path = get_image(line, i)
            if not img_path: continue
            temp_files.append(img_path)
            
            cmd = (
                f'ffmpeg -y -loop 1 -i {img_path} -i {v_path} -vf '
                f'"scale=720:1280,format=yuv420p,drawtext=text=\'{line[:40]}...\':fontcolor=yellow:fontsize=35:x=(w-text_w)/2:y=h-300:box=1:boxcolor=black@0.6" '
                f'-c:v libx264 -preset superfast -tune stillimage -c:a aac -shortest {out}'
            )
            subprocess.run(cmd, shell=True)
            if os.path.exists(out): clips.append(out)

        if clips:
            final_vid = f"final_{cid}.mp4"
            list_fn = f"list_{cid}.txt"
            with open(list_fn, "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {list_fn} -c copy {final_vid}", shell=True)
            
            with open(final_vid, "rb") as v:
                bot.send_video(cid, v, caption="✅ तैयार है!")
            temp_files.extend([final_vid, list_fn])

    except Exception as e:
        bot.send_message(cid, f"❌ Error: {str(e)}")
    finally:
        for f in temp_files:
            if os.path.exists(f): os.remove(f)
        bot.delete_message(cid, msg.message_id)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    bot.polling(none_stop=True)
        
