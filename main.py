import os
import requests
import random
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from datetime import datetime

# --- الإعدادات السيادية ---
FB_TOKEN   = os.getenv("FB_TOKEN")
PAGE_ID    = os.getenv("PAGE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

def log(msg): print(f"🛡️ [ZAIN-CORE] {msg}", flush=True)

def get_unique_content():
    """توليد محتوى غير مكرر باستخدام بصمة زمنية"""
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # دمج الثواني في الطلب لضمان اختلاف النتائج في كل تشغيل
        timestamp = datetime.now().strftime("%S")
        prompt = f"TimeRef:{timestamp}. Write 1 powerful success quote (Arabic & English) and 1 specific keyword for a 4K luxury video. Format: Arabic | English | Keyword"
        
        response = model.generate_content(prompt)
        if "|" in response.text:
            return [p.strip() for p in response.text.split("|")]
    except Exception as e:
        log(f"⚠️ Gemini Logic Error: {e}")
    return ["التميز هو لغتنا.", "Excellence is our language.", "luxury"]

def apply_watermark(video_url):
    """تحميل الفيديو وإضافة شعار 'عالم الزين' برمجياً"""
    try:
        video_path = "raw_video.mp4"
        output_path = "zain_final.mp4"
        
        # تحميل الفيديو من Pexels
        r = requests.get(video_url, stream=True)
        with open(video_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk: f.write(chunk)
        
        log("🎨 Applying Watermark: عالم الزين")
        clip = VideoFileClip(video_path)
        
        # إنشاء نص اللوجو (شفافية 60%)
        txt_clip = TextClip("عالم الزين", fontsize=50, color='white', font='Arial-Bold')
        txt_clip = txt_clip.set_pos(('right', 'top')).set_duration(clip.duration).set_opacity(0.6)
        
        # دمج الفيديو مع النص وحفظه
        final = CompositeVideoClip([clip, txt_clip])
        final.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
        
        return output_path
    except Exception as e:
        log(f"🚨 Watermark Failed: {e}")
        return None

def publish_unique_empire():
    try:
        arabic, english, keyword = get_unique_content()
        log(f"🔍 Searching deep for: {keyword}")

        headers = {"Authorization": PEXELS_KEY}
        # الحل النهائي للتكرار: القفز لصفحة عشوائية بين 1 و 100
        random_page = random.randint(1, 100)
        px_url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=15&page={random_page}&orientation=portrait"
        
        res = requests.get(px_url, headers=headers).json()
        
        if res.get('videos') and len(res['videos']) > 0:
            # اختيار فيديو عشوائي من نتائج الصفحة العشوائية
            selected_video = random.choice(res['videos'])
            video_url = selected_video['video_files'][0]['link']
            
            log("🚀 Deploying Video with Meta API...")
            
            # الوصف الفيروسي
            final_caption = f"✨ {arabic}\n💫 {english}\n\n#عالم_الزين #Success #Viral"
            
            # ملاحظة: سنستخدم الـ file_url حالياً لضمان استقرار السيرفر 
            # وإذا أردت تفعيل اللوجو (الذي يتطلب قوة معالجة كبيرة) سنقوم برفع الملف المدمج.
            fb_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
            payload = {
                'file_url': video_url,
                'description': final_caption,
                'access_token': FB_TOKEN
            }
            
            fb_res = requests.post(fb_url, data=payload).json()
            if "id" in fb_res:
                log(f"✅ EXCELLENT! Unique Reel Published: {fb_res['id']}")
            else:
                log(f"🚨 Meta Refused: {fb_res}")
        else:
            log("❌ No videos found in this search cluster, retrying next time.")

    except Exception as e:
        log(f"🚨 Critical System Failure: {e}")

if __name__ == "__main__":
    publish_unique_empire()
