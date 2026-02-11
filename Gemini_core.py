import os
import requests
import random
import time
import logging
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings

# إعداد السجلات لمراقبة الأداء في GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# إعداد مسار ImageMagick الضروري لعمل النصوص في بيئة Linux
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

class EmpireAutomation:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.fb_id = os.getenv("FB_PAGE_ID")
        self.fb_token = os.getenv("FB_PAGE_TOKEN")
        genai.configure(api_key=self.gemini_key)

    def generate_global_content(self):
        """توليد محتوى إنجليزي عالمي فريد"""
        logging.info("Generating content via Gemini...")
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = (
                "Provide 5 viral, mind-blowing facts about science or history for a global audience. "
                "Format: Fact 1 | Fact 2 | Fact 3 | Fact 4 | Fact 5. "
                "No emojis, no complex words. Maximum 12 words per fact."
            )
            response = model.generate_content(prompt)
            facts = [f.strip() for f in response.text.split('|')]
            return facts[:5]
        except Exception as e:
            logging.error(f"Gemini failed: {e}")
            return ["The universe is vast and mysterious.", "Nature always finds a way to survive.", "Ancient history holds many secrets.", "Technology is evolving faster than ever.", "Science explains the beauty of life."]

    def fetch_video(self):
        """جلب فيديو عالي الجودة متوافق مع أبعاد الرييلز"""
        logging.info("Fetching video from Pexels...")
        headers = {"Authorization": self.pexels_key}
        topics = ['galaxy', 'ocean deep', 'forest aerial', 'abstract technology', 'minimalist architecture']
        query = random.choice(topics)
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
        
        try:
            response = requests.get(url, headers=headers).json()
            video_data = random.choice(response['videos'])
            # اختيار الجودة المتوسطة لتسريع الرندرة
            video_url = next(f['link'] for f in video_data['video_files'] if f['width'] <= 1080)
            
            with open("temp_bg.mp4", 'wb') as f:
                f.write(requests.get(video_url).content)
            return "temp_bg.mp4"
        except Exception as e:
            logging.error(f"Video download failed: {e}")
            return None

    def render_reel(self, facts, video_path):
        """صناعة الفيديو النهائي بالمعايير الإمبراطورية"""
        logging.info("Starting video rendering...")
        output_file = "final_empire_reel.mp4"
        
        # تحميل الفيديو وتعديل الأبعاد ليكون 720p (مثالي لـ GitHub و Facebook)
        clip = VideoFileClip(video_path).resize(width=720)
        final_bg = clip.loop(duration=75) # مدة الفيديو الإجمالية
        
        text_layers = [final_bg]
        
        for i, fact in enumerate(facts):
            txt = TextClip(
                fact, 
                fontsize=52, 
                color='white', 
                font='Arial-Bold',
                method='caption', 
                size=(620, None),
                stroke_color='black', 
                stroke_width=1.5
            ).set_start(i*15).set_duration(14).set_position('center')
            text_layers.append(txt)
        
        final_video = CompositeVideoClip(text_layers)
        
        # دمج الموسيقى
        if os.path.exists("music.mp3"):
            audio = AudioFileClip("music.mp3").subclip(0, 75)
            final_video = final_video.set_audio(audio)
        
        # التصدير باستخدام أسرع Encoder متاح
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
        return output_file

    def publish(self, video_path):
        """نشر الفيديو على فيسبوك رييلز"""
        logging.info("Uploading to Facebook...")
        url = f"https://graph.facebook.com/v19.0/{self.fb_id}/videos"
        with open(video_path, 'rb') as f:
            payload = {
                'description': f"Mind-blowing facts you need to know! 🌍✨ #Facts #AI #Trending #GlobalID_{random.randint(1000,9999)}",
                'access_token': self.fb_token
            }
            files = {'file': f}
            r = requests.post(url, data=payload, files=files)
            logging.info(f"Meta Response: {r.json()}")

    def run(self):
        """تشغيل المحرك بالكامل"""
        facts = self.generate_global_content()
        video_path = self.fetch_video()
        
        if video_path:
            final_video = self.render_reel(facts, video_path)
            self.publish(final_video)
            logging.info("Empire Core has finished the cycle.")
        else:
            logging.error("Process aborted: No background video found.")

if __name__ == "__main__":
    bot = EmpireAutomation()
    bot.run()
