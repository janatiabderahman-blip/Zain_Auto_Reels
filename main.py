import os
import requests
import random
# التصحيح النهائي لطريقة الاستدعاء
from google.genai import Client 
from datetime import datetime

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"👑 [EMPIRE-SYSTEM] {msg}", flush=True)

def get_viral_content():
    try:
        # الربط بالمكتبة الجديدة
        client = Client(api_key=GEMINI_KEY)
        # نيشات تضمن حركة بصرية مبهرة (تجنب الـ GIF)
        niches = [
            "Hyper-realistic cinematic nature 4k",
            "Luxury lifestyle city motion",
            "Abstract gold and black liquid 4k"
        ]
        prompt = f"Topic: {random.choice(niches)}. Write 1 viral success quote and 1 Pexels search keyword. Format: Quote | Keyword"
        
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        
        if response.text and "|" in response.text:
            return [p.strip() for p in response.text.split("|")]
    except Exception as e:
        log(f"⚠️ Gemini Error: {e}")
    return ["Success is hidden in your daily routine.", "modern luxury"]

def publish_empire_reel():
    try:
        quote, keyword = get_viral_content()
        log(f"🎯 Target Keyword: {keyword}")

        headers = {"Authorization": PEXELS_KEY}
        # زيادة عدد النتائج لضمان وجود فيديوهات HD
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=20&orientation=portrait"
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos'):
            # فلترة: نختار فيديو مدته كافية ليكون Reel (15-30 ثانية) وبجودة عالية
            valid_videos = [v for v in res['videos'] if 12 <= v['duration'] <= 35]
            target_video = random.choice(valid_videos if valid_videos else res['videos'])
            
            # استخراج رابط الجودة العالية (HD) حصراً
            video_url = next((f['link'] for f in target_video['video_files'] if f['width'] >= 720), target_video['video_files'][0]['link'])
            
            # النشر المباشر عبر Meta
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {
                'file_url': video_url,
                'description': f"🔥 {quote}\n\n#Success #Motivation #Wealth #Viral",
                'access_token': FB_TOKEN
            }
            
            fb_res = requests.post(fb_url, data=payload).json()
            if "id" in fb_res:
                log(f"🚀 BOOM! Viral Reel Live: {fb_res['id']}")
            else:
                log(f"🚨 Meta Error: {fb_res}")
        else:
            log("❌ No videos found on Pexels.")

    except Exception as e:
        log(f"🚨 System Failure: {e}")

if __name__ == "__main__":
    publish_empire_reel()
