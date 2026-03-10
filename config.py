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

# Supported cities with coordinates (sorted by region)
SUPPORTED_CITIES = {
    # --- China: Municipalities ---
    "Beijing": {"lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai"},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737, "tz": "Asia/Shanghai"},
    "Chongqing": {"lat": 29.4316, "lon": 106.9123, "tz": "Asia/Shanghai"},
    "Tianjin": {"lat": 39.3434, "lon": 117.3616, "tz": "Asia/Shanghai"},
    # --- China: Provincial Capitals ---
    "Harbin": {"lat": 45.8038, "lon": 126.5350, "tz": "Asia/Shanghai"},
    "Changchun": {"lat": 43.8171, "lon": 125.3235, "tz": "Asia/Shanghai"},
    "Shenyang": {"lat": 41.8057, "lon": 123.4315, "tz": "Asia/Shanghai"},
    "Hohhot": {"lat": 40.8424, "lon": 111.7490, "tz": "Asia/Shanghai"},
    "Urumqi": {"lat": 43.8256, "lon": 87.6168, "tz": "Asia/Urumqi"},
    "Lhasa": {"lat": 29.6520, "lon": 91.1721, "tz": "Asia/Shanghai"},
    "Xining": {"lat": 36.6171, "lon": 101.7782, "tz": "Asia/Shanghai"},
    "Lanzhou": {"lat": 36.0611, "lon": 103.8343, "tz": "Asia/Shanghai"},
    "Yinchuan": {"lat": 38.4872, "lon": 106.2309, "tz": "Asia/Shanghai"},
    "Xi'an": {"lat": 34.3416, "lon": 108.9398, "tz": "Asia/Shanghai"},
    "Taiyuan": {"lat": 37.8706, "lon": 112.5489, "tz": "Asia/Shanghai"},
    "Shijiazhuang": {"lat": 38.0428, "lon": 114.5149, "tz": "Asia/Shanghai"},
    "Zhengzhou": {"lat": 34.7466, "lon": 113.6253, "tz": "Asia/Shanghai"},
    "Jinan": {"lat": 36.6512, "lon": 116.9972, "tz": "Asia/Shanghai"},
    "Hefei": {"lat": 31.8206, "lon": 117.2272, "tz": "Asia/Shanghai"},
    "Nanjing": {"lat": 32.0603, "lon": 118.7969, "tz": "Asia/Shanghai"},
    "Hangzhou": {"lat": 30.2741, "lon": 120.1551, "tz": "Asia/Shanghai"},
    "Fuzhou": {"lat": 26.0745, "lon": 119.2965, "tz": "Asia/Shanghai"},
    "Nanchang": {"lat": 28.6820, "lon": 115.8579, "tz": "Asia/Shanghai"},
    "Wuhan": {"lat": 30.5928, "lon": 114.3055, "tz": "Asia/Shanghai"},
    "Changsha": {"lat": 28.2282, "lon": 112.9388, "tz": "Asia/Shanghai"},
    "Guangzhou": {"lat": 23.1291, "lon": 113.2644, "tz": "Asia/Shanghai"},
    "Nanning": {"lat": 22.8170, "lon": 108.3665, "tz": "Asia/Shanghai"},
    "Haikou": {"lat": 20.0174, "lon": 110.3492, "tz": "Asia/Shanghai"},
    "Chengdu": {"lat": 30.5728, "lon": 104.0668, "tz": "Asia/Shanghai"},
    "Guiyang": {"lat": 26.6470, "lon": 106.6302, "tz": "Asia/Shanghai"},
    "Kunming": {"lat": 25.0389, "lon": 102.7183, "tz": "Asia/Shanghai"},
    # --- China: SARs & Taiwan ---
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694, "tz": "Asia/Hong_Kong"},
    "Macau": {"lat": 22.1987, "lon": 113.5439, "tz": "Asia/Macau"},
    "Taipei": {"lat": 25.0330, "lon": 121.5654, "tz": "Asia/Taipei"},
    # --- China: Major Cities ---
    "Shenzhen": {"lat": 22.5431, "lon": 114.0579, "tz": "Asia/Shanghai"},
    "Dalian": {"lat": 38.9140, "lon": 121.6147, "tz": "Asia/Shanghai"},
    "Qingdao": {"lat": 36.0671, "lon": 120.3826, "tz": "Asia/Shanghai"},
    "Xiamen": {"lat": 24.4798, "lon": 118.0894, "tz": "Asia/Shanghai"},
    "Suzhou": {"lat": 31.2990, "lon": 120.5853, "tz": "Asia/Shanghai"},
    "Wuxi": {"lat": 31.4912, "lon": 120.3119, "tz": "Asia/Shanghai"},
    "Ningbo": {"lat": 29.8683, "lon": 121.5440, "tz": "Asia/Shanghai"},
    "Dongguan": {"lat": 23.0208, "lon": 113.7518, "tz": "Asia/Shanghai"},
    "Foshan": {"lat": 23.0218, "lon": 113.1219, "tz": "Asia/Shanghai"},
    "Zhuhai": {"lat": 22.2710, "lon": 113.5767, "tz": "Asia/Shanghai"},
    "Sanya": {"lat": 18.2528, "lon": 109.5120, "tz": "Asia/Shanghai"},
    "Guilin": {"lat": 25.2736, "lon": 110.2907, "tz": "Asia/Shanghai"},
    # --- East Asia (Other) ---
    "Tokyo": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo"},
    "Osaka": {"lat": 34.6937, "lon": 135.5023, "tz": "Asia/Tokyo"},
    "Seoul": {"lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul"},
    "Busan": {"lat": 35.1796, "lon": 129.0756, "tz": "Asia/Seoul"},
    # --- Southeast Asia ---
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore"},
    "Bangkok": {"lat": 13.7563, "lon": 100.5018, "tz": "Asia/Bangkok"},
    "Kuala Lumpur": {"lat": 3.1390, "lon": 101.6869, "tz": "Asia/Kuala_Lumpur"},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456, "tz": "Asia/Jakarta"},
    "Manila": {"lat": 14.5995, "lon": 120.9842, "tz": "Asia/Manila"},
    "Ho Chi Minh City": {"lat": 10.8231, "lon": 106.6297, "tz": "Asia/Ho_Chi_Minh"},
    "Hanoi": {"lat": 21.0278, "lon": 105.8342, "tz": "Asia/Ho_Chi_Minh"},
    # --- South Asia ---
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata"},
    "New Delhi": {"lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata"},
    # --- Middle East ---
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai"},
    "Abu Dhabi": {"lat": 24.4539, "lon": 54.3773, "tz": "Asia/Dubai"},
    "Riyadh": {"lat": 24.7136, "lon": 46.6753, "tz": "Asia/Riyadh"},
    "Istanbul": {"lat": 41.0082, "lon": 28.9784, "tz": "Europe/Istanbul"},
    "Tel Aviv": {"lat": 32.0853, "lon": 34.7818, "tz": "Asia/Jerusalem"},
    # --- Europe ---
    "London": {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"},
    "Berlin": {"lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin"},
    "Rome": {"lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome"},
    "Madrid": {"lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid"},
    "Barcelona": {"lat": 41.3874, "lon": 2.1686, "tz": "Europe/Madrid"},
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "tz": "Europe/Amsterdam"},
    "Zurich": {"lat": 47.3769, "lon": 8.5417, "tz": "Europe/Zurich"},
    "Vienna": {"lat": 48.2082, "lon": 16.3738, "tz": "Europe/Vienna"},
    "Moscow": {"lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},
    "Stockholm": {"lat": 59.3293, "lon": 18.0686, "tz": "Europe/Stockholm"},
    "Athens": {"lat": 37.9838, "lon": 23.7275, "tz": "Europe/Athens"},
    "Lisbon": {"lat": 38.7223, "lon": -9.1393, "tz": "Europe/Lisbon"},
    "Dublin": {"lat": 53.3498, "lon": -6.2603, "tz": "Europe/Dublin"},
    "Prague": {"lat": 50.0755, "lon": 14.4378, "tz": "Europe/Prague"},
    "Warsaw": {"lat": 52.2297, "lon": 21.0122, "tz": "Europe/Warsaw"},
    "Helsinki": {"lat": 60.1699, "lon": 24.9384, "tz": "Europe/Helsinki"},
    # --- North America ---
    "New York": {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
    "Chicago": {"lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago"},
    "San Francisco": {"lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
    "Washington D.C.": {"lat": 38.9072, "lon": -77.0369, "tz": "America/New_York"},
    "Toronto": {"lat": 43.6532, "lon": -79.3832, "tz": "America/Toronto"},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207, "tz": "America/Vancouver"},
    "Mexico City": {"lat": 19.4326, "lon": -99.1332, "tz": "America/Mexico_City"},
    "Miami": {"lat": 25.7617, "lon": -80.1918, "tz": "America/New_York"},
    "Seattle": {"lat": 47.6062, "lon": -122.3321, "tz": "America/Los_Angeles"},
    "Boston": {"lat": 42.3601, "lon": -71.0589, "tz": "America/New_York"},
    # --- South America ---
    "Sao Paulo": {"lat": -23.5505, "lon": -46.6333, "tz": "America/Sao_Paulo"},
    "Buenos Aires": {"lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
    "Rio de Janeiro": {"lat": -22.9068, "lon": -43.1729, "tz": "America/Sao_Paulo"},
    "Lima": {"lat": -12.0464, "lon": -77.0428, "tz": "America/Lima"},
    "Bogota": {"lat": 4.7110, "lon": -74.0721, "tz": "America/Bogota"},
    "Santiago": {"lat": -33.4489, "lon": -70.6693, "tz": "America/Santiago"},
    # --- Oceania ---
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney"},
    "Melbourne": {"lat": -37.8136, "lon": 144.9631, "tz": "Australia/Melbourne"},
    "Auckland": {"lat": -36.8485, "lon": 174.7633, "tz": "Pacific/Auckland"},
    # --- Africa ---
    "Cairo": {"lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo"},
    "Lagos": {"lat": 6.5244, "lon": 3.3792, "tz": "Africa/Lagos"},
    "Johannesburg": {"lat": -26.2041, "lon": 28.0473, "tz": "Africa/Johannesburg"},
    "Nairobi": {"lat": -1.2921, "lon": 36.8219, "tz": "Africa/Nairobi"},
    "Cape Town": {"lat": -33.9249, "lon": 18.4241, "tz": "Africa/Johannesburg"},
    "Casablanca": {"lat": 33.5731, "lon": -7.5898, "tz": "Africa/Casablanca"},
}

# Severe weather check interval (minutes)
SEVERE_CHECK_INTERVAL = 15
