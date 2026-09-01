import requests
import json

def get_gold_price():
    url = "https://www.tgju.org/price-chart/geram18"  # قیمت گرم طلا
    try:
        response = requests.get(url)
        # سایت tgju داده‌ها رو توی یه تگ خاص داره، این یه روش سریع و خرابکاریه!
        # برای سادگی، از API غیررسمی استفاده می‌کنیم (برای شروع)
        # بهتره از کتابخونه‌ی `tgju-api` استفاده کنی
        return 0  # فعلاً یه مقدار تستی
    except:
        return None

# توی نسخه نهایی، یه دیکشنری توی مموری می‌ذاریم که قیمت قبلی رو نگه داره و مقایسه کنه.