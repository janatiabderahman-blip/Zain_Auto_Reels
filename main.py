import os
import requests
import google.generativeai as genai
import random
from datetime import datetime

FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🚀 [ELITE-EXPERT] {msg}", flush=True)

def get_content_final():
    genai.configure(api_key=GEMINI_KEY)
    # استخدام المسار الصحيح للموديل لتجنب الـ 404
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    try:
        # طلب نيشات فخمة لضمان فيديوهات قوية
        niches = ["Luxury car cinematic", "Dubai skyline night", "Modern architecture drone", "Successful businessman lifestyle"]
        selected_niche = random.choice(niches)
        prompt = f"Give me 1 powerful success quote and 1 specific keyword for {selected_niche}. Format: Quote | Keyword"
        response = model.generate_content(prompt)
        if response and "|" in response.text:
            return [p.strip() for p in response.text.split("|")]
    except:
        return ["Your ambition is your only limit.", "luxury lifestyle"]
    return ["Dream big.", "success"]

def publish_v2_strategy():
    try:
        quote, keyword = get_content_final()
        log(f"🎯 Target: {keyword}")
        
        headers = {"Authorization": PEXELS_KEY}
        # فلترة البحث لجلب فيديوهات طولية (Portrait) وعالية الجودة فقط
        random_pg = random.randint(1, 10)
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=10&page={random_pg}&orientation=portrait&size=large"
        
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos'):
            # التعديل الجوهري: اختيار أعلى جودة متاحة للفيديو (HD/4K)
            best_video = random.choice(res['videos'])
            # فلترة الملفات لاختيار ملف بجودة عالية وليس "SD" أو "GIF"
            video_files = [f for f in best_video['video_files'] if f['width'] >= 720]
            video_url = video_files[0]['link'] if video_files else best_video['video_files'][0]['link']
            
            log(f"✅ High-Quality Video Secured: {keyword}")
            
            # النشر مع وصف "فيروسي"
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {
                'file_url': video_url,
                'description': f"💎 {quote}\n\n#Success #Luxury #Viral #Motivation",
                'access_token': FB_TOKEN
            }
            
            final_res = requests.post(fb_url, data=payload).json()
            if "id" in final_res:
                log(f"🎉 EXCELLENT! Viral Reel ID: {final_res['id']}")
            else:
                log(f"🚨 Meta Error: {final_res}")
        else:
            log("❌ No HD Videos Found.")

    except Exception as e:
        log(f"🚨 System Failure: {str(e)}")

if __name__ == "__main__":
    publish_v2_strategy()
