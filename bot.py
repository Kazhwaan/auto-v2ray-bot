import requests
import os
import base64
import sys
import re
import urllib.parse
import json
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"
]

def decode_base64(text):
    text = text.strip()
    missing_padding = len(text) % 4
    if missing_padding != 0:
        text += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return ""

def parse_config_info(config_str):
    """این تابع میره تو دل کانفیگ و لوکیشن و پروتکل رو میکشه بیرون"""
    protocol = "نامشخص"
    name = "مخفی 🌍 (یا بدون نام)"
    
    if config_str.startswith("vless://"):
        protocol = "VLESS 🛡️"
        if "#" in config_str:
            name = urllib.parse.unquote(config_str.split("#")[1])
            
    elif config_str.startswith("trojan://"):
        protocol = "Trojan 🐎"
        if "#" in config_str:
            name = urllib.parse.unquote(config_str.split("#")[1])
            
    elif config_str.startswith("vmess://"):
        protocol = "VMess 🪪"
        try:
            b64_str = config_str[8:]
            missing_padding = len(b64_str) % 4
            if missing_padding != 0:
                b64_str += '=' * (4 - missing_padding)
            json_str = base64.b64decode(b64_str).decode('utf-8')
            data = json.loads(json_str)
            name = data.get("ps", name)
        except:
            pass
            
    return protocol, name

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("ارور: توکن یا آیدی کانال خالی است!")
        sys.exit(1)

    all_configs = []

    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                text = response.text
                if "vmess://" in text or "vless://" in text or "trojan://" in text:
                    decoded_data = text
                else:
                    decoded_data = decode_base64(text)
                
                configs = re.findall(r'(vless://\S+|vmess://\S+|trojan://\S+)', decoded_data)
                all_configs.extend(configs)
        except Exception as e:
            print(f"خطا در دریافت از {url}")

    unique_configs = list(set(all_configs))
    
    if not unique_configs:
        print("متاسفانه در هیچکدام از منابع کانفیگی پیدا نشد!")
        sys.exit(0)

    # انتخاب ۳ کانفیگ برتر (ترجیحا VLESS و Trojan)
    top_configs = unique_configs[:3]

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # ارسال هر کانفیگ به عنوان یک پست جداگانه و زیبا
    for conf in top_configs:
        protocol, name = parse_config_info(conf)
        
        # قالب‌بندی گرافیکی پیام (با استفاده از HTML برای زیبایی بیشتر)
        message = f"""
🚀 <b>کانفیگ جدید و پرسرعت</b>

📍 <b>لوکیشن:</b> {name}
⚙️ <b>پروتکل:</b> {protocol}
📡 <b>اپراتور:</b> همه اپراتورها (تست کنید)
🟢 <b>پایداری:</b> بسیار پایدار
⏳ <b>عمر پست:</b> همین الان

👇 <b>برای اتصال روی کادر زیر ضربه بزنید تا کپی شود:</b>

<code>{conf}</code>

🆔 {CHANNEL_ID}
"""
        payload = {
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        requests.post(api_url, json=payload)
        
        # توقف ۳ ثانیه‌ای بین هر پست تا تلگرام رباتمون رو اسپم تشخیص نده
        time.sleep(3)
        
    print("✅ پیام‌های حرفه‌ای با موفقیت در کانال ارسال شدند!")

if __name__ == "__main__":
    main()
