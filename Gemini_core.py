import os
import requests
import logging
from genai import Client # استخدام المكتبة الجديدة حصراً

logging.basicConfig(level=logging.INFO)

class EmpireEngine:
    def __init__(self):
        # الربط بـ API الجديد عبر المكتبة الحديثة
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = Client(api_key=self.api_key) if self.api_key else None
        
        # مفاتيح النظام الأخرى
        self.pexels_key = os.getenv("PEXELS_KEY")

    def generate_content(self):
        logging.info("Generating content via New google-genai SDK...")
        try:
            # الطريقة الجديدة لاستدعاء الموديل (تلقائياً v1 Stable)
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents="Write 3 short space facts. Format: Fact | Fact | Fact"
            )
            return response.text.split('|')
        except Exception as e:
            logging.error(f"New API Error: {e}")
            return ["Space is infinite.", "The Moon orbits Earth.", "Sun is a star."]

    def fetch_video(self):
        # التحقق من مفتاح Pexels (الذي أثبت نجاحه في صورتك الأخيرة)
        if not self.pexels_key:
            logging.error("PEXELS_KEY is missing!")
            return None
        
        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=galaxy&per_page=1"
        try:
            r = requests.get(url, headers=headers)
            video_url = r.json()['videos'][0]['video_files'][0]['link']
            with open("bg.mp4", "wb") as f:
                f.write(requests.get(video_url).content)
            logging.info("✅ Video secured via Pexels.")
            return "bg.mp4"
        except Exception as e:
            logging.error(f"Pexels Error: {e}")
            return None

    def run(self):
        if not self.client:
            logging.error("Client initialization failed.")
            return
            
        video = self.fetch_video()
        facts = self.generate_content()
        
        if video and facts:
            logging.info("🚀 System ready for Final Render!")
            # كود المونتاج والنشر...

if __name__ == "__main__":
    EmpireEngine().run()
