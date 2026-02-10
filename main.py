import os
import time
import random
import requests
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

# =========================
# Secrets من GitHub
# =========================
FB_TOKEN = os.getenv("FB_TOKEN")
PAGE_ID  = os.getenv("PAGE_ID")

# =========================
# ملفات العمل
# =========================
RAW   = Path("raw.mp4")
PROC  = Path("proc.mp4")
MUSIC = Path("music.mp3")
FINAL = Path("final.mp4")

# =========================
# مواضيع ترند (وصف + نص على الفيديو)
# =========================
TREND_TOPICS = [
    "Oddly Satisfying AI Loop",
    "Relaxing Visual Therapy",
    "AI Motion Art for Your Mind",
    "Mind Calming Visual ASMR",
    "Endless Satisfying AI Motion",
]

# فئات نبحث بها في Mixkit (بدون key)
MIXKIT_CATEGORIES = [
    "satisfying",
    "abstract",
    "relaxing",
    "nature",
    "technology",
    "background",
]

# موسيقى CC0 مجانية (يمكن تغييرها لاحقًا)
MUSIC_URL = (
    "https://files.freemusicarchive.org/storage-freemusicarchive-org/"
    "music/no_curator/Scott_Holmes_Music/Corporate__Motivational_Music/"
    "Scott_Holmes_Music_-_Inspiring_Corporate.mp3"
)

# =========================
# أدوات مساعدة
# =========================

def log(msg: str):
    print(msg, flush=True)

def clean():
    for f in [RAW, PROC, MUSIC, FINAL]:
        if f.exists():
            try:
                f.unlink()
                log(f"🧹 Deleted: {f}")
            except Exception as e:
                log(f"⚠️ Could not delete {f}: {e}")

def validate_env():
    if not FB_TOKEN:
        raise RuntimeError("❌ FB_TOKEN غير موجود في Secrets")
    if not PAGE_ID:
        raise RuntimeError("❌ PAGE_ID غير موجود في Secrets")

def run_cmd(cmd: list[str]):
    log(f"🔧 Running: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line.rstrip())
    proc.wait()
    log(f"🔚 Exit code: {proc.returncode}")
    if proc.returncode != 0:
        raise RuntimeError(f"❌ Command failed: {' '.join(cmd)}")

# =========================
# جلب فيديو CC0 من Mixkit (بدون key)
# =========================

def mixkit_search_and_download(max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            query = random.choice(MIXKIT_CATEGORIES)
            url   = f"https://mixkit.co/free-stock-video/{query}/"
            log(f"🔍 Searching Mixkit (attempt {attempt}): {url}")

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            links = soup.select("a.video-item__thumb")
            if not links:
                log("⚠️ No videos found on this page, retrying...")
                continue

            chosen = random.choice(links)
            video_page = "https://mixkit.co" + chosen["href"]
            log(f"🎬 Selected video page: {video_page}")

            r2 = requests.get(video_page, timeout=30)
            r2.raise_for_status()
            soup2 = BeautifulSoup(r2.text, "html.parser")

            download_btn = soup2.select_one("a#download-button")
            if not download_btn:
                log("⚠️ No download button found, retrying...")
                continue

            video_url = download_btn["href"]
            log(f"⬇️ Downloading CC0 video: {video_url}")

            vr = requests.get(video_url, timeout=60)
            vr.raise_for_status()
            with RAW.open("wb") as f:
                f.write(vr.content)

            # فحص سريع للتأكد أن الملف فيديو صالح
            log("🔎 Validating downloaded video with ffprobe...")
            probe_cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
                str(RAW),
            ]
            probe = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if probe.returncode != 0 or "video" not in probe.stdout.lower():
                log("⚠️ File is not a valid video, retrying...")
                RAW.unlink(missing_ok=True)
                continue

            log("✅ Valid CC0 video downloaded and validated.")
            return

        except Exception as e:
            log(f"⚠️ Error in Mixkit attempt {attempt}: {e}")

    raise RuntimeError("❌ Failed to get a valid video from Mixkit after retries.")

# =========================
# موسيقى CC0
# =========================

def download_music():
    log("🎵 Downloading CC0 music...")
    r = requests.get(MUSIC_URL, timeout=60)
    r.raise_for_status()
    with MUSIC.open("wb") as f:
        f.write(r.content)
    log("✅ Music downloaded")

# =========================
# “AI-style” داخل ffmpeg (ألوان + نص + شكل ترندي)
# =========================

def process_video_with_ai_style(text: str):
    log("🎨 Processing video with AI-style effects + text...")

    draw = (
        f"drawtext=text='{text}':"
        "fontcolor=white:fontsize=48:"
        "x=(w-text_w)/2:y=h-200:"
        "box=1:boxcolor=black@0.4:boxborderw=10"
    )

    vf = (
        "scale=1080:1920,"
        "fps=30,"
        "eq=contrast=1.15:brightness=0.03:saturation=1.2,"
        "vignette,"
        f"{draw}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(RAW),
        "-vf", vf,
        "-c:a", "aac",
        "-b:a", "128k",
        str(PROC),
    ]
    run_cmd(cmd)
    if not PROC.exists():
        raise RuntimeError("❌ Processed video not created")
    log("✅ AI-styled processed video ready")

# =========================
# دمج الموسيقى مع الفيديو
# =========================

def add_music_to_video():
    log("🎧 Adding music to video...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(PROC),
        "-i", str(MUSIC),
        "-map", "0:v",
        "-map", "1:a",
        "-shortest",
        str(FINAL),
    ]
    run_cmd(cmd)
    if not FINAL.exists():
        raise RuntimeError("❌ Final video not created")
    log("✅ Final video with music ready")

# =========================
# رفع الريل إلى فيسبوك
# =========================

def upload_to_facebook(description: str):
    log("📡 Starting Facebook upload session...")
    init = requests.post(
        f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels",
        data={"upload_phase": "start", "access_token": FB_TOKEN},
        timeout=60,
    )
    init.raise_for_status()
    js = init.json()
    if "video_id" not in js or "upload_url" not in js:
        raise RuntimeError(f"❌ Unexpected init response: {js}")

    video_id   = js["video_id"]
    upload_url = js["upload_url"]
    log(f"✅ Upload session created. video_id={video_id}")

    with FINAL.open("rb") as f:
        up = requests.post(
            upload_url,
            data=f,
            headers={"Authorization": f"OAuth {FB_TOKEN}"},
            timeout=300,
        )
    if not up.ok:
        raise RuntimeError(f"❌ Upload failed: {up.status_code} {up.text}")
    log("✅ Video data uploaded")

    delay = random.randint(10, 60)
    log(f"⏳ Smart delay before finish: {delay} seconds...")
    time.sleep(delay)

    finish = requests.post(
        f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels",
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "description": description,
            "access_token": FB_TOKEN,
        },
        timeout=60,
    )
    finish.raise_for_status()
    log(f"🎉 Reel published successfully. Response: {finish.json()}")

# =========================
# نقطة التشغيل
# =========================

def run():
    log("🚀 Starting AI+CC auto-reels bot (no key)...")
    validate_env()
    clean()

    topic = random.choice(TREND_TOPICS)
    log(f"🔥 Selected topic: {topic}")

    mixkit_search_and_download()
    download_music()
    process_video_with_ai_style(topic)
    add_music_to_video()

    desc = f"🔥 {topic} (Auto-generated AI-style CC0 reel)"
    upload_to_facebook(desc)

    clean()
    log("🏁 Bot finished successfully")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        raise
