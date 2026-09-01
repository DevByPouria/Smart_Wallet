import pytesseract
from PIL import Image
import re
import io

# توی سرور حتماً باید Tesseract نصب باشه (برای Render توی Requirements.txt می‌نویسیم)
def extract_amount_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # تبدیل به سیاه و سفید برای دقت بهتر
        text = pytesseract.image_to_string(image, lang='fas')  # 'fas' برای فارسی
        # پیدا کردن اعداد فارسی یا انگلیسی توی متن
        numbers = re.findall(r'(\d{1,3}(?:[\,\.]\d{3})*|\d+)', text)
        if numbers:
            # آخرین عدد بزرگ رو به عنوان مبلغ در نظر می‌گیریم (معمولاً مبلغ کل)
            amount = numbers[-1].replace(',', '').replace('.', '')
            return int(amount)
        return None
    except Exception as e:
        print(f"OCR Error: {e}")
        return None