import os
import time
import logging
import requests
from google import genai

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


class EmpireEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.pexels_key = os.getenv("PEXELS_KEY")

        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY missing")

        self.client = genai.Client(
            api_key=self.api_key,
            http_options={"api_version": "v1"}
        )

        # ✅ الموديلات الوحيدة المستقرة حاليًا
        self.model_candidates = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-latest"
        ]

    def generate_content_safe(self, prompt, retries=3):
        for model in self.model_candidates:
            for i in range(retries):
                try:
                    logging.info(f"Trying {model} (Attempt {i+1})")
                    r = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    if r and r.text:
                        logging.info("✅ Success")
                        return r.text
                except Exception as e:
                    logging.warning(f"{model} failed: {e}")
                    time.sleep(2)

        logging.critical("🚨 All models failed – using fallback")
        return "Space is vast and mysterious | Black holes warp spacetime | The universe is expanding"

    def fetch_video_safe(self):
        if not self.pexels_key:
            return None

        try:
            r = requests.get(
                "https://api.pexels.com/videos/search?query=galaxy&per_page=1",
                headers={"Authorization": self.pexels_key},
                timeout=10
            )
            r.raise_for_status()
            video = r.json()["videos"][0]["video_files"][0]["link"]
            data = requests.get(video).content
            with open("bg.mp4", "wb") as f:
                f.write(data)
            return "bg.mp4"
        except Exception as e:
            logging.error(f"Video error: {e}")
            return None

    def run(self):
        video = self.fetch_video_safe()
        text = self.generate_content_safe(
            "Write 3 amazing space facts separated by |"
        )

        facts = [x.strip() for x in text.split("|") if x.strip()]
        logging.info(f"🚀 Ready: {facts[0]}")
        logging.info("✅ Automation completed safely")


if __name__ == "__main__":
    EmpireEngine().run()
