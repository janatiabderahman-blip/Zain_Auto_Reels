import os
import requests
import google.generativeai as genai
import random
from datetime import datetime

# الإعدادات السيادية
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🔥 [VIRAL-EXPERT-ROOT] {msg}", flush=True)

def get_viral_logic():
    """توليد محتوى يعتمد على سيكولوجية الانتشار"""
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # استراتيجية النيشات الأكثر ربحية وانتشاراً (High CPM)
    viral_niches = [
        "Luxury Lifestyle and Success",
        "Deep Psychological Facts about Humans",
        "Wealth Mindset and Money Secrets",
        "Mind-blowing Facts about the Universe",
        "Unbelievable Ancient History Secrets"
    ]
    selected = random.choice(viral_niches)
    
    prompt = f"""
    Create a VIRAL post for Facebook. Target niche: {selected}.
    1. A 'Hook' line in Arabic and English that makes people stop scrolling.
    2. A 'Story/Fact' that is shocking or highly motivating.
    3. 1 Precise English keyword for a high-quality 4K video search.
    Format: Hook | Story | Keyword
    """
    
    try:
        res = model.generate_content(prompt).text.split("|")
        return [i.strip() for i in res]
    except:
        return ["Wait until the end.. | انتظر للنهاية", "Focus on your goals. | ركز على أهدافك", "Success"]

def publish_dominator():
    """نظام النشر الإمبراطوري - اختيار فيديوهات تخطف الأنفاس"""
    try:
        hook, story, keyword = get_viral_logic()
        log(f"🎯 Target Niche Keyword: {keyword}")

        # البحث عن فيديو 4K بجودة سينمائية
        headers = {"Authorization": PEXELS_KEY}
        # اختيار عشوائي لصفحة النتائج لضمان عدم التكرار نهائياً
        random_pg = random.randint(1, 20)
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=10&page={random_pg}&orientation=portrait"
        
        v_data = requests.get(px_url, headers=headers).json()
        if not v_data.get('videos'):
             # fallback إذا فشل البحث
             v_data = requests.get(f"https://api.pexels.com/videos/search?query=luxury&per_page=1", headers=headers).json()

        # اختيار فيديو عشوائي من النتائج لزيادة التنوع
        video_url = random.choice(v_data['videos'])['video_files'][0]['link']
        
        # صياغة المنشور الفيروسي
        viral_desc = f"🚀 {hook}\n\n{story}\n\n.\n.\n#Viral #Trending #Success #Mindset #Exploration #Reels #Motivation"
        
        # إرسال الأمر لفيسبوك
        fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
        payload = {
            'file_url': video_url,
            'description': viral_desc,
            'access_token': FB_TOKEN
        }
        
        response = requests.post(fb_url, data=payload).json()
        if "id" in response:
            log(f"✅ VIRAL REEL DEPLOYED! ID: {response['id']}")
        else:
            log(f"❌ Deploy Failed: {response}")

    except Exception as e:
        log(f"🚨 System Error: {e}")

if __name__ == "__main__":
    # تشغيل نظام الاكتساح
    publish_dominator()
