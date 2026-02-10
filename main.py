import os
import requests
import random
import time
# الانتقال للمكتبة الجديدة بناءً على تحذير الصورة الثالثة
from google import genai 
from datetime import datetime

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"👑 [ELITE-SYSTEM] {msg}", flush=True)

def get_viral_content():
    """استخدام المكتبة الجديدة لضمان عدم حدوث 404"""
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        # نيشات تضمن حركة بصرية قوية (Drone, Cinematic, Motion)
        niches = ["Cinematic drone shot of luxury city", "High speed sport car motion", "Abstract liquid motion 4k"]
        prompt = f"Create a viral hook and a search keyword for: {random.choice(niches)}. Format: Hook | Keyword"
        
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        if "|" in response.text:
            return [p.strip() for p in response.text.split("|")]
    except Exception as e:
        log(f"⚠️ Gemini Error: {e}")
    return ["Unstoppable Mindset.", "luxury motion"]

def publish_empire_reel():
    try:
        hook, keyword = get_viral_content()
        log(f"🎯 Target: {keyword}")

        headers = {"Authorization": PEXELS_KEY}
        # جلب فيديوهات أكثر لضمان جودة الاختيار
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=15&orientation=portrait"
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos'):
            # فلترة: استبعاد الفيديوهات القصيرة جداً التي تبدو كـ GIF
            valid_videos = [v for v in res['videos'] if v['duration'] > 12]
            best_video = random.choice(valid_videos if valid_videos else res['videos'])
            
            # اختيار ملف الجودة العالية (HD) حصراً
            video_url = next((f['link'] for f in best_video['video_files'] if f['width'] >= 720), best_video['video_files'][0]['link'])
            
            # الوصف الفيروسي
            description = f"🔥 {hook}\n\n#Success #Motivation #Wealth #Reels"
            
            # الرفع لفيسبوك
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {'file_url': video_url, 'description': description, 'access_token': FB_TOKEN}
            
            final_res = requests.post(fb_url, data=payload).json()
            if "id" in final_res:
                log(f"🎉 DEPLOYED SUCCESSFULLY: {final_res['id']}")
            else:
                log(f"🚨 Meta Error: {final_res}")
        else:
            log("❌ Pexels Search Empty")

    except Exception as e:
        log(f"🚨 System Error: {e}")

if __name__ == "__main__":
    publish_empire_reel()
