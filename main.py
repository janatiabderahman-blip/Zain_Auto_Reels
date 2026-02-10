import os
import requests
import google.generativeai as genai
import random
from datetime import datetime

# --- الإعدادات (نفس القديم تماماً) ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🛡️ [AI-SURGEON] {msg}", flush=True)

def get_content_final():
    """نفس الدالة التي نجحت معك مع تأمين التقسيم"""
    genai.configure(api_key=GEMINI_KEY)
    # جلب الوقت الحالي لإضافته للطلب لضمان عدم التكرار
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    for model_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            log(f"🧬 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            # طلب بسيط وواضح لضمان استلام التنسيق الصحيح
            prompt = f"Time {timestamp}: Give me 1 success quote and 1 keyword for video search. Format: Quote | Keyword"
            response = model.generate_content(prompt)
            
            if response and response.text:
                if "|" in response.text:
                    parts = [p.strip() for p in response.text.split("|")]
                    if len(parts) >= 2: return parts
        except Exception as e:
            log(f"⚠️ {model_name} failed: {str(e)[:30]}")
    
    return ["Success is a journey, not a destination.", "motivation"]

def publish_v2_strategy():
    """هذه هي الاستراتيجية التي نجحت (file_url) مع إضافة عشوائية بسيطة"""
    try:
        # 1. جلب المحتوى
        content = get_content_final()
        quote, keyword = content[0], content[1]
        log(f"💡 AI Content: {keyword}")
        
        # 2. البحث عن الفيديو (نفس المنطق القديم مع إضافة عشوائية الصفحات)
        headers = {"Authorization": PEXELS_KEY}
        # كلمات احتياطية لضمان عدم حدوث خطأ 'videos'
        search_keywords = [keyword, "luxury", "success", "motivation", "nature"]
        
        video_direct_url = None
        for kw in search_keywords:
            log(f"🔍 Searching Pexels for: {kw}")
            # التغيير الوحيد: صفحة عشوائية لضمان عدم تكرار الفيديو
            random_page = random.randint(1, 15)
            px_url = f"https://api.pexels.com/videos/search?query={kw}&per_page=5&page={random_page}&orientation=portrait"
            res = requests.get(px_url, headers=headers).json()
            
            if res.get('videos') and len(res['videos']) > 0:
                # اختيار فيديو عشوائي من النتائج الـ 5
                video_direct_url = random.choice(res['videos'])['video_files'][0]['link']
                log(f"✅ Video Found: {kw}")
                break
        
        if not video_direct_url:
            raise ValueError("No videos found.")

        # 3. أمر النشر المباشر (نفس الكود الذي اشتغل معك 100%)
        log("🚀 Sending Direct Import command to Meta...")
        fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
        
        # صياغة الوصف ليكون فيروسياً (عربي وإنجليزي) كما طلبت
        description = f"🔥 {quote}\n\n#success #motivation #growth #viral"
        
        payload = {
            'file_url': video_direct_url,
            'description': description,
            'access_token': FB_TOKEN
        }
        
        final_res = requests.post(fb_url, data=payload).json()
        
        if "id" in final_res:
            log(f"🎉 SUCCESS! ID: {final_res['id']}")
        else:
            log(f"🚨 Meta Error: {final_res}")

    except Exception as e:
        log(f"🚨 Critical Failure: {str(e)}")

if __name__ == "__main__":
    publish_v2_strategy()
