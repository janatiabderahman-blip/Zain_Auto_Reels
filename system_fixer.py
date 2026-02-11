import os
import sys
import requests
import google.generativeai as genai
from moviepy.config import change_settings

def run_diagnostic():
    print("🚀 [System Fixer] Starting Deep Diagnostic...")
    print("-" * 50)

    # 1. فحص المتغيرات البيئية (Secrets)
    secrets = ["GEMINI_API_KEY", "PEXELS_API_KEY", "FB_PAGE_ID", "FB_PAGE_TOKEN"]
    missing = []
    for s in secrets:
        if not os.getenv(s):
            missing.append(s)
    
    if missing:
        print(f"❌ ERROR: Missing Secrets: {missing}")
    else:
        print("✅ SUCCESS: All Environment Secrets are loaded.")

    # 2. فحص محرك النصوص (ImageMagick)
    print("🔍 Checking ImageMagick Configuration...")
    try:
        # محاولة العثور على المسار الافتراضي في GitHub Actions
        im_path = "/usr/bin/convert"
        if os.path.exists(im_path):
            change_settings({"IMAGEMAGICK_BINARY": im_path})
            print(f"✅ SUCCESS: ImageMagick found at {im_path}")
        else:
            print("⚠️ WARNING: ImageMagick not found at default path. Text rendering might fail.")
    except Exception as e:
        print(f"❌ ERROR: ImageMagick config failed: {e}")

    # 3. فحص الاتصال بـ Gemini AI
    print("🔍 Testing Gemini AI Connection...")
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Test")
        if response.text:
            print("✅ SUCCESS: Gemini AI is responding correctly.")
    except Exception as e:
        print(f"❌ ERROR: Gemini AI Connection Failed: {e}")

    # 4. فحص صلاحية Meta API (Facebook)
    print("🔍 Checking Meta Graph API Token...")
    fb_id = os.getenv("FB_PAGE_ID")
    fb_token = os.getenv("FB_PAGE_TOKEN")
    if fb_id and fb_token:
        fb_url = f"https://graph.facebook.com/v19.0/{fb_id}?access_token={fb_token}"
        try:
            r = requests.get(fb_url).json()
            if "name" in r:
                print(f"✅ SUCCESS: Connected to Facebook Page: {r['name']}")
            else:
                print(f"❌ ERROR: Meta Token invalid or expired. Response: {r}")
        except Exception as e:
            print(f"❌ ERROR: Meta API Request failed: {e}")

    print("-" * 50)
    print("🛠️ Diagnostic Finished.")

if __name__ == "__main__":
    run_diagnostic()
