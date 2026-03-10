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

# --- Weather emoji mapping ---
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
    if temp >= 35: return "#E53E3E"
    if temp >= 28: return "#DD6B20"
    if temp >= 22: return "#D69E2E"
    if temp >= 15: return "#38A169"
    if temp >= 5:  return "#3182CE"
    return "#805AD5"


# --- Page Config ---
st.set_page_config(
    page_title="WeatherWiseBot",
    page_icon="https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/26c8.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Light Theme CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

/* ---- Hero Header ---- */
.hero-container {
    background: linear-gradient(135deg, #EBF4FF 0%, #E0ECFB 40%, #F0F7FF 100%);
    border: 1px solid #D0E1F9;
    border-radius: 20px;
    padding: 36px 40px 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -10%;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, rgba(74,144,217,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-logo {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, #4A90D9, #5BA3EC);
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    color: white;
    font-weight: 800;
    flex-shrink: 0;
    animation: logoBounce 2.5s ease-in-out infinite;
    box-shadow: 0 4px 16px rgba(74,144,217,0.25);
}
@keyframes logoBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1A365D;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-title span {
    color: #4A90D9;
}
.hero-sub {
    font-size: 1rem;
    color: #718096;
    margin-top: 4px;
    font-weight: 400;
}

/* floating weather icons */
.hero-floats {
    position: absolute;
    top: 0; right: 0;
    width: 180px; height: 100%;
    pointer-events: none;
}
.hf { position: absolute; opacity: 0.12; animation: hfFloat 5s ease-in-out infinite; }
.hf1 { font-size: 1.8rem; top: 12%; right: 25%; animation-delay: 0s; }
.hf2 { font-size: 2rem; top: 55%; right: 50%; animation-delay: 1.5s; }
.hf3 { font-size: 1.5rem; top: 65%; right: 10%; animation-delay: 3s; }
.hf4 { font-size: 1.6rem; top: 10%; right: 60%; animation-delay: 2s; }
@keyframes hfFloat {
    0%, 100% { transform: translateY(0); opacity: 0.12; }
    50% { transform: translateY(-10px); opacity: 0.22; }
}

/* ---- Cards ---- */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 14px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0,0,0,0.06);
}

/* Weather Hero Card */
.weather-hero-card {
    background: linear-gradient(135deg, #4A90D9 0%, #5BA3EC 50%, #6DB3F8 100%);
    border-radius: 20px;
    padding: 32px;
    color: white;
    position: relative;
    overflow: hidden;
    margin-bottom: 18px;
}
.weather-hero-card::after {
    content: '';
    position: absolute;
    top: -30%; right: -10%;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.weather-temp-big {
    font-size: 4rem;
    font-weight: 800;
    letter-spacing: -3px;
    line-height: 1;
    margin: 8px 0;
}
.weather-city-name { font-size: 1.4rem; font-weight: 600; margin-bottom: 0; }
.weather-desc { font-size: 1.1rem; opacity: 0.9; text-transform: capitalize; }
.weather-pill {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
    padding: 6px 14px;
    margin: 3px;
    font-size: 0.82rem;
    font-weight: 500;
}

/* Forecast Day Card */
.forecast-day {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    color: #2D3748;
    transition: transform 0.2s, box-shadow 0.2s;
}
.forecast-day:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.fd-name { font-size: 0.75rem; font-weight: 600; color: #A0AEC0; text-transform: uppercase; letter-spacing: 1px; }
.fd-emoji { font-size: 2rem; margin: 8px 0; }
.fd-high { font-size: 1.3rem; font-weight: 700; color: #2D3748; }
.fd-low { font-size: 0.85rem; color: #A0AEC0; }
.fd-rain { font-size: 0.72rem; color: #4A90D9; margin-top: 4px; font-weight: 500; }

/* Mini Metric */
.mini-metric {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}
.mm-icon { font-size: 1.4rem; margin-bottom: 4px; }
.mm-value { font-size: 1.5rem; font-weight: 700; color: #2D3748; }
.mm-label { font-size: 0.68rem; color: #A0AEC0; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

/* Compare Card */
.compare-card {
    background: linear-gradient(135deg, #4A90D9 0%, #5BA3EC 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    text-align: center;
}

/* Outfit Card */
.outfit-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 28px;
    color: #2D3748;
}
.outfit-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #A0AEC0;
    margin-bottom: 8px;
    margin-top: 16px;
}
.outfit-tag {
    display: inline-block;
    background: #EBF4FF;
    border: 1px solid #D0E1F9;
    border-radius: 8px;
    padding: 7px 14px;
    margin: 3px;
    font-size: 0.85rem;
    font-weight: 500;
    color: #2B6CB0;
}
.outfit-note {
    background: #FFFAF0;
    border-left: 3px solid #ED8936;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-top: 10px;
    font-size: 0.83rem;
    color: #C05621;
}

/* Alert Cards */
.alert-danger {
    background: linear-gradient(135deg, #FEB2B2 0%, #FC8181 100%);
    border: 1px solid #FEB2B2;
    border-radius: 14px;
    padding: 22px;
    color: #742A2A;
    margin-bottom: 12px;
}
.alert-danger h4 { margin: 0 0 6px 0; font-weight: 700; font-size: 1.05rem; }
.alert-danger p { margin: 0; font-size: 0.88rem; }
.alert-sev {
    display: inline-block;
    background: rgba(116,42,42,0.15);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
    color: #9B2C2C;
}
.alert-ok {
    background: linear-gradient(135deg, #C6F6D5 0%, #9AE6B4 100%);
    border: 1px solid #9AE6B4;
    border-radius: 14px;
    padding: 24px;
    color: #22543D;
    text-align: center;
}

/* SMS Phone Mockup */
.sms-phone {
    background: #FFFFFF;
    border: 2px solid #E2E8F0;
    border-radius: 22px;
    padding: 18px;
    max-width: 380px;
    margin: 10px auto;
}
.sms-header {
    text-align: center;
    font-size: 0.72rem;
    color: #A0AEC0;
    margin-bottom: 10px;
    font-weight: 500;
}
.sms-bubble {
    background: #EBF4FF;
    border: 1px solid #D0E1F9;
    border-radius: 14px 14px 4px 14px;
    padding: 14px 16px;
    color: #2D3748;
    font-size: 0.82rem;
    line-height: 1.55;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Event Item */
.ev-item {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.ev-icon {
    background: linear-gradient(135deg, #4A90D9, #5BA3EC);
    border-radius: 12px;
    width: 46px; height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}
.ev-body { flex: 1; }
.ev-body h4 { margin: 0; font-size: 0.95rem; font-weight: 600; color: #2D3748; }
.ev-body p { margin: 2px 0 0 0; font-size: 0.78rem; color: #A0AEC0; }
.badge-pending {
    background: #FEFCBF;
    color: #975A16;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 600;
    border: 1px solid #F6E05E;
}
.badge-done {
    background: #C6F6D5;
    color: #276749;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 600;
    border: 1px solid #9AE6B4;
}

/* Monitor Bar */
.monitor-bar {
    background: #EBF4FF;
    border: 1px solid #D0E1F9;
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}
.monitor-bar p { margin: 0; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #F0F4FA;
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #4A5568;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #EDF2F7;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 500;
    font-size: 0.85rem;
}

/* Footer */
.footer {
    text-align: center;
    padding: 24px 0 12px 0;
    color: #A0AEC0;
    font-size: 0.72rem;
    letter-spacing: 0.3px;
}

/* History Item */
.hist-item {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 6px;
    font-size: 0.82rem;
    color: #4A5568;
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
    <div style="text-align:center;margin-bottom:24px">
        <div style="width:64px;height:64px;background:linear-gradient(135deg,#4A90D9,#5BA3EC);border-radius:16px;display:inline-flex;align-items:center;justify-content:center;font-size:1.8rem;color:white;font-weight:800;box-shadow:0 4px 14px rgba(74,144,217,0.3);animation:logoBounce 2.5s ease-in-out infinite">W</div>
        <div style="font-size:1.15rem;font-weight:700;color:#1A365D;margin-top:10px;letter-spacing:-0.3px">WeatherWiseBot</div>
        <div style="font-size:0.72rem;color:#A0AEC0;margin-top:2px">Your Smart Weather Buddy</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### User Settings")

    settings = get_user_settings()
    city_list = list(SUPPORTED_CITIES.keys())

    phone = st.text_input("Phone Number (E.164)", value=settings["phone_number"] if settings else "+85200000000")

    primary_city = st.selectbox(
        "Primary City", city_list,
        index=city_list.index(settings["primary_city"]) if settings and settings["primary_city"] in city_list else 0,
    )
    secondary_city = st.selectbox(
        "Secondary City (optional)", [""] + city_list,
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
        st.markdown('<div style="text-align:center;color:#38A169;font-size:0.8rem;margin-top:8px">&#9679; Scheduler Running</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;color:#CBD5E0;font-size:0.8rem;margin-top:8px">&#9679; Scheduler Stopped</div>', unsafe_allow_html=True)


# --- Hero Header ---
st.markdown("""
<div class="hero-container">
    <div style="display:flex;align-items:center;gap:22px;flex-wrap:wrap">
        <div class="hero-logo">W</div>
        <div>
            <p class="hero-title">Weather<span>Wise</span>Bot</p>
            <p class="hero-sub">Your smart weather buddy &mdash; forecasts, outfit tips & alerts</p>
        </div>
    </div>
    <div class="hero-floats">
        <span class="hf hf1">&#127782;&#65039;</span>
        <span class="hf hf2">&#9728;&#65039;</span>
        <span class="hf hf3">&#10052;&#65039;</span>
        <span class="hf hf4">&#127752;</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Weather", "Outfit", "Alerts", "Planner", "SMS Log",
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

            st.markdown(f"""
            <div class="weather-hero-card">
                <p class="weather-city-name">{forecast_city}</p>
                <p class="weather-desc">{emoji} {current['description'].title()}</p>
                <p class="weather-temp-big" style="color:white">{current['temperature']}&#176;C</p>
                <p style="font-size:0.88rem;opacity:0.75;margin-top:-4px">Feels like {current['feels_like']}&#176;C</p>
                <div style="margin-top:14px">
                    <span class="weather-pill">Humidity {current['humidity']}%</span>
                    <span class="weather-pill">Wind {current['wind_speed']} m/s</span>
                    <span class="weather-pill">Clouds {current['clouds']}%</span>
                    <span class="weather-pill">Vis {current['visibility']/1000:.1f} km</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            for col, icon, val, label in [
                (col1, "&#127777;&#65039;", f"{current['temperature']}&#176;", "Temperature"),
                (col2, "&#128167;", f"{current['humidity']}%", "Humidity"),
                (col3, "&#127744;", f"{current['wind_speed']} m/s", "Wind"),
                (col4, "&#128065;", f"{current['visibility']/1000:.1f} km", "Visibility"),
            ]:
                col.markdown(f"""
                <div class="mini-metric">
                    <div class="mm-icon">{icon}</div>
                    <div class="mm-value">{val}</div>
                    <div class="mm-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

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
                            <div class="fd-name">{day_name}<br/>{d[5:]}</div>
                            <div class="fd-emoji">{day_emoji}</div>
                            <div class="fd-high">{max(temps):.0f}&#176;</div>
                            <div class="fd-low">{min(temps):.0f}&#176;</div>
                            <div class="fd-rain">Rain {max(rain_chances):.0f}%</div>
                        </div>
                        """, unsafe_allow_html=True)

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
                col.markdown(f"""
                <div class="compare-card">
                    <p style="font-size:1.15rem;font-weight:600;margin:0">{name}</p>
                    <p style="font-size:2rem;margin:4px 0">{e}</p>
                    <p style="font-size:2.4rem;font-weight:800;margin:4px 0">{w['temperature']}&#176;C</p>
                    <p style="font-size:0.88rem;opacity:0.8;margin:0">{w['description'].title()}</p>
                    <div style="margin-top:10px">
                        <span class="weather-pill">Humidity {w['humidity']}%</span>
                        <span class="weather-pill">Wind {w['wind_speed']} m/s</span>
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

            st.markdown(f"""
            <div class="weather-hero-card" style="padding:20px 28px">
                <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">
                    <div style="font-size:2.4rem">{emoji}</div>
                    <div>
                        <p style="margin:0;font-size:1.2rem;font-weight:700">{outfit_city}</p>
                        <p style="margin:0;opacity:0.75;font-size:0.9rem">{summary['description'].title()}</p>
                    </div>
                    <div style="margin-left:auto;text-align:right">
                        <p style="margin:0;font-size:1.8rem;font-weight:800">{summary['current_temp']}&#176;C</p>
                        <p style="margin:0;font-size:0.78rem;opacity:0.65">Rain {summary['rain_chance']}% | Wind {summary['wind_speed']} m/s</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            layers_html = "".join(f'<span class="outfit-tag">{l}</span>' for l in rec['layers'])
            acc_html = "".join(f'<span class="outfit-tag">{a}</span>' for a in rec['accessories']) if rec['accessories'] else ""
            notes_html = "".join(f'<div class="outfit-note">{n}</div>' for n in rec['special_notes']) if rec['special_notes'] else ""

            st.markdown(f"""
            <div class="outfit-card">
                <h3 style="margin-top:0;color:#2B6CB0;font-weight:700;font-size:1.15rem">Outfit Recommendation</h3>
                <div class="outfit-label">Clothing Layers</div>
                <div>{layers_html}</div>
                <div class="outfit-label">Footwear</div>
                <div><span class="outfit-tag">{rec['footwear']}</span></div>
                {'<div class="outfit-label">Accessories</div><div>' + acc_html + '</div>' if acc_html else ''}
                {notes_html}
            </div>
            """, unsafe_allow_html=True)

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
                <div class="sms-header">SMS Preview</div>
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
    <div class="monitor-bar">
        <div style="font-size:1.3rem">&#128225;</div>
        <div>
            <p style="font-weight:600;color:#2D3748;font-size:0.92rem">Monitoring: {', '.join(alert_cities)}</p>
            <p style="font-size:0.78rem;color:#A0AEC0">Auto-check every 15 minutes when scheduler is running</p>
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
                    <div class="alert-danger">
                        <h4>{alert.get('event', 'Weather Alert')}</h4>
                        <p>{alert.get('description', '')}</p>
                        <span class="alert-sev">{sev}</span>
                    </div>
                    """, unsafe_allow_html=True)

                if st.button(f"Send Alert SMS for {city}", key=f"btn_alert_sms_{city}"):
                    settings = get_user_settings()
                    if settings:
                        result = send_severe_alert_sms(settings["phone_number"], city, alerts)
                        st.success(f"Alert SMS {result['status']}!")
            else:
                st.markdown(f"""
                <div class="alert-ok">
                    <p style="font-size:1.6rem;margin:0 0 6px 0">&#9989;</p>
                    <p style="margin:0;font-size:1.05rem;font-weight:600">All Clear in {city}</p>
                    <p style="margin:4px 0 0 0;font-size:0.82rem;opacity:0.7">No severe weather alerts detected</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("##### Recent Alert History")
    recent_alerts = get_recent_alerts(limit=10)
    if recent_alerts:
        for alert in recent_alerts:
            st.markdown(f"""
            <div class="hist-item">
                <span style="color:#A0AEC0">{alert['detected_at']}</span>
                <span style="margin:0 8px;color:#E2E8F0">|</span>
                <span style="font-weight:600;color:#2D3748">{alert['city']}</span>
                <span style="margin:0 8px;color:#E2E8F0">|</span>
                <span style="color:#DD6B20">{alert['alert_type']}</span>
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
                    event_date.strftime("%Y-%m-%d"), event_time.strftime("%H:%M"), notify_before,
                )
                st.success(f"Event added: {event_desc}")

    st.markdown("")
    st.markdown("##### Upcoming Events")

    EVENT_ICONS = {"Flight": "&#9992;&#65039;", "Train": "&#128646;", "Outdoor Activity": "&#9968;&#65039;", "Business Trip": "&#128188;", "Other": "&#128197;"}

    events = get_events(upcoming_only=True)
    if events:
        for ev in events:
            icon = EVENT_ICONS.get(ev['event_type'], "&#128197;")
            badge = '<span class="badge-done">Notified</span>' if ev["notified"] else '<span class="badge-pending">Pending</span>'

            st.markdown(f"""
            <div class="ev-item">
                <div class="ev-icon">{icon}</div>
                <div class="ev-body">
                    <h4>{ev['event_description']}</h4>
                    <p>{ev['origin_city']} &#8594; {ev['destination_city']} | {ev['event_date']} {ev['event_time']}</p>
                </div>
                {badge}
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Actions: {ev['event_description']}"):
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
                                <div class="sms-header">Travel Outfit Advice</div>
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
            with st.expander(f"{sms['message_type'].upper()} | {sms['sent_at']}"):
                st.markdown(f"**To:** {sms['phone_number']}  |  **Status:** {sms['status']}")
                st.markdown(f"""
                <div class="sms-phone">
                    <div class="sms-header">{sms['message_type']}</div>
                    <div class="sms-bubble">{sms['message_body']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No SMS history yet. Send a test message or start the scheduler.")


# --- Footer ---
st.markdown("""
<div class="footer">
    WeatherWiseBot &mdash; Stay weather-wise, every day
</div>
""", unsafe_allow_html=True)
