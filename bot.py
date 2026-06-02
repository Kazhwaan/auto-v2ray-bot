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

def safe_base64_decode(text):
    try:
        text = re.sub(r'\s+', '', text.strip())
        text += '=' * (len(text) % 4)
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return ""

def run_bot():
    # بهترین منابع استخراج کانفیگ‌های قدرتمند
    SOURCES = [
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality",
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
        "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
        "https://raw.githubusercontent.com/w177140/v2rayN-configs/main/vless.txt"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                # استخراج مستقیم
                all_configs.extend(re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+)', res.text))
                # استخراج از متن‌های کدگذاری شده
                decoded = safe_base64_decode(res.text)
                if decoded:
                    all_configs.extend(re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+)', decoded))
        except: continue

    if not all_configs:
        return send_msg("⚠️ <b>ربات:</b> متاسفانه تمام منابع گیت‌هاب مسدود هستند.")

    unique = list(dict.fromkeys(reversed(all_configs)))
    
    # اولویت‌بندی شدید برای نت ایران
    def get_score(conf):
        c = conf.lower()
        return (20 if "reality" in c else 0) + (15 if any(x in c for x in ["mci","mtn","irancell","mahsa"]) else 0) + (10 if "vless" in c else 0)

    unique.sort(key=get_score, reverse=True)

    # جدا کردن 15 کانفیگ برتر
    final_configs = unique[:15]
    
    # چسباندن تمام کانفیگ‌ها به هم با یک خط فاصله
    bulk_configs_text = "\n\n".join(final_configs)
    safe_bulk_configs = html.escape(bulk_configs_text)
    
    iran_time = get_iran_time()

    # ارسال یک پیام واحد و خفن به کانال
    msg = f"""
🚀 <b>بسته {len(final_configs)} تایی کانفیگ‌های داغ و ضد فیلتر</b>

✅ <b>بدون نیاز به لینک و بدون ارور آپدیت!</b>
این روش غیرقابل فیلتر است. تمام کانفیگ‌ها از سرورهای آزاد استخراج شده‌اند.

👇 <b>آموزش استفاده:</b>
۱. فقط کافیست روی کادر زیر <b>یک بار ضربه بزنید</b> تا کل ۱۵ کانفیگ کپی شوند.
۲. وارد برنامه هیدیفای (Hiddify) یا v2rayNG شوید.
۳. دکمه <b>+ (افزودن)</b> را زده و <b>Import from Clipboard (از کلیپ‌بورد)</b> را انتخاب کنید.

<code>{safe_bulk_configs}</code>

⏰ <b>زمان استخراج:</b> {iran_time}
🆔 {CHANNEL_ID}
"""
    res = send_msg(msg.strip())
    
    if res.status_code != 200:
        send_msg(f"❌ <b>تلگرام پیام را رد کرد! ارور:</b>\n<pre>{html.escape(res.text)}</pre>")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        sys.exit(1)
    try:
        run_bot()
    except Exception as e:
        send_msg(f"❌ <b>ارور سرور گیت‌هاب:</b>\n<pre>{html.escape(str(e))}</pre>")
        sys.exit(1)
