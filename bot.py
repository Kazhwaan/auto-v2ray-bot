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
    except:
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
    except:
        return "🔴 تایم‌اوت"

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
