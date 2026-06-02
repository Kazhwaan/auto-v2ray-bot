import requests
import os
import base64
import sys
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()

# 🔥 پیشنهاد عالی خودت: استفاده از بهترین و جدیدترین منابع به جای یک منبع
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"
]

def decode_base64(text):
    text = text.strip()
    # حل مشکل ریاضی Base64 (همون اروری که اعصابت رو خرد کرد)
    missing_padding = len(text) % 4
    if missing_padding != 0:
        text += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return ""

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("ارور: توکن یا آیدی کانال خالی است!")
        sys.exit(1)

    all_configs = []

    # گشتن در تمام منابع یکی پس از دیگری
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                text = response.text
                
                # بررسی اینکه آیا متن رمزنگاری شده است یا نه
                if "vmess://" in text or "vless://" in text or "trojan://" in text:
                    decoded_data = text
                else:
                    decoded_data = decode_base64(text)
                
                # شکار کانفیگ‌ها با استفاده از الگو (Regex)
                configs = re.findall(r'(vless://\S+|vmess://\S+|trojan://\S+)', decoded_data)
                all_configs.extend(configs)
        except Exception as e:
            print(f"خطا در دریافت از {url}: {e}")

    # حذف کانفیگ‌های تکراری
    unique_configs = list(set(all_configs))
    
    if not unique_configs:
        print("متاسفانه در هیچکدام از منابع کانفیگی پیدا نشد!")
        sys.exit(0)

    # انتخاب ۳ کانفیگ از لیست (می‌تونی این عدد رو تغییر بدی)
    top_configs = unique_configs[:3]

    message = "🚀 **جدیدترین کانفیگ‌های V2Ray:**\n\n"
    for conf in top_configs:
        message += f"`{conf}`\n\n"
    message += "💡 برای کپی روی کانفیگ کلیک کنید."

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    tg_res = requests.post(api_url, json=payload)
    
    if tg_res.status_code != 200:
        print(f"تلگرام پیام را رد کرد!\n{tg_res.text}")
        sys.exit(1)
        
    print("✅ پیام با موفقیت در کانال ارسال شد!")

if __name__ == "__main__":
    main()
