"""
Critical Items Agent: Reviews all extracted data and determines 0-2 critical items
from a senior PM perspective. Runs after all other extraction agents complete.
Uses Sonnet for strong judgment and instruction-following.
"""

from pathlib import Path
from anthropic import AsyncAnthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

CRITICAL_ITEMS_TOOLS = [{
    "name": "critical_items_assessment",
    "description": "PM assessment of critical items for stakeholder report",
    "input_schema": {
        "type": "object",
        "properties": {
            "critical_items": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 2,
            },
        },
        "required": ["critical_items"],
    }
}]


async def assess_critical_items(
    client: AsyncAnthropic,
    daily_result: dict,
    schedule_result: dict,
    minutes_result: dict,
    report_week_str: str,
    weather_context: str = None,
) -> list[str]:
    """Review all extracted data and return 0-2 critical items."""
    system = (PROMPTS_DIR / "critical_items_system.md").read_text(encoding="utf-8")

    # Build context from all sources
    sections = []

    # Project status
    progress = daily_result.get("overall_progress", "")
    status = daily_result.get("schedule_status", "")
    if progress:
        sections.append(f"PROJECT STATUS: {progress}% complete, {status}")

    # Activities completed this week
    activities = daily_result.get("activities_completed", [])
    if activities:
        sections.append("ACTIVITIES COMPLETED THIS WEEK:\n" +
                         "\n".join(f"- {a}" for a in activities))

    # 3-week schedule matrix
    for i in range(1, 4):
        dates = schedule_result.get(f"week{i}_dates", "")
        level = schedule_result.get(f"week{i}_level", "")
        acts = schedule_result.get(f"week{i}_activities", [])
        if dates and dates != "TBD":
            sections.append(
                f"WEEK {i} ({dates}) — Impact: {level}\n" +
                "\n".join(f"- {a}" for a in acts))

    # Schedule notes from minutes
    schedule_notes = minutes_result.get("schedule_notes", "")
    if schedule_notes:
        sections.append(f"SCHEDULE NOTES FROM OAC MEETING:\n{schedule_notes}")

    # Coordination items from minutes
    coord = minutes_result.get("coordination_items", [])
    if coord:
        sections.append("COORDINATION ITEMS FROM OAC MEETING:\n" +
                         "\n".join(f"- {c}" for c in coord))

    # Upcoming schedule (3-week look-ahead)
    planned = schedule_result.get("planned_activities", [])
    if planned:
        sections.append("PLANNED ACTIVITIES NEXT WEEK:\n" +
                         "\n".join(f"- {p}" for p in planned))

    # Special considerations from schedule
    special = schedule_result.get("special_considerations", [])
    if special:
        sections.append("SPECIAL CONSIDERATIONS:\n" +
                         "\n".join(f"- {s}" for s in special))

    # Issues from daily extractions
    daily_extractions = daily_result.get("_daily_extractions", [])
    all_issues = []
    for ext in daily_extractions:
        all_issues.extend(ext.get("issues", []))
    if all_issues:
        sections.append("ISSUES NOTED IN DAILY REPORTS:\n" +
                         "\n".join(f"- {i}" for i in all_issues))

    # Weather conflict (only present when there IS a conflict)
    if weather_context:
        sections.append(weather_context)

    context = "\n\n".join(sections)

    response = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=500,
        system=system,
        tools=CRITICAL_ITEMS_TOOLS,
        tool_choice={"type": "tool", "name": "critical_items_assessment"},
        messages=[{
            "role": "user",
            "content": (
                f"Review the following data for the week of {report_week_str} "
                f"and determine if there are any critical items (0-2) worth "
                f"reporting to the school principal and district.\n\n{context}"
            )
        }],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input.get("critical_items", [])
    return []
