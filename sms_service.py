"""
WeatherWiseBot SMS Service - Twilio Integration
"""
import logging
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from database import log_sms

logger = logging.getLogger(__name__)


def _get_twilio_client():
    """Initialize Twilio client if credentials are configured."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        return None
    try:
        from twilio.rest import Client
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except ImportError:
        logger.warning("Twilio package not installed. SMS will be simulated.")
        return None


def send_sms(to_number, message_body, message_type="general"):
    """
    Send SMS via Twilio. Falls back to simulation if Twilio not configured.

    Args:
        to_number: Recipient phone number (E.164 format)
        message_body: SMS text content
        message_type: Type tag for logging (daily_forecast, severe_alert, event_reminder)

    Returns:
        dict with status and details
    """
    # Truncate to SMS limit
    if len(message_body) > 1600:
        message_body = message_body[:1597] + "..."

    client = _get_twilio_client()

    if client:
        try:
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number,
            )
            log_sms(to_number, message_type, message_body, status="sent")
            logger.info(f"SMS sent to {to_number}: SID={message.sid}")
            return {"status": "sent", "sid": message.sid}
        except Exception as e:
            log_sms(to_number, message_type, message_body, status=f"failed: {e}")
            logger.error(f"SMS failed to {to_number}: {e}")
            return {"status": "failed", "error": str(e)}
    else:
        # Simulation mode
        log_sms(to_number, message_type, message_body, status="simulated")
        logger.info(f"[SIMULATED SMS] To: {to_number}\n{message_body}")
        return {"status": "simulated", "message": message_body}


def send_daily_forecast_sms(to_number, city, summary, clothing):
    """Format and send daily forecast SMS."""
    lines = [
        f"WeatherWiseBot Daily Forecast",
        f"City: {city}",
        f"Temp: {summary['current_temp']}C (Feels like {summary['feels_like']}C)",
        f"Range: {summary['min_temp']}C - {summary['max_temp']}C",
        f"Condition: {summary['description'].title()}",
        f"Humidity: {summary['humidity']}%  Wind: {summary['wind_speed']} m/s",
        f"Rain Chance: {summary['rain_chance']}%",
        f"",
        f"Outfit Tip: {clothing['suggestion']}",
    ]
    body = "\n".join(lines)
    return send_sms(to_number, body, message_type="daily_forecast")


def send_severe_alert_sms(to_number, city, alerts):
    """Format and send severe weather alert SMS."""
    lines = [f"SEVERE WEATHER ALERT - {city}"]
    for alert in alerts:
        lines.append(f"[{alert.get('event', 'Alert')}]")
        lines.append(alert.get("description", ""))
        lines.append("")
    lines.append("Stay safe! - WeatherWiseBot")
    body = "\n".join(lines)
    return send_sms(to_number, body, message_type="severe_alert")


def send_event_reminder_sms(to_number, event, origin_weather, dest_weather, clothing_advice):
    """Format and send event reminder SMS."""
    lines = [
        f"WeatherWiseBot Event Reminder",
        f"Event: {event['event_description']}",
        f"Date: {event['event_date']} at {event['event_time']}",
        f"",
    ]
    if origin_weather:
        lines.append(f"Origin ({event.get('origin_city', '')}): {origin_weather['temperature']}C, {origin_weather['description']}")
    if dest_weather:
        lines.append(f"Destination ({event.get('destination_city', '')}): {dest_weather['temperature']}C, {dest_weather['description']}")
    lines.append("")
    lines.append(clothing_advice)
    lines.append("")
    lines.append("Have a safe trip! - WeatherWiseBot")
    body = "\n".join(lines)
    return send_sms(to_number, body, message_type="event_reminder")
