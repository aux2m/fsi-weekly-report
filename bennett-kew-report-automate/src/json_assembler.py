"""
JSON Assembler: Merges all pipeline outputs into the flat dict that generate_report.py expects.
"""

import os
import json
import re
from pathlib import Path
from .calendar_utils import ReportWeek


def apply_abbreviations(text: str, abbreviations: dict) -> str:
    """Apply mandatory abbreviations to a text string."""
    for full, abbrev in abbreviations.items():
        # Case-insensitive word boundary replacement
        pattern = re.compile(re.escape(full), re.IGNORECASE)
        text = pattern.sub(abbrev, text)
    return text


def apply_abbreviations_to_list(items: list[str], abbreviations: dict) -> list[str]:
    """Apply abbreviations to each item in a list."""
    return [apply_abbreviations(item, abbreviations) for item in items]


def assemble_json(config: dict, rw: ReportWeek,
                  daily_result: dict, schedule_result: dict,
                  minutes_result: dict, photo_result: dict) -> dict:
    """
    Merge all pipeline outputs into the final data dict.
    Returns the flat dict that generate_report.py expects.
    """
    static = config["static_data"]
    paths = config["paths"]
    abbrevs = config.get("abbreviations", {})

    # Start with static data
    data = dict(static)

    # Calendar data
    data["report_number"] = f"{rw.report_number:02d}"
    data["report_week"] = rw.report_week_str
    data["issued_date"] = rw.issued_date_str
    data["countdown_days"] = str(rw.countdown_days)

    # Daily report analysis
    data["phase"] = daily_result.get("phase", "Construction")
    data["overall_progress"] = daily_result.get("overall_progress", "0")
    data["schedule_status"] = daily_result.get("schedule_status", "On Schedule")

    activities = daily_result.get("activities_completed", [])
    data["activities_completed"] = apply_abbreviations_to_list(activities, abbrevs)

    milestones = daily_result.get("milestones_achieved", [])
    # Merge milestones from minutes
    minutes_milestones = minutes_result.get("milestones_mentioned", [])
    all_milestones = _deduplicate(milestones + minutes_milestones)
    data["milestones_achieved"] = apply_abbreviations_to_list(all_milestones, abbrevs)

    critical = daily_result.get("critical_items", [])
    minutes_critical = minutes_result.get("critical_items", [])
    all_critical = _deduplicate(critical + minutes_critical)
    data["critical_items"] = apply_abbreviations_to_list(all_critical, abbrevs)

    # Schedule data
    for key in ["week1_dates", "week1_level", "week1_activities",
                "week2_dates", "week2_level", "week2_activities",
                "week3_dates", "week3_level", "week3_activities",
                "planned_activities", "noise_index", "noise_level",
                "special_considerations"]:
        val = schedule_result.get(key, [])
        if isinstance(val, list):
            data[key] = apply_abbreviations_to_list(val, abbrevs)
        else:
            data[key] = apply_abbreviations(str(val), abbrevs) if val else ""

    # Photos
    data["photos"] = photo_result.get("photos", [])
    data["photo_captions"] = photo_result.get("photo_captions", [])

    # Logos
    logos_dir = paths.get("logos_dir", "")
    data["logo_fs"] = os.path.join(logos_dir, "fs_logo.png")
    data["logo_bk"] = os.path.join(logos_dir, "bk_logo.jpg")
    data["logo_iusd"] = os.path.join(logos_dir, "iusd_logo.jpg")

    # Apply overrides if present
    overrides_path = Path(__file__).parent.parent / "input" / "overrides.json"
    if overrides_path.exists():
        try:
            with open(overrides_path) as f:
                overrides = json.load(f)
            data.update(overrides)
            print(f"  Applied {len(overrides)} manual overrides")
        except Exception as e:
            print(f"  Warning: Could not load overrides: {e}")

    # Validation
    _validate(data)

    return data


def _deduplicate(items: list[str]) -> list[str]:
    """Remove near-duplicate items (case-insensitive first 30 chars)."""
    seen = set()
    result = []
    for item in items:
        key = item[:30].lower().strip()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _validate(data: dict):
    """Validate assembled data has all required fields."""
    required = [
        "report_number", "report_week", "issued_date", "project_name",
        "countdown_days", "phase", "overall_progress", "schedule_status",
        "activities_completed", "commitment_text", "contact_name",
    ]
    missing = [k for k in required if k not in data or not data[k]]
    if missing:
        print(f"  WARNING: Missing required fields: {missing}")

    acts = data.get("activities_completed", [])
    if len(acts) < 5:
        print(f"  WARNING: Only {len(acts)} activities (minimum 5 expected)")
    elif len(acts) > 7:
        print(f"  WARNING: {len(acts)} activities (maximum 7 expected)")
        data["activities_completed"] = acts[:7]
