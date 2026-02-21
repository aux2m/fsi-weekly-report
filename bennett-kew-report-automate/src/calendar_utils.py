"""
Calendar utilities for report week calculation and date validation.
ALWAYS runs first in the pipeline to establish canonical dates.
"""

from datetime import date, datetime, timedelta
from dataclasses import dataclass


@dataclass
class ReportWeek:
    monday: date
    tuesday: date
    wednesday: date
    thursday: date
    friday: date
    report_week_str: str      # "MM/DD—MM/DD"
    issued_date_str: str      # "Friday, Month D, YYYY"
    countdown_days: int
    report_number: int


SUBSTANTIAL_COMPLETION = date(2026, 8, 9)
REPORT_START = date(2025, 9, 15)  # Week 1 Monday


def get_report_week(target_date: str = None, report_number: int = None,
                    start_date: str = None, completion_date: str = None) -> ReportWeek:
    """
    Determine the canonical report week from a target date.
    target_date: YYYY-MM-DD string, defaults to most recent Friday.
    """
    if completion_date:
        sc = datetime.strptime(completion_date, "%Y-%m-%d").date()
    else:
        sc = SUBSTANTIAL_COMPLETION

    if start_date:
        rs = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        rs = REPORT_START

    if target_date:
        friday = datetime.strptime(target_date, "%Y-%m-%d").date()
        # If not a Friday, find the Friday of that week
        if friday.weekday() != 4:
            days_to_friday = (4 - friday.weekday()) % 7
            if days_to_friday == 0:
                days_to_friday = 7
            friday = friday + timedelta(days=days_to_friday)
            # If target is past Friday, use previous Friday
            if friday > datetime.strptime(target_date, "%Y-%m-%d").date() + timedelta(days=6):
                friday -= timedelta(days=7)
    else:
        today = date.today()
        days_since_friday = (today.weekday() - 4) % 7
        friday = today - timedelta(days=days_since_friday)

    monday = friday - timedelta(days=4)
    tuesday = friday - timedelta(days=3)
    wednesday = friday - timedelta(days=2)
    thursday = friday - timedelta(days=1)

    # Report week string: MM/DD—MM/DD
    report_week_str = f"{monday.strftime('%m/%d')}\u2014{friday.strftime('%m/%d')}"

    # Issued date: "Friday, Month D, YYYY"
    issued_date_str = f"Friday, {friday.strftime('%B')} {friday.day}, {friday.year}"

    # Countdown
    countdown = (sc - friday).days

    # Report number: weeks since start date
    if report_number is not None:
        rn = report_number
    else:
        weeks = (friday - rs).days // 7
        rn = max(1, weeks + 1)

    return ReportWeek(
        monday=monday,
        tuesday=tuesday,
        wednesday=wednesday,
        thursday=thursday,
        friday=friday,
        report_week_str=report_week_str,
        issued_date_str=issued_date_str,
        countdown_days=countdown,
        report_number=rn,
    )


def weekday_dates(rw: ReportWeek) -> list[date]:
    """Return all 5 weekday dates."""
    return [rw.monday, rw.tuesday, rw.wednesday, rw.thursday, rw.friday]


# School/federal holidays relevant to IUSD calendar (2025-2026 school year)
KNOWN_HOLIDAYS = {
    date(2025, 9, 1): "Labor Day",
    date(2025, 11, 11): "Veterans Day",
    date(2025, 11, 27): "Thanksgiving",
    date(2025, 11, 28): "Thanksgiving break",
    date(2025, 12, 22): "Winter break begins",
    date(2026, 1, 5): "Winter break ends",
    date(2026, 1, 19): "Martin Luther King Jr. Day",
    date(2026, 2, 16): "Presidents' Day",
    date(2026, 3, 30): "Spring break begins",
    date(2026, 4, 3): "Spring break ends",
    date(2026, 5, 25): "Memorial Day",
    date(2026, 6, 11): "Last day of school",
    date(2026, 7, 3): "Independence Day (observed)",
}


def upcoming_holidays(rw: ReportWeek, weeks_ahead: int = 3) -> list[tuple[date, str]]:
    """Return holidays falling within the next N weeks after report Friday."""
    start = rw.friday + timedelta(days=1)
    end = start + timedelta(weeks=weeks_ahead)
    return [(d, name) for d, name in sorted(KNOWN_HOLIDAYS.items())
            if start <= d <= end]


if __name__ == "__main__":
    rw = get_report_week("2026-02-06")
    print(f"Report Week: {rw.report_week_str}")
    print(f"Issued: {rw.issued_date_str}")
    print(f"Countdown: {rw.countdown_days} days")
    print(f"Report #: {rw.report_number}")
    print(f"Mon-Fri: {rw.monday} to {rw.friday}")
