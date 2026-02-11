import os
import requests
import random
import logging
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings

# إعدادات النظام الأساسية
logging.basicConfig(level=logging.INFO)
# تأكد من أن ImageMagick مثبت في المسار الصحيح ببيئة Linux
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

class EmpireEngine:
    def __init__(self):
        # الإصلاح الذهبي: استخدام 'rest' لتجنب أخطاء v1beta و 404
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.gemini_key, transport='rest')
        
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.fb_page_id = os.getenv("FB_PAGE_ID")
        self.fb_token = os.getenv("FB_PAGE_TOKEN")

    def generate_stable_content(self):
        """توليد محتوى باستخدام gemini-1.5-flash المستقر"""
        logging.info("Generating stable content via Gemini...")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Give me 5 mind-blowing short facts about space or technology. Separate them with '|'."
            response = model.generate_content(prompt)
            
            if response.text:
                facts = [f.strip() for f in response.text.split('|') if len(f) > 5]
                return facts
            return ["Space is vast.", "AI is changing the world.", "Technology never stops."]
        except Exception as e:
            logging.error(f"Gemini API Error: {e}")
            return ["The universe is expanding.", "Coding is a superpower.", "Innovation drives progress."]

    def fetch_background_video(self):
        """جلب فيديو من Pexels مع التحقق من صحة المفتاح"""
        logging.info("Fetching background video from Pexels...")
        if not self.pexels_key:
            logging.error("PEXELS_API_KEY is empty in Environment Variables!")
            return None

        headers = {"Authorization": self.pexels_key}
        # البحث عن فيديوهات طبيعة أو مجرات بجودة عالية
        search_url = "https://api.pexels.com/videos/search?query=galaxy&per_page=5"
        
        try:
            r = requests.get(search_url, headers=headers)
            r.raise_for_status()
            data = r.json()
            
            if 'videos' in data and data['videos']:
                video_url = random.choice(data['videos'])['video_files'][0]['link']
                video_data = requests.get(video_url).content
                with open("bg_video.mp4", "wb") as f:
                    f.write(video_data)
                return "bg_video.mp4"
            return None
        except Exception as e:
            logging.error(f"Pexels fetch failed: {e}")
            return None

    def create_reel(self):
        """دمج المحتوى والفيديو وإنتاج الرييل النهائي"""
        video_path = self.fetch_background_video()
        facts = self.generate_stable_content()

        if not video_path or not facts:
            logging.error("Missing assets. Aborting process.")
            return

        try:
            logging.info("Starting rendering process...")
            # تحميل الفيديو وقصه (15 ثانية كحد أقصى)
            clip = VideoFileClip(video_path).subclip(0, 15).resize(height=1920)
            
            # إضافة النصوص (تبسيطاً سنعرض حقيقة واحدة عشوائية في هذا المثال)
            fact_text = random.choice(facts)
            txt_clip = TextClip(fact_text, fontsize=70, color='white', font='Arial-Bold', 
                                method='caption', size=(clip.w*0.8, None))
            txt_clip = txt_clip.set_position('center').set_duration(15)

            # دمج الفيديو مع النص
            final_video = CompositeVideoClip([clip, txt_clip])
            
            # حفظ الفيديو بإعدادات سريعة لتجنب استهلاك موارد GitHub
            final_output = "final_reel.mp4"
            final_video.write_videofile(final_output, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")
            
            logging.info(f"✅ Reel created successfully: {final_output}")
            # هنا يمكنك إضافة كود الـ Post إلى فيسبوك
            
        except Exception as e:
            logging.error(f"Rendering failed: {e}")

if __name__ == "__main__":
    engine = EmpireEngine()
    engine.create_reel()
