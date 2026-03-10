"""
WeatherWiseBot Database Layer - SQLite operations
"""
import sqlite3
import json
from datetime import datetime
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            primary_city TEXT NOT NULL DEFAULT 'Hong Kong',
            secondary_city TEXT DEFAULT '',
            notification_time TEXT DEFAULT '07:00',
            severe_alerts_enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS schedule_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            event_type TEXT NOT NULL,
            event_description TEXT NOT NULL,
            origin_city TEXT,
            destination_city TEXT,
            event_date TEXT NOT NULL,
            event_time TEXT NOT NULL,
            notify_hours_before INTEGER DEFAULT 24,
            notified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES user_settings(id)
        );

        CREATE TABLE IF NOT EXISTS forecast_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            forecast_data TEXT NOT NULL,
            clothing_recommendation TEXT,
            fetched_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sms_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            message_type TEXT NOT NULL,
            message_body TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            sent_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS alert_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            alert_description TEXT NOT NULL,
            severity TEXT,
            sent INTEGER DEFAULT 0,
            detected_at TEXT DEFAULT (datetime('now'))
        );
    """)

    # Insert default user if not exists
    cursor.execute("SELECT COUNT(*) FROM user_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO user_settings (phone_number, primary_city, secondary_city, notification_time)
            VALUES ('+85200000000', 'Hong Kong', 'Shanghai', '07:00')
        """)

    conn.commit()
    conn.close()


# --- User Settings ---

def get_user_settings(user_id=1):
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_settings WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_settings(phone_number, primary_city, secondary_city, notification_time, severe_alerts_enabled, user_id=1):
    conn = get_connection()
    conn.execute("""
        UPDATE user_settings
        SET phone_number=?, primary_city=?, secondary_city=?, notification_time=?,
            severe_alerts_enabled=?, updated_at=datetime('now')
        WHERE id=?
    """, (phone_number, primary_city, secondary_city, notification_time, int(severe_alerts_enabled), user_id))
    conn.commit()
    conn.close()


# --- Schedule Events ---

def add_event(event_type, event_description, origin_city, destination_city, event_date, event_time, notify_hours_before=24):
    conn = get_connection()
    conn.execute("""
        INSERT INTO schedule_events (event_type, event_description, origin_city, destination_city, event_date, event_time, notify_hours_before)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (event_type, event_description, origin_city, destination_city, event_date, event_time, notify_hours_before))
    conn.commit()
    conn.close()


def get_events(upcoming_only=True):
    conn = get_connection()
    if upcoming_only:
        rows = conn.execute(
            "SELECT * FROM schedule_events WHERE event_date >= date('now') ORDER BY event_date, event_time"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM schedule_events ORDER BY event_date DESC, event_time DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_event(event_id):
    conn = get_connection()
    conn.execute("DELETE FROM schedule_events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


def mark_event_notified(event_id):
    conn = get_connection()
    conn.execute("UPDATE schedule_events SET notified = 1 WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


# --- Forecast Log ---

def log_forecast(city, forecast_data, clothing_recommendation):
    conn = get_connection()
    conn.execute("""
        INSERT INTO forecast_log (city, forecast_data, clothing_recommendation)
        VALUES (?, ?, ?)
    """, (city, json.dumps(forecast_data), clothing_recommendation))
    conn.commit()
    conn.close()


def get_recent_forecasts(city, limit=5):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM forecast_log WHERE city = ? ORDER BY fetched_at DESC LIMIT ?", (city, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- SMS Log ---

def log_sms(phone_number, message_type, message_body, status="sent"):
    conn = get_connection()
    conn.execute("""
        INSERT INTO sms_log (phone_number, message_type, message_body, status)
        VALUES (?, ?, ?, ?)
    """, (phone_number, message_type, message_body, status))
    conn.commit()
    conn.close()


def get_sms_history(limit=20):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM sms_log ORDER BY sent_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Alert Log ---

def log_alert(city, alert_type, alert_description, severity, sent=False):
    conn = get_connection()
    conn.execute("""
        INSERT INTO alert_log (city, alert_type, alert_description, severity, sent)
        VALUES (?, ?, ?, ?, ?)
    """, (city, alert_type, alert_description, severity, int(sent)))
    conn.commit()
    conn.close()


def get_recent_alerts(limit=10):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM alert_log ORDER BY detected_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
