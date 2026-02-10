import os
import time
import requests
import subprocess
import google.generativeai as genai  # الطريقة الصحيحة والمستقرة
from pathlib import Path

# استدعاء مفاتيح الربط (Secrets)
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

RAW, FINAL = Path("raw.mp4"), Path("final.mp4")

def log(msg): print(f"💎 [ZAIN-EXPERT] {msg}", flush=True)

def get_ai_content():
    """توليد محتوى احترافي باستخدام Gemini 1.5 Flash المستقر"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # برومبت احترافي لجلب محتوى فيروسي (Viral Content)
        prompt = (
            "Create a high-impact Facebook Reel concept. "
            "Return exactly in this format: Quote | English Search Keyword | Professional Description"
        )
        
        response = model.generate_content(prompt)
        parts = [p.strip() for p in response.text.split("|")]
        
        if len(parts) < 3: raise ValueError("AI Format Error")
        return parts
    except Exception as e:
        log(f"⚠️ AI Error: {e}. Switching to Backup Strategy.")
        return ["Success is not final, failure is not fatal.", "inspiration", "Keep moving forward! #motivation #success"]

def download_hd_video(keyword):
    """جلب فيديو عالي الدقة 1080p لضمان جودة المحتوى"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    
    res = requests.get(url, headers=headers).json()
    if not res.get('videos'):
        # رابط احتياطي دائم لضمان عدم توقف البوت
        video_url = "https://cdn.pixabay.com/vimeo/239902912/forest-12157.mp4"
    else:
        # اختيار أعلى دقة متاحة (Full HD)
        video_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
    
    with RAW.open("wb") as f:
        f.write(requests.get(video_url, timeout=60).content)
    log("✅ HD Video ready.")

def process_video_expert(text):
    """معالجة سينمائية احترافية باستخدام FFmpeg"""
    # فلتر توسيط النص، ضبط الحجم، وتحسين الألوان
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "eq=contrast=1.1:brightness=0.03:saturation=1.2," # تحسين اللون سينمائياً
        f"drawtext=text='{text}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.5:boxborderw=35" # خلفية نص احترافية
    )
    cmd = ["ffmpeg", "-y", "-i", str(RAW), "-vf", vf, "-c:a", "aac", "-shortest", str(FINAL)]
    subprocess.run(cmd, check=True)

def publish_to_facebook(desc):
    """الرفع الرسمي عبر فيسبوك Graph API v18.0"""
    log("📡 Publishing to Facebook Reels...")
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
    
    # المرحلة 1: البداية
    init = requests.post(url, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    video_id, upload_url = init["video_id"], init["upload_url"]
    
    # المرحلة 2: الرفع الفعلي
    with FINAL.open("rb") as f:
        requests.post(upload_url, data=f, headers={"Authorization": f"OAuth {FB_TOKEN}"})
    
    # المرحلة 3: انتظار المعالجة (هام جداً للصفحات الكبيرة)
    time.sleep(40)
    
    # المرحلة 4: الإنهاء والوصف
    finish = requests.post(url, data={
        "upload_phase": "finish", "video_id": video_id, 
        "description": desc, "access_token": FB_TOKEN
    })
    log(f"🎉 Reel Published! ID: {video_id}")

def run():
    try:
        log("🚀 Zain Expert Bot Started...")
        quote, key, desc = get_ai_content()
        log(f"💡 Topic: {key}")
        download_hd_video(key)
        process_video_expert(quote)
        publish_to_facebook(desc)
    except Exception as e:
        log(f"❌ Final Error: {e}")
    finally:
        # تنظيف الملفات للحفاظ على مساحة GitHub
        for f in [RAW, FINAL]:
            if f.exists(): f.unlink()

if __name__ == "__main__":
    run()
