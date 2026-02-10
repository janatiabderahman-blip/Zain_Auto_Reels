import os
import time
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path

# CONFIG
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
RAW, FINAL = Path("raw.mp4"), Path("final.mp4")

def log(msg): print(f"🚀 [ZAIN-AI] {msg}", flush=True)

def get_creative():
    """توليد محتوى ذكي باستخدام Gemini 1.5 Flash"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Return exactly: Quote | Search Keyword | Description"
        response = model.generate_content(prompt)
        return [p.strip() for p in response.text.split("|")]
    except:
        return ["Believe in yourself.", "mountain", "Daily motivation! #success"]

def download_video(keyword):
    """تحميل فيديو عالي الجودة"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    v_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
    with RAW.open("wb") as f: f.write(requests.get(v_url).content)

def render(text):
    """المعالجة الاحترافية بـ FFmpeg"""
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawtext=text='{text}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.5:boxborderw=40"
    )
    subprocess.run(["ffmpeg", "-y", "-i", str(RAW), "-vf", vf, "-c:a", "aac", str(FINAL)], check=True)

def publish(desc):
    """أمر النشر العام الفوري لضمان الظهور على الصفحة"""
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
    # البدء
    init = requests.post(url, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    # الرفع
    with FINAL.open("rb") as f:
        requests.post(init["upload_url"], data=f, headers={"Authorization": f"OAuth {FB_TOKEN}"})
    # الانتظار لمعالجة فيسبوك
    time.sleep(60)
    # النشر العام النهائي (أهم خطوة)
    res = requests.post(url, data={
        "upload_phase": "finish",
        "video_id": init["video_id"],
        "description": desc,
        "video_state": "PUBLISHED", # هذا السطر يضمن الظهور العلني
        "access_token": FB_TOKEN
    })
    log(f"Result: {res.status_code} - {res.text}")

if __name__ == "__main__":
    try:
        quote, key, desc = get_creative()
        download_video(key)
        render(quote)
        publish(desc)
    except Exception as e:
        log(f"Error: {e}")
