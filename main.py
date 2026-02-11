import os
import requests
import ffmpeg
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import time

# --- الإعدادات ---
HF_TOKEN = os.getenv("HF_TOKEN")
PEXELS_KEY = os.getenv("PEXELS_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def generate_ai_text(prompt):
    """توليد نصوص تسويقية قوية باستخدام Gemini"""
    try:
        response = model.generate_content(f"Write a viral, short social media caption and a headline for: {prompt}. Keep it engaging!")
        return response.text.split('\n')[0] # نأخذ أول سطر كعنوان
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return "Discover the Magic of AI 🚀"

def fetch_video(query):
    """جلب فيديو عالي الجودة من Pexels"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
    try:
        r = requests.get(url, headers=headers)
        video_url = r.json()['videos'][0]['video_files'][0]['link']
        video_data = requests.get(video_url).content
        with open("raw_video.mp4", "wb") as f:
            f.write(video_data)
        return "raw_video.mp4"
    except Exception as e:
        print(f"❌ Video fetch error: {e}")
        return None

def process_video_ffmpeg(input_path, text, output_path):
    """إضافة نص احترافي للفيديو باستخدام FFmpeg مباشرة (بديل MoviePy)"""
    try:
        # إعداد الفلتر لإضافة نص في المنتصف بخلفية شبه شفافة
        (
            ffmpeg
            .input(input_path)
            .drawtext(
                text=text,
                fontsize=36,
                fontcolor='white',
                box=1,
                boxcolor='black@0.5',
                boxborderw=5,
                x='(w-text_w)/2',
                y='(h-text_h)/2',
                fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' # مسار الخط في Linux/GitHub
            )
            .output(output_path, vcodec='libx264', acodec='copy', shortest=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"❌ FFmpeg error: {e.stderr.decode()}")
        return None

def upload_to_facebook(video_path, caption):
    """رفع الفيديو إلى Facebook Reels"""
    url = f"https://graph-video.facebook.com/v19.0/{FB_PAGE_ID}/videos"
    with open(video_path, "rb") as f:
        payload = {
            'access_token': FB_PAGE_TOKEN,
            'description': caption,
        }
        files = {'source': f}
        r = requests.post(url, data=payload, files=files)
        return r.json()

def main():
    os.makedirs("output_videos", exist_ok=True)
    topics = ["Future Technology", "Deep Ocean", "Cyberpunk City"]
    
    for i, topic in enumerate(topics):
        print(f"🚀 Processing: {topic}")
        video_file = fetch_video(topic)
        if video_file:
            caption = generate_ai_text(topic)
            output = f"output_videos/empire_reel_{i}.mp4"
            if process_video_ffmpeg(video_file, caption, output):
                res = upload_to_facebook(output, caption)
                print(f"✅ Success! FB Response: {res}")
            time.sleep(5)

if __name__ == "__main__":
    main()
