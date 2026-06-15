#!/usr/bin/env python3
"""
CLI Weather App using Open-Meteo (100% free, no API key needed!)
Usage: python weather.py <city name>
"""

import requests
import sys
from datetime import datetime

# ── API URLs ──────────────────────────────────────────────────────────────────

GEO_URL     = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ── Weather code descriptions ─────────────────────────────────────────────────

WEATHER_CODES = {
    0:  ("Clear Sky",           "☀️"),
    1:  ("Mainly Clear",        "🌤️"),
    2:  ("Partly Cloudy",       "⛅"),
    3:  ("Overcast",            "☁️"),
    45: ("Foggy",               "🌫️"),
    48: ("Icy Fog",             "🌫️"),
    51: ("Light Drizzle",       "🌦️"),
    53: ("Moderate Drizzle",    "🌦️"),
    55: ("Heavy Drizzle",       "🌧️"),
    61: ("Slight Rain",         "🌧️"),
    63: ("Moderate Rain",       "🌧️"),
    65: ("Heavy Rain",          "🌧️"),
    71: ("Slight Snow",         "🌨️"),
    73: ("Moderate Snow",       "🌨️"),
    75: ("Heavy Snow",          "❄️"),
    80: ("Slight Showers",      "🌦️"),
    81: ("Moderate Showers",    "🌧️"),
    82: ("Violent Showers",     "⛈️"),
    95: ("Thunderstorm",        "⛈️"),
    99: ("Thunderstorm + Hail", "⛈️"),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_coordinates(city):
    """Step 1: Convert city name → latitude & longitude."""
    response = requests.get(GEO_URL, params={"name": city, "count": 1})
    response.raise_for_status()
    data = response.json()

    if "results" not in data or not data["results"]:
        print(f"❌ City '{city}' not found. Please check the spelling.")
        sys.exit(1)

    result = data["results"][0]
    return {
        "name":      result["name"],
        "country":   result.get("country", ""),
        "latitude":  result["latitude"],
        "longitude": result["longitude"],
        "timezone":  result.get("timezone", "UTC"),
    }


def get_weather(lat, lon, timezone):
    """Step 2: Fetch weather data using coordinates."""
    params = {
        "latitude":       lat,
        "longitude":      lon,
        "current":        "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation",
        "daily":          "temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum",
        "timezone":       timezone,
        "forecast_days":  5,
    }
    response = requests.get(WEATHER_URL, params=params)
    response.raise_for_status()
    return response.json()


def feels_like_desc(apparent, actual):
    diff = apparent - actual
    if diff <= -3:
        return "Feels colder than it is"
    elif diff >= 3:
        return "Feels warmer than it is"
    else:
        return "Feels about right"


def wind_description(speed):
    if speed < 5:
        return "Calm"
    elif speed < 20:
        return "Light breeze"
    elif speed < 40:
        return "Moderate wind"
    elif speed < 60:
        return "Strong wind"
    else:
        return "Storm!"


# ── Display ───────────────────────────────────────────────────────────────────

def display_weather(location, weather):
    current = weather["current"]
    daily   = weather["daily"]

    temp       = current["temperature_2m"]
    feels      = current["apparent_temperature"]
    humidity   = current["relative_humidity_2m"]
    wind       = current["wind_speed_10m"]
    rain       = current["precipitation"]
    code       = current["weather_code"]

    condition, icon = WEATHER_CODES.get(code, ("Unknown", "🌡️"))
    now = datetime.now().strftime("%A, %d %b %Y  %H:%M")

    print()
    print(f"{'═'*48}")
    print(f"  {icon}  Weather in {location['name']}, {location['country']}")
    print(f"  📅 {now}")
    print(f"{'═'*48}")
    print(f"  🌡️  Temperature   : {temp}°C")
    print(f"  🤔 Feels Like    : {feels}°C  ({feels_like_desc(feels, temp)})")
    print(f"  🌤️  Condition     : {condition}")
    print(f"  💧 Humidity      : {humidity}%")
    print(f"  💨 Wind Speed    : {wind} km/h  ({wind_description(wind)})")
    print(f"  🌧️  Precipitation : {rain} mm")
    print(f"{'─'*48}")

    # 5-day forecast
    print(f"  📆 5-Day Forecast")
    print(f"{'─'*48}")
    for i in range(5):
        date     = daily["time"][i]
        hi       = daily["temperature_2m_max"][i]
        lo       = daily["temperature_2m_min"][i]
        d_code   = daily["weather_code"][i]
        d_rain   = daily["precipitation_sum"][i]
        _, d_icon = WEATHER_CODES.get(d_code, ("Unknown", "🌡️"))

        # Format date as "Mon 09 Jun"
        d_label = datetime.strptime(date, "%Y-%m-%d").strftime("%a %d %b")
        rain_str = f"  🌧️ {d_rain}mm" if d_rain > 0 else ""
        print(f"  {d_label}  {d_icon}  ↑{hi}°C  ↓{lo}°C{rain_str}")

    print(f"{'═'*48}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("\n⚠️  Please provide a city name.")
        print("   Usage: python weather.py <city>")
        print("   Examples:")
        print("     python weather.py Butwal")
        print("     python weather.py Kathmandu")
        print("     python weather.py London\n")
        sys.exit(1)

    city = " ".join(sys.argv[1:])

    print(f"\n🔍 Fetching weather for '{city}'...")

    try:
        # Step 1: city name → coordinates
        location = get_coordinates(city)

        # Step 2: coordinates → weather data (JSON)
        weather = get_weather(location["latitude"], location["longitude"], location["timezone"])

        # Step 3: display the weather nicely
        display_weather(location, weather)

    except requests.exceptions.ConnectionError:
        print("❌ No internet connection. Please check your network.")
    except requests.exceptions.HTTPError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Something went wrong: {e}")


if __name__ == "__main__":
    main()