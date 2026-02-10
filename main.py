import os
import time
import requests
import subprocess
import google.generativeai as genai  # الطريقة المستقرة والمضمونة
from pathlib import Path

# جلب المفاتيح من بيئة GitHub Actions
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

RAW, FINAL = Path("raw.mp4"), Path("final.mp4")

def log(msg): print(f"💎 [ZAIN-AI-PRO] {msg}", flush=True)

def get_ai_creative():
    """توليد محتوى فريد باستخدام الإصدار المستقر لتجنب خطأ 404"""
    genai.configure(api_key=GEMINI_KEY)
    # استخدام نموذج flash-1.5 المستقر عالمياً
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = "Create a viral Facebook Reel concept. Return format: Quote | Video Keyword | Long Description"
    
    try:
        response = model.generate_content(prompt)
        parts = [p.strip() for p in response.text.split("|")]
        if len(parts) < 3: raise ValueError("AI Format Error")
        return parts
    except Exception as e:
        log(f"⚠️ AI falling back to defaults due to: {e}")
        return ["Keep Pushing Forward", "motivation", "Stay inspired every day! #motivation"]

def download_video_pexels(keyword):
    """جلب فيديو عالي الجودة 1080p"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    
    if not res.get('videos'):
        # فيديو احتياطي في حال فشل البحث
        video_url = "https://cdn.pixabay.com/vimeo/239902912/forest-12157.mp4"
    else:
        video_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
        
    with RAW.open("wb") as f:
        f.write(requests.get(video_url).content)

def process_video_pro(text):
    """المعالجة الاحترافية بـ FFmpeg"""
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawtext=text='{text}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.5:boxborderw=30"
    )
    subprocess.run(["ffmpeg", "-y", "-i", str(RAW), "-vf", vf, "-c:a", "aac", str(FINAL)], check=True)

def upload_to_facebook(description):
    """الرفع الرسمي عبر فيسبوك v18.0"""
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
    init = requests.post(url, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    
    with FINAL.open("rb") as f:
        requests.post(init["upload_url"], data=f, headers={"Authorization": f"OAuth {FB_TOKEN}"})
    
    time.sleep(30)
    requests.post(url, data={
        "upload_phase": "finish", "video_id": init["video_id"], 
        "description": description, "access_token": FB_TOKEN
    })

def run():
    try:
        log("🚀 Starting AI Pro Bot (Final Fixed Version)...")
        quote, key, desc = get_ai_creative()
        log(f"💡 Topic: {key}")
        download_video_pexels(key)
        process_video_pro(quote)
        upload_to_facebook(desc)
        log("✅ Success! Reel is live.")
    except Exception as e:
        log(f"❌ Critical Error: {e}")
    finally:
        for f in [RAW, FINAL]:
            if f.exists(): f.unlink()

if __name__ == "__main__":
    run()
