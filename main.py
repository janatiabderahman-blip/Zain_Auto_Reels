import os
import time
import requests
import subprocess
from google import genai
from pathlib import Path

# جلب المفاتيح من بيئة GitHub Actions
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

RAW, FINAL = Path("raw.mp4"), Path("final.mp4")

def log(msg): print(f"💎 [ZAIN-AI-PRO] {msg}", flush=True)

def get_ai_creative():
    """استخدام المكتبة الرسمية الجديدة google-genai لإصلاح خطأ 404"""
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = "Create a viral Facebook Reel concept. Return exactly this format: Quote | Video Keyword | Long Description"
    
    # استخدام النموذج المحدث gemini-2.0-flash لضمان القبول العالمي
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    return [p.strip() for p in response.text.split("|")]

def download_video_pexels(keyword):
    """جلب فيديو عالي الجودة من Pexels"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    video_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
    with RAW.open("wb") as f:
        f.write(requests.get(video_url).content)

def process_video_pro(text):
    """معالجة الفيديو باستخدام FFmpeg"""
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawtext=text='{text}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.5:boxborderw=30"
    )
    subprocess.run(["ffmpeg", "-y", "-i", str(RAW), "-vf", vf, "-c:a", "aac", str(FINAL)], check=True)

def upload_to_facebook(description):
    """الرفع الرسمي عبر فيسبوك Graph API v18.0"""
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
        log("🚀 Starting AI Pro Bot with new google-genai library...")
        quote, key, desc = get_ai_creative()
        log(f"💡 AI Content Generated: {quote}")
        download_video_pexels(key)
        process_video_pro(quote)
        upload_to_facebook(desc)
        log("✅ Process Completed Successfully!")
    except Exception as e:
        log(f"❌ Final Error: {e}")
    finally:
        for f in [RAW, FINAL]: 
            if f.exists(): f.unlink()

if __name__ == "__main__":
    run()
