import requests
import os
import re
import html
import sys
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()

def send_msg(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
        json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    )

def run_bot():
    # سورس‌های دائمی و سنگین که هیچ‌وقت آدرسشون عوض نمی‌شه
    SOURCES = [
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                # جمع‌آوری مستقیم پروتکل‌های پرسرعت
                all_configs.extend(re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+)', res.text))
        except:
            continue

    if not all_configs:
        send_msg("⚠️ منابع موقتاً خالی هستند.")
        return

    # حذف تکراری‌ها
    unique = list(dict.fromkeys(all_configs))
    
    # برداشتن ۱۰ کانفیگ داغ و تازه
    final_configs = unique[:10]
    
    bulk_text = "\n\n".join(final_configs)
    safe_bulk = html.escape(bulk_text)
    
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    iran_time = datetime.now(iran_tz).strftime("%Y/%m/%d - %H:%M:%S")

    msg = f"""
🔥 <b>بسته ۱۰ تایی کانفیگ‌های جدید و پرسرعت VLESS</b> 🔥

💡 <b>آموزش اتصال سریع در ویندوز و گوشی:</b>
کافیست روی کادر زیر <b>یک‌بار ضربه بزنید</b> تا کل ۱۰ کانفیگ کپی شوند، سپس در برنامه Hiddify یا v2rayNG دکمه <b>+ (کلیپ‌بورد)</b> را بزنید. حتماً تیک <b>Fragment</b> را در تنظیمات برنامه روشن کنید.

<code>{safe_bulk}</code>

⏰ <b>زمان استخراج:</b> {iran_time}
🆔 {CHANNEL_ID}
"""
    send_msg(msg.strip())

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        sys.exit(1)
    try:
        run_bot()
    except Exception as e:
        send_msg(f"❌ ارور: {html.escape(str(e))}")
        sys.exit(1)
