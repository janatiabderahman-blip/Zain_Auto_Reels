import os
import time
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path

# 1. إعدادات الهوية والوصول (تأكد من وجودها في GitHub Secrets)
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

# 2. تحديد مسارات الجذور (Root Paths) لضمان الاستقرار في بيئة Linux
BASE_DIR = Path(__file__).resolve().parent
RAW_PATH = BASE_DIR / "raw_video.mp4"
FINAL_PATH = BASE_DIR / "final_reel.mp4"

def log(msg): 
    print(f"🧠 [GEMINI-GUARD] {msg}", flush=True)

def self_healing_clean():
    """صيانة ذاتية: تنظيف الجذور قبل وبعد كل دورة"""
    for file in [RAW_PATH, FINAL_PATH]:
        if file.exists():
            file.unlink()

def gemini_content_engine():
    """محرك المحتوى: دمج قدراتي لإنتاج نصوص تضمن المشاهدات المليونية"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # برومبت استراتيجي للهروب من المحتوى المكرر
        prompt = "Generate a viral quote for a reel. Format: Quote | SearchKeyword | Description #viral"
        response = model.generate_content(prompt)
        parts = [p.strip() for p in response.text.split("|")]
        return parts if len(parts) >= 3 else ["Success is built daily.", "office", "Join the winning side! #success"]
    except Exception as e:
        log(f"Gemini Engine Warning: {e}. Switching to internal storage.")
        return ["Keep going, the top is near.", "mountain", "Daily inspiration! #motivation"]

def download_and_verify(keyword):
    """تحميل الفيديو والتحقق من جودته برمجياً"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
    try:
        res = requests.get(url, headers=headers).json()
        video_url = [f['link'] for f in res['videos'][0]['video_files'] if f['width'] >= 1080][0]
        with open(RAW_PATH, "wb") as f:
            f.write(requests.get(video_url, timeout=60).content)
        log("✅ HD Media secured in root.")
    except Exception as e:
        log(f"Media Failure: {e}. Loading redundancy asset.")
        # رابط احتياطي ثابت وعالي الجودة
        fallback = "https://cdn.pixabay.com/vimeo/239902912/forest-12157.mp4"
        with open(RAW_PATH, "wb") as f:
            f.write(requests.get(fallback).content)

def cinematic_render(text):
    """المعالجة السينمائية: دمج النص بأسلوب الشركات الكبرى لزيادة وقت المشاهدة"""
    log("🎨 Rendering cinematic layers...")
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawtext=text='{text}':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.6:boxborderw=50"
    )
    # استخدام x264 لضمان أعلى توافق مع فيسبوك
    subprocess.run(["ffmpeg", "-y", "-i", str(RAW_PATH), "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", str(FINAL_PATH)], check=True)

def publish_with_handshake(description):
    """السر النهائي: المصافحة الثنائية (Binary Handshake) لمنع خطأ 6000"""
    log("📡 Initiating Secure Binary Handshake with Meta...")
    endpoint = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    
    # الخطوة 1: حجز الجلسة
    init = requests.post(endpoint, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    video_id, upload_url = init.get("video_id"), init.get("upload_url")
    
    if not video_id:
        log(f"❌ Session Error: {init}")
        return

    # الخطوة 2: ضخ البيانات (السر: إرسال Raw Binary مع حجم الملف)
    file_size = FINAL_PATH.stat().st_size
    log(f"📦 Shipping {file_size} bytes directly to Meta root...")
    
    with open(FINAL_PATH, "rb") as video_file:
        upload_res = requests.post(
            upload_url, 
            data=video_file,
            headers={
                "Authorization": f"OAuth {FB_TOKEN}",
                "file_size": str(file_size),
                "offset": "0",
                "Content-Type": "application/octet-stream"
            }
        )
    log(f"📤 Handshake Status: {upload_res.status_code}")

    # الخطوة 3: التبريد (Cool-down) لضمان انتهاء الفحص الأمني في فيسبوك
    log("⏳ Meta processing (120s mandatory cooldown)...")
    time.sleep(120)

    # الخطوة 4: النشر الإجباري العلني (Force Public)
    final_res = requests.post(endpoint, data={
        "upload_phase": "finish",
        "video_id": video_id,
        "description": description,
        "video_state": "PUBLISHED",
        "access_token": FB_TOKEN
    }).json()
    
    if "success" in final_res or "id" in final_res:
        log("🎉 [MISSION ACCOMPLISHED] Reel is now LIVE on your page!")
    else:
        log(f"🚨 Final Warning from Meta: {final_res}")

def run_expert_system():
    try:
        self_healing_clean()
        quote, keyword, desc = gemini_content_engine()
        log(f"🚀 Gemini Strategy: Publishing on {keyword} topic.")
        download_and_verify(keyword)
        cinematic_render(quote)
        publish_with_handshake(desc)
    except Exception as e:
        log(f"🚨 Critical Failure: {e}")
    finally:
        self_healing_clean()
        log("🧹 Root sanitized for next cycle.")

if __name__ == "__main__":
    run_expert_system()
    
    video_check = requests.get(
        f"https://graph.facebook.com/v19.0/{video_id}?fields=permalink_url,status&access_token={FB_TOKEN}"
    ).json()
    log(f"🔗 Video Permanent Link: {video_check.get('permalink_url')}")
    log(f"📊 Video Status: {video_check.get('status')}")
