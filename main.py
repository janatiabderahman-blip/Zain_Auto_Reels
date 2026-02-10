import os
import requests
import random
from google import genai 

# الإعدادات
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"👑 [ELITE-SYSTEM] {msg}", flush=True)

def get_viral_content():
    try:
        # استخدام المكتبة الجديدة كلياً
        client = genai.Client(api_key=GEMINI_KEY)
        niches = ["Cinematic luxury life", "Mindset of champions", "Modern architecture 4k"]
        prompt = f"Topic: {random.choice(niches)}. Format: Quote | Keyword"
        
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        # التحقق من وجود النص والفاصل |
        if response.text and "|" in response.text:
            return [p.strip() for p in response.text.split("|")]
    except Exception as e:
        log(f"⚠️ Gemini API Error: {e}")
    return ["Discipline is the bridge between goals and accomplishment.", "motivation"]

def publish_empire_reel():
    try:
        content = get_viral_content()
        quote, keyword = content[0], content[1]
        log(f"🎯 Strategy Keyword: {keyword}")

        headers = {"Authorization": PEXELS_KEY}
        # جلب فيديوهات عالية الجودة حصراً
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=15&orientation=portrait&size=large"
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos'):
            # اختيار فيديو مدته كافية ليكون Reel حقيقي (أكثر من 12 ثانية)
            valid_videos = [v for v in res['videos'] if v['duration'] > 12]
            best_video = random.choice(valid_videos if valid_videos else res['videos'])
            
            # استخراج رابط الجودة العالية
            video_url = next((f['link'] for f in best_video['video_files'] if f['width'] >= 720), best_video['video_files'][0]['link'])
            
            # النشر المباشر
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {
                'file_url': video_url,
                'description': f"🔥 {quote}\n\n#Success #Motivation #Wealth",
                'access_token': FB_TOKEN
            }
            
            final_res = requests.post(fb_url, data=payload).json()
            if "id" in final_res:
                log(f"🎉 SUCCESS! Reel Published: {final_res['id']}")
            else:
                log(f"🚨 Meta Error: {final_res}")
        else:
            log("❌ No videos found on Pexels.")

    except Exception as e:
        log(f"🚨 System Error: {e}")

if __name__ == "__main__":
    publish_empire_reel()
