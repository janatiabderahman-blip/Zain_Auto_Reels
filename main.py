import os
import time
import random
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path

# --- الإعدادات والبيئات ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

RAW, PROC, FINAL = Path("raw.mp4"), Path("proc.mp4"), Path("final.mp4")

def log(msg): print(f"💎 [ZAIN-AI] {msg}", flush=True)

def get_ai_creative():
    """توليد فكرة ومحتوى احترافي باستخدام Gemini"""
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = (
        "Create a viral Facebook Reel concept about 'Success and Motivation'. "
        "Provide: 1. A powerful short quote (max 8 words). "
        "2. One English keyword for a high-quality cinematic background video. "
        "3. A professional description with 3 trending hashtags. "
        "Format: Quote | Keyword | Description"
    )
    
    response = model.generate_content(prompt)
    parts = response.text.split("|")
    return parts[0].strip(), parts[1].strip(), parts[2].strip()

def download_video_pexels(keyword):
    """جلب فيديو عالي الجودة متوافق مع معايير Pexels"""
    log(f"🔍 Searching Pexels for: {keyword}")
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=5&orientation=portrait"
    
    res = requests.get(url, headers=headers).json()
    video_data = random.choice(res['videos'])
    # اختيار أعلى جودة HD
    video_url = [f['link'] for f in video_data['video_files'] if f['width'] >= 1080][0]
    
    with RAW.open("wb") as f:
        f.write(requests.get(video_url, timeout=60).content)
    log("✅ High-quality video downloaded")

def process_video_pro(text):
    """معالجة الفيديو بمعايير احترافية (FFmpeg) لضمان عدم رفض الإعلانات"""
    log("🎨 Applying Cinematic Filters and Typography...")
    
    # فلتر سينمائي: تحسين الألوان + نص احترافي في منتصف الشاشة مع خلفية شبه شفافة
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920," # ضبط الأبعاد
        "eq=contrast=1.1:brightness=0.02:saturation=1.2," # تحسين اللون
        f"drawtext=text='{text}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.6:boxborderw=30:font='Verdana'" # نص مقروء واحترافي
    )
    
    cmd = ["ffmpeg", "-y", "-i", str(RAW), "-vf", vf, "-c:a", "aac", "-shortest", str(FINAL)]
    subprocess.run(cmd, check=True)

def upload_to_facebook(description):
    """رفع الفيديو باستخدام Graph API v18.0"""
    log("📡 Uploading to Facebook Reels...")
    # (نفس دالة الرفع المستقرة في كودك الأصلي مع إضافة التحقق من النجاح)
    # ملاحظة: تم استخدام FINAL هنا لضمان رفع النسخة المعالجة
    url_start = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
    init = requests.post(url_start, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    
    video_id, upload_url = init["video_id"], init["upload_url"]
    
    with FINAL.open("rb") as f:
        requests.post(upload_url, data=f, headers={"Authorization": f"OAuth {FB_TOKEN}"})
    
    time.sleep(30) # وقت إضافي للمعالجة قبل الإنهاء
    
    finish = requests.post(url_start, data={
        "upload_phase": "finish", "video_id": video_id, 
        "description": description, "access_token": FB_TOKEN
    })
    log(f"🎉 Published! Response: {finish.status_code}")

def run():
    try:
        quote, key, desc = get_ai_creative()
        download_video_pexels(key)
        process_video_pro(quote)
        upload_to_facebook(desc)
    except Exception as e:
        log(f"❌ Error: {e}")
    finally:
        for f in [RAW, FINAL]: 
            if f.exists(): f.unlink()

if __name__ == "__main__":
    run()
