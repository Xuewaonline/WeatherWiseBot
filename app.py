"""
WeatherWiseBot - Main Streamlit Application
An Intelligent Weather Forecast Notification System
"""
import streamlit as st
from datetime import datetime, date, timedelta

from database import (
    init_db, get_user_settings, update_user_settings,
    add_event, get_events, delete_event,
    get_sms_history, get_recent_alerts, get_recent_forecasts,
)
from weather_api import fetch_current_weather, fetch_forecast, get_daily_summary, fetch_weather_alerts
from clothing_engine import get_clothing_recommendation, get_event_clothing
from sms_service import send_daily_forecast_sms, send_severe_alert_sms, send_event_reminder_sms
from scheduler_service import start_scheduler, stop_scheduler, job_daily_forecast, job_check_severe_weather
from config import SUPPORTED_CITIES

# --- Weather icon mapping ---
WEATHER_ICONS = {
    "clear sky": "sun_behind_cloud", "few clouds": "sun_behind_small_cloud",
    "scattered clouds": "cloud", "broken clouds": "cloud",
    "overcast clouds": "cloud", "shower rain": "cloud_with_rain",
    "rain": "cloud_with_rain", "light rain": "cloud_with_rain",
    "moderate rain": "cloud_with_rain", "heavy intensity rain": "cloud_with_rain",
    "thunderstorm": "cloud_with_lightning_and_rain", "snow": "snowflake",
    "mist": "fog", "haze": "fog", "fog": "fog",
}

WEATHER_EMOJI = {
    "clear sky": "&#9728;&#65039;", "few clouds": "&#9925;",
    "scattered clouds": "&#9729;&#65039;", "broken clouds": "&#9729;&#65039;",
    "overcast clouds": "&#9729;&#65039;", "shower rain": "&#127783;&#65039;",
    "rain": "&#127783;&#65039;", "light rain": "&#127782;&#65039;",
    "moderate rain": "&#127783;&#65039;", "heavy intensity rain": "&#127783;&#65039;",
    "thunderstorm": "&#9889;", "snow": "&#10052;&#65039;",
    "mist": "&#127787;&#65039;", "haze": "&#127787;&#65039;", "fog": "&#127787;&#65039;",
}

def get_weather_emoji(desc):
    d = desc.lower() if desc else ""
    for key, emoji in WEATHER_EMOJI.items():
        if key in d:
            return emoji
    return "&#127780;&#65039;"

def get_temp_color(temp):
    if temp >= 35: return "#ff4444"
    if temp >= 28: return "#ff8c00"
    if temp >= 22: return "#ffd700"
    if temp >= 15: return "#7ec8e3"
    if temp >= 5:  return "#4a90d9"
    return "#a0c4ff"

def get_uv_bar(rain_chance):
    color = "#4caf50" if rain_chance < 30 else "#ff9800" if rain_chance < 60 else "#f44336"
    return f'<div style="background:#2a2a3e;border-radius:10px;height:8px;width:100%;margin:4px 0"><div style="background:{color};border-radius:10px;height:8px;width:{min(rain_chance, 100)}%"></div></div>'


# --- Page Config ---
st.set_page_config(
    page_title="WeatherWiseBot",
    page_icon="https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/26c8.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Global CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ---- Base font size bump ---- */
html, body, [class*="css"] { font-size: 16px !important; }
.stMarkdown, .stMarkdown p, .stText { font-size: 1.05rem !important; }
.stSelectbox label, .stTextInput label, .stDateInput label,
.stTimeInput label, .stNumberInput label, .stToggle label {
    font-size: 0.95rem !important; font-weight: 500 !important;
}
.stSelectbox [data-baseweb="select"], .stTextInput input,
.stDateInput input, .stTimeInput input {
    font-size: 1rem !important;
}
button[kind="primary"], button[kind="secondary"], .stButton button {
    font-size: 0.95rem !important;
}

/* ---- Header ---- */
.hero-container {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a4e 30%, #302b63 60%, #24243e 100%);
    border-radius: 24px;
    padding: 40px 40px 35px 40px;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -15%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(66,165,245,0.12) 0%, transparent 70%);
    border-radius: 50%;
}

/* ---- Mascot ---- */
.hero-mascot {
    position: relative;
    width: 90px;
    height: 90px;
    flex-shrink: 0;
    animation: mascotBounce 2s ease-in-out infinite;
}
.mascot-cloud {
    font-size: 5rem;
    line-height: 1;
    filter: drop-shadow(0 4px 12px rgba(66,165,245,0.4));
}
.mascot-face {
    position: absolute;
    bottom: -2px;
    right: -4px;
    font-size: 1.8rem;
    animation: wiggle 3s ease-in-out infinite;
}
@keyframes mascotBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
@keyframes wiggle {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(6deg); }
    75% { transform: rotate(-6deg); }
}

/* ---- Floating doodles ---- */
.hero-weather-doodles {
    position: absolute;
    top: 0;
    right: 0;
    width: 200px;
    height: 100%;
    pointer-events: none;
}
.doodle {
    position: absolute;
    opacity: 0.18;
    animation: floatUp 6s ease-in-out infinite;
}
.d1 { font-size: 2rem; top: 15%; right: 20%; animation-delay: 0s; }
.d2 { font-size: 2.4rem; top: 50%; right: 60%; animation-delay: 1.2s; }
.d3 { font-size: 1.6rem; top: 70%; right: 15%; animation-delay: 2.5s; }
.d4 { font-size: 1.8rem; top: 10%; right: 55%; animation-delay: 3.8s; }
.d5 { font-size: 2.2rem; top: 55%; right: 35%; animation-delay: 0.8s; }
@keyframes floatUp {
    0%, 100% { transform: translateY(0) scale(1); opacity: 0.18; }
    50% { transform: translateY(-12px) scale(1.1); opacity: 0.3; }
}

.hero-title {
    font-size: 3.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #64b5f6, #42a5f5, #1e88e5, #90caf9, #64b5f6);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s ease infinite;
    margin: 0;
    letter-spacing: -1px;
}
@keyframes shimmer {
    0% { background-position: 0% center; }
    50% { background-position: 100% center; }
    100% { background-position: 0% center; }
}
.hero-sub {
    font-size: 1.25rem;
    color: rgba(255,255,255,0.55);
    margin-top: 6px;
    font-weight: 400;
    letter-spacing: 0.3px;
}

/* ---- Cards ---- */
.glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.weather-hero-card {
    background: linear-gradient(135deg, #1a237e 0%, #283593 40%, #1565c0 100%);
    border-radius: 20px;
    padding: 35px 35px 30px 35px;
    color: white;
    position: relative;
    overflow: hidden;
    margin-bottom: 24px;
}
.weather-hero-card p { margin-bottom: 0; }
.weather-hero-card::after {
    content: '';
    position: absolute;
    top: -30%;
    right: -10%;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.weather-temp-big {
    font-size: 4.2rem;
    font-weight: 800;
    letter-spacing: 2px;
    line-height: 1.3;
    margin: 20px 0 16px 0;
}
.weather-desc {
    font-size: 1.3rem;
    font-weight: 400;
    opacity: 0.85;
    text-transform: capitalize;
    margin-bottom: 8px;
}
.weather-detail {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 8px 16px;
    margin: 4px;
    font-size: 0.95rem;
    font-weight: 500;
}
.weather-city-name {
    font-size: 1.6rem;
    font-weight: 600;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}

/* ---- Forecast Day Card ---- */
.forecast-day {
    background: linear-gradient(180deg, rgba(30,60,114,0.6) 0%, rgba(42,82,152,0.4) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 14px;
    text-align: center;
    color: white;
    transition: transform 0.2s;
}
.forecast-day:hover { transform: translateY(-3px); }
.forecast-day-name { font-size: 0.85rem; font-weight: 600; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.5px; line-height: 1.5; margin-bottom: 4px; }
.forecast-emoji { font-size: 2.2rem; margin: 10px 0; }
.forecast-temp-high { font-size: 1.5rem; font-weight: 700; line-height: 1.4; margin-bottom: 2px; }
.forecast-temp-low { font-size: 0.95rem; opacity: 0.6; line-height: 1.4; }
.forecast-rain { font-size: 0.8rem; opacity: 0.5; margin-top: 6px; }

/* ---- Outfit Card ---- */
.outfit-hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 30px;
    color: white;
}
.outfit-section-title {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.4);
    margin-bottom: 8px;
    margin-top: 18px;
}
.outfit-item {
    display: inline-block;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 10px 18px;
    margin: 4px;
    font-size: 1rem;
    font-weight: 500;
    color: white;
}
.outfit-note {
    background: rgba(255,152,0,0.1);
    border-left: 3px solid #ff9800;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-top: 12px;
    font-size: 0.95rem;
    color: #ffcc80;
}

/* ---- Alert Card ---- */
.alert-hero {
    background: linear-gradient(135deg, #b71c1c 0%, #d32f2f 50%, #c62828 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.alert-hero::before {
    content: '&#9888;&#65039;';
    position: absolute;
    top: 10px;
    right: 15px;
    font-size: 2rem;
    opacity: 0.2;
}
.alert-hero h4 { margin: 0 0 8px 0; font-weight: 700; font-size: 1.25rem; }
.alert-hero p { margin: 0; font-size: 1rem; opacity: 0.9; }
.alert-severity {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
}

.alert-safe {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    text-align: center;
}

/* ---- SMS Preview ---- */
.sms-phone {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 20px;
    max-width: 380px;
    margin: 10px auto;
}
.sms-phone-header {
    text-align: center;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.4);
    margin-bottom: 12px;
    font-weight: 500;
}
.sms-bubble {
    background: rgba(66,165,245,0.15);
    border: 1px solid rgba(66,165,245,0.2);
    border-radius: 14px 14px 4px 14px;
    padding: 14px 16px;
    color: rgba(255,255,255,0.9);
    font-size: 0.95rem;
    line-height: 1.55;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* ---- Event Card ---- */
.event-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.event-icon {
    background: linear-gradient(135deg, #1e88e5, #42a5f5);
    border-radius: 12px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}
.event-info { flex: 1; }
.event-info h4 { margin: 0; font-size: 1.1rem; font-weight: 600; color: white; }
.event-info p { margin: 2px 0 0 0; font-size: 0.9rem; color: rgba(255,255,255,0.5); }
.event-badge-pending {
    background: rgba(255,152,0,0.15);
    color: #ffb74d;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.event-badge-done {
    background: rgba(76,175,80,0.15);
    color: #81c784;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* ---- Metric Mini Card ---- */
.mini-metric {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
}
.mini-metric-icon { font-size: 1.5rem; margin-bottom: 8px; }
.mini-metric-value { font-size: 1.5rem; font-weight: 700; color: white; line-height: 1.3; margin-bottom: 4px; }
.mini-metric-label { font-size: 0.78rem; color: rgba(255,255,255,0.4); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 6px; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: rgba(255,255,255,0.7);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 14px 28px;
    font-weight: 800 !important;
    font-size: 1.15rem !important;
}
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span {
    font-weight: 800 !important;
    font-size: 1.15rem !important;
}

/* ---- Compare Card ---- */
.compare-card {
    background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    text-align: center;
}
.compare-vs {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 8px 0;
}

/* ---- Footer ---- */
.footer {
    text-align: center;
    padding: 20px 0 10px 0;
    color: rgba(255,255,255,0.2);
    font-size: 0.85rem;
    letter-spacing: 0.5px;
}

/* Hide Streamlit defaults */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- Init ---
init_db()

if "scheduler_running" not in st.session_state:
    st.session_state.scheduler_running = False


# --- Sidebar ---
with st.sidebar:
    st.markdown("")
    st.markdown("""
    <div style="text-align:center;margin-bottom:20px">
        <div style="font-size:3.8rem;margin-bottom:2px;animation: mascotBounce 2s ease-in-out infinite">&#9925;</div>
        <div style="font-size:1.35rem;font-weight:800;color:#64b5f6;letter-spacing:-0.5px">WeatherWiseBot</div>
        <div style="font-size:0.8rem;color:rgba(255,255,255,0.35);margin-top:2px">Your Smart Weather Buddy</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### User Settings")

    settings = get_user_settings()
    city_list = list(SUPPORTED_CITIES.keys())

    phone = st.text_input("Phone Number", value=settings["phone_number"] if settings else "+85200000000")

    primary_city = st.selectbox(
        "Primary City",
        city_list,
        index=city_list.index(settings["primary_city"]) if settings and settings["primary_city"] in city_list else 0,
    )
    secondary_city = st.selectbox(
        "Secondary City (optional)",
        [""] + city_list,
        index=(city_list.index(settings["secondary_city"]) + 1) if settings and settings["secondary_city"] in city_list else 0,
    )
    notification_time = st.time_input(
        "Daily Notification Time",
        value=datetime.strptime(settings["notification_time"] if settings else "07:00", "%H:%M").time(),
    )
    severe_enabled = st.toggle(
        "Severe Weather Alerts",
        value=bool(settings["severe_alerts_enabled"]) if settings else True,
    )

    if st.button("Save Settings", use_container_width=True, type="primary"):
        update_user_settings(
            phone, primary_city, secondary_city,
            notification_time.strftime("%H:%M"), severe_enabled,
        )
        st.success("Settings saved!")

    st.markdown("---")
    st.markdown("### Scheduler")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start", use_container_width=True, type="primary"):
            start_scheduler(notification_time.strftime("%H:%M"))
            st.session_state.scheduler_running = True
    with col2:
        if st.button("Stop", use_container_width=True):
            stop_scheduler()
            st.session_state.scheduler_running = False

    if st.session_state.scheduler_running:
        st.markdown('<div style="text-align:center;color:#4caf50;font-size:0.8rem;margin-top:8px">&#9679; Scheduler Running</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;color:rgba(255,255,255,0.3);font-size:0.8rem;margin-top:8px">&#9679; Scheduler Stopped</div>', unsafe_allow_html=True)


# --- Hero Header ---
st.markdown("""
<div class="hero-container">
    <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
        <div class="hero-mascot">
            <div class="mascot-cloud">&#9925;</div>
        </div>
        <div>
            <p class="hero-title">WeatherWiseBot</p>
            <p class="hero-sub">Your smart weather buddy &#8212; forecasts, outfit tips & alerts!</p>
        </div>
        <div class="hero-weather-doodles">
            <span class="doodle d1">&#127782;&#65039;</span>
            <span class="doodle d2">&#9728;&#65039;</span>
            <span class="doodle d3">&#10052;&#65039;</span>
            <span class="doodle d4">&#9889;</span>
            <span class="doodle d5">&#127752;</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "&#127780;&#65039;  Weather",
    "&#128084;  Outfit",
    "&#9888;&#65039;  Alerts",
    "&#9992;&#65039;  Planner",
    "&#128172;  SMS",
])


# ===== TAB 1: Weather Forecast =====
with tab1:
    forecast_city = st.selectbox("Select City", city_list, key="forecast_city")

    if st.button("Get Forecast", type="primary", key="btn_forecast"):
        with st.spinner("Fetching weather data..."):
            current = fetch_current_weather(forecast_city)
            forecast = fetch_forecast(forecast_city)

        if "error" in current:
            st.error(f"Error: {current['error']}")
        else:
            emoji = get_weather_emoji(current['description'])
            temp_color = get_temp_color(current['temperature'])

            # Hero weather card
            st.markdown(f"""
            <div class="weather-hero-card">
                <p class="weather-city-name">{forecast_city}</p>
                <p class="weather-desc">{emoji} {current['description'].title()}</p>
                <p class="weather-temp-big" style="color:{temp_color}">{current['temperature']:.1f}&#176;C</p>
                <p style="font-size:0.95rem;opacity:0.6;margin-top:6px">Feels like {current['feels_like']:.1f}&#176;C</p>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            for col, icon, val, label in [
                (col1, "&#127777;&#65039;", f"{current['temperature']:.1f}&#176;C", "Temperature"),
                (col2, "&#128167;", f"{current['humidity']:.1f}%", "Humidity"),
                (col3, "&#127744;", f"{current['wind_speed']:.1f} m/s", "Wind"),
                (col4, "&#128065;", f"{current['visibility']/1000:.1f} km", "Visibility"),
            ]:
                col.markdown(f"""
                <div class="mini-metric">
                    <div class="mini-metric-icon">{icon}</div>
                    <div class="mini-metric-value">{val}</div>
                    <div class="mini-metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

            # 5-day forecast
            if "forecasts" in forecast:
                st.markdown("")
                st.markdown("##### 5-Day Forecast")
                by_date = {}
                for f in forecast["forecasts"]:
                    d = f["datetime"][:10]
                    by_date.setdefault(d, []).append(f)

                cols = st.columns(min(5, len(by_date)))
                for i, (d, items) in enumerate(list(by_date.items())[:5]):
                    with cols[i]:
                        temps = [it["temperature"] for it in items]
                        rain_chances = [it["rain_chance"] for it in items]
                        mid_desc = items[len(items)//2]["description"]
                        day_emoji = get_weather_emoji(mid_desc)
                        day_name = datetime.strptime(d, "%Y-%m-%d").strftime("%a")
                        st.markdown(f"""
                        <div class="forecast-day">
                            <div class="forecast-day-name">{day_name}<br/>{d[5:]}</div>
                            <div class="forecast-emoji">{day_emoji}</div>
                            <div class="forecast-temp-high">{max(temps):.1f}&#176;</div>
                            <div class="forecast-temp-low">{min(temps):.1f}&#176;</div>
                            <div class="forecast-rain">&#9730; {max(rain_chances):.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Compare
    st.markdown("")
    st.markdown("##### Compare Two Cities")
    cc1, cc2 = st.columns(2)
    with cc1:
        compare1 = st.selectbox("City 1", city_list, key="cmp1")
    with cc2:
        compare2 = st.selectbox("City 2", city_list, index=1, key="cmp2")

    if st.button("Compare", key="btn_compare"):
        with st.spinner("Fetching..."):
            w1 = fetch_current_weather(compare1)
            w2 = fetch_current_weather(compare2)

        if "error" not in w1 and "error" not in w2:
            col1, col2 = st.columns(2)
            for col, w, name in [(col1, w1, compare1), (col2, w2, compare2)]:
                e = get_weather_emoji(w['description'])
                tc = get_temp_color(w['temperature'])
                col.markdown(f"""
                <div class="compare-card">
                    <p style="font-size:1.2rem;font-weight:600;margin:0">{name}</p>
                    <p style="font-size:2rem;margin:0">{e}</p>
                    <p style="font-size:2.5rem;font-weight:800;color:{tc};margin:5px 0">{w['temperature']:.1f}&#176;C</p>
                    <p style="font-size:0.9rem;opacity:0.7;margin:0">{w['description'].title()}</p>
                    <div style="margin-top:10px">
                        <span class="weather-detail">&#128167; {w['humidity']:.1f}%</span>
                        <span class="weather-detail">&#127744; {w['wind_speed']:.1f} m/s</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Failed to fetch weather data.")


# ===== TAB 2: Outfit Recommendation =====
with tab2:
    outfit_city = st.selectbox("Select City", city_list, key="outfit_city")

    if st.button("Get Recommendation", type="primary", key="btn_outfit"):
        with st.spinner("Analyzing weather..."):
            summary = get_daily_summary(outfit_city)

        if summary:
            rec = get_clothing_recommendation(
                summary["current_temp"], summary["rain_chance"],
                summary["wind_speed"], summary["description"],
            )
            emoji = get_weather_emoji(summary['description'])

            # Weather summary strip
            st.markdown(f"""
            <div class="weather-hero-card" style="padding:20px 30px">
                <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
                    <div style="font-size:2.5rem">{emoji}</div>
                    <div>
                        <p style="margin:0;font-size:1.3rem;font-weight:700">{outfit_city}</p>
                        <p style="margin:0;opacity:0.6">{summary['description'].title()}</p>
                    </div>
                    <div style="margin-left:auto;text-align:right">
                        <p style="margin:0;font-size:2rem;font-weight:800">{summary['current_temp']:.1f}&#176;C</p>
                        <p style="margin:0;font-size:0.8rem;opacity:0.5">Rain {summary['rain_chance']:.1f}% | Wind {summary['wind_speed']:.1f} m/s</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Outfit card
            layers_html = "".join(f'<span class="outfit-item">&#128085; {l}</span>' for l in rec['layers'])
            acc_html = "".join(f'<span class="outfit-item">&#127890; {a}</span>' for a in rec['accessories']) if rec['accessories'] else ""
            notes_html = "".join(f'<div class="outfit-note">{n}</div>' for n in rec['special_notes']) if rec['special_notes'] else ""

            st.markdown(f"""
            <div class="outfit-hero">
                <h3 style="margin-top:0;color:#64b5f6;font-weight:700">&#128084; Outfit Recommendation</h3>
                <div class="outfit-section-title">Clothing</div>
                <div>{layers_html}</div>
                <div class="outfit-section-title">Footwear</div>
                <div><span class="outfit-item">&#128095; {rec['footwear']}</span></div>
                {'<div class="outfit-section-title">Accessories</div><div>' + acc_html + '</div>' if acc_html else ''}
            </div>
            """, unsafe_allow_html=True)

            # SMS preview as phone mockup
            st.markdown("")
            st.markdown("##### SMS Preview")
            sms_text = (
                f"WeatherWiseBot - {outfit_city}\n"
                f"Temp: {summary['current_temp']}C, {summary['description'].title()}\n"
                f"Rain: {summary['rain_chance']}%\n\n"
                f"Outfit: {rec['suggestion']}"
            )
            st.markdown(f"""
            <div class="sms-phone">
                <div class="sms-phone-header">&#128172; SMS Preview</div>
                <div class="sms-bubble">{sms_text}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Send as SMS Now", key="btn_send_outfit"):
                settings = get_user_settings()
                if settings:
                    result = send_daily_forecast_sms(settings["phone_number"], outfit_city, summary, rec)
                    st.success(f"SMS {result['status']}!")
        else:
            st.error("Could not fetch weather data. Check your API key.")


# ===== TAB 3: Severe Weather Alerts =====
with tab3:
    alert_cities = [primary_city]
    if secondary_city:
        alert_cities.append(secondary_city)

    st.markdown(f"""
    <div class="glass-card" style="display:flex;align-items:center;gap:14px">
        <div style="font-size:1.5rem">&#128225;</div>
        <div>
            <p style="margin:0;font-weight:600;color:white">Monitoring: {', '.join(alert_cities)}</p>
            <p style="margin:0;font-size:0.8rem;color:rgba(255,255,255,0.4)">Auto-check every 15 minutes when scheduler is running</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Check Now", type="primary", key="btn_check_alerts"):
        for city in alert_cities:
            with st.spinner(f"Checking {city}..."):
                alerts = fetch_weather_alerts(city)

            if alerts:
                for alert in alerts:
                    sev = alert.get('severity', 'unknown').upper()
                    st.markdown(f"""
                    <div class="alert-hero">
                        <h4>&#9888;&#65039; {alert.get('event', 'Weather Alert')}</h4>
                        <p>{alert.get('description', '')}</p>
                        <span class="alert-severity">{sev}</span>
                    </div>
                    """, unsafe_allow_html=True)

                if st.button(f"Send Alert SMS for {city}", key=f"btn_alert_sms_{city}"):
                    settings = get_user_settings()
                    if settings:
                        result = send_severe_alert_sms(settings["phone_number"], city, alerts)
                        st.success(f"Alert SMS {result['status']}!")
            else:
                st.markdown(f"""
                <div class="alert-safe">
                    <div style="font-size:2rem;margin-bottom:8px">&#9989;</div>
                    <p style="margin:0;font-size:1.1rem;font-weight:600">All Clear in {city}</p>
                    <p style="margin:4px 0 0 0;font-size:0.85rem;opacity:0.7">No severe weather alerts detected</p>
                </div>
                """, unsafe_allow_html=True)

    # Alert history
    st.markdown("")
    st.markdown("##### Recent Alert History")
    recent_alerts = get_recent_alerts(limit=10)
    if recent_alerts:
        for alert in recent_alerts:
            st.markdown(f"""
            <div class="glass-card" style="padding:12px 18px;margin-bottom:8px">
                <span style="font-size:0.75rem;color:rgba(255,255,255,0.3)">{alert['detected_at']}</span>
                <span style="margin:0 10px;color:rgba(255,255,255,0.15)">|</span>
                <span style="font-weight:600;color:white">{alert['city']}</span>
                <span style="margin:0 10px;color:rgba(255,255,255,0.15)">|</span>
                <span style="color:#ffcc80">{alert['alert_type']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No alert history yet.")


# ===== TAB 4: Schedule Plan Helper =====
with tab4:
    st.markdown("Add travel events and receive weather-based SMS reminders before your trip.")

    with st.form("event_form"):
        event_type = st.selectbox("Event Type", ["Flight", "Train", "Outdoor Activity", "Business Trip", "Other"])
        event_desc = st.text_input("Event Description", placeholder="e.g., Flight: Shenzhen 2PM to Shanghai 4PM")

        col1, col2 = st.columns(2)
        with col1:
            origin = st.selectbox("Origin City", city_list, key="event_origin")
        with col2:
            destination = st.selectbox("Destination City", city_list, index=1, key="event_dest")

        col3, col4 = st.columns(2)
        with col3:
            event_date = st.date_input("Event Date", value=date.today() + timedelta(days=1), min_value=date.today())
        with col4:
            event_time = st.time_input("Event Time", value=datetime.strptime("14:00", "%H:%M").time())

        notify_before = st.selectbox("Notify Before", [12, 24, 48], index=1, format_func=lambda x: f"{x} hours")

        submitted = st.form_submit_button("Add Schedule Plan", type="primary", use_container_width=True)
        if submitted:
            if not event_desc:
                st.error("Please enter an event description.")
            else:
                add_event(
                    event_type, event_desc, origin, destination,
                    event_date.strftime("%Y-%m-%d"),
                    event_time.strftime("%H:%M"),
                    notify_before,
                )
                st.success(f"Event added: {event_desc}")

    st.markdown("")
    st.markdown("##### Upcoming Events")

    EVENT_TYPE_ICONS = {"Flight": "&#9992;&#65039;", "Train": "&#128646;", "Outdoor Activity": "&#9968;&#65039;", "Business Trip": "&#128188;", "Other": "&#128197;"}

    events = get_events(upcoming_only=True)
    if events:
        for ev in events:
            icon = EVENT_TYPE_ICONS.get(ev['event_type'], "&#128197;")
            badge = '<span class="event-badge-done">Notified</span>' if ev["notified"] else '<span class="event-badge-pending">Pending</span>'

            st.markdown(f"""
            <div class="event-item">
                <div class="event-icon">{icon}</div>
                <div class="event-info">
                    <h4>{ev['event_description']}</h4>
                    <p>{ev['origin_city']} &#8594; {ev['destination_city']} | {ev['event_date']} {ev['event_time']}</p>
                </div>
                {badge}
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Actions for: {ev['event_description']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Preview Weather", key=f"preview_{ev['id']}"):
                        o_weather = fetch_current_weather(ev["origin_city"]) if ev.get("origin_city") else None
                        d_weather = fetch_current_weather(ev["destination_city"]) if ev.get("destination_city") else None

                        if o_weather and "error" not in o_weather:
                            o_weather["city"] = ev["origin_city"]
                            st.markdown(f"**{ev['origin_city']}**: {o_weather['temperature']}C, {o_weather['description']}")
                        if d_weather and "error" not in d_weather:
                            d_weather["city"] = ev["destination_city"]
                            st.markdown(f"**{ev['destination_city']}**: {d_weather['temperature']}C, {d_weather['description']}")

                        if o_weather and d_weather and "error" not in o_weather and "error" not in d_weather:
                            advice = get_event_clothing(o_weather, d_weather, ev["event_type"])
                            st.markdown(f"""
                            <div class="sms-phone">
                                <div class="sms-phone-header">&#9992;&#65039; Travel Outfit Advice</div>
                                <div class="sms-bubble">{advice}</div>
                            </div>
                            """, unsafe_allow_html=True)

                with col2:
                    if st.button("Send Reminder", key=f"remind_{ev['id']}"):
                        settings = get_user_settings()
                        o_w = fetch_current_weather(ev["origin_city"]) if ev.get("origin_city") else None
                        d_w = fetch_current_weather(ev["destination_city"]) if ev.get("destination_city") else None
                        advice = ""
                        if o_w and d_w and "error" not in o_w and "error" not in d_w:
                            o_w["city"] = ev["origin_city"]
                            d_w["city"] = ev["destination_city"]
                            advice = get_event_clothing(o_w, d_w, ev["event_type"])
                        result = send_event_reminder_sms(settings["phone_number"], ev, o_w, d_w, advice)
                        st.success(f"Reminder SMS {result['status']}!")

                with col3:
                    if st.button("Delete", key=f"del_{ev['id']}", type="secondary"):
                        delete_event(ev["id"])
                        st.rerun()
    else:
        st.info("No upcoming events. Add a schedule plan above.")


# ===== TAB 5: SMS & Notification Log =====
with tab5:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send Test Forecast SMS", type="primary", use_container_width=True):
            settings = get_user_settings()
            if settings:
                summary = get_daily_summary(settings["primary_city"])
                if summary:
                    rec = get_clothing_recommendation(
                        summary["current_temp"], summary["rain_chance"],
                        summary["wind_speed"], summary["description"],
                    )
                    result = send_daily_forecast_sms(settings["phone_number"], settings["primary_city"], summary, rec)
                    st.success(f"Test SMS {result['status']}!")
                else:
                    st.error("Could not fetch weather data.")
    with col2:
        if st.button("Trigger Severe Check", use_container_width=True):
            job_check_severe_weather()
            st.success("Severe weather check completed!")

    st.markdown("")
    st.markdown("##### Message History")

    sms_history = get_sms_history(limit=20)
    if sms_history:
        for sms in sms_history:
            status_color = "#4caf50" if sms['status'] == 'sent' else "#ff9800" if sms['status'] == 'simulated' else "#f44336"
            with st.expander(f"{sms['message_type'].upper()} | {sms['sent_at']}"):
                st.markdown(f"**To:** {sms['phone_number']}  |  **Status:** :{sms['status']}:")
                st.markdown(f"""
                <div class="sms-phone">
                    <div class="sms-phone-header">&#128172; {sms['message_type']}</div>
                    <div class="sms-bubble">{sms['message_body']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No SMS history yet. Send a test message or start the scheduler.")


# --- Footer ---
st.markdown("""
<div class="footer">
    &#9925; WeatherWiseBot &mdash; Stay weather-wise, every day!
</div>
""", unsafe_allow_html=True)
