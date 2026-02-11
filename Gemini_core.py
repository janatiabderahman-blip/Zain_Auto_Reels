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

        self.client = None
        self.model_candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]

        if not self.api_key:
            logging.error("❌ GEMINI_API_KEY not found")
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            self.model_candidates = self._discover_models()
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            self.client = None

    def _discover_models(self):
        """Auto-detect supported models"""
        try:
            models = []
            for m in self.client.models.list():
                if "generateContent" in m.supported_generation_methods:
                    models.append(m.name)
            if models:
                logging.info(f"✅ Discovered models: {models}")
                return models
        except Exception as e:
            logging.warning(f"Model discovery failed: {e}")

        logging.warning("⚠️ Using fallback model list")
        return self.model_candidates

    def generate_content_safe(self, prompt, retries=3):
        """Auto retry + auto fallback"""
        if not self.client:
            logging.error("AI client unavailable, using fallback text")
            return self._fallback_text()

        for model in self.model_candidates:
            for attempt in range(1, retries + 1):
                try:
                    logging.info(f"Trying {model} (Attempt {attempt})")
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    if response and response.text:
                        logging.info(f"✅ Success with {model}")
                        return response.text
                except Exception as e:
                    logging.warning(f"{model} failed: {e}")
                    time.sleep(2)

            logging.error(f"❌ Model {model} exhausted retries")

        logging.critical("🚨 All models failed")
        return self._fallback_text()

    def _fallback_text(self):
        return (
            "Space is vast and mysterious | "
            "Black holes bend space and time | "
            "The universe is constantly expanding"
        )

    def fetch_video_safe(self):
        """Safe Pexels video fetch"""
        if not self.pexels_key:
            logging.warning("PEXELS_KEY missing")
            return None

        headers = {"Authorization": self.pexels_key}
        url = "https://api.pexels.com/videos/search?query=galaxy&per_page=1"

        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()

            videos = r.json().get("videos", [])
            if not videos:
                raise ValueError("No videos returned")

            video_url = videos[0]["video_files"][0]["link"]
            video_data = requests.get(video_url, timeout=15).content

            with open("bg.mp4", "wb") as f:
                f.write(video_data)

            logging.info("🎬 Video secured")
            return "bg.mp4"

        except Exception as e:
            logging.error(f"Video fetch failed: {e}")
            return None

    def run(self):
        if not self.client:
            logging.error("System halted: No AI client")
            return

        video = self.fetch_video_safe()
        facts_raw = self.generate_content_safe(
            "Write 3 amazing space facts separated by |"
        )

        facts = [f.strip() for f in facts_raw.split("|") if f.strip()]
        while len(facts) < 3:
            facts.append("Exploring the universe beyond imagination")

        if video:
            logging.info(f"🚀 Ready: {facts[0][:40]}...")
        else:
            logging.warning("⚠️ Proceeding without video")

        logging.info("✅ Automation completed safely")


if __name__ == "__main__":
    EmpireEngine().run()
