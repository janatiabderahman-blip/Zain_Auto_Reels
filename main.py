import requests, os, time

# جلب البيانات السرية من إعدادات GitHub
TOKEN = os.getenv('FB_TOKEN')
PAGE_ID = os.getenv('PAGE_ID')

def run_bot():
    # تنظيف الملفات القديمة لضمان عدم امتلاء الذاكرة
    for f in ["v.mp4", "final.mp4"]:
        if os.path.exists(f): os.remove(f)

    print("🚀 جاري صيد فيديو ترند جديد...")
    # كود تحميل الفيديو مع فلتر للجودة والوقت
    cmd = "yt-dlp -f 'best[ext=mp4]' --max-downloads 1 --match-filter 'duration < 60' -o 'v.mp4' 'ytsearch15:satisfying gadgets shorts'"
    os.system(cmd)

    if os.path.exists("v.mp4"):
        print("✅ تم التحميل. جاري كسر الحقوق وتغيير البصمة...")
        # تغيير البصمة الرقمية: قلب الفيديو أفقياً وتغيير الحجم
        os.system("ffmpeg -i v.mp4 -vf 'hflip,scale=1080:1920' -c:a copy final.mp4 -y")
        
        if os.path.exists("final.mp4"):
            print("📡 جاري الرفع لفيسبوك...")
            url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"
            
            # بدء عملية الرفع
            init = requests.post(url, data={'upload_phase': 'start', 'access_token': TOKEN}).json()
            
            if 'video_id' in init:
                video_id = init['video_id']
                with open("final.mp4", 'rb') as f:
                    requests.post(init['upload_url'], data=f, headers={'Authorization': f'OAuth {TOKEN}'})
                
                print("⏳ انتظار معالجة فيسبوك (60 ثانية)...")
                time.sleep(60) # وقت ضروري لضمان عدم حدوث خطأ 6000
                
                # النشر النهائي
                res = requests.post(url, data={
                    'upload_phase': 'finish', 'video_id': video_id, 
                    'video_state': 'PUBLISHED', 'description': 'Check this out! ✨ #ZainWorld', 
                    'access_token': TOKEN
                }).json()
                print(f"🏁 النتيجة: {res}")
            else:
                print(f"❌ مشكلة في التوكن أو الصلاحيات: {init}")
    else:
        print("⚠️ لم يتم العثور على فيديوهات جديدة الآن.")

if __name__ == "__main__":
    run_bot()
