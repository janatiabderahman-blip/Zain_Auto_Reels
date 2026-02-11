import os
import requests
import ffmpeg
import google.generativeai as genai
import time

# إحضار الإعدادات من نظام GitHub Secrets
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

# إعداد محرك الذكاء الاصطناعي
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_viral_caption(topic):
    """توليد نص جذاب يشبه الفيديوهات المنتشرة"""
    prompt = f"Write a short, viral hook (max 10 words) for a video about {topic}. No hashtags."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Wait for the end! 🔥"

def fetch_video(query):
    """جلب فيديو رأسي (Portrait) مناسب للـ Reels"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and r.json().get('videos'):
        video_url = r.json()['videos'][0]['video_files'][0]['link']
        with open("raw.mp4", "wb") as f:
            f.write(requests.get(video_url).content)
        return "raw.mp4"
    return None

def create_empire_reel(input_path, text):
    """إضافة النص في منتصف الفيديو بشكل احترافي"""
    output = "final_reel.mp4"
    try:
        (
            ffmpeg
            .input(input_path)
            .drawtext(
                text=text,
                fontsize=40,
                fontcolor='white',
                x='(w-text_w)/2',
                y='(h-text_h)/2+100', # مكان النص
                box=1,
                boxcolor='black@0.6', # خلفية للنص لسهولة القراءة
                boxborderw=15,
                fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
            )
            .output(output, vcodec='libx264', acodec='copy')
            .overwrite_output()
            .run()
        )
        return output
    except Exception as e:
        print(f"❌ FFmpeg Error: {e}")
        return None

def upload_to_facebook(file_path, caption):
    """رفع الفيديو النهائي لصفحتك"""
    url = f"https://graph-video.facebook.com/v19.0/{FB_PAGE_ID}/videos"
    with open(file_path, "rb") as f:
        files = {'source': f}
        data = {'access_token': FB_PAGE_TOKEN, 'description': caption}
        r = requests.post(url, files=files, data=data)
        return r.json()

def main():
    # مواضيع تجذب المشاهدات
    topics = ["Luxury Life", "Nature Wonders", "Future Tech"]
    import random
    topic = random.choice(topics)
    
    print(f"🎬 Starting: {topic}")
    video = fetch_video(topic)
    if video:
        text = get_viral_caption(topic)
        final_video = create_empire_reel(video, text)
        if final_video:
            res = upload_to_facebook(final_video, f"{text} #AI #Empire")
            print(f"🚀 Success: {res}")

if __name__ == "__main__":
    main()
