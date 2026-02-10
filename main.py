import os
import requests
import random
import google.generativeai as genai
from datetime import datetime

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🚀 [ELITE-FIX] {msg}", flush=True)

def get_viral_logic():
    try:
        genai.configure(api_key=GEMINI_KEY)
        # الإصلاح: استخدام الاسم المباشر للموديل لتجنب خطأ 404
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = "Give me 1 viral success quote and 1 Pexels keyword. Format: Quote | Keyword"
        response = model.generate_content(prompt)
        
        if "|" in response.text:
            return [p.strip() for p in response.text.split("|")]
    except Exception as e:
        log(f"⚠️ Gemini Error: {e}")
    return ["Success is a decision.", "luxury"]

def publish_dominator():
    try:
        quote, keyword = get_viral_logic()
        log(f"🎯 Target: {keyword}")

        headers = {"Authorization": PEXELS_KEY}
        # استراتيجية البحث الموسع لضمان إيجاد فيديو
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=15&orientation=portrait"
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos') and len(res['videos']) > 0:
            # نختار أفضل فيديو من النتائج (نفضل الطويل ولكن نقبل المتاح)
            videos_list = res['videos']
            # محاولة البحث عن فيديو بجودة عالية أولاً
            selected_video = next((v for v in videos_list if v['duration'] > 10), videos_list[0])
            
            # سحب أول رابط ملف فيديو متاح (لضمان عدم الفشل)
            video_url = selected_video['video_files'][0]['link']
            
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {
                'file_url': video_url,
                'description': f"🔥 {quote}\n\n#Success #Motivation #Viral",
                'access_token': FB_TOKEN
            }
            
            final_res = requests.post(fb_url, data=payload).json()
            if "id" in final_res:
                log(f"✅ SUCCESS: {final_res['id']}")
            else:
                log(f"🚨 Meta Error: {final_res}")
        else:
            log("❌ Pexels Search Empty")

    except Exception as e:
        log(f"🚨 Critical Failure: {e}")

if __name__ == "__main__":
    publish_dominator()
