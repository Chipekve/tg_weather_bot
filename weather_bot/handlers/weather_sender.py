import os
import requests
import logging
from datetime import datetime
from aiogram import Bot
from database import SessionLocal, User

API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.weatherapi.com/v1/forecast.json"


def format_weather_block(title: str, temp: float, feels_like: float, condition: str) -> str:
    return (
        f"<b>{title}:</b>\n"
        f"• 🌡 Температура: <b>{temp}°C</b>\n"
        f"• 🤔 Ощущается как: <b>{feels_like}°C</b>\n"
        f"• ☁️ Состояние: <i>{condition}</i>\n"
    )


def extract_night_stats(hours: list) -> tuple:
    night_hours = [
        hour for hour in hours
        if 0 <= datetime.fromisoformat(hour['time']).hour <= 6
    ]
    if not night_hours:
        return "–", "–", "–"

    avg_temp = round(sum(h['temp_c'] for h in night_hours) / len(night_hours))
    avg_feels_like = round(sum(h['feelslike_c'] for h in night_hours) / len(night_hours))
    condition = night_hours[0]['condition']['text']
    return avg_temp, avg_feels_like, condition


def get_today_weather_summary_weatherapi(city: str, lang='ru') -> str:
    try:
        params = {
            'key': API_KEY,
            'q': city,
            'days': 1,
            'lang': lang,
            'aqi': 'no',
            'alerts': 'no'
        }

        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        location_name = data['location']['name']
        forecast = data['forecast']['forecastday'][0]
        day = forecast['day']
        hours = forecast['hour']

        # День
        day_temp = round(day['avgtemp_c'])
        day_feels_like = day_temp  # WeatherAPI даёт только avgtemp, можно заменить в будущем
        day_condition = day['condition']['text']

        # Ночь
        night_temp, night_feels_like, night_condition = extract_night_stats(hours)

        summary = (
            f"🌤 <b>Прогноз на сегодня в {location_name}:</b>\n\n"
            f"{format_weather_block('☀️ Днём', day_temp, day_feels_like, day_condition)}\n"
            f"{format_weather_block('🌙 Ночью', night_temp, night_feels_like, night_condition)}"
        )

        return summary.strip()

    except Exception as e:
        return f"⚠️ Ошибка при получении прогноза: {e}"


async def send_weather_to_subscribers(bot: Bot):
    session = SessionLocal()
    try:
        users = session.query(User).filter(User.is_subscribed == True).all()

        for user in users:
            if not user.city:
                continue

            summary = get_today_weather_summary_weatherapi(user.city)

            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=summary,
                    parse_mode='HTML'
                )
            except Exception as e:
                logging.error(f"⚠️ Не удалось отправить сообщение {user.telegram_id}: {e}")
    finally:
        session.close()
