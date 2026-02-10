import os
import requests
import google.generativeai as genai
import random
import time

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"👑 [EMPIRE-LOGIC] {msg}", flush=True)

def get_viral_strategy():
    """هنا يكمن الفرق: صياغة محتوى يعتمد على سيكولوجية التوقف عن التمرير"""
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # استهداف نيشات "الأثرياء" لرفع الـ CPM
    viral_niches = [
        "Hidden psychology of billionaires",
        "Visuals that satisfy the brain 4K",
        "Dark truth about success",
        "Futuristic luxury aesthetics"
    ]
    
    prompt = f"""
    Target Niche: {random.choice(viral_niches)}
    Task: Create a viral Reel post.
    1. Hook: A shocking sentence that starts with 'Do you know why...' or 'Stop scrolling if...'.
    2. Content: 1 Deep success secret.
    3. Search Term: 1 Cinematic Pexels keyword.
    Format: Hook | Content | Keyword
    """
    try:
        res = model.generate_content(prompt).text.split("|")
        return [i.strip() for i in res]
    except:
        return ["Wait.. this is for you.", "The secret is consistency.", "luxury"]

def deploy_viral_empire():
    try:
        hook, content, keyword = get_viral_strategy()
        log(f"🎯 Strategy: {hook}")

        # صيد الفيديو: لن نأخذ أي فيديو، سنأخذ الأفضل فقط
        headers = {"Authorization": PEXELS_KEY}
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=40&orientation=portrait&size=large"
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos'):
            # فلترة ذكية: نختار الفيديوهات التي مدتها بين 10-25 ثانية (المثالية للريلز)
            premium_videos = [v for v in res['videos'] if 10 <= v['duration'] <= 25]
            target_video = random.choice(premium_videos if premium_videos else res['videos'])
            video_url = target_video['video_files'][0]['link']
            
            # بناء الوصف الفيروسي الاحترافي
            final_caption = (
                f"🚨 {hook.upper()}\n\n"
                f"{content}\n\n"
                f"Follow for the 1% mindset. 💎\n\n"
                f"#Mindset #Wealth #Success #ViralReels #Billionaire"
            )

            # النشر عبر سيرفرات Meta العملاقة
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {
                'file_url': video_url,
                'description': final_caption,
                'access_token': FB_TOKEN
            }
            
            fb_res = requests.post(fb_url, data=payload).json()
            if "id" in fb_res:
                log(f"🚀 BOOM! Viral Reel Live: {fb_res['id']}")
            else:
                log(f"🚨 Meta Blocked: {fb_res}")

    except Exception as e:
        log(f"🚨 Error: {e}")

if __name__ == "__main__":
    deploy_viral_empire()
