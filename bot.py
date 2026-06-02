import requests
import os
import base64
import sys
import re
import urllib.parse
import json
import time
import socket
import html
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()

# منابع اختصاصی فقط برای VLESS و Reality (مخصوص فیلترینگ سختگیرانه ایران)
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity"
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
        # اگر آی‌پی دامنه بود اول تبدیلش میکنیم
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            try:
                ip = socket.gethostbyname(ip)
            except:
                return "🔴 تایم‌اوت"
                
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        start = time.time()
        s.connect((ip, int(port)))
        end = time.time()
        s.close()
        ping_ms = int((end - start) * 1000)
        return f"🟢 متصل ({ping_ms}ms)"
    except:
        return "🔴 تایم‌اوت"

def get_real_location(ip):
    """رفع مشکل لوکیشن EbraSha: اگر آی‌پی مخفی بود دیگه اسم سازنده رو چاپ نمیکنه"""
    if not ip:
        return "مخفی (پشت CDN) ☁️"
    try:
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            try:
                ip = socket.gethostbyname(ip)
            except:
                return "مخفی (دامنه) 🌐"
                
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
    return "نامشخص 🌍"

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
                
                # فقط VLESS و Trojan رو استخراج میکنیم (VMess کلا از رده خارج شد)
                configs = re.findall(r'(vless://\S+|trojan://\S+)', decoded_data)
                all_configs.extend(configs)
        except Exception as e:
            pass

    seen = set()
    unique_configs = []
    for conf in reversed(all_configs):
        if conf not in seen:
            unique_configs.append(conf)
            seen.add(conf)
            
    if not unique_configs:
        print("ارور: تمام منابع خالی یا از دسترس خارج شده‌اند!")
        sys.exit(1)

    final_configs = []
    untested_configs = []
    
    for conf in unique_configs:
        protocol, name, ip, port = parse_config_info(conf)
        ping_status = tcp_ping(ip, port)
        
        item = {
            "conf": conf,
            "protocol": protocol,
            "ip": ip,
            "ping": ping_status
        }
        
        # شکار ویژه: اولویت شدید با کانفیگ‌های Reality که تو ایران عالی کار میکنن
        if "متصل" in ping_status:
            if "reality" in conf.lower():
                final_configs.insert(0, item) # میذارتش اول لیست
            else:
                final_configs.append(item)
        else:
            untested_configs.append(item)
            
        if len(final_configs) >= 3:
            break

    if len(final_configs) < 3:
        needed = 3 - len(final_configs)
        final_configs.extend(untested_configs[:needed])

    if not final_configs:
        sys.exit(1)

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    iran_time_str = get_iran_time()
    
    # برای اینکه تو ایران وصل بشن، ۳ تا کانفیگ رو می‌فرستیم
    for item in final_configs[:3]:
        # اصلاح لوکیشن با استفاده از تابع جدید
        real_location = get_real_location(item['ip'])
        
        safe_conf = html.escape(item['conf'])
