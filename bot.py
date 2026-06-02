import requests
import os
import base64
import sys
import re
import traceback

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()

SOURCE_URL = "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("ارور: توکن یا آیدی کانال خالی است!")
        sys.exit(1)

    try:
        response = requests.get(SOURCE_URL, timeout=15)
        if response.status_code != 200:
            print("ارور در دریافت کانفیگ‌ها از منبع.")
            sys.exit(1)
            
        # 🧹 صافی جادویی: حذف تمام کاراکترهای مزاحم و غیرمجاز از فایلی که دانلود کردیم
        raw_text = response.text
        clean_b64 = re.sub(r'[^A-Za-z0-9+/=]', '', raw_text)
        
        # حالا با خیال راحت رمزگشایی می‌کنیم
        decoded_bytes = base64.b64decode(clean_b64)
        decoded_data = decoded_bytes.decode('utf-8', errors='ignore')
        
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
            print(f"تلگرام پیام را رد کرد! دلیل:\n{tg_res.text}")
            sys.exit(1)
            
        print("✅ پیام با موفقیت در کانال ارسال شد!")

    except Exception as e:
        print(f"ارور ناشناخته:\n")
        traceback.print_exc() # این خط دقیقا میگه کدوم خط از کد ارور داده
        sys.exit(1)

if __name__ == "__main__":
    main()
