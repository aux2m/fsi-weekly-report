"""
Schedule Agent: Extracts 3-week impact matrix from look-ahead schedule PDF.
Uses Anthropic API (Haiku) for simple table parsing.
"""

from pathlib import Path
from anthropic import AsyncAnthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

SCHEDULE_TOOLS = [{
    "name": "schedule_data",
    "description": "Structured schedule extraction",
    "input_schema": {
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
}]


async def process_schedule(client: AsyncAnthropic, schedule_text: str,
                           report_week_str: str,
                           holidays: list[tuple] = None,
                           master_schedule_context: str = None) -> dict:
    """Extract 3-week impact data from schedule text + master schedule."""
    system = (PROMPTS_DIR / "schedule_extraction_system.md").read_text(encoding="utf-8")

    # Build holiday context if any fall in the 3-week window
    holiday_note = ""
    if holidays:
        holiday_lines = [f"  - {d.strftime('%m/%d')} ({d.strftime('%A')}): {name}"
                         for d, name in holidays]
        holiday_note = (
            "\n\nUpcoming holidays/school calendar events in the 3-week window:\n"
            + "\n".join(holiday_lines)
            + "\nInclude relevant holidays in special_considerations "
            "(e.g., no school impact on holiday, or adjusted work schedule)."
        )

    # Build master schedule section
    master_note = ""
    if master_schedule_context:
        master_note = f"\n\n{master_schedule_context}"

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=system,
        tools=SCHEDULE_TOOLS,
        tool_choice={"type": "tool", "name": "schedule_data"},
        messages=[{
            "role": "user",
            "content": (
                f"Extract the 3-week look-ahead data. "
                f"The current report week is {report_week_str}. "
                f"Remember: SIS Week 1 = current report week (skip it). "
                f"YOUR Week 1 = the week AFTER {report_week_str}.\n\n"
                f"SIS (Short Interval Schedule) text:\n{schedule_text}"
                f"{holiday_note}"
                f"{master_note}"
            )
        }],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return _empty_schedule()


def empty_schedule() -> dict:
    """Return empty schedule data when no schedule file found."""
    return _empty_schedule()


def _empty_schedule() -> dict:
    return {
        "week1_dates": "TBD", "week1_level": "MODERATE", "week1_activities": ["TBD"],
        "week2_dates": "TBD", "week2_level": "MODERATE", "week2_activities": ["TBD"],
        "week3_dates": "TBD", "week3_level": "MODERATE", "week3_activities": ["TBD"],
        "planned_activities": ["Activities to be determined from schedule"],
        "noise_index": "Moderate", "noise_level": "3/5",
        "special_considerations": ["Coordinate with school for campus activities"],
    }
