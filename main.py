import os
import requests
import google.generativeai as genai
import time
from datetime import datetime

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🛡️ [GLOBAL-EXPERT-SYSTEM] {msg}", flush=True)

def get_ai_creative_content(mode="reel"):
    """توليد محتوى احترافي (حقائق أو ريلز) بلغتين"""
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if mode == "post":
        prompt = "أعطني حقيقة مذهلة أو قصة قصيرة جداً ملهمة باللغة العربية مع ترجمتها الإنجليزية. التنسيق: النص العربي | النص الإنجليزي"
    else:
        prompt = "Give me 1 viral high-hook success quote and 1 search keyword for a luxury/business video. Format: Quote | Keyword"
    
    try:
        response = model.generate_content(prompt)
        return [p.strip() for p in response.text.split("|")]
    except:
        return ["النجاح يتطلب الصبر | Success requires patience", "Success"] if mode == "post" else ["Dream Big.", "luxury"]

def post_text_story():
    """نشر منشورات نصية (قصص وحقائق) كل 30 دقيقة"""
    log("📝 Generating Fact/Story Post...")
    content = get_ai_creative_content(mode="post")
    arabic_text, english_text = content[0], content[1]
    
    full_post = f"🌟 {arabic_text}\n\n✨ {english_text}\n\n#Facts #Stories #Wisdom #حقائق"
    
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    payload = {'message': full_post, 'access_token': FB_TOKEN}
    res = requests.post(url, data=payload).json()
    if "id" in res: log(f"✅ Text Post Published: {res['id']}")

def publish_viral_reel():
    """نشر ريلزات جذابة (High-Quality Reels) كل ساعة"""
    log("🎬 Preparing Viral Reel...")
    quote, keyword = get_content_final_upgraded() # دالة البحث المحدثة
    
    headers = {"Authorization": PEXELS_KEY}
    # كلمات بحث تجذب المشاهدات (Luxury, Success, Nature)
    search_keywords = [keyword, "luxury lifestyle", "satisfying", "urban life"]
    
    video_url = None
    for kw in search_keywords:
        px_url = f"https://api.pexels.com/videos/search?query={kw}&per_page=1&orientation=portrait"
        res = requests.get(px_url, headers=headers).json()
        if res.get('videos'):
            video_url = res['videos'][0]['video_files'][0]['link']
            break
            
    if video_url:
        fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
        payload = {
            'file_url': video_url,
            'description': f"{quote}\n\n#Reels #Motivation #Success #Trending",
            'access_token': FB_TOKEN
        }
        res = requests.post(fb_url, data=payload).json()
        if "id" in res: log(f"🎉 Viral Reel Published: {res['id']}")

def get_content_final_upgraded():
    # نفس دالتك الناجحة مع تحسين جودة الكلمات
    content = get_ai_creative_content(mode="reel")
    return content[0], content[1]

if __name__ == "__main__":
    # هذا السكريبت مصمم ليتم تشغيله بواسطة GitHub Actions
    # سيتم التحكم في التوقيت عبر ملف YAML (نص ساعة للمنشورات، ساعة للريلز)
    # سنقوم بتقسيم التشغيل بناءً على وقت الساعة
    current_minute = datetime.now().minute
    current_hour = datetime.now().hour

    # منطق التشغيل الذكي:
    post_text_story() # يتم نشره في كل تشغيل (كل 30 دقيقة)
    
    if current_minute < 30: # يتم نشر الريلز مرة واحدة كل ساعة (في بداية الساعة)
        publish_viral_reel()
