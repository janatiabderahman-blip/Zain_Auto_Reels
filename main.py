import os
import requests
import random
import google.generativeai as genai # العودة للمكتبة المستقرة
from datetime import datetime

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🚀 [FINAL-CHECK] {msg}", flush=True)

def get_viral_logic():
    """استخدام المسار المضمون لتجنب خطأ 404"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        # نستخدم 1.5-flash لأنه الأسرع والأكثر استقراراً حالياً
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # كلمات مفتاحية تضمن حركة بصرية قوية
        seed_topics = ["Cinematic speed", "Ocean waves 4k", "Luxury interior motion", "Cyberpunk city traffic"]
        topic = random.choice(seed_topics)
        
        prompt = f"Topic: {topic}. Give me 1 short viral quote and 1 specific Pexels keyword. Format: Quote | Keyword"
        response = model.generate_content(prompt)
        
        if "|" in response.text:
            return [p.strip() for p in response.text.split("|")]
    except Exception as e:
        log(f"⚠️ Gemini Fallback: {e}")
    return ["Your only limit is you.", "luxury"]

def publish_dominator():
    try:
        quote, keyword = get_viral_logic()
        log(f"🎯 Target Keyword: {keyword}")

        headers = {"Authorization": PEXELS_KEY}
        # استراتيجية البحث العشوائي لقتل التكرار
        rand_pg = random.randint(1, 15)
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=10&page={rand_pg}&orientation=portrait"
        
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos') and len(res['videos']) > 0:
            # التعديل الذهبي: نختار فيديو طويل (أكثر من 15 ثانية) لضمان الحركة وعدم كونه GIF
            selected_video = None
            for v in res['videos']:
                if v['duration'] >= 15: # نضمن أنه فيديو حقيقي
                    selected_video = v
                    break
            
            if not selected_video: selected_video = res['videos'][0]
            
            # سحب رابط الجودة العالية HD
            video_url = selected_video['video_files'][0]['link']
            
            # النشر الفيروسي لـ Meta
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {
                'file_url': video_url,
                'description': f"🔥 {quote}\n\n#Success #Motivation #Viral #Reels",
                'access_token': FB_TOKEN
            }
            
            final_res = requests.post(fb_url, data=payload).json()
            if "id" in final_res:
                log(f"✅ BOOM! Published Successfully: {final_res['id']}")
            else:
                log(f"🚨 Meta Error: {final_res}")
        else:
            log("❌ No HD Videos Found.")

    except Exception as e:
        log(f"🚨 System Error: {e}")

if __name__ == "__main__":
    publish_dominator()
