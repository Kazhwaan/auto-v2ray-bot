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
                
        elif
