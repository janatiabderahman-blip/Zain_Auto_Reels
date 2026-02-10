import os
import subprocess
import sys
from pathlib import Path

def log_fix(msg): print(f"🔧 [AUTO-FIXER] {msg}", flush=True)

def repair_system():
    log_fix("Starting System Audit...")
    # 1. تنظيف الجذور من أي ملفات عالقة
    extensions = ['*.mp4', '*.tmp', 'raw*', 'final*']
    for ext in extensions:
        for file in Path(".").glob(ext):
            try:
                file.unlink()
            except: pass
    
    # 2. التأكد من تحديث المكتبات الأساسية
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "google-generativeai", "python-dotenv"], check=True)
    except Exception as e:
        log_fix(f"Repair Error: {e}")

if __name__ == "__main__":
    repair_system()
    log_fix("System is sanitized and ready.")
