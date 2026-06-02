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
import traceback
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

def get_tester_location():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=3).json()
        cc = res.get("country", "US")
        flag = chr(ord(cc[0]) + 127397) + chr(ord(cc[1]) + 127397)
        return f"{cc} {flag}"
    except Exception:
        return "US 🇺🇸"

def tcp_ping(ip, port):
    if not ip or not port:
        return "🟡 نامشخص"
    try:
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            ip = socket.gethostbyname(ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        start = time.time()
        s.connect((ip, int(port)))
        end = time.time()
        s.close()
        ping_ms = int((end - start) * 1000)
        return f"🟢 متصل ({ping_ms}ms)"
    except Exception:
        return "🔴 تایم‌اوت"

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

def decode_base64(text):
    text = text.strip()
    missing_padding = len(text) % 4
    if missing_padding != 0:
        text += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except Exception:
        return ""

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
        else:
            b64_str = config_str[8:]
            missing_padding = len(b64_str) % 4
            if missing_padding != 0:
                b64_str += '=' * (4 - missing_padding)
            json_str = base64.b64decode(b64_str).decode('utf-8')
            data = json.loads(json_str)
            ip = data.get("add", "")
            port = data.get("port", "")
    except Exception:
        pass
    return protocol, name, ip, port

def run_bot():
    # بزرگترین لیست منابع فعال و قدرتمند
    SOURCES = [
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality",
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/vless",
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
        "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
        "https://raw.githubusercontent.com/w177140/v2rayN-configs/main/vless.txt",
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                text = response.text
                
                # استراتژی 1: جستجو در متن ساده
                configs_plain = re.findall(r'(vless://[^\s<>"\']+|trojan://[^\s<>"\']+|vmess://[^\s<>"\']+)', text)
                all_configs.extend(configs_plain)
                
                # استراتژی 2: جستجو در حالت کدگذاری شده (Base64)
                try:
                    decoded = decode_base64(text)
                    if decoded:
                        configs_b64 = re.findall(r'(vless://[^\s<>"\']+|trojan://[^\s<>"\']+|vmess://[^\s<>"\']+)', decoded)
                        all_configs.extend(configs_b64)
                except Exception:
                    pass
        except Exception:
            continue

    if not all_configs:
        send_msg("⚠️ <b>ربات:</b> هیچ کانفیگی در منابع یافت نشد یا سرورها مسدود هستند.")
        return

    # حذف تکراری‌ها و حفظ ترتیب (از آخر به اول برای دریافت جدیدترین‌ها)
    seen = set()
    unique = []
    for c in reversed(all_configs):
        if c not in seen:
            unique.append(c)
            seen.add(c)
            
    # اولویت شدید با VLESS و Reality
    def get_score(conf):
        conf_lower = conf.lower()
        score = 0
        if "reality" in conf_lower: score += 10
        if "vless://" in conf_lower: score += 5
        if "trojan://" in conf_lower: score += 2
        return score

    unique.sort(key=get_score, reverse=True)

    final_configs = []
    # فقط 30 تای اول رو تست میکنیم که گیت‌هاب خسته نشه
    for conf in unique[:30]:
        protocol, name, ip, port = parse_config_info(conf)
        ping_status = tcp_ping(ip, port)
        
        item = {
            "conf": conf,
            "protocol": protocol,
            "ip": ip,
            "ping": ping_status
        }
        
        if "متصل" in ping_status:
            final_configs.append(item)
            
        if len(final_configs) >= 3:
            break

    # اگر متصل پیدا نکرد، باز هم 3 تا میذاره که کانال خالی نمونه
    if len(final_configs) < 3:
        needed = 3 - len(final_configs)
        untested = [c for c in unique if c not in [f['conf'] for f in final_configs]]
        for conf in untested[:needed]:
            protocol, name, ip, port = parse_config_info(conf)
            final_configs.append({
                "conf": conf,
                "protocol": protocol,
                "ip": ip,
                "ping": "🔴 بررسی نشده (فایروال روشن)"
            })

    iran_time_str = get_iran_time()
    tester_loc = get_tester_location()

    for item in final_configs:
        real_location = get_real_location(item['ip'])
        
        safe_conf = html.escape(item['conf'])
        safe_loc = html.escape(real_location)
        
        message = f"""
🚀 <b>کانفیگ جدید و ضد فیلتر</b>

📍 <b>لوکیشن:</b> {safe_loc}
⚙️ <b>پروتکل:</b> {item['protocol']}
📡 <b>وضعیت سرور:</b> {item['ping']} (تست از {tester_loc})
⏰ <b>زمان استخراج:</b> {iran_time_str}

👇 <b>برای اتصال روی کادر زیر ضربه بزنید تا کپی شود:</b>

<code>{safe_conf}</code>

🆔 {CHANNEL_ID}
"""
        res = send_msg(message.strip())
        
        if res.status_code != 200:
            err = f"❌ <b>تلگرام اجازه ارسال یک کانفیگ را نداد! دلیل ارور:</b>\n\n<pre>{html.escape(res.text)}</pre>"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
                "chat_id": CHANNEL_ID,
                "text": err,
                "parse_mode": "HTML"
            })
            
        time.sleep(3)

if __name__ == "__main__":
    main()
