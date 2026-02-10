import os
import time
import requests

class GeminiRoot:
    def __init__(self, token, page_id):
        self.token = token
        self.page_id = page_id
        self.log_prefix = "🤖 [GEMINI-CORE-SERVER]"

    def verify_status(self, video_id):
        """فحص حالة الفيديو في خوادم Meta ومنع الاستعجال"""
        url = f"https://graph.facebook.com/v19.0/{video_id}"
        params = {'fields': 'status', 'access_token': self.token}
        
        print(f"{self.log_prefix} Waiting for Meta to process the binary stream...")
        for i in range(20):  # محاولة الفحص لمدة 10 دقائق
            try:
                res = requests.get(url, params=params).json()
                status = res.get('status', {}).get('video_status')
                
                if status == 'ready':
                    print(f"{self.log_prefix} ✅ Video is READY. Proceeding to public launch.")
                    return True
                elif status in ['deleted', 'error']:
                    print(f"{self.log_prefix} ❌ Meta rejected the file. Check resolution.")
                    return False
                
                print(f"{self.log_prefix} Current Status: {status} (Check #{i+1})...")
                time.sleep(30)
            except:
                time.sleep(10)
        return False

    def final_publish(self, video_id, description):
        """الأمر النهائي للنشر العلني (Published)"""
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/video_reels"
        data = {
            'upload_phase': 'finish',
            'video_id': video_id,
            'description': description,
            'video_state': 'PUBLISHED',
            'access_token': self.token
        }
        return requests.post(url, data=data).json()
