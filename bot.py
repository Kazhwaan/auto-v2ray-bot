import requests
import os
import base64
import sys
import re
import urllib.parse
import json
import time
import socket
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"
]

def get_iran_time():
    """محاسبه دقیق ساعت و تاریخ ایران"""
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(iran_tz).strftime("%Y/%m/%d - %H:%M:%S")

def tcp_ping(ip, port):
    """تست زنده بودن سرور و گرفتن پینگ واقعی"""
    if not ip or not port:
        return "🟡 نامشخص"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0) # فقط ۲ ثانیه منتظر جواب میمونه
        start = time.time()
        s.connect((ip, int(port)))
        end = time.time()
        s.close()
        ping_ms = int((end - start) * 1000)
        return f"🟢 متصل ({ping_ms}ms)"
    except:
        return "🔴 تایم‌اوت (سرور خاموش)"

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
    """استخراج پروتکل، اسم، آی‌پی و پورت برای تست"""
    protocol = "نامشخص"
    name = "مخفی 🌍"
    ip = ""
    port = ""
    
    try:
        if config_str.startswith("vless://"):
            protocol = "VLESS 🛡️"
            if "#" in config_str:
                name = urllib.parse.unquote(config_str.split("#")[1])
            match = re.search(r'://[^@]+@([^:]+):(\d+)', config_str)
            if match:
                ip, port = match.groups()
                
        elif config_str.startswith("trojan://"):
            protocol = "Trojan 🐎"
            if "#" in config_str:
                name = urllib.parse.unquote(config_str.split("#")[1])
            match = re.search(r'://[^@]+@([^:]+):(\d+)', config_str)
            if match:
                ip, port = match.groups()
                
        elif config_str.startswith("vmess://"):
            protocol = "VMess 🪪"
            b64_str = config_str[8:]
            missing_padding = len(b64_str) % 4
            if missing_padding != 0:
                b64_str += '=' * (4 - missing_padding)
            json_str = base64.b64decode(b64_str).decode('utf-8')
            data = json.loads(json_str)
            name = data.get("ps", name)
            ip = data.get("add", "")
            port = data.get("port", "")
    except:
        pass
            
    return protocol, name, ip, port

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

    # سیستم هوشمند: تست کانفیگ‌ها و جدا کردن فقط ۳ عدد کانفیگ سالم
    valid_configs = []
    print("در حال تست پینگ کانفیگ‌ها...")
    
    for conf in unique_configs:
        protocol, name, ip, port = parse_config_info(conf)
        ping_status = tcp_ping(ip, port)
        
        # اگر سرور وصل شد، اونو به لیست ارسال اضافه کن
        if "متصل" in ping_status:
            valid_configs.append({
                "conf": conf,
                "protocol": protocol,
                "name": name,
                "ping": ping_status
            })
        
        # به محض اینکه ۳ تا سالم پیدا کردیم، دیگه بقیه رو تست نکن
        if len(valid_configs) >= 3:
            break

    if not valid_configs:
        print("هیچ کانفیگ سالمی (تست شده) پیدا نشد. ربات خاموش می‌شود.")
        sys.exit(0)

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    iran_time_str = get_iran_time()
    
    for item in valid_configs:
        message = f"""
🚀 <b>کانفیگ جدید و پرسرعت</b>

📍 <b>لوکیشن:</b> {item['name']}
⚙️ <b>پروتکل:</b> {item['protocol']}
📡 <b>وضعیت سرور:</b> {item['ping']}
⏰ <b>زمان استخراج:</b> {iran_time_str}

👇 <b>برای اتصال روی کادر زیر ضربه بزنید تا کپی شود:</b>

<code>{item['conf']}</code>

🆔 {CHANNEL_ID}
"""
        payload = {
            "chat_id": CHANNEL_ID,
            "text": message.strip(),
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        requests.post(api_url, json=payload)
        time.sleep(3)
        
    print("✅ پیام‌های تست‌شده و حرفه‌ای با موفقیت ارسال شدند!")

if __name__ == "__main__":
    main()
