import os
import re
import time
import telebot
import yt_dlp

BOT_TOKEN = "7998126948:AAFEAP_iEH2eMlmG9vXYK-ojMddnmfXpEks"
bot = telebot.TeleBot(BOT_TOKEN)
TEMP_FOLDER = "temp_downloads"
MAX_VIDEO_SIZE_MB = 50

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

def extract_tiktok_url(text):
    patterns = [
        r'(https?://(?:vm\.|vt\.|www\.|m\.)?tiktok\.com/\S+)',
        r'(https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def download_tiktok_video(url):
    ydl_opts = {
        'outtmpl': f'{TEMP_FOLDER}/%(title)s_%(id)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'no_color': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        if not os.path.exists(file_path):
            base = os.path.splitext(file_path)[0]
            for ext in ['.mp4', '.webm', '.mkv']:
                candidate = base + ext
                if os.path.exists(candidate):
                    file_path = candidate
                    break
        return file_path

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✨ أهلاً بك! أرسل رابط تيك توك.")

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    url = extract_tiktok_url(message.text)
    if not url:
        bot.reply_to(message, "❌ أرسل رابط تيك توك صالح.")
        return
    status_msg = bot.reply_to(message, "⏳ جاري التحميل...")
    try:
        video_path = download_tiktok_video(url)
        file_size_mb = os.path.getsize(video_path) / (1024*1024)
        if file_size_mb > MAX_VIDEO_SIZE_MB:
            os.remove(video_path)
            bot.edit_message_text("⚠️ الفيديو أكبر من 50 ميجابايت", message.chat.id, status_msg.message_id)
            return
        with open(video_path, 'rb') as vid:
            bot.send_video(message.chat.id, vid, caption="✅ تم التحميل")
        bot.delete_message(message.chat.id, status_msg.message_id)
        time.sleep(30)
        os.remove(video_path)
    except Exception as e:
        bot.edit_message_text(f"⚠️ فشل: {str(e)[:100]}", message.chat.id, status_msg.message_id)

print("✅ البوت شغال...")
bot.infinity_polling()