import requests, os, time, random

TOKEN = os.getenv('FB_TOKEN')
PAGE_ID = os.getenv('PAGE_ID')

def run_bot():
    os.system("rm -rf *.mp4")
    # صيد فيديو ترند عالمي
    os.system("yt-dlp -f 'best[ext=mp4]' --max-downloads 1 -o 'raw.mp4' 'ytsearch15:satisfying gadgets shorts'")
    
    if os.path.exists("raw.mp4"):
        # تعديل تقني لكسر الحقوق وخطأ 6000
        os.system("ffmpeg -i raw.mp4 -vf \"hflip,scale=1080:1920,setpts=0.99*PTS\" -c:a copy pro.mp4 -y")
        
        url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
        init = requests.post(url, data={'upload_phase': 'start', 'access_token': TOKEN}).json()
        
        if 'video_id' in init:
            v_id = init['video_id']
            with open("pro.mp4", 'rb') as f:
                requests.post(init['upload_url'], data=f, headers={'Authorization': f'OAuth {TOKEN}'})
            
            time.sleep(60) # انتظار المعالجة
            requests.post(url, data={
                'upload_phase': 'finish', 'video_id': v_id, 
                'video_state': 'PUBLISHED', 'description': 'Mind-blowing! ✨ #ZainWorld', 
                'access_token': TOKEN
            })
            print("🎉 Done!")

if __name__ == "__main__":
    run_bot()
