"""
Minutes Agent: Extracts critical items, milestones, and coordination items from meeting minutes.
Uses Anthropic API (Haiku) for simple text extraction.
"""

from pathlib import Path
from anthropic import AsyncAnthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

MINUTES_TOOLS = [{
    "name": "minutes_data",
    "description": "Structured meeting minutes extraction",
    "input_schema": {
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
}]


async def process_minutes(client: AsyncAnthropic, minutes_text: str) -> dict:
    """Extract key information from meeting minutes text."""
    system = (PROMPTS_DIR / "minutes_extraction_system.md").read_text(encoding="utf-8")

    response = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1000,
        system=system,
        tools=MINUTES_TOOLS,
        tool_choice={"type": "tool", "name": "minutes_data"},
        messages=[{
            "role": "user",
            "content": f"Extract key items from these OAC meeting minutes:\n\n{minutes_text}"
        }],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return empty_minutes()


def empty_minutes() -> dict:
    return {
        "critical_items": [],
        "milestones_mentioned": [],
        "coordination_items": [],
        "schedule_notes": "",
    }
