import requests
import os
import base64

# دریافت اطلاعات مخفی از تنظیمات گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# آدرس یک مخزن معروف که کانفیگ‌های روزانه رو جمع‌آوری می‌کنه
SOURCE_URL = "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt"

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

def main():
    try:
        # دانلود کانفیگ‌ها از اینترنت
        response = requests.get(SOURCE_URL)
        if response.status_code == 200:
            # دیکود کردن و مرتب‌سازی
            raw_data = response.text
            decoded_data = base64.b64decode(raw_data).decode('utf-8')
            configs = decoded_data.splitlines()
            
            # انتخاب ۳ کانفیگ اول برای جلوگیری از شلوغ شدن کانال
            top_configs = configs[:3] 
            
            message = "🚀 **کانفیگ‌های جدید V2Ray:**\n\n"
            for conf in top_configs:
                message += f"`{conf}`\n\n"
            
            message += "💡 برای کپی روی کانفیگ کلیک کنید."
            
            send_to_telegram(message)
            print("کانفیگ‌ها با موفقیت به کانال ارسال شدند!")
        else:
            print("خطا در دریافت اطلاعات از منبع.")
    except Exception as e:
        print(f"خطای سیستمی: {e}")

if __name__ == "__main__":
    main()
