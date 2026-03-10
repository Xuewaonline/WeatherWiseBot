"""
WeatherWiseBot Configuration
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try Streamlit secrets first, fall back to env vars
def _get_secret(key, default=""):
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

# OpenWeatherMap API
WEATHER_API_KEY = _get_secret("WEATHER_API_KEY", "demo_key")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Twilio SMS
TWILIO_ACCOUNT_SID = _get_secret("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = _get_secret("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = _get_secret("TWILIO_PHONE_NUMBER", "")

# Database - use /tmp on cloud (writable), local dir otherwise
_local_db = os.path.join(os.path.dirname(__file__), "weatherwisebot.db")
_cloud_db = "/tmp/weatherwisebot.db"
DB_PATH = _cloud_db if os.environ.get("STREAMLIT_SHARING_MODE") or not os.access(os.path.dirname(__file__) or ".", os.W_OK) else _local_db

# Supported cities with coordinates
SUPPORTED_CITIES = {
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694, "tz": "Asia/Hong_Kong"},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737, "tz": "Asia/Shanghai"},
    "Beijing": {"lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai"},
    "Shenzhen": {"lat": 22.5431, "lon": 114.0579, "tz": "Asia/Shanghai"},
    "Guangzhou": {"lat": 23.1291, "lon": 113.2644, "tz": "Asia/Shanghai"},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore"},
    "London": {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
    "New York": {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney"},
}

# Severe weather check interval (minutes)
SEVERE_CHECK_INTERVAL = 15
