import os
import requests
import google.generativeai as genai
from pathlib import Path

# --- الإعدادات (تأكد من وجودها في Secrets) ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🤖 [SYSTEM-ROOT] {msg}", flush=True)

def get_content_safe():
    """حل مشكلة 404 عبر تجربة الموديلات المتاحة تلقائياً"""
    genai.configure(api_key=GEMINI_KEY)
    # نجرب flash أولاً، وإذا فشل ننتقل لـ pro تلقائياً
    for model_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            log(f"Attempting to wake up: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Viral Quote | One Keyword | Short Description")
            parts = [p.strip() for p in response.text.split("|")]
            if len(parts) >= 2: return parts
        except Exception as e:
            log(f"Model {model_name} busy or not found. Switching...")
    return ["Success is a journey.", "growth", "Keep moving forward! #success"]

def publish_url_strategy():
    """الطريق الجديد: الرفع عبر الرابط المباشر (تجاوز خطأ 6000 نهائياً)"""
    try:
        # 1. جلب البيانات
        quote, keyword, desc = get_content_safe()
        
        # 2. الحصول على رابط فيديو مباشر من Pexels
        log(f"Searching for video: {keyword}")
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait"
        headers = {"Authorization": PEXELS_KEY}
        res = requests.get(px_url, headers=headers).json()
        video_direct_url = res['videos'][0]['video_files'][0]['link']
        
        # 3. أمر النشر المباشر (فيسبوك يحمل الفيديو من الرابط مباشرة)
        # هذا لا يحتاج لرفع ملف من GitHub، لذا لن يظهر خطأ 'Video Missing'
        log("Sending direct import command to Meta...")
        fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
        payload = {
            'file_url': video_direct_url,
            'description': f"{quote}\n\n{desc}",
            'access_token': FB_TOKEN
        }
        
        final_res = requests.post(fb_url, data=payload).json()
        
        if "id" in final_res:
            log(f"🎉 SUCCESS! Meta is importing your Reel. ID: {final_res['id']}")
        else:
            log(f"🚨 Meta rejected the command: {final_res}")

    except Exception as e:
        log(f"🚨 Critical Failure: {str(e)}")

if __name__ == "__main__":
    publish_url_strategy()
