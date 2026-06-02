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

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    return requests.post(url, json=payload)

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("ارور: توکن یا آیدی کانال خالی است!")
        sys.exit(1)
        
    try:
        run_bot()
    except Exception as e:
        error_msg = f"❌ <b>ارور در سرور گیت‌هاب:</b>\n\n<pre>{html.escape(str(e))}</pre>"
        send_msg(error_msg)
        sys.exit(1)

def get_iran_time():
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(iran_tz).strftime("%Y/%m/%d - %H:%M:%S") + " (به وقت ایران)"

def get_real_location(ip):
    if not ip: 
        return "مخفی (پشت CDN) ☁️"
    try:
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            ip = socket.gethostbyname(ip)
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3).json()
        if "country" in res:
            cc = res["country"]
            flag = chr(ord(cc[0]) + 127397) + chr(ord(cc[1]) + 127397)
            city = res.get("city", "")
            if city:
                return f"{city}, {cc} {flag}"
            else:
                return f"{cc} {flag}"
    except Exception:
        pass
    return "نامشخص 🌍"

def tcp_ping(ip, port):
    if not ip or not port:
        return "🟡 وضعیت: مخفی (تست فقط در ایران)"
    try:
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            ip = socket.gethostbyname(ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        start = time.time()
        s.connect((ip, int(port)))
        end = time.time()
        s.close()
        ping_ms = int((end - start) * 1000)
        return f"🟢 متصل ({ping_ms}ms) - تست خارجی"
    except Exception:
        return "🔵 مسدود برای خارج (سالم در ایران)"

def parse_config_info(config_str):
    protocol = "نامشخص"
    name = "مخفی 🌍"
    ip = ""
    port = ""
    try:
        if config_str.startswith("vless://"):
            protocol = "VLESS 🛡️"
        elif config_str.startswith("trojan://"):
            protocol = "Trojan 🐎"
        elif config_str.startswith("vmess://"):
            protocol = "VMess 🪪"
            
        if "#" in config_str:
            name = urllib.parse.unquote(config_str.split("#")[1])
            
        if not config_str.startswith("vmess://"):
            match = re.search(r'://[^@]+@([^:]+):(\d+)', config_str)
            if match:
                ip, port = match.groups()
    except Exception:
        pass
    return protocol, name, ip, port

def safe_base64_decode(text):
    """رمزگشای وحشی: هرچی Base64 باشه رو به زور باز میکنه"""
    try:
        text = text.strip()
        text = re.sub(r'\s+', '', text)
        missing_padding = len(text) % 4
        if missing_padding != 0:
            text += '=' * (4 - missing_padding)
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return ""

def run_bot():
    # بزرگ‌ترین لیست منابعِ آپدیت‌شده در کل گیت‌هاب
    SOURCES = [
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality",
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/vless",
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
        "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
        "https://raw.githubusercontent.com/w177140/v2rayN-configs/main/vless.txt",
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity",
        "https://raw.githubusercontent.com/ts-sf/fly/main/v2",
        "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
        "https://raw.githubusercontent.com/Epodonnis/v2ray-configs/main/All_Configs_Sub.txt",
        "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                text = response.text
                
                # ۱. شکار مستقیم تو متن ساده
                configs_plain = re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+|vmess://[^\s<>]+)', text)
                all_configs.extend(configs_plain)
                
                # ۲. شکار تو متن‌های رمزگذاری شده (Base64)
                decoded_text = safe_base64_decode(text)
                if decoded_text:
                    configs_b64 = re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+|vmess://[^\s<>]+)', decoded_text)
                    all_configs.extend(configs_b64)
        except Exception:
            continue

    if not all_configs:
        send_msg("⚠️ <b>ربات:</b> متاسفانه تمام ۱۰ منبع اصلی مسدود یا خالی هستند! لطفاً بعداً تلاش کنید.")
        return

    # حذف تکراری‌ها و نگه‌داشتن جدیدترین‌ها
    seen = set()
    unique = []
    for c in reversed(all_configs):
        if c not in seen:
            unique.append(c)
            seen.add(c)
            
    # سیستم امتیازدهی به شدت حساس برای نت ایران
    def get_score(conf):
        conf_lower = conf.lower()
        score = 0
        # اگر کلماتی مثل mahsa یا اپراتورها تو اسمش بود رو هوا بزن!
        if "mahsa" in conf_lower: score += 50
        if "reality" in conf_lower: score += 20
        if "vless://" in conf_lower: score += 10
        if "mci" in conf_lower or "mtn" in conf_lower or "irancell" in conf_lower or "rightel" in conf_lower: score += 15
        if "vmess://" in conf_lower: score -= 5 # VMess رو کمتر دوست داریم چون تو ایران ضعیفه
        return score

    unique.sort(key=get_score, reverse=True)

    # انتخاب ۳ کانفیگ اول (که بالاترین امتیاز رو برای ایران دارن)
    final_configs = []
    for conf in unique[:3]:
        protocol, name, ip, port = parse_config_info(conf)
        ping_status = tcp_ping(ip, port)
        
        final_configs.append({
            "conf": conf,
            "protocol": protocol,
            "ip": ip,
            "name": name,
            "ping": ping_status
        })

    iran_time_str = get_iran_time()

    for item in final_configs:
        real_location = get_real_location(item['ip'])
        
        name_lower = item['name'].lower()
        if "mci" in name_lower or "mtn" in name_lower or "irancell" in name_lower or "mahsa" in name_lower:
            real_location = f"{real_location} ({item['name']})"
        
        safe_conf = html.escape(item['conf'])
        safe_loc = html.escape(real_location)
        
        message = f"""
🚀 <b>کانفیگ فوق‌سریع و اختصاصی</b>

📍 <b>لوکیشن:</b> {safe_loc}
⚙️ <b>پروتکل:</b> {item['protocol']}
📡 <b>وضعیت سرور:</b> {item['ping']}
⏰ <b>زمان استخراج:</b> {iran_time_str}

👇 <b>برای اتصال روی کادر زیر ضربه بزنید:</b>

<code>{safe_conf}</code>

🆔 {CHANNEL_ID}
"""
        res = send_msg(message.strip())
        
        if res.status_code != 200:
            err = f"❌ <b>تلگرام پیام را رد کرد! ارور:</b>\n\n<pre>{html.escape(res.text)}</pre>"
            send_msg(err)
            
        time.sleep(3)

if __name__ == "__main__":
    main()
