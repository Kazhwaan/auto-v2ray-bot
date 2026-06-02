import requests
import os
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
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    return requests.post(url, json=payload)

def get_iran_time():
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    return datetime.now(iran_tz).strftime("%Y/%m/%d - %H:%M:%S")

def parse_config_info(config_str):
    protocol, name = "نامشخص", "کانفیگ 🌍"
    try:
        if config_str.startswith("vless://"): protocol = "VLESS 🛡️"
        elif config_str.startswith("trojan://"): protocol = "Trojan 🐎"
        if "#" in config_str: name = urllib.parse.unquote(config_str.split("#")[1])
    except: pass
    return protocol, name

def run_bot():
    SOURCES = [
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix",
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                all_configs.extend(re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+)', res.text))
        except: continue

    unique = list(dict.fromkeys(reversed(all_configs)))
    final_configs = unique[:3] 

    iran_time = get_iran_time()

    # پیام اشتراک با پروکسی جدید (ghp.ci) و بک‌آپ مستقیم
    sub_message = f"""
🌟 <b>لینک‌های اشتراک (سابسکریپشن) - آپدیت خودکار</b> 🌟

لینک‌های زیر را در هیدیفای (Hiddify) یا v2rayNG کپی کرده و آپدیت کنید تا صدها کانفیگ دریافت کنید.

🟢 <b>لینک‌های ضد فیلتر (آپدیت بدون نیاز به VPN):</b>
<code>https://ghp.ci/https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt</code>

<code>https://ghp.ci/https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix</code>

---
🔴 <b>لینک‌های مستقیم (اگر لینک‌های بالا کار نکردند، برای آپدیت این لینک‌ها باید ابتدا یک فیلترشکن موقت روشن کنید):</b>
<code>https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt</code>

<code>https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix</code>

⏰ <b>زمان آپدیت:</b> {iran_time}
🆔 {CHANNEL_ID}
"""
    send_msg(sub_message.strip())
    time.sleep(3)

    # ارسال کانفیگ‌های تکی
    for conf in final_configs:
        protocol, name = parse_config_info(conf)
        safe_conf = html.escape(conf)
        safe_name = html.escape(name)
        
        msg = f"""
🚀 <b>کانفیگ تکی جدید</b>

📍 <b>نام:</b> {safe_name}
⚙️ <b>پروتکل:</b> {protocol}

💡 <i>در صورت عدم اتصال، حتماً گزینه <b>Fragment (فرگمنت)</b> را روشن کنید.</i>

👇 <b>برای اتصال ضربه بزنید:</b>

<code>{safe_conf}</code>

🆔 {CHANNEL_ID}
"""
        send_msg(msg.strip())
        time.sleep(2)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        sys.exit(1)
    try:
        run_bot()
    except Exception as e:
        send_msg(f"❌ <b>ارور:</b>\n<pre>{html.escape(str(e))}</pre>")
        sys.exit(1)
