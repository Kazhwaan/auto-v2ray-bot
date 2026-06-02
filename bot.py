import requests
import os
import base64
import sys

# دریافت اطلاعات مخفی
raw_token = os.environ.get("BOT_TOKEN", "")
raw_channel = os.environ.get("CHANNEL_ID", "")

# 🧹 فیلتر جادویی: حذف تمام کاراکترهای نامرئی و غیرانگلیسی که موقع کپی کردن اضافه میشن
BOT_TOKEN = "".join(c for c in raw_token if c.isascii()).strip()
CHANNEL_ID = "".join(c for c in raw_channel if c.isascii()).strip()

SOURCE_URL = "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("ارور سیستم: توکن یا آیدی کانال خالی است!")
        sys.exit(1)

    try:
        response = requests.get(SOURCE_URL, timeout=15)
        if response.status_code != 200:
            print(f"ارور در دانلود کانفیگ‌ها. کد: {response.status_code}")
            sys.exit(1)
            
        decoded_data = base64.b64decode(response.text).decode('utf-8')
        configs = [line for line in decoded_data.splitlines() if line.strip()]
        
        if len(configs) == 0:
            print("منبع خالی بود. چیزی برای ارسال نیست.")
            sys.exit(0)
            
        top_configs = configs[:3]
        message = "🚀 **کانفیگ‌های جدید V2Ray:**\n\n"
        for conf in top_configs:
            message += f"`{conf}`\n\n"
        message += "💡 برای کپی روی کانفیگ کلیک کنید."

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        tg_res = requests.post(url, json=payload)
        
        if tg_res.status_code != 200:
            print(f"تلگرام پیام را رد کرد! دلیل ارور:\n{tg_res.text}")
            sys.exit(1)
            
        print("✅ پیام با موفقیت در کانال ارسال شد!")

    except Exception as e:
        print(f"ارور ناشناخته: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
