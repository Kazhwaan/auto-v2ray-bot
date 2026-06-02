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
    # سورس‌های مادر که خود هیدیفای و مهسا ازشون تغذیه می‌کنن
    SOURCES = [
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality",
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity"
    ]
    
    all_configs = []
    for url in SOURCES:
        try:
            # فقط دانلود سریع، بدون معطلی
            res = requests.get(url, timeout=7)
            if res.status_code == 200:
                # شکار کانفیگ‌ها
                all_configs.extend(re.findall(r'(vless://[^\s<>]+|trojan://[^\s<>]+)', res.text))
        except:
            continue

    if not all_configs:
        send_msg("⚠️ <b>اخطار:</b> نتوانستم به منابع گیت‌هاب متصل شوم. لطفا لینک‌های اشتراک را دستی در هیدیفای آپدیت کنید.")
        return

    # حذف تکراری‌ها
    unique = list(dict.fromkeys(all_configs))
    
    # برداشتن 10 تای آخر (جدیدترین‌هایی که همین الان ساخته شدن)
    final_configs = unique[-10:]
    final_configs.reverse()
    
    # چسباندن کانفیگ‌ها به هم
    bulk_text = "\n\n".join(final_configs)
    safe_bulk = html.escape(bulk_text)
    
    # محاسبه زمان
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    iran_time = datetime.now(iran_tz).strftime("%Y/%m/%d - %H:%M:%S")

    msg = f"""
🔥 <b>بسته ۱۰ تایی کانفیگ‌های داغ (سورس Mahsa و Hiddify)</b> 🔥

💡 <b>راز اتصال ۱۰۰٪ (ترفند هیدیفای):</b>
اگر می‌خواهید این کانفیگ‌ها مثل بمب کار کنند، باید در برنامه Hiddify تیک <b>Fragment</b> را روشن کنید. هیدیفای این کانفیگ‌ها را با شبکه WARP ترکیب می‌کند تا فیلترینگ دور زده شود.

👇 <b>یک‌بار روی کادر زیر ضربه بزنید تا کل ۱۰ کانفیگ کپی شوند، سپس در هیدیفای + را بزنید:</b>

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
        send_msg(f"❌ <b>ارور کرش ربات:</b>\n<pre>{html.escape(str(e))}</pre>")
        sys.exit(1)
