import os
import requests
import logging
# التصحيح النهائي للاستدعاء
from google import genai 

logging.basicConfig(level=logging.INFO)

class EmpireEngine:
    def __init__(self):
        # جلب المفاتيح من GitHub Secrets
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.pexels_key = os.getenv("PEXELS_KEY")
        
        # إعداد العميل (Client) بالطريقة الجديدة
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logging.error("GEMINI_API_KEY is missing!")

    def generate_content(self):
        logging.info("Generating content via google-genai...")
        try:
            # استخدام الطريقة الجديدة في المكتبة الرسمية
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents="Write 3 tech facts. Format: Fact | Fact | Fact"
            )
            return response.text.split('|')
        except Exception as e:
            logging.error(f"GenAI Import/API Error: {e}")
            return ["AI is smart.", "Tech is fast.", "Data is key."]

    def fetch_video(self):
        # التحقق من Pexels
        if not self.pexels_key:
            logging.error("PEXELS_KEY is empty!")
            return None
        
        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=tech&per_page=1"
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            video_url = r.json()['videos'][0]['video_files'][0]['link']
            with open("bg.mp4", "wb") as f:
                f.write(requests.get(video_url).content)
            logging.info("✅ Video secured.")
            return "bg.mp4"
        except Exception as e:
            logging.error(f"Pexels Error: {e}")
            return None

    def run(self):
        if not self.client: return
        video = self.fetch_video()
        facts = self.generate_content()
        if video and facts:
            logging.info("🚀 Done! No more Import errors.")

if __name__ == "__main__":
    EmpireEngine().run()
