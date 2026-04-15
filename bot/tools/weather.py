import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_weather(city: str) -> str:
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather API key not configured. Please set WEATHER_API_KEY in your .env file."

    city = city.strip().rstrip("?.,!")
    if not city:
        city = "London"

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )
        resp = requests.get(url, timeout=6)
        data = resp.json()

        if resp.status_code == 200:
            name = data["name"]
            country = data["sys"]["country"]
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            desc = data["weather"][0]["description"].capitalize()
            wind = data["wind"]["speed"]
            return (
                f"🌤 **{name}, {country}** — {desc}\n"
                f"🌡 Temp: **{temp:.1f}°C** (feels like {feels:.1f}°C)\n"
                f"💧 Humidity: {humidity}% | 💨 Wind: {wind} m/s"
            )
        elif resp.status_code == 404:
            return f"❌ City **'{city}'** not found. Please check the spelling."
        else:
            return f"❌ Weather API error: {data.get('message', 'Unknown error')}"
    except requests.Timeout:
        return "❌ Weather request timed out. Please try again."
    except Exception as e:
        return f"❌ Error fetching weather: {str(e)}"
