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
    # استخراج چند کانفیگ تکی داغ
    SOURCES = [
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality",
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                all_configs.extend(re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+)', res.text))
        except: continue

    unique = list(dict.fromkeys(reversed(all_configs)))
    final_configs = unique[:3] # ۳ تا کانفیگ داغ تکی

    iran_time = get_iran_time()

    # ۱. ارسال لینک‌های اشتراک جادویی (ترفند هیدیفای)
    sub_message = f"""
🌟 <b>لینک‌های اشتراک (سابسکریپشن) - آپدیت خودکار</b> 🌟

با کپی کردن لینک‌های زیر در هیدیفای (Hiddify) یا v2rayNG و زدن دکمه آپدیت، برنامه شما صدها کانفیگ را بررسی کرده و <b>سالم‌ترین‌های مخصوص نت شما</b> را جدا می‌کند!

👇 <b>لینک اشتراک VLESS (پیشنهادی):</b>
<code>https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt</code>

👇 <b>لینک اشتراک Reality (مخصوص همراه اول و مخابرات):</b>
<code>https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality</code>

👇 <b>لینک اشتراک ترکیبی (مخصوص ایرانسل):</b>
<code>https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity</code>

⏰ <b>زمان آپدیت:</b> {iran_time}
🆔 {CHANNEL_ID}
"""
    send_msg(sub_message.strip())
    time.sleep(3)

    # ۲. ارسال کانفیگ‌های تکی
    for conf in final_configs:
        protocol, name = parse_config_info(conf)
        safe_conf = html.escape(conf)
        safe_name = html.escape(name)
        
        msg = f"""
🚀 <b>کانفیگ تکی جدید</b>

📍 <b>نام:</b> {safe_name}
⚙️ <b>پروتکل:</b> {protocol}

💡 <i>در صورت عدم اتصال، حتماً گزینه <b>Fragment (فرگمنت)</b> را در برنامه خود روشن کنید.</i>

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
