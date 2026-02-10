import os
import time
import random
import requests
import subprocess
from pathlib import Path

FB_TOKEN = os.getenv("FB_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

FINAL = Path("final.mp4")

# مصادر فيديوهات Creative Commons (قانونية)
CC_VIDEOS = [
    "https://cdn.pixabay.com/vimeo/123456789.mp4",
    "https://cdn.videvo.net/videvo_files/video/free/2023-01/somefile.mp4",
    "https://assets.mixkit.co/videos/preview/mixkit-satisfying-liquid-1234.mp4"
]

def log(msg):
    print(msg, flush=True)

def download_cc_video():
    url = random.choice(CC_VIDEOS)
    log(f"🎬 تحميل فيديو CC قانوني: {url}")
    r = requests.get(url)
    with open("raw.mp4", "wb") as f:
        f.write(r.content)
    return Path("raw.mp4")

def generate_ai_video():
    log("🤖 توليد فيديو AI (محاكاة)…")
    # هنا تضع API حقيقية لاحقًا مثل Runway أو Pika أو Kaiber
    # الآن نستخدم فيديو CC كبديل
    return download_cc_video()

def transform_video(input_file):
    log("🎨 تعديل الفيديو (تأثيرات + تغيير حجم)…")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-vf", "scale=1080:1920,fps=30",
        "-c:a", "copy",
        str(FINAL)
    ]
    subprocess.run(cmd, check=True)
    log("✅ تم تجهيز final.mp4")

def upload_to_facebook():
    log("📡 بدء رفع الريل…")
    init = requests.post(
        f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels",
        data={"upload_phase": "start", "access_token": FB_TOKEN}
    ).json()

    video_id = init["video_id"]
    upload_url = init["upload_url"]

    with open(FINAL, "rb") as f:
        requests.post(upload_url, data=f, headers={"Authorization": f"OAuth {FB_TOKEN}"})

    time.sleep(20)

    finish = requests.post(
        f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels",
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "description": "🔥 AI + CC satisfying reel",
            "access_token": FB_TOKEN
        }
    ).json()

    log(f"🎉 تم نشر الريل بنجاح: {finish}")

def run():
    log("🚀 بدء البوت القانوني Zain Auto Bot…")

    # اختيار بين AI أو CC
    if random.random() < 0.5:
        src = download_cc_video()
    else:
        src = generate_ai_video()

    transform_video(src)
    upload_to_facebook()

    log("🏁 انتهى العمل بنجاح.")

if __name__ == "__main__":
    run()
