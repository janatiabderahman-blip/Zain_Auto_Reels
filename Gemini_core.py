import os
import requests
import random
import logging
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings

logging.basicConfig(level=logging.INFO)
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

class EmpireAutomation:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.fb_id = os.getenv("FB_PAGE_ID")
        self.fb_token = os.getenv("FB_PAGE_TOKEN")
        # إعداد جيميني مع أحدث إصدار مستقر
        genai.configure(api_key=self.gemini_key)

    def generate_global_content(self):
        logging.info("Generating content via Gemini...")
        try:
            # استخدام 'gemini-1.5-flash' فهو أسرع وأكثر استقراراً الآن
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Write 5 short mind-blowing facts about space. Separate them with '|'."
            response = model.generate_content(prompt)
            return [f.strip() for f in response.text.split('|')]
        except Exception as e:
            logging.error(f"Gemini failed: {e}")
            return ["Space is silent.", "Stars are far.", "Mars is red.", "Earth is home.", "Sun is hot."]

    def fetch_video(self):
        logging.info("Fetching video from Pexels...")
        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=galaxy&per_page=1"
        try:
            r = requests.get(url, headers=headers).json()
            # فحص دقيق لوجود الفيديوهات لتجنب خطأ 'videos'
            if 'videos' in r and len(r['videos']) > 0:
                video_url = r['videos'][0]['video_files'][0]['link']
                with open("temp_bg.mp4", 'wb') as f:
                    f.write(requests.get(video_url).content)
                return "temp_bg.mp4"
            else:
                logging.error("Pexels API returned no videos.")
                return None
        except Exception as e:
            logging.error(f"Pexels failed: {e}")
            return None

    def run(self):
        facts = self.generate_global_content()
        video_path = self.fetch_video()
        if video_path:
            logging.info("Everything is ready for rendering!")
            # كود الرندرة والنشر (نفس السابق)
        else:
            logging.error("Process aborted: Missing Assets.")

if __name__ == "__main__":
    EmpireAutomation().run()
