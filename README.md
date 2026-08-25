<div dir="rtl" align="right">

# ربات آب‌وهوای بندرخمیر

یک ربات تلگرامی فارسی برای دریافت وضعیت آب‌وهوای بندرخمیر، زمان‌های جزر و مد و معرفی کوتاه شهر خمیر.

## قابلیت‌ها

- نمایش دما، دمای احساسی، رطوبت، سرعت باد و وضعیت آسمان
- نمایش همه‌ی زمان‌های مد و جزر همان روز
- نمایش ارتفاع آب برای هر رخداد به واحد متر
- تبدیل زمان رخدادهای جزر و مد به وقت ایران
- منوی دکمه‌ای فارسی برای استفاده‌ی راحت در گوشی
- پیام خوش‌آمدگویی برای کاربران جدید
- دستور `/about` برای معرفی شهر بندرخمیر
- نمایش پیام در حال دریافت و پیام خطای قابل‌فهم
- پشتیبانی از HTTP و SOCKS5 proxy برای اتصال به سرویس‌ها

## دستورات ربات

| دستور | کاربرد |
| --- | --- |
| `/start` | نمایش پیام خوش‌آمدگویی و منوی اصلی |
| `/weather` | دریافت آب‌وهوای بندرخمیر |
| `/tides` | نمایش زمان‌های مد و جزر روز |
| `/all` | نمایش هم‌زمان آب‌وهوا و جزر و مد |
| `/about` | معرفی کوتاه شهر خمیر |

## پیش‌نیازها

- Python 3.10 یا بالاتر
- توکن ربات از [BotFather](https://t.me/BotFather)
- کلید API از [OpenWeather](https://openweathermap.org/api)
- کلید API از [Stormglass](https://stormglass.io/)

## نصب در ویندوز

ابتدا پروژه را دریافت و وارد پوشه‌ی آن شوید:

```powershell
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

ساخت محیط مجازی و نصب وابستگی‌ها:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## تنظیم فایل محیطی

فایل `.env.example` را با نام `.env` کپی کنید:

```powershell
Copy-Item .env.example .env
```

سپس `.env` را باز کنید و مقدارهای واقعی را قرار دهید:

```env
TELEGRAM_TOKEN=توکن_ربات_تلگرام
WEATHER_API_KEY=کلید_OpenWeather
STORMGLASS_API_KEY=کلید_Stormglass
TELEGRAM_PROXY=
```

اگر سرور شما بدون proxy به تلگرام و APIها وصل می‌شود، مقدار `TELEGRAM_PROXY` را خالی بگذارید. برای proxy نمونه:

```env
TELEGRAM_PROXY=socks5://IP:PORT
```

> فایل `.env` محرمانه است و نباید در GitHub آپلود شود. این فایل در `.gitignore` قرار گرفته است.

## اجرای ربات

```powershell
python bot.py
```

اگر چند نسخه‌ی Python روی سیستم دارید، از همان interpreterای استفاده کنید که وابستگی‌ها روی آن نصب شده‌اند:

```powershell
C:/Users/USERNAME/AppData/Local/Programs/Python/Python313/python.exe bot.py
```

## استقرار روی Railway

1. فایل‌های `bot.py`، `requirements.txt`، `.env.example`، `.gitignore` و `README.md` را در GitHub قرار دهید.
2. فایل `.env` را آپلود نکنید.
3. در Railway یک پروژه از مخزن GitHub بسازید.
4. در بخش **Variables** این متغیرها را اضافه کنید:

```env
TELEGRAM_TOKEN=توکن_جدید_ربات
WEATHER_API_KEY=کلید_OpenWeather
STORMGLASS_API_KEY=کلید_Stormglass
TELEGRAM_PROXY=
```

5. دستور اجرای سرویس را روی مقدار زیر قرار دهید:

```text
python bot.py
```

6. فقط یک نمونه از ربات را اجرا کنید؛ اجرای هم‌زمان روی کامپیوتر و Railway باعث خطای `Conflict` می‌شود.

## خطاهای رایج

### خطای `Conflict: terminated by other getUpdates request`

یعنی دو نسخه از ربات با یک توکن در حال اجرا هستند. نسخه‌ی اضافی را متوقف کنید و در Railway فقط یک Replica فعال نگه دارید.

### خطای `ModuleNotFoundError`

وابستگی‌ها را در همان محیط Pythonای نصب کنید که ربات را با آن اجرا می‌کنید:

```powershell
pip install -r requirements.txt
```

### خطای اتصال به تلگرام یا APIها

اتصال اینترنت و مقدار `TELEGRAM_PROXY` را بررسی کنید. اگر از SOCKS5 استفاده می‌کنید، proxy باید به شکل زیر باشد:

```text
socks5://IP:PORT
```

### تمام‌شدن سهمیه‌ی Stormglass

این خطا از محدودیت حساب Stormglass است و با کد ربات ارتباطی ندارد. برای جلوگیری از مصرف زیاد، در نسخه‌های بعدی می‌توان cache و محدودیت درخواست اضافه کرد.

## نکات امنیتی

- توکن تلگرام و کلیدهای API را داخل کد، GitHub یا README ننویسید.
- اگر secretها افشا شدند، آن‌ها را فوراً از BotFather و پنل سرویس‌ها تعویض کنید.
- برای GitHub فقط `.env.example` را منتشر کنید.
- متغیرهای محرمانه را در بخش Variables سرویس استقرار ذخیره کنید.

## ایده‌های توسعه‌ی آینده

- cache کردن پاسخ‌ها برای کاهش مصرف API
- انتخاب تاریخ برای پیش‌بینی جزر و مد روزهای آینده
- انتخاب شهر یا موقعیت مکانی توسط کاربر
- ثبت خطاها در log بدون نمایش جزئیات فنی به کاربر
- افزودن اعلان روزانه‌ی آب‌وهوا و جزر و مد
- افزودن تست خودکار برای توابع API

## مجوز

این پروژه برای استفاده و توسعه‌ی شخصی ساخته شده است. در صورت انتشار عمومی، می‌توانید یک فایل `LICENSE` مناسب به پروژه اضافه کنید.

</div>
