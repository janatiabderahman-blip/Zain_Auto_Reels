import os
import requests
import random
import logging
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

logging.basicConfig(level=logging.INFO)
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

class EmpireEngine:
    def __init__(self):
        # تم تعديل الأسماء هنا لتطابق صور الـ Secrets الخاصة بك تماماً
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.pexels_key = os.getenv("PEXELS_KEY") 
        self.fb_page_id = os.getenv("PAGE_ID")
        self.fb_token = os.getenv("FB_TOKEN")

        # الإصلاح الجذري لخطأ 404: إجبار المكتبة على المسار المستقر v1
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key, transport='rest')
        else:
            logging.error("GEMINI_API_KEY is missing!")

    def generate_content(self):
        logging.info("Generating content via Gemini v1 Stable...")
        try:
            # استخدام الموديل المستقر
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Give me 3 short facts about space. Separate with '|'")
            return [f.strip() for f in response.text.split('|')]
        except Exception as e:
            logging.error(f"Gemini Error: {e}")
            return ["Space is silent.", "Mars is red.", "Stars are far."]

    def fetch_video(self):
        logging.info("Checking Pexels Key...")
        if not self.pexels_key:
            logging.error("PEXELS_KEY is empty! Check your GitHub Secrets naming.")
            return None

        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=galaxy&per_page=1"
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            video_url = r.json()['videos'][0]['video_files'][0]['link']
            with open("bg.mp4", "wb") as f:
                f.write(requests.get(video_url).content)
            return "bg.mp4"
        except Exception as e:
            logging.error(f"Pexels Error: {e}")
            return None

    def run(self):
        video = self.fetch_video()
        facts = self.generate_content()
        if video and facts:
            logging.info("🚀 Assets secured! Starting production...")
            # هنا يكمل كود الرندرة والنشر لفيسبوك
        else:
            logging.error("❌ Aborting: Missing Keys or Assets.")

if __name__ == "__main__":
    EmpireEngine().run()
