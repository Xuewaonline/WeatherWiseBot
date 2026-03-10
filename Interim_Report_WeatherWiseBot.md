# WeatherWiseBot: An Intelligent Weather Forecast Notification System

## Interim Report

---

**Course:** COMP 8960SEF Capstone Project

**Programme:** MCOMPF - Master of Computing

**School:** School of Science and Technology, Hong Kong Metropolitan University (HKMU)

**Student Name:** HE Xue

**Student ID:** 13927408

**Supervisor:** Dr. Jeff Au Yeung

**Submission Date:** March 2026

---

## Abstract

This interim report presents the progress made on the WeatherWiseBot capstone project, an intelligent weather forecast notification system that delivers region-specific weather forecasts, clothing recommendations, severe weather alerts, and schedule-based travel reminders via SMS. The system is built using Python with a Streamlit web interface, SQLite for data persistence, OpenWeatherMap for weather data retrieval, and Twilio for SMS delivery. Since the initial project proposal, the core system architecture has been designed and all primary modules have been implemented, including the weather API integration layer, a rule-based clothing recommendation engine, an SMS notification service with simulation fallback, a background task scheduler using APScheduler, and a five-tab Streamlit web dashboard. This report details the system design, implementation progress, testing conducted to date, challenges encountered, and the remaining work required before final submission. The project is on track to meet its stated objectives, with the principal remaining tasks involving comprehensive end-to-end testing, user interface refinement, and the preparation of user documentation.

---

## Table of Contents

1. Introduction
2. Literature Review and Background
3. System Design and Architecture
4. Implementation Details
5. Testing and Current Results
6. Challenges and Solutions
7. Remaining Work and Timeline
8. Conclusion
9. References

---

## 1. Introduction

### 1.1 Project Background

Weather conditions significantly influence daily decisions, from clothing selection to travel planning. While numerous weather applications exist, many provide generic forecasts without actionable guidance tailored to individual schedules and locations. This observation motivated the development of WeatherWiseBot, an intelligent weather forecast notification system that bridges the gap between raw meteorological data and practical, personalised recommendations delivered proactively via SMS.

The project was proposed in the initial report submitted for COMP 8960SEF as a system that would integrate real-time weather data with a rule-based recommendation engine and schedule-aware notifications. The fundamental objectives remain unchanged: to provide users with region-specific forecasts and outfit recommendations, to alert users of severe weather conditions in near real-time, and to support travel planning through dual-city weather reports linked to scheduled events such as flights and business trips.

### 1.2 Project Objectives

The primary objectives of WeatherWiseBot, as defined in the initial report, are as follows:

1. Deliver region-specific daily weather forecasts with clothing recommendations via SMS at a user-specified time.
2. Monitor severe weather conditions across user-configured cities at 15-minute intervals and dispatch alert notifications.
3. Provide a Schedule Plan Helper that links upcoming travel events to weather forecasts for both origin and destination cities.
4. Implement a rule-based clothing recommendation engine that considers temperature, precipitation probability, wind speed, and weather descriptions.
5. Present all functionality through an intuitive web-based interface built with Streamlit.

### 1.3 Scope of This Report

This interim report covers the work completed between the initial proposal and the current date. It provides an updated literature review, a detailed account of the system architecture, descriptions of each implemented module with relevant code excerpts, a summary of testing activities, a discussion of challenges encountered and their resolutions, and a timeline for the remaining work.

---

## 2. Literature Review and Background

### 2.1 Weather Information Systems

The availability of weather data through public APIs has enabled the development of a wide range of weather-related applications. OpenWeatherMap, one of the most widely used weather data providers, offers both current conditions and forecast endpoints supporting over 200,000 cities worldwide (OpenWeatherMap, 2024). Their API delivers data in JSON format, including temperature, humidity, wind speed, precipitation probability, and textual weather descriptions, making it well-suited for programmatic consumption. The One Call API 3.0 further extends functionality with government-issued severe weather alerts, a critical feature for safety-oriented applications.

Research by Thornes and Stephenson (2001) demonstrated that tailored weather information significantly improves decision-making in daily activities. More recently, Zabini et al. (2015) found that personalised weather notifications increase user engagement and weather preparedness compared to generic forecasts. These findings support the design rationale of WeatherWiseBot, which aims to transform raw forecast data into context-specific, actionable advice.

### 2.2 Rule-Based Expert Systems

Rule-based systems remain a practical approach for domain-specific recommendation tasks where the decision logic can be explicitly codified. As described by Jackson (1998), rule-based expert systems encode domain knowledge as production rules (if-then statements) that fire when conditions match input data. For the clothing recommendation domain, rules can be defined across multiple dimensions including temperature ranges, precipitation probability thresholds, wind speed categories, and special weather conditions such as snow or thunderstorms. This approach was chosen over machine learning alternatives due to its transparency, ease of modification, and deterministic behaviour, all desirable properties in a system where users need to trust the recommendations they receive.

### 2.3 SMS Notification Systems

Despite the proliferation of mobile applications, SMS remains a highly effective notification channel due to its near-universal reach and high open rates. Twilio, a cloud communications platform, provides a robust API for programmatic SMS delivery supporting the E.164 international phone number format (Twilio, 2024). The platform offers delivery status tracking, message queuing, and global carrier support. For development and testing purposes, SMS simulation (logging messages without actual delivery) is a common pattern that reduces costs during iterative development, a strategy adopted in WeatherWiseBot.

### 2.4 Web Application Frameworks for Data-Driven Applications

Streamlit has emerged as a leading framework for building interactive web applications in Python, particularly for data-driven use cases (Streamlit, 2024). Its reactive programming model, where the script re-executes on each user interaction, simplifies state management and UI updates. The framework provides built-in components for forms, charts, layouts, and custom HTML/CSS injection, enabling rapid prototyping of feature-rich dashboards without requiring front-end expertise. For a capstone project where the primary development effort should focus on the application logic rather than web infrastructure, Streamlit represents an appropriate technology choice.

### 2.5 Background Task Scheduling

APScheduler (Advanced Python Scheduler) is a mature library for scheduling Python functions to execute at specified intervals or cron-like schedules (APScheduler Documentation, 2024). It supports multiple scheduling paradigms including interval-based, cron-based, and date-based triggers, and can operate as a background scheduler within a running application. This capability is essential for WeatherWiseBot, which must perform periodic severe weather checks and time-triggered daily forecast deliveries without blocking the web interface.

---

## 3. System Design and Architecture

### 3.1 Architectural Overview

WeatherWiseBot follows a layered architecture comprising four principal layers: the Presentation Layer, the Application Layer, the Data Layer, and the Integration Layer. This separation of concerns promotes maintainability and allows each layer to evolve independently.

**Presentation Layer:** The Streamlit web interface serves as the primary user interaction point. It is organised into five tabs (Weather Forecast, Outfit Recommendation, Severe Weather Alerts, Schedule Plan Helper, and SMS and Notification Log) with a sidebar for user settings and scheduler control. Custom CSS provides gradient-styled cards for weather data, alerts, outfit recommendations, and SMS previews.

**Application Layer:** This layer contains the core business logic implemented across four Python modules. The scheduling service orchestrates three background jobs: daily forecast delivery, severe weather monitoring at 15-minute intervals, and event reminder checks every 30 minutes. The clothing recommendation engine applies a hierarchy of temperature, rain, wind, and condition-specific rules. The event parser links scheduled events to weather data for both origin and destination cities.

**Data Layer:** SQLite serves as the persistent storage backend with five tables: `user_settings` (phone number, preferred cities, notification preferences), `schedule_events` (travel events with origin/destination cities, dates, and notification parameters), `forecast_log` (historical forecast data with associated clothing recommendations), `sms_log` (complete record of sent and simulated messages), and `alert_log` (detected severe weather events with severity classifications).

**Integration Layer:** Two external services are integrated. The OpenWeatherMap API provides current weather data, five-day forecasts, and severe weather alerts through its REST endpoints. The Twilio API handles SMS delivery with a simulation fallback for development environments where API credentials are not configured.

### 3.2 Data Flow

The typical data flow for a daily forecast notification proceeds as follows. The APScheduler triggers the `job_daily_forecast` function at the user-configured time. This function retrieves user settings from the SQLite database, fetches current weather and forecast data from OpenWeatherMap for the user's primary and secondary cities, passes the weather parameters to the clothing recommendation engine to generate an outfit suggestion, logs the forecast and recommendation to the database, formats the combined weather and outfit information into an SMS message, and dispatches it through the Twilio service (or logs it in simulation mode). A similar flow applies to severe weather checks and event reminders, with variations in the triggering schedule and message content.

### 3.3 Database Schema

The database schema was designed to support comprehensive logging and user personalisation. The `user_settings` table stores one record per user with fields for phone number in E.164 format, primary and secondary city names, preferred notification time, and a Boolean flag for severe alert opt-in. The `schedule_events` table associates events with origin and destination cities, enabling dual-city weather lookups. Foreign key relationships link events to users. Temporal fields use ISO 8601 format strings for cross-platform compatibility. The three logging tables (`forecast_log`, `sms_log`, `alert_log`) provide an audit trail for all system activity.

---

## 4. Implementation Details

### 4.1 Configuration Module (config.py)

The configuration module centralises all system parameters. API keys and sensitive credentials are loaded from environment variables using the `python-dotenv` library, ensuring secrets are never hard-coded. The module defines ten supported cities spanning multiple continents (Hong Kong, Shanghai, Beijing, Shenzhen, Guangzhou, Tokyo, Singapore, London, New York, and Sydney) with their geographic coordinates and time zone identifiers. The severe weather check interval is set to 15 minutes as a configurable constant.

### 4.2 Database Module (database.py)

The database module provides a complete data access layer built on Python's `sqlite3` standard library. The `init_db` function creates all five tables using `CREATE TABLE IF NOT EXISTS` statements, ensuring idempotent initialisation. A default user record is inserted if the `user_settings` table is empty, providing a working configuration for first-time use. The module exposes CRUD functions for each entity: `get_user_settings` and `update_user_settings` for preferences; `add_event`, `get_events`, `delete_event`, and `mark_event_notified` for schedule management; `log_forecast` and `get_recent_forecasts` for forecast history; `log_sms` and `get_sms_history` for message tracking; and `log_alert` and `get_recent_alerts` for alert records. The `sqlite3.Row` row factory is used throughout to enable dictionary-style access to query results.

### 4.3 Weather API Module (weather_api.py)

The weather API module encapsulates all communication with OpenWeatherMap. The `fetch_current_weather` function calls the `/weather` endpoint with geographic coordinates (latitude/longitude) from the supported cities dictionary and returns a normalised dictionary containing temperature in Celsius, feels-like temperature, humidity, pressure, wind speed and direction, cloud coverage, hourly rainfall, visibility, and a textual weather description. The `fetch_forecast` function queries the `/forecast` endpoint, which provides data in three-hour intervals over five days, and extracts temperature, precipitation probability (converted from a 0-1 scale to 0-100 percentage), and rain volume for each interval.

The `fetch_weather_alerts` function implements a two-tier alert retrieval strategy. It first attempts to query the One Call API 3.0 for official government-issued weather alerts. If this endpoint is unavailable (due to subscription tier limitations), the function falls back to a rule-based alert derivation from current conditions. This fallback checks for strong winds exceeding 17 m/s (approximately 60 km/h), extreme temperatures above 38 degrees Celsius or below negative 5 degrees Celsius, heavy rainfall exceeding 30 mm/h, low visibility below 1000 metres, and severe descriptions such as thunderstorms or blizzards. Each detected condition generates an alert object with an event name, severity classification, and descriptive message.

The `get_daily_summary` function aggregates current and forecast data into a single summary by computing the day's maximum and minimum temperatures, peak rain chance, and collecting all weather descriptions. This summary serves as the input for both SMS formatting and the clothing recommendation engine.

### 4.4 Clothing Recommendation Engine (clothing_engine.py)

The clothing recommendation engine is a rule-based system that accepts four weather parameters (temperature, rain chance, wind speed, and description text) and produces a structured recommendation comprising clothing layers, footwear, accessories, and special advisory notes. The temperature rules define eight distinct ranges from extreme heat (above 35 degrees Celsius) to extreme cold (below 0 degrees Celsius), each mapping to appropriate clothing layers. For example, temperatures between 0 and 5 degrees Celsius trigger a recommendation for a thermal base layer, warm sweater, and winter coat, along with scarf and gloves as accessories.

Rain probability adjustments modify the base recommendation at three thresholds: above 70 percent (waterproof outerwear and sturdy umbrella), above 40 percent (compact umbrella), and above 20 percent (foldable umbrella as a precaution). Wind speed adjustments add windproof layers for speeds above 15 m/s and suggest windbreakers for speeds above 8 m/s when temperatures are cool. Condition-specific rules handle snow (waterproof boots with grip, thermal base layer), thunderstorms (stay-indoors advisory), and fog or mist (bright or reflective clothing suggestion). For clear hot days, sun protection accessories and SPF advice are added.

The `get_event_clothing` function extends the engine for travel scenarios. It generates separate recommendations for both origin and destination weather conditions, evaluates the temperature difference between the two cities, and produces a combined advisory. When the temperature difference exceeds 10 degrees Celsius, the system explicitly recommends dressing in removable layers based on the colder city's conditions while packing lighter alternatives for the warmer destination. This dual-city awareness is a distinctive feature of WeatherWiseBot that addresses a genuine pain point for travellers.

### 4.5 SMS Service Module (sms_service.py)

The SMS service module manages message delivery through Twilio with a graceful simulation fallback. The `_get_twilio_client` function checks for the presence of all three required credentials (account SID, auth token, and phone number) and returns `None` if any are missing, triggering simulation mode. Messages are truncated to 1,600 characters to respect SMS segment limits. Three specialised formatting functions handle the distinct message types: `send_daily_forecast_sms` composes a structured forecast with temperature range, conditions, humidity, wind, rain chance, and an outfit tip; `send_severe_alert_sms` formats urgent alerts with event names and descriptions; and `send_event_reminder_sms` includes origin and destination weather alongside clothing advice. All messages are logged to the database with their delivery status (sent, simulated, or failed with error details).

### 4.6 Scheduler Service (scheduler_service.py)

The scheduler service uses APScheduler's `BackgroundScheduler` to manage three concurrent jobs. The daily forecast job runs on a cron trigger at the user-specified notification time and iterates over the user's primary and secondary cities to fetch, process, log, and deliver forecasts. The severe weather check job runs on an interval trigger every 15 minutes, querying alerts for monitored cities and dispatching SMS notifications when alerts are detected. The event reminder job runs every 30 minutes, scanning for upcoming events whose notification window has been reached (determined by the `notify_hours_before` parameter) and that have not yet been notified. The `start_scheduler` function accepts the notification time as a parameter and configures all three jobs with `replace_existing=True` to support reconfiguration without restart. The `stop_scheduler` function provides clean shutdown.

### 4.7 Web Application (app.py)

The main Streamlit application integrates all modules into a cohesive five-tab dashboard. The sidebar provides persistent access to user settings (phone number, primary and secondary cities, notification time, and severe alert toggle) with a save button that writes to the database, and scheduler start/stop controls with visual status indicators.

The Weather Forecast tab offers single-city forecasts with current conditions displayed in styled gradient cards, four metric columns (temperature, humidity, wind, visibility), and a five-day forecast grouped by date. It also includes a city comparison feature that renders two cities' current conditions side by side.

The Outfit Recommendation tab fetches weather data for a selected city, generates and displays a clothing recommendation in a styled card with layers, footwear, accessories, and notes, and provides an SMS preview with a one-click send option.

The Severe Weather Alerts tab shows the monitored cities and check interval, offers a manual check button that renders alerts in red gradient cards with severity levels, and displays a historical alert log.

The Schedule Plan Helper tab provides a form for adding events (with type, description, origin and destination cities, date, time, and notification lead time), lists upcoming events in expandable sections with preview weather, send reminder, and delete actions.

The SMS and Notification Log tab includes test buttons for triggering forecast SMS and severe weather checks, and displays the 20 most recent SMS records in expandable entries showing recipient, type, status, timestamp, and full message body.

---

## 5. Testing and Current Results

### 5.1 Unit Testing

Individual modules have been tested in isolation during development. The clothing recommendation engine was tested with boundary values for each temperature range (for instance, 34.9 and 35.0 degrees Celsius to verify the extreme heat threshold) and with various combinations of rain chance and wind speed to confirm that accessory and note additions function correctly. The database module was verified by exercising all CRUD operations and confirming data integrity through round-trip read-after-write tests. The weather API module was tested with valid and invalid city names to ensure proper error handling.

### 5.2 Integration Testing

Integration between modules was tested by tracing complete workflows. The daily forecast pipeline was exercised end-to-end: fetching weather data from OpenWeatherMap, passing it through the clothing engine, formatting the SMS, and logging the result. In simulation mode (without Twilio credentials), the SMS content was verified against expected formatting. The event reminder workflow was tested by creating events with various notification windows and confirming that the scheduler triggered reminders at the appropriate times.

### 5.3 Current Results

The system currently runs successfully in simulation mode with all five Streamlit tabs functioning as designed. Weather data is fetched correctly from OpenWeatherMap for all ten supported cities. The clothing recommendation engine produces contextually appropriate suggestions across the full temperature range. The scheduler starts and stops cleanly, and all three background jobs execute on schedule. SMS messages are logged with "simulated" status when Twilio credentials are not configured. The web interface renders correctly with custom CSS styling across the gradient-styled cards and tabbed layout.

---

## 6. Challenges and Solutions

### 6.1 API Rate Limiting and Reliability

The OpenWeatherMap free tier imposes a rate limit of 60 calls per minute. With severe weather checks running every 15 minutes across two cities and additional on-demand queries from the web interface, careful management was required. The solution involved structuring the API calls efficiently within each job execution and implementing error handling with informative messages rather than retry loops that could exacerbate rate limiting. The `get_daily_summary` function consolidates current and forecast queries to minimise redundant calls.

### 6.2 One Call API Access

The One Call API 3.0, which provides government-issued weather alerts, requires a paid subscription. To maintain functionality on the free tier, the `fetch_weather_alerts` function implements a fallback mechanism that derives alerts from current conditions using threshold-based rules. This ensures the severe weather alert feature remains operational regardless of the API subscription level, though with reduced coverage compared to official alert feeds.

### 6.3 Streamlit Session State and Scheduler Lifecycle

Streamlit's execution model, where the entire script re-runs on each interaction, posed challenges for managing the background scheduler. Starting the scheduler on every re-run would create duplicate job instances. This was resolved by using `st.session_state` to track the scheduler's running status and by passing `replace_existing=True` when adding jobs, ensuring idempotent behaviour across re-runs. The scheduler's `BackgroundScheduler` runs in a separate thread that persists across Streamlit re-executions within the same server session.

### 6.4 SMS Message Length Constraints

SMS messages are limited to 160 characters per segment, with longer messages split into multiple segments at increased cost. Weather forecasts with full outfit recommendations can easily exceed this limit. The solution was to set a practical truncation limit of 1,600 characters (approximately 10 SMS segments) and to design the message templates to prioritise essential information (temperature, conditions, and the primary outfit suggestion) at the beginning of the message.

---

## 7. Remaining Work and Timeline

### 7.1 Remaining Tasks

The following tasks remain before final submission:

1. **Comprehensive Testing (Weeks 1-2):** Conduct systematic end-to-end testing covering all user workflows, edge cases (network failures, API errors, empty database states), and boundary conditions. Develop a formal test plan with documented test cases and results.

2. **Twilio Live Testing (Week 2):** Configure Twilio credentials in a staging environment and verify actual SMS delivery, including message formatting on various mobile devices and delivery status tracking.

3. **User Interface Refinement (Week 3):** Improve the visual design based on usability feedback, add loading states and error messages for all asynchronous operations, and ensure responsive layout across screen sizes.

4. **Performance Evaluation (Week 3):** Measure API response times, database query performance, and scheduler reliability over extended operation periods. Document system resource usage.

5. **Documentation (Week 4):** Prepare user manual, installation guide, and deployment instructions. Complete the final report with full testing results and reflective analysis.

6. **Final Report Preparation (Week 4):** Compile all findings, results, and reflections into the final capstone report.

### 7.2 Timeline

| Week | Period | Tasks |
|------|--------|-------|
| 1 | Mid March 2026 | Unit and integration test plan; begin systematic testing |
| 2 | Late March 2026 | Complete testing; Twilio live SMS verification |
| 3 | Early April 2026 | UI refinement; performance evaluation |
| 4 | Mid April 2026 | Documentation; final report writing and submission |

---

## 8. Conclusion

This interim report has presented the substantial progress made on the WeatherWiseBot project. The system architecture has been fully designed and all core modules have been implemented, including the OpenWeatherMap API integration, the rule-based clothing recommendation engine, the Twilio SMS service with simulation fallback, the APScheduler-based background task system, and the five-tab Streamlit web dashboard. The system successfully delivers region-specific weather forecasts with clothing recommendations, monitors severe weather conditions at configurable intervals, and supports schedule-linked travel weather advisories with dual-city outfit guidance.

The project is proceeding in accordance with the timeline established in the initial report. The principal challenges encountered, including API rate limiting, One Call API access restrictions, Streamlit session state management, and SMS length constraints, have been addressed through pragmatic engineering solutions. The remaining work focuses on comprehensive testing, live SMS verification, interface polish, and documentation. The project is well-positioned for successful completion by the final submission deadline.

---

## 9. References

APScheduler Documentation. (2024). *Advanced Python Scheduler*. Available at: https://apscheduler.readthedocs.io/ (Accessed: February 2026).

Jackson, P. (1998). *Introduction to Expert Systems*. 3rd edn. Harlow: Addison-Wesley.

OpenWeatherMap. (2024). *OpenWeatherMap API Documentation*. Available at: https://openweathermap.org/api (Accessed: February 2026).

Streamlit. (2024). *Streamlit Documentation*. Available at: https://docs.streamlit.io/ (Accessed: February 2026).

Thornes, J.E. and Stephenson, D.B. (2001). 'How to judge the quality and value of weather forecast products', *Meteorological Applications*, 8(3), pp. 307-314.

Twilio. (2024). *Twilio Programmable SMS Documentation*. Available at: https://www.twilio.com/docs/sms (Accessed: February 2026).

Zabini, F., Grasso, V., Magno, R., Meneguzzo, F. and Gozzini, B. (2015). 'Communication and interpretation of regional weather forecasts: a survey of the Italian public', *Meteorological Applications*, 22(3), pp. 483-494.

---

*End of Interim Report*
