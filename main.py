import os
import time
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path
from gemini_core import GeminiRoot  # استدعاء الجذر الذكي

# الإعدادات
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
FINAL_FILE = Path("final_reel.mp4")

def log(msg): print(f"🚀 [ENTERPRISE-SYSTEM] {msg}", flush=True)

def generate_viral_content():
    """توليد المحتوى عبر Gemini 1.5 Flash"""
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    res = model.generate_content("Viral Quote | Keyword | Description #viral").text
    return [i.strip() for i in res.split("|")]

def download_and_render(keyword, text):
    """تحميل ومعالجة الفيديو بجودة 1080p"""
    # التحميل من Pexels
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    v_url = requests.get(url, headers=headers).json()['videos'][0]['video_files'][0]['link']
    with open("raw.mp4", "wb") as f: f.write(requests.get(v_url).content)
    
    # FFmpeg: إضافة النص والسينما
    vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,drawtext=text='{text}':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:boxborderw=40"
    subprocess.run(["ffmpeg", "-y", "-i", "raw.mp4", "-vf", vf, "-c:a", "aac", str(FINAL_FILE)], check=True)

def main_execution():
    try:
        # 1. تجهيز المحتوى
        quote, key, desc = generate_viral_content()
        download_and_render(key, quote)
        
        # 2. المصافحة الثنائية (Binary Handshake)
        endpoint = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
        init = requests.post(endpoint, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
        video_id, upload_url = init["video_id"], init["upload_url"]
        
        # الرفع كبيانات خام (حل خطأ 6000)
        file_size = FINAL_FILE.stat().st_size
        with open(FINAL_FILE, "rb") as f:
            requests.post(upload_url, data=f, headers={
                "Authorization": f"OAuth {FB_TOKEN}",
                "file_size": str(file_size),
                "offset": "0",
                "Content-Type": "application/octet-stream"
            })
        
        # 3. تدخل "الجذر الذكي" للمراقبة والنشر
        core = GeminiRoot(FB_TOKEN, PAGE_ID)
        if core.verify_status(video_id):
            result = core.final_publish(video_id, desc)
            log(f"✅ Mission Accomplished: {result}")
        
    except Exception as e:
        log(f"🚨 System Failure: {e}")

if __name__ == "__main__":
    main_execution()
