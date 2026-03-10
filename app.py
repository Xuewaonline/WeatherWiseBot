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

# --- Page Config ---
st.set_page_config(
    page_title="WeatherWiseBot",
    page_icon="https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/26c8.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1e88e5, #42a5f5, #64b5f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .weather-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        margin-bottom: 15px;
    }
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
    }
    .event-card {
        background: linear-gradient(135deg, #a8e6cf 0%, #88d8a8 100%);
        padding: 15px;
        border-radius: 10px;
        color: #333;
        margin-bottom: 10px;
    }
    .outfit-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 15px;
        color: #333;
    }
    .sms-preview {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85rem;
        white-space: pre-wrap;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Init ---
init_db()

if "scheduler_running" not in st.session_state:
    st.session_state.scheduler_running = False


# --- Sidebar: User Settings ---
with st.sidebar:
    st.markdown("### Settings")

    settings = get_user_settings()

    phone = st.text_input("Phone Number (E.164)", value=settings["phone_number"] if settings else "+85200000000")
    city_list = list(SUPPORTED_CITIES.keys())

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
        "Enable Severe Weather Alerts",
        value=bool(settings["severe_alerts_enabled"]) if settings else True,
    )

    if st.button("Save Settings", use_container_width=True, type="primary"):
        update_user_settings(
            phone, primary_city, secondary_city,
            notification_time.strftime("%H:%M"), severe_enabled,
        )
        st.success("Settings saved!")

    st.divider()

    # Scheduler control
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
        st.success("Scheduler is running")
    else:
        st.info("Scheduler is stopped")


# --- Header ---
st.markdown('<p class="main-header">WeatherWiseBot</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">An Intelligent Weather Forecast Notification System</p>', unsafe_allow_html=True)

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Weather Forecast",
    "Outfit Recommendation",
    "Severe Weather Alerts",
    "Schedule Plan Helper",
    "SMS & Notification Log",
])


# ===== TAB 1: Weather Forecast =====
with tab1:
    st.subheader("Region-Specific Weather Forecast")

    forecast_city = st.selectbox("Select City", city_list, key="forecast_city")

    if st.button("Get Forecast", type="primary", key="btn_forecast"):
        with st.spinner("Fetching weather data..."):
            current = fetch_current_weather(forecast_city)
            forecast = fetch_forecast(forecast_city)

        if "error" in current:
            st.error(f"Error fetching weather: {current['error']}")
        else:
            # Current weather display
            st.markdown(f"""
            <div class="weather-card">
                <h2>{forecast_city}</h2>
                <h1>{current['temperature']}°C</h1>
                <p>Feels like {current['feels_like']}°C | {current['description'].title()}</p>
                <p>Humidity: {current['humidity']}% | Wind: {current['wind_speed']} m/s | Clouds: {current['clouds']}%</p>
            </div>
            """, unsafe_allow_html=True)

            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Temperature", f"{current['temperature']}°C", f"Feels {current['feels_like']}°C")
            col2.metric("Humidity", f"{current['humidity']}%")
            col3.metric("Wind Speed", f"{current['wind_speed']} m/s")
            col4.metric("Visibility", f"{current['visibility'] / 1000:.1f} km")

            # 5-day forecast
            if "forecasts" in forecast:
                st.markdown("#### 5-Day Forecast")
                # Group by date
                by_date = {}
                for f in forecast["forecasts"]:
                    d = f["datetime"][:10]
                    by_date.setdefault(d, []).append(f)

                cols = st.columns(min(5, len(by_date)))
                for i, (d, items) in enumerate(list(by_date.items())[:5]):
                    with cols[i]:
                        temps = [it["temperature"] for it in items]
                        rain_chances = [it["rain_chance"] for it in items]
                        st.markdown(f"**{d}**")
                        st.markdown(f"High: {max(temps):.1f}°C")
                        st.markdown(f"Low: {min(temps):.1f}°C")
                        st.markdown(f"Rain: {max(rain_chances):.0f}%")
                        st.markdown(f"{items[len(items)//2]['description'].title()}")

    # Quick compare two cities
    st.divider()
    st.markdown("#### Compare Two Cities")
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
                with col:
                    st.markdown(f"""
                    <div class="weather-card">
                        <h3>{name}</h3>
                        <h2>{w['temperature']}°C</h2>
                        <p>{w['description'].title()}</p>
                        <p>Humidity: {w['humidity']}% | Wind: {w['wind_speed']} m/s</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Failed to fetch weather for one or both cities.")


# ===== TAB 2: Outfit Recommendation =====
with tab2:
    st.subheader("Outfit Recommendation")

    outfit_city = st.selectbox("Select City", city_list, key="outfit_city")

    if st.button("Get Recommendation", type="primary", key="btn_outfit"):
        with st.spinner("Analyzing weather..."):
            summary = get_daily_summary(outfit_city)

        if summary:
            rec = get_clothing_recommendation(
                summary["current_temp"],
                summary["rain_chance"],
                summary["wind_speed"],
                summary["description"],
            )

            st.markdown(f"""
            <div class="weather-card">
                <h3>{outfit_city} - Current Conditions</h3>
                <p>Temperature: {summary['current_temp']}°C | Rain Chance: {summary['rain_chance']}% | Wind: {summary['wind_speed']} m/s</p>
                <p>{summary['description'].title()}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="outfit-card">
                <h3>Outfit Recommendation</h3>
                <p><strong>Clothing Layers:</strong></p>
                <ul>{''.join(f'<li>{l}</li>' for l in rec['layers'])}</ul>
                <p><strong>Footwear:</strong> {rec['footwear']}</p>
                {'<p><strong>Accessories:</strong> ' + ', '.join(rec['accessories']) + '</p>' if rec['accessories'] else ''}
                {'<p><strong>Notes:</strong> ' + ' '.join(rec['special_notes']) + '</p>' if rec['special_notes'] else ''}
            </div>
            """, unsafe_allow_html=True)

            # SMS preview
            st.markdown("#### SMS Preview")
            sms_text = (
                f"WeatherWiseBot - {outfit_city}\n"
                f"Temp: {summary['current_temp']}°C, {summary['description'].title()}\n"
                f"Rain: {summary['rain_chance']}%\n\n"
                f"Outfit: {rec['suggestion']}"
            )
            st.markdown(f'<div class="sms-preview">{sms_text}</div>', unsafe_allow_html=True)

            if st.button("Send as SMS Now", key="btn_send_outfit"):
                settings = get_user_settings()
                if settings:
                    result = send_daily_forecast_sms(settings["phone_number"], outfit_city, summary, rec)
                    st.success(f"SMS {result['status']}!")
        else:
            st.error("Could not fetch weather data. Check your API key.")


# ===== TAB 3: Severe Weather Alerts =====
with tab3:
    st.subheader("Severe Weather Alerts")

    alert_cities = [primary_city]
    if secondary_city:
        alert_cities.append(secondary_city)

    st.info(f"Monitoring: {', '.join(alert_cities)} | Check interval: every 15 minutes")

    if st.button("Check Now", type="primary", key="btn_check_alerts"):
        for city in alert_cities:
            with st.spinner(f"Checking {city}..."):
                alerts = fetch_weather_alerts(city)

            if alerts:
                for alert in alerts:
                    st.markdown(f"""
                    <div class="alert-card">
                        <h4>{alert.get('event', 'Weather Alert')}</h4>
                        <p>{alert.get('description', '')}</p>
                        {'<p>Severity: ' + alert.get('severity', 'unknown').upper() + '</p>' if 'severity' in alert else ''}
                    </div>
                    """, unsafe_allow_html=True)

                if st.button(f"Send Alert SMS for {city}", key=f"btn_alert_sms_{city}"):
                    settings = get_user_settings()
                    if settings:
                        result = send_severe_alert_sms(settings["phone_number"], city, alerts)
                        st.success(f"Alert SMS {result['status']}!")
            else:
                st.success(f"No severe weather alerts for {city}.")

    # Alert history
    st.divider()
    st.markdown("#### Recent Alert History")
    recent_alerts = get_recent_alerts(limit=10)
    if recent_alerts:
        for alert in recent_alerts:
            st.markdown(f"**{alert['detected_at']}** | {alert['city']} | {alert['alert_type']} | {alert['severity']}")
    else:
        st.info("No alert history yet.")


# ===== TAB 4: Schedule Plan Helper =====
with tab4:
    st.subheader("Schedule Plan Helper")
    st.markdown("Add travel events and receive weather-based SMS reminders before your trip.")

    with st.form("event_form"):
        st.markdown("#### Add New Event")

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

        submitted = st.form_submit_button("Add Schedule Plan", type="primary")

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

    # Preview weather for event
    st.divider()
    st.markdown("#### Upcoming Events")

    events = get_events(upcoming_only=True)
    if events:
        for ev in events:
            status_icon = "[Notified]" if ev["notified"] else "[Pending]"
            with st.expander(f"{status_icon} {ev['event_description']} - {ev['event_date']} {ev['event_time']}"):
                st.markdown(f"**Type:** {ev['event_type']}")
                st.markdown(f"**Route:** {ev.get('origin_city', 'N/A')} -> {ev.get('destination_city', 'N/A')}")
                st.markdown(f"**Notify:** {ev['notify_hours_before']}h before")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Preview Weather", key=f"preview_{ev['id']}"):
                        o_weather = fetch_current_weather(ev["origin_city"]) if ev.get("origin_city") else None
                        d_weather = fetch_current_weather(ev["destination_city"]) if ev.get("destination_city") else None

                        if o_weather and "error" not in o_weather:
                            o_weather["city"] = ev["origin_city"]
                            st.markdown(f"**{ev['origin_city']}**: {o_weather['temperature']}°C, {o_weather['description']}")
                        if d_weather and "error" not in d_weather:
                            d_weather["city"] = ev["destination_city"]
                            st.markdown(f"**{ev['destination_city']}**: {d_weather['temperature']}°C, {d_weather['description']}")

                        if o_weather and d_weather and "error" not in o_weather and "error" not in d_weather:
                            advice = get_event_clothing(o_weather, d_weather, ev["event_type"])
                            st.markdown(f'<div class="sms-preview">{advice}</div>', unsafe_allow_html=True)

                with col2:
                    if st.button("Send Reminder Now", key=f"remind_{ev['id']}"):
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
                    if st.button("Delete", key=f"del_{ev['id']}"):
                        delete_event(ev["id"])
                        st.rerun()
    else:
        st.info("No upcoming events. Add a schedule plan above.")


# ===== TAB 5: SMS & Notification Log =====
with tab5:
    st.subheader("SMS & Notification Log")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Send Test Forecast SMS", type="primary"):
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
        if st.button("Trigger Severe Check"):
            job_check_severe_weather()
            st.success("Severe weather check completed!")

    st.divider()
    st.markdown("#### Recent SMS History")

    sms_history = get_sms_history(limit=20)
    if sms_history:
        for sms in sms_history:
            with st.expander(f"[{sms['status'].upper()}] {sms['message_type']} - {sms['sent_at']}"):
                st.markdown(f"**To:** {sms['phone_number']}")
                st.markdown(f'<div class="sms-preview">{sms["message_body"]}</div>', unsafe_allow_html=True)
    else:
        st.info("No SMS history yet. Send a test message or start the scheduler.")


# --- Footer ---
st.divider()
st.markdown(
    "<div style='text-align: center; color: #999; font-size: 0.8rem;'>"
    "WeatherWiseBot - COMP 8960SEF Capstone Project | HKMU 2026"
    "</div>",
    unsafe_allow_html=True,
)
