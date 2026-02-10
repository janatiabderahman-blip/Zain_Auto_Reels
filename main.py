import os
import time
import random
import requests
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

FB_TOKEN = os.getenv("FB_TOKEN")
PAGE_ID  = os.getenv("PAGE_ID")

RAW   = Path("raw.mp4")
PROC  = Path("proc.mp4")
MUSIC = Path("music.mp3")
FINAL = Path("final.mp4")

TREND_TOPICS = [
    "Oddly Satisfying AI Loop",
    "Relaxing Visual Therapy",
    "AI Motion Art for Your Mind",
    "Mind Calming Visual ASMR",
    "Endless Satisfying AI Motion",
]

MUSIC_URL = (
    "https://files.freemusicarchive.org/storage-freemusicarchive-org/"
    "music/no_curator/Scott_Holmes_Music/Corporate__Motivational_Music/"
    "Scott_Holmes_Music_-_Inspiring_Corporate.mp3"
)

def log(msg):
    print(msg, flush=True)

def clean():
    for f in [RAW, PROC, MUSIC, FINAL]:
        if f.exists():
            f.unlink()

def validate_env():
    if not FB_TOKEN:
        raise RuntimeError("❌ FB_TOKEN missing")
    if not PAGE_ID:
        raise RuntimeError("❌ PAGE_ID missing")

def run_cmd(cmd):
    log(f"🔧 Running: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line.rstrip())
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError("❌ ffmpeg failed")

# =========================
# LifeOfVids — يعمل 100٪
# =========================
def lifeofvids_download():
    url = "https://www.lifeofvids.com/videos/"
    log(f"🔍 Searching LifeOfVids: {url}")

    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("a.download")
    if not items:
        raise RuntimeError("❌ No videos found on LifeOfVids")

    chosen = random.choice(items)
    video_url = chosen["href"]

    log(f"⬇️ Downloading CC0 video: {video_url}")

    vr = requests.get(video_url, timeout=60)
    vr.raise_for_status()
    with RAW.open("wb") as f:
        f.write(vr.content)

    log("✅ Video downloaded successfully")

def download_music():
    log("🎵 Downloading CC0 music...")
    r = requests.get(MUSIC_URL, timeout=60)
    r.raise_for_status()
    with MUSIC.open("wb") as f:
        f.write(r.content)
    log("✅ Music downloaded")

def process_video_with_ai_style(text):
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

def upload_to_facebook(description):
    log("📡 Starting Facebook upload session...")
    init = requests.post(
        f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels",
        data={"upload_phase": "start", "access_token": FB_TOKEN},
        timeout=60,
    )
    init.raise_for_status()
    js = init.json()

    video_id   = js["video_id"]
    upload_url = js["upload_url"]

    with FINAL.open("rb") as f:
        requests.post(
            upload_url,
            data=f,
            headers={"Authorization": f"OAuth {FB_TOKEN}"},
            timeout=300,
        )

    time.sleep(20)

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
    log(f"🎉 Reel published successfully: {finish.json()}")

def run():
    log("🚀 Starting AI+CC auto-reels bot (LifeOfVids version)...")
    validate_env()
    clean()

    topic = random.choice(TREND_TOPICS)
    log(f"🔥 Selected topic: {topic}")

    lifeofvids_download()
    download_music()
    process_video_with_ai_style(topic)
    add_music_to_video()

    desc = f"🔥 {topic} (Auto-generated AI-style CC0 reel)"
    upload_to_facebook(desc)

    clean()
    log("🏁 Bot finished successfully")

if __name__ == "__main__":
    run()
