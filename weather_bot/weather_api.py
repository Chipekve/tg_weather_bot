import aiohttp
import asyncio
import logging
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

BASE_URL = "http://api.weatherapi.com/v1"


async def fetch_weather(
    city: Optional[str] = None,
    city_id: Optional[str] = None,
    retries: int = 3,
    forecast_days: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    if not city and not city_id:
        return None

    params = {
        "key": WEATHER_API_KEY,
        "lang": "ru",
        "q": f"id:{city_id}" if city_id else city,
    }

    # Если хотим прогноз, меняем endpoint и добавляем параметр days
    endpoint = "current.json"
    if forecast_days:
        endpoint = "forecast.json"
        params["days"] = forecast_days

    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BASE_URL}/{endpoint}", params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logging.warning(f"WeatherAPI returned status {response.status}")
        except Exception as e:
            logging.error(f"Weather API error on attempt {attempt + 1}: {e}")
        await asyncio.sleep(1)
    return None


async def search_cities(query: str, retries: int = 3) -> Optional[List[Dict[str, Any]]]:
    if len(query) < 2:
        return None

    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BASE_URL}/search.json",
                    params={"key": WEATHER_API_KEY, "q": query},
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logging.warning(f"City search failed with status {response.status}")
        except Exception as e:
            logging.error(f"City search error on attempt {attempt + 1}: {e}")
        await asyncio.sleep(1)
    return None
