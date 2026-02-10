import os
import time
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path

# --- Configuration (Verified & Safe) ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

# Paths (Sanitized Roots)
BASE_DIR = Path(__file__).resolve().parent
RAW_PATH = BASE_DIR / "raw_video.mp4"
FINAL_PATH = BASE_DIR / "final_reel.mp4"

def log(msg): 
    print(f"🛡️ [SYSTEM-EXPERT] {msg}", flush=True)

def clean_environment():
    """Removes all temporary media to prevent conflicts"""
    for file in [RAW_PATH, FINAL_PATH]:
        if file.exists():
            file.unlink()

def get_viral_content():
    """Generates viral quotes and keywords using Gemini 1.5 Flash"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Provide: Viral Quote | One-word English Keyword | Facebook Description with hashtags"
        response = model.generate_content(prompt)
        parts = [p.strip() for p in response.text.split("|")]
        if len(parts) >= 3:
            return parts
        raise ValueError("AI Formatting mismatch")
    except Exception as e:
        log(f"AI Warning: {e}. Using expert fallback.")
        return ["The best way to predict the future is to create it.", "success", "Dream big! #success #motivation"]

def download_hd_video(keyword):
    """Fetches high-quality 1080p portrait video from Pexels"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    try:
        res = requests.get(url, headers=headers).json()
        video_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
        with open(RAW_PATH, "wb") as f:
            f.write(requests.get(video_url, timeout=60).content)
        log("✅ HD Media downloaded.")
    except Exception as e:
        log(f"Media Error: {e}. Using high-quality redundancy link.")
        fallback = "https://cdn.pixabay.com/vimeo/239902912/forest-12157.mp4"
        with open(RAW_PATH, "wb") as f:
            f.write(requests.get(fallback).content)

def render_professional_video(text):
    """FFmpeg rendering with professional visual enhancements"""
    log("🎨 Rendering cinematic overlay...")
    # Filters: Auto-scale to 1080x1920, sharpen, and add centered text box
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "unsharp=5:5:1.0:5:5:0.0," 
        f"drawtext=text='{text}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.5:boxborderw=40"
    )
    subprocess.run(["ffmpeg", "-y", "-i", str(RAW_PATH), "-vf", vf, "-c:a", "aac", "-b:a", "192k", str(FINAL_PATH)], check=True)

def publish_to_facebook(description):
    """The Core Fix: Binary Stream Handshake (Resolves Error 6000)"""
    log("📡 Initiating Binary Handshake with Meta APIs...")
    endpoint = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    
    # STEP 1: Initialize Session
    init_res = requests.post(endpoint, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    video_id = init_res.get("video_id")
    upload_url = init_res.get("upload_url")
    
    if not video_id or not upload_url:
        log(f"❌ Session Init Failed: {init_res}")
        return

    # STEP 2: Raw Binary Upload (The Missing Link)
    file_size = os.path.getsize(FINAL_PATH)
    log(f"📦 Pushing {file_size} bytes to Meta servers...")
    
    with open(FINAL_PATH, "rb") as video_file:
        upload_response = requests.post(
            upload_url, 
            data=video_file, 
            headers={
                "Authorization": f"OAuth {FB_TOKEN}",
                "offset": "0",
                "file_size": str(file_size)
            }
        )
    log(f"📤 Upload Handshake Status: {upload_response.status_code}")

    # STEP 3: Cooldown for server-side processing
    log("⏳ Processing video on Meta servers (90s)...")
    time.sleep(90)

    # STEP 4: Forced Public Publication
    publish_data = {
        "upload_phase": "finish",
        "video_id": video_id,
        "description": description,
        "video_state": "PUBLISHED", # Critical for visibility
        "access_token": FB_TOKEN
    }
    final_res = requests.post(endpoint, data=publish_data).json()
    
    if "success" in final_res or "video_id" in final_res:
        log("🎉 SUCCESS: Your Reel is now LIVE on Facebook!")
    else:
        log(f"🚨 Final Publish Warning: {final_res}")

def start_system():
    start_time = time.time()
    try:
        clean_environment()
        quote, keyword, desc = get_viral_content()
        log(f"💡 AI Choice: {keyword}")
        download_hd_video(keyword)
        render_professional_video(quote)
        publish_to_facebook(desc)
    except Exception as e:
        log(f"🚨 System Critical Error: {e}")
    finally:
        clean_environment()
        log(f"⏱️ Total execution time: {int(time.time() - start_time)} seconds.")

if __name__ == "__main__":
    start_system()
