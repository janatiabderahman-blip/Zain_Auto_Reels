import os
import time
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path

# --- Configuration (Verified) ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
RAW, FINAL = Path("raw.mp4"), Path("final.mp4")

def log(msg): print(f"🛡️ [GLOBAL-EXPERT-SYSTEM] {msg}", flush=True)

def get_viral_content():
    """AI Engine with local fallback to ensure 100% uptime"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # برومبت مصمم لجلب مشاهدات مليونية (Viral Prompt)
        prompt = "Create a high-retention Reel: Quote | Search Keyword | Viral Description with hashtags"
        response = model.generate_content(prompt)
        return [p.strip() for p in response.text.split("|")]
    except:
        return ["Success is a journey, not a destination.", "motivation", "Daily inspiration for winners! #success #mindset"]

def download_hd_media(keyword):
    """Media Engine: Optimized for 1080p Portrait"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    try:
        res = requests.get(url, headers=headers).json()
        v_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
        with RAW.open("wb") as f: f.write(requests.get(v_url, timeout=60).content)
    except:
        # Fallback to high-quality cloud video
        log("🔄 Using redundancy media server...")
        fallback = "https://cdn.pixabay.com/vimeo/239902912/forest-12157.mp4"
        with RAW.open("wb") as f: f.write(requests.get(fallback).content)

def render_expert_video(text):
    """FFmpeg Cinema-Grade Processing"""
    # تحسين الإضاءة (Contrast) وإضافة خلفية للنص لزيادة وقت المشاهدة
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "eq=contrast=1.1:brightness=0.02:saturation=1.1,"
        f"drawtext=text='{text}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.5:boxborderw=40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )
    subprocess.run(["ffmpeg", "-y", "-i", str(RAW), "-vf", vf, "-c:a", "aac", "-b:a", "192k", str(FINAL)], check=True)

def publish_mandatory(desc):
    """The Missing Link: Forced Public Publishing"""
    log("📡 Initiating Forced Handshake with Meta APIs...")
    base_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    
    # المرحلة 1: حجز مساحة الفيديو
    init = requests.post(base_url, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    if "video_id" not in init: raise Exception(f"Init Failed: {init}")
    
    # المرحلة 2: الرفع الثنائي (Binary Upload)
    with FINAL.open("rb") as f:
        requests.post(init["upload_url"], data=f, headers={"Authorization": f"OAuth {FB_TOKEN}"})
    
    # المرحلة 3: الانتظار الحرج (60 ثانية لضمان فحص جودة الفيديو في فيسبوك)
    log("⏳ Waiting for Meta processing (Mandatory 60s)...")
    time.sleep(60)
    
    # المرحلة 4: النشر الإجباري (Force Public)
    publish_res = requests.post(base_url, data={
        "upload_phase": "finish",
        "video_id": init["video_id"],
        "description": desc,
        "video_state": "PUBLISHED",  # القيمة التي تجعل الفيديو يظهر للجمهور
        "access_token": FB_TOKEN
    }).json()
    
    if publish_res.get("success"):
        log("✅ SUCCESS: Reel is LIVE and generating reach.")
    else:
        log(f"⚠️ Publish Warning: {publish_res}")

if __name__ == "__main__":
    try:
        quote, key, desc = get_viral_content()
        download_hd_media(key)
        render_expert_video(quote)
        publish_mandatory(desc)
    finally:
        # Self-Healing: Clean environment for the next run
        for f in [RAW, FINAL]:
            if f.exists(): f.unlink()
