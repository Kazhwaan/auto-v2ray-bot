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

def get_tester_location():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5).json()
        country_code = res.get("country", "US")
        country_map = {
            "US": "آمریکا 🇺🇸", "NL": "هلند 🇳🇱", "DE": "آلمان 🇩🇪", 
            "GB": "انگلیس 🇬🇧", "FR": "فرانسه 🇫🇷", "FI": "فنلاند 🇫🇮"
        }
        return country_map.get(country_code, f"سرور خارجی ({country_code})")
    except:
        return "سرور گیت‌هاب"

def get_iran_time():
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(iran_tz).strftime("%Y/%m/%d - %H:%M:%S") + " (به وقت ایران)"

def tcp_ping(ip, port):
    if not ip or not port:
        return "🟡 نامشخص"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        start = time.time()
        s.connect((ip, int(port)))
        end = time.time()
        s.close()
        ping_ms = int((end - start) * 1000)
        return f"🟢 متصل ({ping_ms}ms)"
    except:
        return "🔴 تایم‌اوت (احتمالاً مسدود برای سرورهای خارجی)"

def get_real_location(ip, original_name):
    clean_name = re.sub(r'[^\w\s\-\.]', '', original_name).strip()
    if not clean_name:
        clean_name = "سرور ناشناس"

    if not ip:
        return f"{clean_name} 🌍"

    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=4).json()
        if "country" in res:
            cc = res["country"]
            flag = chr(ord(cc[0]) + 127397) + chr(ord(cc[1]) + 127397)
            city = res.get("city", "")
            if city:
                return f"{city}, {cc} {flag}"
            else:
                return f"{cc} {flag}"
    except:
        pass
    return f"{clean_name} 🌍"

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

    tester_loc = get_tester_location()

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
            pass

    unique_configs = list(set(all_configs))
    if not unique_configs:
        print("منبع خالی است.")
        sys.exit(0)

    # جدا کردن کانفیگ‌های تست شده و تست نشده
    final_configs = []
    untested_configs = []
    
    for conf in unique_configs:
        protocol, name, ip, port = parse_config_info(conf)
        ping_status = tcp_ping(ip, port)
        
        item = {
            "conf": conf,
            "protocol": protocol,
            "name": name,
            "ip": ip,
            "ping": ping_status
        }
        
        if "متصل" in ping_status:
            final_configs.append(item)
        else:
            untested_configs.append(item)
            
        if len(final_configs) >= 3:
            break

    # ترفند طلایی: اگر کمتر از 3 کانفیگ متصل پیدا کردیم، بقیه رو از همون لیست تایم‌اوت شده‌ها برمیداریم
    if len(final_configs) < 3:
        needed = 3 - len(final_configs)
        final_configs.extend(untested_configs[:needed])

    if not final_configs:
        print("هیچ کانفیگی برای ارسال پیدا نشد.")
        sys.exit(1)

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    iran_time_str = get_iran_time()
    
    for item in final_configs:
        real_location = get_real_location(item['ip'], item['name'])
        
        message = f"""
🚀 <b>کانفیگ جدید و پرسرعت</b>

📍 <b>لوکیشن:</b> {real_location}
⚙️ <b>پروتکل:</b> {item['protocol']}
📡 <b>وضعیت سرور:</b> {item['ping']} (تست از {tester_loc})
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
        
    print("✅ ارسال موفقیت‌آمیز بود!")

if __name__ == "__main__":
    main()
