"""
Daily Report Agent: Processes 5 daily reports ONE AT A TIME, then synthesizes into weekly summary.
Uses Anthropic API (Sonnet) for construction domain knowledge.
"""

import json
import asyncio
from pathlib import Path
from anthropic import AsyncAnthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


EXTRACT_TOOLS = [{
    "name": "extract_daily_data",
    "description": "Extract structured data from a daily construction report",
    "input_schema": {
        "type": "object",
        "properties": {
            "date": {"type": "string", "description": "Report date"},
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
}]

SYNTHESIS_TOOLS = [{
    "name": "weekly_synthesis",
    "description": "Synthesize 5 daily reports into weekly summary",
    "input_schema": {
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
}]


async def extract_single_day(client: AsyncAnthropic, text: str, day_label: str) -> dict:
    """Extract data from one daily report. Sequential to manage tokens."""
    system = _load_prompt("daily_report_system.md")
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",  # Haiku for extraction (Sonnet reserved for synthesis)
        max_tokens=1500,
        system=system,
        tools=EXTRACT_TOOLS,
        tool_choice={"type": "tool", "name": "extract_daily_data"},
        messages=[{
            "role": "user",
            "content": f"Extract data from this {day_label} daily report:\n\n{text}"
        }],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return {"date": day_label, "activities": [], "error": "No extraction"}


async def synthesize_week(client: AsyncAnthropic, daily_extractions: list[dict],
                          report_week: str) -> dict:
    """Combine 5 daily extractions into weekly narrative summary."""
    system = _load_prompt("weekly_synthesis_system.md")

    # Build summary of all 5 days
    days_text = ""
    for ext in daily_extractions:
        days_text += f"\n--- {ext.get('date', 'Unknown')} ---\n"
        days_text += f"Activities: {'; '.join(ext.get('activities', []))}\n"
        days_text += f"Equipment: {', '.join(ext.get('equipment', []))}\n"
        days_text += f"Issues: {'; '.join(ext.get('issues', []))}\n"
        days_text += f"Testing: {'; '.join(ext.get('testing', []))}\n"
        days_text += f"Weather: {ext.get('weather', 'N/A')}\n"
        days_text += f"Coordination: {'; '.join(ext.get('coordination', []))}\n"

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system,
        tools=SYNTHESIS_TOOLS,
        tool_choice={"type": "tool", "name": "weekly_synthesis"},
        messages=[{
            "role": "user",
            "content": (
                f"Synthesize these 5 daily reports for the week of {report_week} "
                f"into a weekly progress summary:\n{days_text}"
            )
        }],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return {"error": "No synthesis", "activities_completed": []}


async def process_daily_reports(client: AsyncAnthropic, daily_texts: list[dict],
                                report_week_str: str) -> dict:
    """
    Main entry: process 5 daily reports sequentially, then synthesize.
    daily_texts: list of dicts from pdf_extractor.extract_daily_report()
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    extractions = []

    for i, dt in enumerate(daily_texts):
        day_label = day_names[i] if i < len(day_names) else f"Day {i+1}"
        print(f"  Extracting {day_label}: {dt['filename']}")
        ext = await extract_single_day(client, dt["full_text"], day_label)
        extractions.append(ext)

    print("  Synthesizing weekly summary...")
    result = await synthesize_week(client, extractions, report_week_str)
    result["_daily_extractions"] = extractions  # keep for audit
    return result
