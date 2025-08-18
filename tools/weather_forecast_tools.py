# tools/weather_forecast.py
import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from datetime import datetime
from collections import defaultdict

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

@tool("get_weather_forecast", return_direct=False)
def get_weather_forecast(location: str) -> str:
    """
    Retrieves real-time weather conditions or forecasts for the next 5 days for a given location. Always used for weather-related queries,
    including temperature, rainfall, humidity, and wind speed, to help farmers plan sowing, irrigation, and harvesting.
    If no country code is provided, defaults to India (IN).
    Example: 'Bhopal' -> 'Bhopal,IN'.
    """
    try:
        # Auto-add country code if missing
        if "," not in location:
            location = location.strip() + ",IN"

        forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": API_KEY,
            "units": "metric"
        }
        data = requests.get(forecast_url, params=params).json()

        if data.get("cod") != "200":
            return f"Error fetching forecast: {data.get('message', 'Unknown error')}"

        # Group by date
        daily_data = defaultdict(list)
        for entry in data["list"]:
            date_str = entry["dt_txt"].split(" ")[0]
            daily_data[date_str].append(entry)

        # Build forecast summary
        forecast_report = f"5-Day Weather Forecast for {location}:\n"
        for date_str, entries in daily_data.items():
            temps = [e["main"]["temp"] for e in entries]
            descriptions = [e["weather"][0]["description"] for e in entries]
            temp_min = min(temps)
            temp_max = max(temps)
            description = max(set(descriptions), key=descriptions.count)
            forecast_report += f"{datetime.strptime(date_str, '%Y-%m-%d').strftime('%d-%b-%Y')}: {description.capitalize()}, {temp_min}°C - {temp_max}°C\n"

        return forecast_report.strip()

    except Exception as e:
        return f"Error fetching forecast: {str(e)}"




