import os
import requests
import google.generativeai as genai
from pathlib import Path

# --- الإعدادات (تأكد من وجودها في Secrets) ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🛡️ [AI-SURGEON] {msg}", flush=True)

def get_content_final():
    """محاولة استدعاء الموديلات المتاحة مع نصوص بديلة جاهزة"""
    genai.configure(api_key=GEMINI_KEY)
    # تجربة الموديلات المتاحة حالياً في API v1beta
    for model_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            log(f"🧬 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Give me 1 success quote and 1 keyword like 'motivation'. Format: Quote | Keyword")
            if response and response.text:
                parts = [p.strip() for p in response.text.split("|")]
                if len(parts) >= 2: return parts
        except Exception as e:
            log(f"⚠️ {model_name} failed: {str(e)[:50]}")
    
    # نص احتياطي في حال فشل كل الموديلات لضمان استمرار السيرفر
    return ["Success is not final, failure is not fatal.", "motivation"]

def publish_v2_strategy():
    """استراتيجية الرفع المباشر مع فحص الأخطاء (حل مشكلة 'videos')"""
    try:
        # 1. جلب المحتوى
        quote, keyword = get_content_final()
        log(f"💡 AI Content: {keyword}")
        
        # 2. البحث عن الفيديو مع نظام "الكلمة البديلة"
        headers = {"Authorization": PEXELS_KEY}
        search_keywords = [keyword, "nature", "business", "abstract"] # كلمات احتياطية
        
        video_direct_url = None
        for kw in search_keywords:
            log(f"🔍 Searching Pexels for: {kw}")
            px_url = f"https://api.pexels.com/videos/search?query={kw}&per_page=1&orientation=portrait"
            res = requests.get(px_url, headers=headers).json()
            
            # التحقق من وجود مفتاح 'videos' ومن أنه ليس فارغاً
            if res.get('videos') and len(res['videos']) > 0:
                video_direct_url = res['videos'][0]['video_files'][0]['link']
                log(f"✅ Video Found for: {kw}")
                break
        
        if not video_direct_url:
            raise ValueError("No videos found for any keywords.")

        # 3. أمر النشر المباشر (تجاوز خطأ 6000)
        log("🚀 Sending Direct Import command to Meta...")
        fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
        payload = {
            'file_url': video_direct_url,
            'description': f"{quote}\n\n#success #motivation #growth",
            'access_token': FB_TOKEN
        }
        
        final_res = requests.post(fb_url, data=payload).json()
        
        if "id" in final_res:
            log(f"🎉 SUCCESS! Reel Import Started. ID: {final_res['id']}")
        else:
            log(f"🚨 Meta Error: {final_res}")

    except Exception as e:
        log(f"🚨 Critical Failure: {str(e)}")

if __name__ == "__main__":
    publish_v2_strategy()
