import os
import requests
import google.generativeai as genai
import random
from datetime import datetime

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🛡️ [AI-SURGEON] {msg}", flush=True)

def get_content_final():
    genai.configure(api_key=GEMINI_KEY)
    # التصحيح: إضافة بادئة models/ لحل خطأ 404 الظاهر في صورتك
    for model_name in ['models/gemini-1.5-flash', 'models/gemini-pro']:
        try:
            log(f"🧬 Trying: {model_name}")
            model = genai.GenerativeModel(model_name)
            # طلب محتوى فيروسي باختصار شديد لضمان الاستجابة
            prompt = "Viral Success Quote | Short Keyword. Format: Quote | Keyword"
            response = model.generate_content(prompt)
            if response and response.text and "|" in response.text:
                return [p.strip() for p in response.text.split("|")]
        except Exception as e:
            log(f"⚠️ {model_name} failed: {str(e)[:40]}")
    
    return ["Your only limit is your mind.", "luxury"]

def publish_v2_strategy():
    try:
        # 1. جلب المحتوى
        quote, keyword = get_content_final()
        log(f"💡 AI Content: {keyword}")
        
        # 2. البحث عن الفيديو - نظام "الصيد المضمون"
        headers = {"Authorization": PEXELS_KEY}
        # كلمات بحث "فيروسية" نلجأ لها إذا فشلت الكلمات الأصلية
        search_keywords = [keyword, "luxury lifestyle", "meditation", "city night", "ocean"]
        
        video_url = None
        for kw in search_keywords:
            log(f"🔍 Searching: {kw}")
            # تقليل per_page لسرعة الاستجابة وزيادة العشوائية في الصفحات
            rand_pg = random.randint(1, 20)
            px_url = f"https://api.pexels.com/videos/search?query={kw}&per_page=15&page={rand_pg}"
            res = requests.get(px_url, headers=headers).json()
            
            if res.get('videos') and len(res['videos']) > 0:
                # اختيار فيديو عشوائي من النتائج لضمان عدم التكرار
                video_url = random.choice(res['videos'])['video_files'][0]['link']
                log(f"✅ Video Found: {kw}")
                break
        
        if not video_url: raise ValueError("Pexels Empty Response")

        # 3. النشر المباشر (الخطة الفيروسية)
        log("🚀 Deploying Viral Post...")
        fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
        
        # وصف احترافي لجذب الخوارزميات
        viral_desc = f"🔥 {quote}\n\n#success #motivation #growth #viral #reels"
        
        payload = {
            'file_url': video_url,
            'description': viral_desc,
            'access_token': FB_TOKEN
        }
        
        final_res = requests.post(fb_url, data=payload).json()
        
        if "id" in final_res:
            log(f"🎉 SUCCESS! Video ID: {final_res['id']}")
        else:
            log(f"🚨 Meta Refused: {final_res}")

    except Exception as e:
        log(f"🚨 Critical Failure: {str(e)}")

if __name__ == "__main__":
    publish_v2_strategy()
