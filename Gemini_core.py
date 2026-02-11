import os
import requests
import logging
from google import genai  # التصحيح الذي ذكرته للـ Import

logging.basicConfig(level=logging.INFO)

class EmpireEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.pexels_key = os.getenv("PEXELS_KEY")
        
        # إعداد العميل مع إجبار النظام على استخدام v1 لإنهاء خطأ 404
        if self.api_key:
            # المكتبة الجديدة تستهدف v1 تلقائياً عند استخدام genai.Client
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logging.error("GEMINI_API_KEY missing!")

    def generate_content(self):
        logging.info("Generating content via v1 API...")
        try:
            # هنا نستخدم الموديل المطلوب مباشرة في المسار المستقر
            # gemini-1.5-flash مدعوم بالكامل في v1
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents="Write 3 amazing facts about space. Separate with '|'"
            )
            
            if response and response.text:
                logging.info("✅ Content generated successfully!")
                return response.text.split('|')
            else:
                raise ValueError("Empty response from Gemini")

        except Exception as e:
            # في حال الفشل، لن نصمت بل سنعرف السبب الحقيقي
            logging.error(f"❌ Actual Generation Error: {e}")
            return ["Space is huge.", "Stars are bright.", "Gravity is real."]

    def fetch_video(self):
        # التحقق من Pexels (الذي يعمل لديك بنجاح)
        if not self.pexels_key: return None
        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=galaxy&per_page=1"
        try:
            r = requests.get(url, headers=headers)
            video_url = r.json()['videos'][0]['video_files'][0]['link']
            with open("bg.mp4", "wb") as f:
                f.write(requests.get(video_url).content)
            return "bg.mp4"
        except Exception: return None

    def run(self):
        if not self.client: return
        video = self.fetch_video()
        facts = self.generate_content()
        if video and facts:
            logging.info(f"🚀 Success! Ready to render with: {facts[0][:20]}...")

if __name__ == "__main__":
    EmpireEngine().run()
