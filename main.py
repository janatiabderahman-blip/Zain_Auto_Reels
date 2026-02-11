import os
import requests
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw
import time

# --- Directories ---
os.makedirs("output_videos", exist_ok=True)

# --- Environment Variables ---
HF_TOKEN = os.getenv("HF_TOKEN")
PEXELS_KEY = os.getenv("PEXELS_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

# --- 1. Generate AI text ---
def generate_text(prompt):
    url = "https://api-inference.huggingface.co/models/bigscience/bloomz-7b1-mt"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            return r.json()[0]["generated_text"]
        except Exception as e:
            print(f"⚠️ Text generation retry {attempt+1}: {e}")
            time.sleep(2)
    print("⚠️ Using fallback text")
    return "Space is vast | Stars shine bright | AI changes the world"

# --- 2. Fetch video from Pexels ---
def fetch_video(query="space"):
    try:
        headers = {"Authorization": PEXELS_KEY}
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        videos = r.json().get("videos", [])
        if videos:
            video_url = videos[0]["video_files"][0]["link"]
            video_path = "temp_video.mp4"
            with open(video_path, "wb") as f:
                f.write(requests.get(video_url).content)
            return video_path
    except Exception as e:
        print("⚠️ Pexels video fetch failed:", e)

    # --- Fallback: create placeholder AI video ---
    img = Image.new("RGB", (720, 1280), color=(20, 20, 50))
    draw = ImageDraw.Draw(img)
    draw.text((50, 600), "AI Generated Video", fill=(255,255,255))
    temp_img_path = "temp_image.png"
    img.save(temp_img_path)
    clip = ImageClip(temp_img_path).set_duration(5)
    clip.write_videofile("temp_video.mp4", fps=24)
    return "temp_video.mp4"

# --- 3. Add text to video ---
def create_reel(video_path, text, output_path):
    clip = VideoFileClip(video_path)
    txt_clip = TextClip(text, fontsize=40, color='white', size=clip.size)
    txt_clip = txt_clip.set_position(("center","top")).set_duration(clip.duration)
    final_clip = CompositeVideoClip([clip, txt_clip])
    final_clip.write_videofile(output_path, fps=24)
    return output_path

# --- 4. Upload video to Facebook ---
def upload_to_facebook(video_path, caption):
    url = f"https://graph-video.facebook.com/v17.0/{FB_PAGE_ID}/videos"
    with open(video_path, "rb") as f:
        files = {"source": f}
        data = {"caption": caption, "access_token": FB_PAGE_TOKEN}
        r = requests.post(url, files=files, data=data)
        r.raise_for_status()
        return r.json()

# --- Main Execution ---
def main():
    queries = ["space", "nature", "ocean"]  # Global topics
    for i, q in enumerate(queries, start=1):
        print(f"🌟 Generating video for topic: {q}")
        video_file = fetch_video(q)
        text = generate_text(f"Write a short global description about a {q} video for social media")
        output_path = f"output_videos/reel_{i}.mp4"
        create_reel(video_file, text, output_path)
        response = upload_to_facebook(output_path, text)
        print(f"✅ Uploaded to Facebook:", response)
        time.sleep(2)  # prevent overload

if __name__ == "__main__":
    main()
