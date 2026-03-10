"""
WeatherWiseBot Scheduler Service - APScheduler for background tasks
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from weather_api import get_daily_summary, fetch_weather_alerts, fetch_current_weather
from clothing_engine import get_clothing_recommendation, get_event_clothing
from sms_service import send_daily_forecast_sms, send_severe_alert_sms, send_event_reminder_sms
from database import (
    get_user_settings, get_events, mark_event_notified,
    log_forecast, log_alert,
)
from config import SEVERE_CHECK_INTERVAL

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def job_daily_forecast():
    """Send daily weather forecast and clothing recommendation."""
    settings = get_user_settings()
    if not settings:
        return

    for city_key in ["primary_city", "secondary_city"]:
        city = settings.get(city_key)
        if not city:
            continue

        summary = get_daily_summary(city)
        if not summary:
            logger.warning(f"Could not fetch forecast for {city}")
            continue

        clothing = get_clothing_recommendation(
            summary["current_temp"],
            summary["rain_chance"],
            summary["wind_speed"],
            summary["description"],
        )

        log_forecast(city, summary, clothing["suggestion"])
        result = send_daily_forecast_sms(settings["phone_number"], city, summary, clothing)
        logger.info(f"Daily forecast for {city}: {result['status']}")


def job_check_severe_weather():
    """Check for severe weather every 15 minutes and send alerts."""
    settings = get_user_settings()
    if not settings or not settings.get("severe_alerts_enabled"):
        return

    for city_key in ["primary_city", "secondary_city"]:
        city = settings.get(city_key)
        if not city:
            continue

        alerts = fetch_weather_alerts(city)
        if alerts:
            for alert in alerts:
                log_alert(
                    city,
                    alert.get("event", "Unknown"),
                    alert.get("description", ""),
                    alert.get("severity", "unknown"),
                    sent=True,
                )
            send_severe_alert_sms(settings["phone_number"], city, alerts)
            logger.warning(f"Severe alerts sent for {city}: {len(alerts)} alert(s)")


def job_check_event_reminders():
    """Check upcoming events and send reminders."""
    settings = get_user_settings()
    if not settings:
        return

    events = get_events(upcoming_only=True)
    now = datetime.now()

    for event in events:
        if event["notified"]:
            continue

        event_dt = datetime.strptime(f"{event['event_date']} {event['event_time']}", "%Y-%m-%d %H:%M")
        hours_until = (event_dt - now).total_seconds() / 3600

        if 0 < hours_until <= event.get("notify_hours_before", 24):
            origin_weather = None
            dest_weather = None
            clothing_advice = ""

            if event.get("origin_city"):
                origin_weather = fetch_current_weather(event["origin_city"])
                if "error" not in origin_weather:
                    origin_weather["city"] = event["origin_city"]
            if event.get("destination_city"):
                dest_weather = fetch_current_weather(event["destination_city"])
                if "error" not in dest_weather:
                    dest_weather["city"] = event["destination_city"]

            if origin_weather and dest_weather and "error" not in origin_weather and "error" not in dest_weather:
                clothing_advice = get_event_clothing(origin_weather, dest_weather, event.get("event_type", "Trip"))
            elif origin_weather and "error" not in origin_weather:
                rec = get_clothing_recommendation(
                    origin_weather["temperature"],
                    origin_weather.get("rain_chance", 0),
                    origin_weather.get("wind_speed", 0),
                    origin_weather.get("description", ""),
                )
                clothing_advice = rec["suggestion"]

            send_event_reminder_sms(
                settings["phone_number"], event, origin_weather, dest_weather, clothing_advice
            )
            mark_event_notified(event["id"])
            logger.info(f"Event reminder sent for: {event['event_description']}")


def start_scheduler(notification_time="07:00"):
    """Start the background scheduler with all jobs."""
    if scheduler.running:
        scheduler.shutdown(wait=False)

    hour, minute = map(int, notification_time.split(":"))

    # Daily forecast at user-specified time
    scheduler.add_job(
        job_daily_forecast,
        "cron",
        hour=hour,
        minute=minute,
        id="daily_forecast",
        replace_existing=True,
    )

    # Severe weather check every 15 minutes
    scheduler.add_job(
        job_check_severe_weather,
        "interval",
        minutes=SEVERE_CHECK_INTERVAL,
        id="severe_weather_check",
        replace_existing=True,
    )

    # Event reminders check every 30 minutes
    scheduler.add_job(
        job_check_event_reminders,
        "interval",
        minutes=30,
        id="event_reminders",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"Scheduler started. Daily forecast at {notification_time}, severe check every {SEVERE_CHECK_INTERVAL}min.")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
