import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import httpx
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY", "")

# آدرس پروکسی را در متغیر محیطی TELEGRAM_PROXY قرار دهید؛ مقدار خالی یعنی بدون پروکسی.
PROXY_URL = os.getenv("TELEGRAM_PROXY", "")

LAT = 27.28
LON = 56.36
TIDE_TIMEZONE = ZoneInfo("Asia/Tehran")


def create_api_client():
    options = {"proxy": PROXY_URL} if PROXY_URL else {}
    return httpx.AsyncClient(timeout=20, **options)


async def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
    try:
        async with create_api_client() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            description = data['weather'][0]['description']
            
            return f"""🌤 وضعیت آب‌وهوای بندرخمیر:

🌡 دما: {temp}°C
🤔 دمای احساسی: {feels_like}°C
💧 رطوبت: {humidity}%
💨 سرعت باد: {wind} متر بر ثانیه
☁️ وضعیت: {description}"""
    except httpx.HTTPStatusError:
        return "❌ سرویس آب‌وهوا فعلاً پاسخ مناسبی نداد. لطفاً کمی بعد دوباره امتحان کن."
    except httpx.RequestError:
        return "❌ اتصال به سرویس آب‌وهوا برقرار نشد. اتصال اینترنت یا پروکسی را بررسی کن."
    except (KeyError, TypeError, ValueError):
        return "❌ اطلاعات آب‌وهوا ناقص یا نامعتبر دریافت شد. لطفاً بعداً دوباره امتحان کن."
    except Exception:
        return "❌ در دریافت آب‌وهوا مشکلی پیش آمد. لطفاً کمی بعد دوباره امتحان کن."


async def get_tides():
    url = f"https://api.stormglass.io/v2/tide/extremes/point?lat={LAT}&lng={LON}"
    headers = {"Authorization": STORMGLASS_API_KEY}
    try:
        async with create_api_client() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            tide_events = data.get("data", [])
            if not tide_events:
                return "⚠️ متأسفانه اطلاعات جزر و مد در دسترس نیست."

            # Stormglass زمان‌ها را UTC می‌فرستد؛ رخدادهای امروز را به وقت ایران فیلتر می‌کنیم.
            parsed_events = []
            for event in tide_events:
                event_time = datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
                local_time = event_time.astimezone(TIDE_TIMEZONE)
                parsed_events.append((local_time, event["type"]))

            today = datetime.now(TIDE_TIMEZONE).date()
            today_events = [event for event in parsed_events if event[0].date() == today]
            if not today_events:
                selected_date = min(parsed_events, key=lambda event: event[0])[0].date()
                today_events = [event for event in parsed_events if event[0].date() == selected_date]
            else:
                selected_date = today

            today_events.sort(key=lambda event: event[0])
            event_lines = []
            for local_time, tide_type in today_events:
                label = "مد (آب بالاست)" if tide_type == "high" else "جزر (آب پایینه)"
                icon = "🌊" if tide_type == "high" else "🏖️"
                event_lines.append(f"{icon} {label} - ساعت {local_time:%H:%M}")

            date_text = selected_date.strftime("%Y/%m/%d")
            return "🌊 جزر و مد بندرخمیر\n" f"📅 تاریخ: {date_text}\n\n" + "\n".join(event_lines)
    except httpx.HTTPStatusError:
        return "❌ سرویس جزر و مد فعلاً پاسخ مناسبی نداد. لطفاً کمی بعد دوباره امتحان کن."
    except httpx.RequestError:
        return "❌ اتصال به سرویس جزر و مد برقرار نشد. اتصال اینترنت یا پروکسی را بررسی کن."
    except (KeyError, TypeError, ValueError):
        return "❌ اطلاعات جزر و مد ناقص یا نامعتبر دریافت شد. لطفاً بعداً دوباره امتحان کن."
    except Exception:
        return "❌ در دریافت جزر و مد مشکلی پیش آمد. لطفاً کمی بعد دوباره امتحان کن."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = ReplyKeyboardMarkup(
        [
            ["🌤 آب‌وهوا", "🌊 جزر و مد"],
            ["📋 همه اطلاعات", "🏝 درباره خمیر"],
        ],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        "سلام، خوش اومدی رفیق! 👋\n"
        "من ربات خمیرم؛ هر وقت خواستی، حال‌وهوای شهر و جزر و مد دریا رو برات میارم.\n\n"
        "از منوی پایین یکی رو بزن یا این دستورها رو بفرست:\n"
        "/weather - آب‌وهوا 🌤\n"
        "/tides - جزر و مد 🌊\n"
        "/all - همه اطلاعات 📋\n"
        "/about - درباره خمیر 🏝",
        reply_markup=menu,
    )


async def reply_with_loading(update: Update, content_loader):
    loading_message = await update.message.reply_text("⏳ یه لحظه صبر کن، دارم اطلاعات رو می‌گیرم...")
    try:
        content = await content_loader()
    except Exception:
        content = "❌ متأسفانه دریافت اطلاعات با مشکل روبه‌رو شد. لطفاً کمی بعد دوباره امتحان کن."
    await loading_message.edit_text(content)


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply_with_loading(update, get_weather)


async def tides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply_with_loading(update, get_tides)


async def all_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def load_all_info():
        weather_info = await get_weather()
        tides_info = await get_tides()
        return weather_info + "\n\n" + tides_info

    await reply_with_loading(update, load_all_info)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def load_about():
        return (
            "🏝 خمیر کجاست؟\n\n"
            "بندرخمیر یکی از شهرهای استان هرمزگانه؛ کنار خلیج فارس و حدود ۷۵ کیلومتری غرب بندرعباس قرار گرفته.\n\n"
            "👥 جمعیت: حدود ۵۴ هزار نفر، بر اساس سرشماری سال ۱۳۹۵.\n\n"
            "🌿 دیدنی‌ها و داشته‌ها:\n"
            "• تالاب بین‌المللی خورخوران و جنگل‌های حرا\n"
            "• ساحل و پهنه‌های زیبای جزر و مدی\n"
            "• قلعه خمیر و پل تاریخی لاتیدان در اطراف شهر\n\n"
            "خمیر به طبیعت دریایی، حرا، فرهنگ ساحلی و مردمان خون‌گرمش شناخته می‌شه."
        )

    await reply_with_loading(update, load_about)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_actions = {
        "🌤 آب‌وهوا": weather,
        "🌊 جزر و مد": tides,
        "📋 همه اطلاعات": all_info,
        "🏝 درباره خمیر": about,
    }
    action = menu_actions.get(update.message.text)
    if action:
        await action(update, context)


def main():
    missing_settings = [
        name for name, value in {
            "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
            "WEATHER_API_KEY": WEATHER_API_KEY,
            "STORMGLASS_API_KEY": STORMGLASS_API_KEY,
        }.items() if not value
    ]
    if missing_settings:
        raise RuntimeError(
            "تنظیمات لازم در فایل .env پیدا نشد: " + ", ".join(missing_settings)
        )

    # اینجا پروکسی رو درست به ربات معرفی می‌کنیم
    if PROXY_URL:
        request = HTTPXRequest(proxy=PROXY_URL)
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).request(request).build()
    else:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("tides", tides))
    app.add_handler(CommandHandler("all", all_info))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    print("🤖 ربات روشن شد! حالا توی تلگرام /start بفرست.")
    app.run_polling()


if __name__ == "__main__":
    main()