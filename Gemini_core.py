import os
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

class EmpireEngineFinal:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.pexels_key = os.getenv("PEXELS_KEY")
        
        # استخدام نموذج Mistral المستقر جداً لتفادي خطأ 410
        self.model_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}

    def generate_content_safe(self, prompt, retries=3):
        # تجهيز الطلب بصيغة تتوافق مع نماذج Instruct
        payload = {
            "inputs": f"<s>[INST] {prompt} [/INST]</s>",
            "parameters": {"max_new_tokens": 100, "temperature": 0.7}
        }
        
        for attempt in range(retries):
            try:
                logging.info(f"HF Request (Attempt {attempt+1})...")
                response = requests.post(self.model_url, headers=self.headers, json=payload, timeout=30)
                
                # معالجة حالة تحميل النموذج
                if response.status_code == 503:
                    wait_time = response.json().get('estimated_time', 20)
                    logging.warning(f"Model loading... waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                # استخراج النص
                text = result[0]['generated_text'] if isinstance(result, list) else result['generated_text']
                # تنظيف النص من الوسوم
                clean_text = text.split("[/INST]")[-1].strip()
                logging.info("✅ Content Secured from Mistral!")
                return clean_text
            except Exception as e:
                logging.error(f"Attempt {attempt+1} failed: {e}")
                time.sleep(5)
        
        return "Space is vast | Technology is fast | AI is the future"

    def fetch_video(self):
        # كود Pexels الذي نجح في الصورة رقم 6
        if not self.pexels_key: return None
        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=galaxy&per_page=1"
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            video_url = r.json()['videos'][0]['video_files'][0]['link']
            with open("bg.mp4", "wb") as f:
                f.write(requests.get(video_url).content)
            logging.info("✅ Pexels Video secured.")
            return "bg.mp4"
        except Exception as e:
            logging.error(f"Pexels error: {e}")
            return None

    def run(self):
        video = self.fetch_video()
        prompt = "Give me 3 short amazing space facts separated by |"
        facts_raw = self.generate_content_safe(prompt)
        
        # تنظيف وفصل الحقائق
        facts = [f.strip() for f in facts_raw.split('|') if len(f) > 5]
        
        if video and len(facts) >= 1:
            logging.info(f"🚀 READY TO GO: Found {len(facts)} facts. Video: bg.mp4")
        else:
            logging.critical("❌ Production failed: Missing Assets.")

if __name__ == "__main__":
    EmpireEngineFinal().run()
