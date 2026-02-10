import os
import time
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path

# ENVIRONMENT CONFIGURATION
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

# PATH CONFIGURATION
BASE_DIR = Path(__file__).resolve().parent
RAW_PATH = BASE_DIR / "raw_video.mp4"
FINAL_PATH = BASE_DIR / "final_reel.mp4"

def log(msg):
    print(f"[*] {msg}", flush=True)

def clean_env():
    """Removes temporary files from the root directory"""
    for file in [RAW_PATH, FINAL_PATH]:
        if file.exists():
            file.unlink()

def get_content_ai():
    """AI Engine: Generates unique content to avoid FB reuse policy"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Create a viral Facebook Reel concept. Format: Quote | Search Keyword | Description"
        response = model.generate_content(prompt)
        return [p.strip() for p in response.text.split("|")]
    except Exception as e:
        log(f"AI_ERROR: {e}")
        return ["Keep going, your hard work will pay off.", "motivation", "Stay inspired! #motivation"]

def download_media(keyword):
    """Media Engine: Fetches HD 1080p video from Pexels API"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    try:
        res = requests.get(url, headers=headers).json()
        video_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
        with open(RAW_PATH, "wb") as f:
            f.write(requests.get(video_url, timeout=60).content)
    except Exception as e:
        log(f"DOWNLOAD_ERROR: {e}")
        # Fallback to a stable CC0 video
        fallback = "https://cdn.pixabay.com/vimeo/239902912/forest-12157.mp4"
        with open(RAW_PATH, "wb") as f:
            f.write(requests.get(fallback).content)

def render_video(text):
    """Graphics Engine: Professional FFmpeg rendering with text-overlay"""
    vf_filters = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawtext=text='{text}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.5:boxborderw=40"
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(RAW_PATH),
        "-vf", vf_filters,
        "-c:a", "aac", "-shortest", str(FINAL_PATH)
    ]
    subprocess.run(cmd, check=True)

def publish_facebook(description):
    """API Engine: Facebook Graph API v18.0 Integration"""
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
    
    # Step 1: Initialize Upload
    init = requests.post(url, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    video_id, upload_url = init["video_id"], init["upload_url"]
    
    # Step 2: Push Binary Data
    with open(FINAL_PATH, "rb") as f:
        requests.post(upload_url, data=f, headers={"Authorization": f"OAuth {FB_TOKEN}"})
    
    # Step 3: Wait for Processing
    time.sleep(45)
    
    # Step 4: Finalize & Publish
    finish = requests.post(url, data={
        "upload_phase": "finish", "video_id": video_id, 
        "description": description, "access_token": FB_TOKEN
    })
    log(f"PUBLISH_STATUS: {finish.status_code}")

def execute():
    try:
        clean_env()
        quote, keyword, desc = get_content_ai()
        download_media(keyword)
        render_video(quote)
        publish_facebook(desc)
    finally:
        clean_env()

if __name__ == "__main__":
    execute()
