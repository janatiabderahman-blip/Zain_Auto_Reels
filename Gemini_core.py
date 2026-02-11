import os
import requests
import time
import logging

# إعدادات التسجيل لمتابعة العمل في GitHub Logs
logging.basicConfig(level=logging.INFO)

class EmpireEngineHF:
    def __init__(self):
        # جلب المفاتيح من البيئة (GitHub Secrets)
        self.hf_token = os.getenv("HF_TOKEN")
        self.pexels_key = os.getenv("PEXELS_KEY")
        
        # استخدام نموذج قوي ومستقر من Hugging Face
        self.model_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}

    def generate_content_safe(self, prompt, retries=3):
        """توليد المحتوى مع ميزة إعادة المحاولة والتبديل التلقائي"""
        payload = {
            "inputs": f"<|user|>\n{prompt}\n<|assistant|>",
            "parameters": {"max_new_tokens": 150, "return_full_text": False}
        }
        
        for attempt in range(retries):
            try:
                logging.info(f"HF Request (Attempt {attempt+1})...")
                response = requests.post(self.model_url, headers=self.headers, json=payload, timeout=30)
                
                # معالجة حالة Model Loading (خطأ 503 الشائع في HF)
                if response.status_code == 503:
                    wait_time = response.json().get('estimated_time', 20)
                    logging.warning(f"Model is loading... waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                # استخراج النص الناتج بناءً على هيكلية HF
                text = result[0]['generated_text'] if isinstance(result, list) else result['generated_text']
                logging.info("✅ Hugging Face Content Secured!")
                return text
                
            except Exception as e:
                logging.error(f"HF Attempt {attempt+1} failed: {e}")
                time.sleep(5)
        
        # Fallback: نص احتياطي في حال فشل الـ API تماماً لضمان عدم توقف الـ Job
        return "Space is eternal | Technology is power | Data is the new oil"

    def fetch_video_pexels(self):
        """جلب فيديو الخلفية من Pexels"""
        if not self.pexels_key:
            logging.error("PEXELS_KEY is missing!")
            return None
            
        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=galaxy&per_page=1"
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
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
        # 1. جلب الفيديو
        video = self.fetch_video_pexels()
        
        # 2. توليد المحتوى
        prompt = "Write 3 short amazing space facts. Format: Fact1 | Fact2 | Fact3"
        content = self.generate_content_safe(prompt)
        
        # 3. معالجة البيانات
        facts = [f.strip() for f in content.split('|')]
        
        if video and facts:
            logging.info(f"🚀 PRODUCTION READY: Found {len(facts)} facts. Video: {video}")
            # هنا يتم استدعاء دالة المونتاج والنشر (MoviePy)
        else:
            logging.critical("❌ Critical Assets missing. Aborting run.")

if __name__ == "__main__":
    EmpireEngineHF().run()
