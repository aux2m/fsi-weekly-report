"""
Email Drafter: Generates principal email from report data.
Uses Anthropic API (Opus) for premium-tone generation.
NEVER sends email — saves to file for review.
"""

from pathlib import Path
from anthropic import AsyncAnthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

EMAIL_TOOLS = [{
    "name": "email_draft",
    "description": "Draft principal email",
    "input_schema": {
        "type": "object",
        "properties": {
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["subject", "body"],
    }
}]


async def draft_email(client: AsyncAnthropic, report_data: dict,
                      config: dict) -> dict:
    """Generate principal email from assembled report data."""
    system = (PROMPTS_DIR / "email_draft_system.md").read_text(encoding="utf-8")

    # Build context for email generation
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

    response = await client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        system=system,
        tools=EMAIL_TOOLS,
        tool_choice={"type": "tool", "name": "email_draft"},
        messages=[{
            "role": "user",
            "content": f"Draft the principal email based on this week's data:\n\n{context}"
        }],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input

    return {
        "subject": f"IUSD: Week #{report_data['report_number']} Construction Update - Bennett-Kew Project",
        "body": "(Email draft generation failed — please write manually)"
    }
