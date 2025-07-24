import os
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube
from flask import Flask
from threading import Thread

TOKEN = "7898219623:AAHRUFZkJ_CjPGAYLjbYoJWchFrg9q7dvQM"
REQUEST_TIMEOUT = 30

# Inisialisasi Flask server
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot Aktif!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# Jalankan Flask di thread terpisah
Thread(target=run_flask).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🎬 **Video Downloader Bot**\n\nKirim link dari:\n- Instagram\n- TikTok\n- YouTube\n\nContoh: `https://www.instagram.com/reel/...`')

def download_youtube(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(filename="video.mp4", timeout=REQUEST_TIMEOUT)
        return open("video.mp4", "rb")
    except Exception as e:
        print(f"Error YouTube: {e}")
        return None

def download_tiktok(url):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT).json()
        video_url = response["data"]["play"]
        video_data = requests.get(video_url, timeout=REQUEST_TIMEOUT).content
        with open("tiktok.mp4", "wb") as f:
            f.write(video_data)
        return open("tiktok.mp4", "rb")
    except Exception as e:
        print(f"Error TikTok: {e}")
        return None

def download_instagram(url):
    try:
        api_url = f"https://api.instagram.com/oembed/?url={url}"
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT).json()
        media_url = response["thumbnail_url"]
        media_data = requests.get(media_url, timeout=REQUEST_TIMEOUT).content
        with open("instagram.mp4", "wb") as f:
            f.write(media_data)
        return open("instagram.mp4", "rb")
    except Exception as e:
        print(f"Error Instagram: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text

        if "instagram.com" in text:
            msg = await update.message.reply_text("⏳ Sedang mengunduh dari Instagram...")
            video = await asyncio.to_thread(download_instagram, text)
            if video:
                await update.message.reply_video(video=video, caption="✅ Berhasil diunduh dari Instagram!", write_timeout=REQUEST_TIMEOUT)
                video.close()
                os.remove("instagram.mp4")
            else:
                await update.message.reply_text("❌ Gagal mengunduh. Pastikan link valid!")

        elif "tiktok.com" in text:
            msg = await update.message.reply_text("⏳ Sedang mengunduh dari TikTok...")
            video = await asyncio.to_thread(download_tiktok, text)
            if video:
                await update.message.reply_video(video=video, caption="✅ Berhasil diunduh dari TikTok!", write_timeout=REQUEST_TIMEOUT)
                video.close()
                os.remove("tiktok.mp4")
            else:
                await update.message.reply_text("❌ Gagal mengunduh. Pastikan link valid!")

        elif "youtube.com" in text or "youtu.be" in text:
            msg = await update.message.reply_text("⏳ Sedang mengunduh dari YouTube...")
            video = await asyncio.to_thread(download_youtube, text)
            if video:
                await update.message.reply_video(video=video, caption="✅ Berhasil diunduh dari YouTube!", write_timeout=REQUEST_TIMEOUT)
                video.close()
                os.remove("video.mp4")
            else:
                await update.message.reply_text("❌ Gagal mengunduh. Pastikan link valid!")

        else:
            await update.message.reply_text("❌ Link tidak dikenali! Kirim link Instagram/TikTok/YouTube.")

    except Exception as e:
        print(f"Error utama: {e}")
        await update.message.reply_text("⚠️ Terjadi error saat memproses. Coba lagi nanti.")

if __name__ == '__main__':
    print("🤖 Bot sedang berjalan...")

    # Konfigurasi Application dengan timeout
    app = Application.builder() \
        .token(TOKEN) \
        .read_timeout(REQUEST_TIMEOUT) \
        .write_timeout(REQUEST_TIMEOUT) \
        .connect_timeout(REQUEST_TIMEOUT) \
        .pool_timeout(REQUEST_TIMEOUT) \
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(
        poll_interval=1,
        timeout=REQUEST_TIMEOUT,
        drop_pending_updates=True
    )
