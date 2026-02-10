import os
import time
import requests
import subprocess
import google.generativeai as genai
from pathlib import Path

# إعدادات الخادم الذكي
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
FINAL_FILE = Path("final_reel.mp4")

def ai_log(msg): print(f"🤖 [GEMINI-SERVER] {msg}", flush=True)

def initialize_ai():
    """تنشيط خادم Gemini في الجذر لضمان استمرارية المحتوى"""
    genai.configure(api_key=GEMINI_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')

def get_smart_content(model):
    """توليد محتوى تفاعلي للهروب من حظر المحتوى المكرر"""
    prompt = "Viral Reel Logic: Quote | Keyword | Pro Description #viral"
    res = model.generate_content(prompt).text
    return [i.strip() for i in res.split("|")]

def smart_publish(description):
    """نظام النشر الذكي المعتمد لحل خطأ 6000 نهائياً"""
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    
    # 1. بدء الجلسة
    init = requests.post(url, data={"upload_phase": "start", "access_token": FB_TOKEN}).json()
    video_id, upload_url = init["video_id"], init["upload_url"]
    
    # 2. الضخ الثنائي الخام (السر لحل مشكلة Video Missing)
    file_size = FINAL_FILE.stat().st_size
    with open(FINAL_FILE, "rb") as f:
        requests.post(upload_url, data=f, headers={
            "Authorization": f"OAuth {FB_TOKEN}",
            "file_size": str(file_size),
            "offset": "0",
            "Content-Type": "application/octet-stream"
        })
    
    # 3. المراقبة الذكية (تحديث مستمر حتى قبول الفيديو)
    ai_log("⏳ Monitoring Meta processing status...")
    for attempt in range(10): # محاولة الفحص لمدة 5 دقائق
        time.sleep(30)
        check = requests.get(f"https://graph.facebook.com/v19.0/{video_id}?fields=status&access_token={FB_TOKEN}").json()
        status = check.get("status", {}).get("video_status", "")
        ai_log(f"Attempt {attempt+1}: Status is {status}")
        
        if status == "ready":
            # 4. النشر النهائي الإجباري
            finish = requests.post(url, data={
                "upload_phase": "finish", "video_id": video_id,
                "description": description, "video_state": "PUBLISHED",
                "access_token": FB_TOKEN
            }).json()
            ai_log(f"✅ Published Successfully: {finish}")
            return True
    return False

# تشغيل الخادم
if __name__ == "__main__":
    model = initialize_ai()
    content = get_smart_content(model)
    # (هنا تضاف خطوات التحميل والمعالجة بـ FFmpeg كما في النسخ السابقة)
    # ثم استدعاء النشر الذكي
    # smart_publish(content[2])
