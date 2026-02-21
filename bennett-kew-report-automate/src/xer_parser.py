"""
XER Parser: Extracts construction activities from Primavera P6 XER export files.
Used as a supplement to the Short Interval Schedule (SIS) when the SIS doesn't
cover all 3 weeks of the report look-ahead.
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ScheduleActivity:
    task_code: str
    task_name: str
    wbs_category: str  # e.g. "Structure", "Foundation Level", "MEP"
    early_start: date
    early_end: date
    status: str  # "Not Started", "Active", "Complete"


def parse_xer(xer_path: str | Path) -> list[ScheduleActivity]:
    """Parse a P6 XER file and return construction activities."""
    xer_path = Path(xer_path)
    if not xer_path.exists():
        print(f"  WARNING: XER file not found: {xer_path}")
        return []

    text = xer_path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    # Parse tables we need: PROJWBS and TASK
    wbs_map = {}  # wbs_id -> wbs_name
    tasks = []
    current_table = None
    fields = []

    for line in lines:
        line = line.rstrip("\r")
        if line.startswith("%T\t"):
            current_table = line.split("\t")[1]
            fields = []
        elif line.startswith("%F\t"):
            fields = line.split("\t")[1:]
        elif line.startswith("%R\t") and fields:
            values = line.split("\t")[1:]
            row = dict(zip(fields, values))

            if current_table == "PROJWBS":
                wbs_id = row.get("wbs_id", "")
                wbs_name = row.get("wbs_name", "")
                wbs_map[wbs_id] = wbs_name

            elif current_table == "TASK":
                tasks.append(row)

    # Construction WBS IDs (Building and its children, plus site work)
    construction_wbs = set()
    for wbs_id, name in wbs_map.items():
        name_lower = name.lower()
        if any(kw in name_lower for kw in [
            "foundation", "structure", "roof level", "mep",
            "finishes", "exteriors", "demo", "building",
            "site improvements", "external site", "close out",
            "testing", "commissioning",
        ]):
            construction_wbs.add(wbs_id)

    # Status mapping
    status_map = {
        "TK_Complete": "Complete",
        "TK_Active": "Active",
        "TK_NotStart": "Not Started",
    }

    # Parse tasks into activities
    activities = []
    for row in tasks:
        wbs_id = row.get("wbs_id", "")
        if wbs_id not in construction_wbs:
            continue

        # Skip milestones and LOE tasks
        task_type = row.get("task_type", "")
        if task_type in ("TT_Mile", "TT_FinMile", "TT_LOE"):
            continue

        status = status_map.get(row.get("status_code", ""), "Unknown")

        # Parse dates (early_start_date and early_end_date)
        start_str = row.get("early_start_date", "")
        end_str = row.get("early_end_date", "")
        if not start_str or not end_str:
            continue

        try:
            early_start = datetime.strptime(start_str.split()[0], "%Y-%m-%d").date()
            early_end = datetime.strptime(end_str.split()[0], "%Y-%m-%d").date()
        except (ValueError, IndexError):
            continue

        activities.append(ScheduleActivity(
            task_code=row.get("task_code", ""),
            task_name=row.get("task_name", ""),
            wbs_category=wbs_map.get(wbs_id, "Unknown"),
            early_start=early_start,
            early_end=early_end,
            status=status,
        ))

    return activities


def get_activities_for_week(activities: list[ScheduleActivity],
                            week_start: date, week_end: date) -> list[ScheduleActivity]:
    """Return activities that overlap with a given week (Mon-Fri)."""
    result = []
    for act in activities:
        if act.status == "Complete":
            continue
        # Activity overlaps the week if it starts before week ends AND ends after week starts
        if act.early_start <= week_end and act.early_end >= week_start:
            result.append(act)
    # Sort by start date, then by name
    result.sort(key=lambda a: (a.early_start, a.task_name))
    return result


def format_master_schedule_context(xer_path: str | Path,
                                    week_start: date,
                                    num_weeks: int = 3) -> str:
    """Parse XER and format activities for the next N weeks as context text.

    Returns a formatted string showing activities per week that can be
    appended to the schedule agent's prompt.
    """
    activities = parse_xer(xer_path)
    if not activities:
        return ""

    sections = []
    sections.append("MASTER SCHEDULE REFERENCE (from Primavera P6):")
    sections.append("Use this as a reference for activities not covered by the SIS.\n")

    current = week_start
    for i in range(num_weeks):
        w_start = current
        w_end = w_start + timedelta(days=4)  # Mon-Fri
        week_acts = get_activities_for_week(activities, w_start, w_end)

        week_label = f"Week {i+1} ({w_start.strftime('%m/%d')}–{w_end.strftime('%m/%d')})"
        if week_acts:
            lines = [f"  {week_label}:"]
            for act in week_acts:
                dur = f"{act.early_start.strftime('%m/%d')}–{act.early_end.strftime('%m/%d')}"
                lines.append(f"    - {act.task_name} [{dur}] ({act.wbs_category})")
            sections.append("\n".join(lines))
        else:
            sections.append(f"  {week_label}: No activities scheduled")

        current += timedelta(weeks=1)

    return "\n".join(sections)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m src.xer_parser <path_to_xer> [start_date YYYY-MM-DD]")
        sys.exit(1)

    xer = sys.argv[1]
    start = date.today()
    if len(sys.argv) > 2:
        start = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
    # Align to Monday
    start = start - timedelta(days=start.weekday())

    print(format_master_schedule_context(xer, start, num_weeks=4))
