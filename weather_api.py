"""
WeatherWiseBot Weather API Integration - OpenWeatherMap
"""
import requests
from datetime import datetime
from config import WEATHER_API_KEY, WEATHER_BASE_URL, SUPPORTED_CITIES


def fetch_current_weather(city_name):
    """Fetch current weather for a city."""
    if city_name not in SUPPORTED_CITIES:
        return {"error": f"City '{city_name}' not supported"}

    city = SUPPORTED_CITIES[city_name]
    try:
        resp = requests.get(
            f"{WEATHER_BASE_URL}/weather",
            params={
                "lat": city["lat"],
                "lon": city["lon"],
                "appid": WEATHER_API_KEY,
                "units": "metric",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "city": city_name,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"].get("deg", 0),
            "clouds": data["clouds"]["all"],
            "rain_1h": data.get("rain", {}).get("1h", 0),
            "visibility": data.get("visibility", 10000),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except requests.RequestException as e:
        return {"error": str(e), "city": city_name}


def fetch_forecast(city_name):
    """Fetch 5-day / 3-hour forecast for a city."""
    if city_name not in SUPPORTED_CITIES:
        return {"error": f"City '{city_name}' not supported"}

    city = SUPPORTED_CITIES[city_name]
    try:
        resp = requests.get(
            f"{WEATHER_BASE_URL}/forecast",
            params={
                "lat": city["lat"],
                "lon": city["lon"],
                "appid": WEATHER_API_KEY,
                "units": "metric",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        forecasts = []
        for item in data["list"]:
            forecasts.append({
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"],
                "wind_speed": item["wind"]["speed"],
                "rain_chance": item.get("pop", 0) * 100,
                "rain_3h": item.get("rain", {}).get("3h", 0),
            })

        return {
            "city": city_name,
            "forecasts": forecasts,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except requests.RequestException as e:
        return {"error": str(e), "city": city_name}


def fetch_weather_alerts(city_name):
    """Fetch weather alerts using One Call API (if available) or simulate from current data."""
    if city_name not in SUPPORTED_CITIES:
        return []

    city = SUPPORTED_CITIES[city_name]
    alerts = []

    # Try One Call API 3.0 for alerts
    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/3.0/onecall",
            params={
                "lat": city["lat"],
                "lon": city["lon"],
                "appid": WEATHER_API_KEY,
                "exclude": "minutely,hourly,daily",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            for alert in data.get("alerts", []):
                alerts.append({
                    "event": alert.get("event", "Unknown"),
                    "sender": alert.get("sender_name", ""),
                    "start": datetime.fromtimestamp(alert["start"]).isoformat(),
                    "end": datetime.fromtimestamp(alert["end"]).isoformat(),
                    "description": alert.get("description", ""),
                })
            return alerts
    except requests.RequestException:
        pass

    # Fallback: derive alerts from current weather conditions
    current = fetch_current_weather(city_name)
    if "error" in current:
        return []

    # Check for severe conditions
    temp = current["temperature"]
    wind = current["wind_speed"]
    rain = current.get("rain_1h", 0)
    vis = current.get("visibility", 10000)
    desc = current["description"].lower()

    if wind > 17.0:  # > 60 km/h
        alerts.append({
            "event": "Strong Wind Warning",
            "severity": "moderate",
            "description": f"Wind speed {wind} m/s ({wind*3.6:.0f} km/h) in {city_name}. Secure loose objects and avoid outdoor activities.",
        })
    if temp > 38:
        alerts.append({
            "event": "Extreme Heat Warning",
            "severity": "severe",
            "description": f"Temperature {temp}C in {city_name}. Stay hydrated, avoid prolonged sun exposure.",
        })
    if temp < -5:
        alerts.append({
            "event": "Extreme Cold Warning",
            "severity": "severe",
            "description": f"Temperature {temp}C in {city_name}. Dress in layers, watch for frostbite.",
        })
    if rain > 30:
        alerts.append({
            "event": "Heavy Rain Warning",
            "severity": "severe",
            "description": f"Heavy rainfall {rain}mm/h in {city_name}. Risk of flooding.",
        })
    if vis < 1000:
        alerts.append({
            "event": "Low Visibility Warning",
            "severity": "moderate",
            "description": f"Visibility {vis}m in {city_name}. Drive carefully.",
        })
    if "thunderstorm" in desc:
        alerts.append({
            "event": "Thunderstorm Warning",
            "severity": "severe",
            "description": f"Thunderstorm reported in {city_name}. Stay indoors.",
        })
    if "snow" in desc and wind > 10:
        alerts.append({
            "event": "Blizzard Warning",
            "severity": "severe",
            "description": f"Snow with strong wind in {city_name}. Travel not recommended.",
        })

    return alerts


def get_daily_summary(city_name):
    """Get a summarized daily forecast for SMS."""
    current = fetch_current_weather(city_name)
    if "error" in current:
        return None

    forecast_data = fetch_forecast(city_name)
    today_forecasts = []
    if "forecasts" in forecast_data:
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        today_forecasts = [f for f in forecast_data["forecasts"] if f["datetime"].startswith(today_str)]

    max_temp = current["temperature"]
    min_temp = current["temperature"]
    max_rain_chance = 0
    descriptions = set()

    for f in today_forecasts:
        max_temp = max(max_temp, f["temperature"])
        min_temp = min(min_temp, f["temperature"])
        max_rain_chance = max(max_rain_chance, f["rain_chance"])
        descriptions.add(f["description"])

    return {
        "city": city_name,
        "current_temp": current["temperature"],
        "feels_like": current["feels_like"],
        "max_temp": round(max_temp, 1),
        "min_temp": round(min_temp, 1),
        "humidity": current["humidity"],
        "wind_speed": current["wind_speed"],
        "description": current["description"],
        "rain_chance": round(max_rain_chance),
        "all_descriptions": list(descriptions),
    }
