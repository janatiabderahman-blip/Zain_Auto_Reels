import os
import requests
import random
import time
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings

# --- إصلاح ثغرة نظام Linux في GitHub ---
# هذا السطر يخبر البرنامج بمكان محرك النصوص لتجنب خطأ ImageMagick Binary
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# --- الإعدادات الأمنية ---
CONFIG = {
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "PEXELS_KEY": os.getenv("PEXELS_API_KEY"),
    "FB_ID": os.getenv("FB_PAGE_ID"),
    "FB_TOKEN": os.getenv("FB_PAGE_TOKEN")
}

genai.configure(api_key=CONFIG["GEMINI_KEY"])

def get_empire_content():
    """توليد محتوى ذكي وفريد لتجاوز خوارزميات كشف التكرار"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = (
            "Act as a professional content creator. Write 5 mind-blowing facts about 'Deep Ocean' or 'Space'. "
            "Format: Fact1 | Fact2 | Fact3 | Fact4 | Fact5. "
            "Keep each fact under 15 words. Avoid any special characters."
        )
        response = model.generate_content(prompt)
        facts = response.text.split('|')
        # تنظيف النصوص من أي فراغات زائدة
        return [f.strip() for f in facts if len(f) > 5]
    except Exception as e:
        print(f"Gemini Error: {e}")
        return ["Nature is full of mysteries.", "Space is expanding every second.", "The ocean is 95% unexplored.", "Stars are light-years away.", "AI is changing the world."]

def download_video():
    """جلب فيديو عالي الجودة متوافق مع شروط فيسبوك"""
    headers = {"Authorization": CONFIG["PEXELS_KEY"]}
    topics = ['nebula', 'ocean', 'galaxy', 'forest']
    url = f"https://api.pexels.com/videos/search?query={random.choice(topics)}&per_page=10&orientation=portrait"
    
    res = requests.get(url, headers=headers).json()
    video_url = random.choice(res['videos'])['video_files'][0]['link']
    
    with open("raw_bg.mp4", 'wb') as f:
        f.write(requests.get(video_url).content)
    return "raw_bg.mp4"

def build_video():
    """بناء الفيديو النهائي - هندسة إمبراطورية"""
    facts = get_empire_content()
    raw_video = download_video()
    
    # تحميل الفيديو مع تحديد الدقة لتوفير موارد السيرفر
    clip = VideoFileClip(raw_video).resize(width=720) 
    
    # ضمان أن الفيديو يزيد عن دقيقة (70 ثانية)
    final_bg = clip.loop(duration=70)
    
    clips = [final_bg]
    
    # توزيع الحقائق الـ 5 زمنياً (كل حقيقة تظهر 14 ثانية)
    for i, fact in enumerate(facts[:5]):
        txt = TextClip(
            fact, 
            fontsize=55, 
            color='white', 
            font='Arial-Bold',
            method='caption', 
            size=(600, None),
            stroke_color='black', 
            stroke_width=2
        ).set_start(i*14).set_duration(13).set_position('center')
        clips.append(txt)
    
    # دمج المكونات
    result = CompositeVideoClip(clips)
    
    # إضافة الموسيقى إذا وجدت
    if os.path.exists("music.mp3"):
        audio = AudioFileClip("music.mp3").set_duration(70)
        result = result.set_audio(audio)
    
    # تصدير الفيديو بأفضل إعدادات ضغط (Fast Encoding) لـ GitHub Actions
    output_name = "empire_reel.mp4"
    result.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    return output_name

def publish_to_fb(video_path):
    """الرفع المباشر لفيسبوك رييلز"""
    url = f"https://graph.facebook.com/v19.0/{CONFIG['FB_ID']}/videos"
    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {
            'description': f"Mind-blowing facts for you! ✨ #Facts #AI #Trending #Global [Ref:{random.randint(100,999)}]",
            'access_token': CONFIG['FB_TOKEN']
        }
        r = requests.post(url, data=data, files=files)
        print(f"Meta Response: {r.json()}")

if __name__ == "__main__":
    print("Starting Empire Automation...")
    video = build_video()
    publish_to_fb(video)
    print("Process Finished Successfully!")
