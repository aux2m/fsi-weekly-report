"""
CLI Agents: All agent functions using Claude CLI backend.
Same prompts and schemas as API agents, different transport.
"""

import os
from pathlib import Path

from .cli_adapter import call_claude

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ── JSON Schemas (extracted from API agent tool definitions) ─────────────

EXTRACT_DAILY_SCHEMA = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "activities": {"type": "array", "items": {"type": "string"}},
        "equipment": {"type": "array", "items": {"type": "string"}},
        "personnel_count": {"type": "string"},
        "issues": {"type": "array", "items": {"type": "string"}},
        "testing": {"type": "array", "items": {"type": "string"}},
        "weather": {"type": "string"},
        "coordination": {"type": "array", "items": {"type": "string"}},
        "subcontractors": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["date", "activities"],
}

WEEKLY_SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "phase": {"type": "string"},
        "overall_progress": {"type": "string"},
        "schedule_status": {"type": "string"},
        "activities_completed": {"type": "array", "items": {"type": "string"}},
        "milestones_achieved": {"type": "array", "items": {"type": "string"}},
        "critical_items": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["phase", "overall_progress", "schedule_status",
                  "activities_completed", "milestones_achieved", "critical_items"],
}

SCHEDULE_SCHEMA = {
    "type": "object",
    "properties": {
        "week1_dates": {"type": "string"},
        "week1_level": {"type": "string"},
        "week1_activities": {"type": "array", "items": {"type": "string"}},
        "week2_dates": {"type": "string"},
        "week2_level": {"type": "string"},
        "week2_activities": {"type": "array", "items": {"type": "string"}},
        "week3_dates": {"type": "string"},
        "week3_level": {"type": "string"},
        "week3_activities": {"type": "array", "items": {"type": "string"}},
        "planned_activities": {"type": "array", "items": {"type": "string"}},
        "noise_index": {"type": "string"},
        "noise_level": {"type": "string"},
        "special_considerations": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["week1_dates", "week1_level", "week1_activities",
                  "week2_dates", "week2_level", "week2_activities",
                  "week3_dates", "week3_level", "week3_activities",
                  "planned_activities", "noise_index", "noise_level",
                  "special_considerations"],
}

MINUTES_SCHEMA = {
    "type": "object",
    "properties": {
        "critical_items": {"type": "array", "items": {"type": "string"}},
        "milestones_mentioned": {"type": "array", "items": {"type": "string"}},
        "coordination_items": {"type": "array", "items": {"type": "string"}},
        "schedule_notes": {"type": "string"},
    },
    "required": ["critical_items", "milestones_mentioned",
                  "coordination_items", "schedule_notes"],
}

PHOTO_SCORES_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "relevance": {"type": "number"},
                    "progress_demo": {"type": "number"},
                    "quality": {"type": "number"},
                    "total_score": {"type": "number"},
                    "description": {"type": "string"},
                    "caption": {"type": "string"},
                },
                "required": ["index", "relevance", "progress_demo",
                             "quality", "total_score", "description", "caption"],
            }
        }
    },
    "required": ["scores"],
}

EMAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "body": {"type": "string"},
    },
    "required": ["subject", "body"],
}


# ── Daily Report Agent (CLI) ────────────────────────────────────────────

async def _extract_single_day_cli(text: str, day_label: str) -> dict:
    """Extract data from one daily report via CLI."""
    system = (PROMPTS_DIR / "daily_report_system.md").read_text(encoding="utf-8")
    try:
        return await call_claude(
            prompt=f"Extract data from this {day_label} daily report:\n\n{text}",
            system_prompt=system,
            model="haiku",
            json_schema=EXTRACT_DAILY_SCHEMA,
        )
    except Exception as e:
        print(f"  CLI extraction failed for {day_label}: {e}")
        return {"date": day_label, "activities": [], "error": str(e)}


async def _synthesize_week_cli(daily_extractions: list[dict],
                               report_week: str) -> dict:
    """Combine daily extractions into weekly narrative via CLI."""
    system = (PROMPTS_DIR / "weekly_synthesis_system.md").read_text(encoding="utf-8")

    days_text = ""
    for ext in daily_extractions:
        days_text += f"\n--- {ext.get('date', 'Unknown')} ---\n"
        days_text += f"Activities: {'; '.join(ext.get('activities', []))}\n"
        days_text += f"Equipment: {', '.join(ext.get('equipment', []))}\n"
        days_text += f"Issues: {'; '.join(ext.get('issues', []))}\n"
        days_text += f"Testing: {'; '.join(ext.get('testing', []))}\n"
        days_text += f"Weather: {ext.get('weather', 'N/A')}\n"
        days_text += f"Coordination: {'; '.join(ext.get('coordination', []))}\n"

    try:
        return await call_claude(
            prompt=(
                f"Synthesize these 5 daily reports for the week of {report_week} "
                f"into a weekly progress summary:\n{days_text}"
            ),
            system_prompt=system,
            model="sonnet",
            json_schema=WEEKLY_SYNTHESIS_SCHEMA,
        )
    except Exception as e:
        print(f"  CLI synthesis failed: {e}")
        return {"error": str(e), "activities_completed": []}


async def process_daily_reports_cli(daily_texts: list[dict],
                                    report_week_str: str) -> dict:
    """Process 5 daily reports sequentially, then synthesize."""
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    extractions = []

    for i, dt in enumerate(daily_texts):
        day_label = day_names[i] if i < len(day_names) else f"Day {i+1}"
        print(f"  [CLI] Extracting {day_label}: {dt['filename']}")
        ext = await _extract_single_day_cli(dt["full_text"], day_label)
        extractions.append(ext)

    print("  [CLI] Synthesizing weekly summary...")
    result = await _synthesize_week_cli(extractions, report_week_str)
    result["_daily_extractions"] = extractions
    return result


# ── Schedule Agent (CLI) ─────────────────────────────────────────────────

def empty_schedule_cli():
    """Default schedule when none available."""
    return {
        "week1_dates": "TBD", "week1_level": "TBD",
        "week1_activities": ["Schedule not available"],
        "week2_dates": "TBD", "week2_level": "TBD",
        "week2_activities": ["Schedule not available"],
        "week3_dates": "TBD", "week3_level": "TBD",
        "week3_activities": ["Schedule not available"],
        "planned_activities": ["Refer to project schedule"],
        "noise_index": "Moderate", "noise_level": "3/5",
        "special_considerations": ["Contact PM for schedule details"],
    }


async def process_schedule_cli(schedule_text: str, report_week_str: str) -> dict:
    """Parse 3-week look-ahead via CLI."""
    system = (PROMPTS_DIR / "schedule_extraction_system.md").read_text(encoding="utf-8")
    try:
        return await call_claude(
            prompt=(
                f"Extract the 3-week look-ahead data from this schedule. "
                f"The current report week is {report_week_str}. "
                f"Week 1 should be the week AFTER the report week.\n\n"
                f"Schedule text:\n{schedule_text}"
            ),
            system_prompt=system,
            model="haiku",
            json_schema=SCHEDULE_SCHEMA,
        )
    except Exception as e:
        print(f"  CLI schedule extraction failed: {e}")
        return empty_schedule_cli()


# ── Minutes Agent (CLI) ──────────────────────────────────────────────────

def empty_minutes_cli():
    """Default minutes when none available."""
    return {
        "critical_items": [],
        "milestones_mentioned": [],
        "coordination_items": [],
        "schedule_notes": "",
    }


async def process_minutes_cli(minutes_text: str) -> dict:
    """Extract meeting minutes via CLI."""
    system = (PROMPTS_DIR / "minutes_extraction_system.md").read_text(encoding="utf-8")
    try:
        return await call_claude(
            prompt=f"Extract key items from these OAC meeting minutes:\n\n{minutes_text}",
            system_prompt=system,
            model="haiku",
            json_schema=MINUTES_SCHEMA,
        )
    except Exception as e:
        print(f"  CLI minutes extraction failed: {e}")
        return empty_minutes_cli()


# ── Photo Selector (CLI) — Uses Read tool for vision ─────────────────────

async def select_photos_cli(candidate_photos: list, activities_completed: list[str],
                            num_photos: int = 2) -> dict:
    """Select and score photos via CLI using Read tool for image viewing."""
    if not candidate_photos:
        return {
            "photos": [], "photo_captions": [], "photo_scores": [],
            "mismatch_warning": "No candidate photos found for this week.",
        }

    candidates = candidate_photos[:4]
    system = (PROMPTS_DIR / "photo_selection_system.md").read_text(encoding="utf-8")

    # Build prompt with file paths for Claude to read
    activities_text = "\n".join(f"- {a}" for a in activities_completed)
    photo_list = "\n".join(
        f"Photo {i}: {path} (dated {d.isoformat()}, file: {os.path.basename(path)})"
        for i, (d, path) in enumerate(candidates)
    )

    prompt = (
        f"This week's completed activities:\n{activities_text}\n\n"
        f"Please read and analyze these {len(candidates)} candidate photos. "
        f"Use the Read tool to view each image, then score them.\n\n"
        f"{photo_list}"
    )

    # Determine the directory containing photos for --add-dir
    photo_dir = str(Path(candidates[0][1]).parent)

    try:
        result = await call_claude(
            prompt=prompt,
            system_prompt=system,
            model="sonnet",
            json_schema=PHOTO_SCORES_SCHEMA,
            tools="Read",
            allowed_tools="Read",
            add_dir=photo_dir,
            timeout=600,
        )
        scores = result.get("scores", [])
    except Exception as e:
        print(f"  CLI photo scoring failed: {e}")
        scores = []

    if not scores:
        selected = candidates[:num_photos]
        return {
            "photos": [p for _, p in selected],
            "photo_captions": ["Construction progress" for _ in selected],
            "photo_scores": [],
            "mismatch_warning": "Photo scoring failed, using most recent photos.",
        }

    scores.sort(key=lambda s: s.get("total_score", 0), reverse=True)
    selected_scores = scores[:num_photos]

    photos = []
    captions = []
    for s in selected_scores:
        idx = s["index"]
        if idx < len(candidates):
            photos.append(candidates[idx][1])
            captions.append(s["caption"])

    avg_score = sum(s.get("total_score", 0) for s in selected_scores) / max(len(selected_scores), 1)
    mismatch = None
    if avg_score < 2.5:
        mismatch = (
            f"Low photo match score ({avg_score:.1f}/5.0). "
            f"Available photos may not represent this week's activities well. "
            f"Consider taking new photos showing: "
            + ", ".join(activities_completed[:3])
        )

    return {
        "photos": photos,
        "photo_captions": captions,
        "photo_scores": scores,
        "mismatch_warning": mismatch,
    }


# ── Email Drafter (CLI) ──────────────────────────────────────────────────

async def draft_email_cli(report_data: dict, config: dict) -> dict:
    """Generate principal email via CLI."""
    system = (PROMPTS_DIR / "email_draft_system.md").read_text(encoding="utf-8")

    context = (
        f"Report #{report_data['report_number']} for week of {report_data['report_week']}\n"
        f"Phase: {report_data['phase']}\n"
        f"Progress: {report_data['overall_progress']}% Complete\n"
        f"Schedule: {report_data['schedule_status']}\n\n"
        f"Activities completed this week:\n"
        + "\n".join(f"- {a}" for a in report_data.get('activities_completed', []))
        + "\n\nMilestones:\n"
        + "\n".join(f"- {m}" for m in report_data.get('milestones_achieved', []))
        + "\n\nCritical items:\n"
        + "\n".join(f"- {c}" for c in report_data.get('critical_items', []))
        + "\n\nNext week planned:\n"
        + "\n".join(f"- {p}" for p in report_data.get('planned_activities', []))
        + f"\n\nNoise level next week: {report_data.get('noise_index', 'Moderate')}"
        + f"\nCountdown: {report_data.get('countdown_days', 'N/A')} calendar days remaining"
    )

    try:
        # Use opus for email (same as premium API setting)
        return await call_claude(
            prompt=f"Draft the principal email based on this week's data:\n\n{context}",
            system_prompt=system,
            model="opus",
            json_schema=EMAIL_SCHEMA,
            timeout=120,
        )
    except Exception as e:
        print(f"  CLI email draft failed: {e}")
        return {
            "subject": f"IUSD: Week #{report_data['report_number']} Construction Update - Bennett-Kew Project",
            "body": "(Email draft generation failed — please write manually)",
        }
