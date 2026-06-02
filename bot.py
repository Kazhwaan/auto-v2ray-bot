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
        sys.exit(1)
    try:
        run_bot()
    except Exception as e:
        send_msg(f"❌ <b>ارور سرور:</b>\n<pre>{html.escape(str(e))}</pre>")
        sys.exit(1)

def get_iran_time():
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(iran_tz).strftime("%Y/%m/%d - %H:%M:%S")

def get_real_location(ip):
    if not ip: return "مخفی (پشت CDN) ☁️"
    try:
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            ip = socket.gethostbyname(ip)
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3).json()
        if "country" in res:
            cc = res["country"]
            flag = chr(ord(cc[0]) + 127397) + chr(ord(cc[1]) + 127397)
            city = res.get("city", "")
            return f"{city}, {cc} {flag}" if city else f"{cc} {flag}"
    except:
        pass
    return "نامشخص 🌍"

def tcp_ping(ip, port):
    if not ip or not port: return "🟡 وضعیت: مخفی"
    try:
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip): ip = socket.gethostbyname(ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        start = time.time()
        s.connect((ip, int(port)))
        end = time.time()
        s.close()
        return f"🟢 متصل ({int((end - start) * 1000)}ms)"
    except:
        return "🔵 فیلترشده (نیازمند فرگمنت یا آی‌پی تمیز)"

def parse_config_info(config_str):
    protocol, name, ip, port = "نامشخص", "مخفی 🌍", "", ""
    try:
        if config_str.startswith("vless://"): protocol = "VLESS 🛡"
        elif config_str.startswith("trojan://"): protocol = "Trojan 🐎"
        
        if "#" in config_str: name = urllib.parse.unquote(config_str.split("#")[1])
        
        match = re.search(r'://[^@]+@([^:]+):(\d+)', config_str)
        if match: ip, port = match.groups()
    except:
        pass
    return protocol, name, ip, port

def safe_base64_decode(text):
    try:
        text = re.sub(r'\s+', '', text.strip())
        text += '=' * (len(text) % 4)
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return ""

def run_bot():
    SOURCES = [
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/vless",
        "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                all_configs.extend(re.findall(r'(vless://[^\s<>]+)', res.text))
                decoded = safe_base64_decode(res.text)
                if decoded: all_configs.extend(re.findall(r'(vless://[^\s<>]+)', decoded))
        except: continue

    if not all_configs: return send_msg("⚠️ <b>ربات:</b> تمام منابع مسدود هستند.")

    unique = list(dict.fromkeys(reversed(all_configs)))
    
    # اولویت دادن به کانفیگ‌های کلاودفلر (WS) برای عملکرد شبیه به هیدیفای
    def get_score(conf):
        c = conf.lower()
        score = 0
        if "type=ws" in c: score += 50
        if "worker" in c or "pages" in c: score += 30
        if "reality" in c: score -= 10 
        return score

    unique.sort(key=get_score, reverse=True)
    
    final_configs = []
    for conf in unique[:50]:
        protocol, name, ip, port = parse_config_info(conf)
        ping = tcp_ping(ip, port)
        # فقط اونایی که پینگ میدن رو جدا می‌کنه
        if "متصل" in ping: 
            final_configs.append({"conf": conf, "protocol": protocol, "ip": ip, "name": name, "ping": ping})
        if len(final_configs) >= 5: break

    iran_time = get_iran_time()

    for item in final_configs:
        loc = html.escape(get_real_location(item['ip']))
        conf_safe = html.escape(item['conf'])
        
        msg = f"""
☁️ <b>کانفیگ جدید VLESS (نسخه Cloudflare/WS)</b>

📍 <b>لوکیشن:</b> {loc}
⚙️ <b>پروتکل:</b> {item['protocol']}
⏰ <b>آپدیت:</b> {iran_time}

💡 <i>این کانفیگ‌ها از نوع WS هستند. برای عملکرد بهتر در هیدیفای، از بخش تنظیمات پیشرفته، <b>«آی‌پی تمیز کلاودفلر (Clean IP)»</b> را روی آن‌ها اعمال کنید.</i>

👇 <b>برای اتصال ضربه بزنید:</b>

<code>{conf_safe}</code>

🆔 {CHANNEL_ID}
"""
        send_msg(msg.strip())
        time.sleep(3)

if __name__ == "__main__":
    main()
