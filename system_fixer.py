import os, subprocess, sys
from pathlib import Path

def repair():
    print("🔧 Auto-Fixer: Auditing Environment...")
    # تنظيف أي بقايا من عمليات فاشلة
    for f in Path(".").glob("*.mp4"): f.unlink()
    # تحديث المكتبات لأحدث إصدار أمان
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "requests", "google-generativeai"], check=True)

if __name__ == "__main__":
    repair()
    print("✅ System Healthy.")
