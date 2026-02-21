"""
Weather module: Fetches forecast from Weather.gov and checks for conflicts
with weather-sensitive construction work.
"""

import requests

WEATHER_GOV_BASE = "https://api.weather.gov"
USER_AGENT = "BennettKewReportAutomation/1.0 (adam.wentworth@fonder-salari.com)"

SENSITIVE_KEYWORDS = [
    "concrete", "pour", "SOG", "slab", "footing",
    "earthwork", "compaction", "grading", "excavat",
    "trench", "backfill", "paving", "asphalt",
    "waterproof", "roofing", "membrane",
]


def get_forecast(lat: float, lon: float) -> list[dict]:
    """Fetch 7-day forecast from Weather.gov. Returns simplified periods or empty list on failure."""
    try:
        headers = {"User-Agent": USER_AGENT}

        # Step 1: Get forecast URL from point
        points_resp = requests.get(
            f"{WEATHER_GOV_BASE}/points/{lat},{lon}",
            headers=headers, timeout=10,
        )
        points_resp.raise_for_status()
        forecast_url = points_resp.json()["properties"]["forecast"]

        # Step 2: Get forecast
        forecast_resp = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_resp.raise_for_status()
        periods = forecast_resp.json()["properties"]["periods"]

        return [{
            "name": p["name"],
            "start": p["startTime"],
            "temperature": p["temperature"],
            "short": p["shortForecast"],
            "precip_pct": p.get("probabilityOfPrecipitation", {}).get("value", 0) or 0,
            "detailed": p["detailedForecast"],
        } for p in periods]
    except Exception as e:
        print(f"  WARNING: Weather fetch failed: {e}")
        return []


def check_weather_conflicts(forecast: list[dict],
                            planned_activities: list[str]) -> str | None:
    """Check if rain forecast conflicts with weather-sensitive planned work.
    Returns conflict description string, or None if no conflict."""

    # Check if any planned work is weather-sensitive
    sensitive_work = []
    all_text = " ".join(planned_activities).lower()
    for kw in SENSITIVE_KEYWORDS:
        if kw.lower() in all_text:
            for act in planned_activities:
                if kw.lower() in act.lower() and act not in sensitive_work:
                    sensitive_work.append(act)

    if not sensitive_work:
        return None

    # Check forecast for rain (daytime periods only)
    rain_days = []
    for period in forecast:
        if "night" in period["name"].lower():
            continue
        short = period["short"].lower()
        precip = period["precip_pct"]
        if precip >= 40 or any(w in short for w in ["rain", "shower", "storm", "thunder"]):
            rain_days.append(f"{period['name']} ({precip}% chance, {period['short']})")

    if not rain_days:
        return None

    return (
        f"WEATHER FORECAST CONFLICT:\n"
        f"Rain in forecast: {'; '.join(rain_days)}\n"
        f"Weather-sensitive work planned: {'; '.join(sensitive_work)}"
    )
