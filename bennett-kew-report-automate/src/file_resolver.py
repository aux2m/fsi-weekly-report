"""
File resolver: finds the correct input files from NAS paths based on report week dates.
"""

import os
import re
from pathlib import Path
from datetime import date, timedelta
from dataclasses import dataclass, field

from .calendar_utils import ReportWeek, weekday_dates


@dataclass
class ResolvedFiles:
    daily_reports: list[tuple[date, str]] = field(default_factory=list)
    schedule: str = None
    minutes: str = None
    candidate_photos: list[tuple[date, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def resolve_daily_reports(daily_dir: str, rw: ReportWeek) -> list[tuple[date, str]]:
    """Find daily report PDFs matching the 5 weekday dates."""
    found = []
    if not os.path.isdir(daily_dir):
        return found

    dates = weekday_dates(rw)
    files = os.listdir(daily_dir)

    for d in dates:
        # Pattern: Bennett_Kew_Site_Improvements_-_Daily_Report_-MM-DD-YYYY.pdf
        mm_dd_yyyy = f"{d.month:02d}-{d.day:02d}-{d.year}"
        target_name = f"Bennett_Kew_Site_Improvements_-_Daily_Report_-{mm_dd_yyyy}.pdf"

        if target_name in files:
            found.append((d, os.path.join(daily_dir, target_name)))
        else:
            # Try alternate patterns
            date_strs = [
                f"{d.month:02d}-{d.day:02d}-{d.year}",
                f"{d.month}-{d.day}-{d.year}",
                f"{d.year}{d.month:02d}{d.day:02d}",
                f"{d.year}-{d.month:02d}-{d.day:02d}",
            ]
            matched = False
            for f_name in files:
                if f_name.lower().endswith('.pdf'):
                    for ds in date_strs:
                        if ds in f_name:
                            found.append((d, os.path.join(daily_dir, f_name)))
                            matched = True
                            break
                    if matched:
                        break

    return found


def parse_schedule_date(filename: str) -> date:
    """Extract date from schedule filename.
    Patterns: '26-02-02' (YY-MM-DD) or '10-20-25' (MM-DD-YY)
    """
    # Extract date portion from filename
    m = re.search(r'(\d{2})-(\d{2})-(\d{2,4})', filename)
    if not m:
        return None
    a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))

    # If first number > 12, it's YY-MM-DD format
    if a > 12:
        year = 2000 + a if a < 100 else a
        return date(year, b, c)
    # If third number > 31, it's MM-DD-YY format
    elif c > 31:
        year = 2000 + c if c < 100 else c
        return date(year, a, b)
    # If third is 2-digit and looks like a year (25, 26)
    elif c >= 25 and c <= 30:
        return date(2000 + c, a, b)
    # Default: assume YY-MM-DD for recent files
    elif a >= 25 and a <= 30:
        return date(2000 + a, b, c)
    else:
        # Try MM-DD-YY
        try:
            return date(2000 + c, a, b)
        except ValueError:
            return None


def resolve_schedule(sched_dir: str, rw: ReportWeek) -> str:
    """Find the latest 3-week look-ahead schedule in the folder."""
    if not os.path.isdir(sched_dir):
        return None

    candidates = []
    for f in os.listdir(sched_dir):
        if not f.lower().endswith('.pdf') or 'Look Ahead' not in f:
            continue
        d = parse_schedule_date(f)
        if d:
            candidates.append((d, os.path.join(sched_dir, f)))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    return None


def parse_minutes_date(filename: str) -> date:
    """Extract date from minutes filename: IUSD_Bennett-Kew OAC Meeting Minutes_YYYY.MM.DD.pdf"""
    m = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def resolve_minutes(mins_dir: str, rw: ReportWeek) -> str:
    """Find the most recent meeting minutes on or before report Friday.
    Prefer clean version over 'w PCN3' annotated.
    """
    if not os.path.isdir(mins_dir):
        return None

    candidates = []
    for f in os.listdir(mins_dir):
        if not f.lower().endswith('.pdf'):
            continue
        d = parse_minutes_date(f)
        if d and d <= rw.friday:
            # Score: clean=1, annotated=0
            clean = 0 if 'PCN3' in f else 1
            candidates.append((d, clean, os.path.join(mins_dir, f)))

    if candidates:
        # Sort by date desc, then prefer clean
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return candidates[0][2]
    return None


def parse_photo_date(filename: str) -> date:
    """Extract date from photo filename. Multiple patterns supported."""
    # YYYYMMDD.NN.jpg
    m = re.match(r'^(\d{4})(\d{2})(\d{2})\.\d+\.', filename)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # YYYYMMDD_HHMMSS.jpg
    m = re.match(r'^(\d{4})(\d{2})(\d{2})_\d{6}\.', filename)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # YYYY.MM.DD.NN.jpg
    m = re.match(r'^(\d{4})\.(\d{2})\.(\d{2})\.\d+\.', filename)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    return None


def resolve_photos(photos_dir: str, rw: ReportWeek, max_candidates: int = 10) -> list[tuple[date, str]]:
    """Find candidate photos, preferring report week, expanding if needed."""
    if not os.path.isdir(photos_dir):
        return []

    extensions = {'.jpg', '.jpeg', '.png'}
    all_photos = []

    for f in os.listdir(photos_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext not in extensions:
            continue
        d = parse_photo_date(f)
        full_path = os.path.join(photos_dir, f)
        if d:
            all_photos.append((d, full_path))
        else:
            # Use file modification time as fallback
            mtime = date.fromtimestamp(os.path.getmtime(full_path))
            all_photos.append((mtime, full_path))

    # Filter to report week first
    week_start = rw.monday
    week_end = rw.friday
    week_photos = [(d, p) for d, p in all_photos if week_start <= d <= week_end]

    if len(week_photos) >= 2:
        week_photos.sort(key=lambda x: x[0], reverse=True)
        return week_photos[:max_candidates]

    # Expand to prior 2 weeks
    expanded_start = week_start - timedelta(days=14)
    expanded = [(d, p) for d, p in all_photos if expanded_start <= d <= week_end]
    expanded.sort(key=lambda x: x[0], reverse=True)
    return expanded[:max_candidates]


def resolve_all_files(config: dict, rw: ReportWeek) -> ResolvedFiles:
    """Resolve all input files for a report week."""
    paths = config['paths']
    result = ResolvedFiles()

    # Daily reports
    result.daily_reports = resolve_daily_reports(paths['daily_reports_dir'], rw)
    missing_days = set(weekday_dates(rw)) - {d for d, _ in result.daily_reports}
    if missing_days:
        for d in sorted(missing_days):
            result.warnings.append(f"Missing daily report for {d.strftime('%A %m/%d')}")

    # Schedule
    result.schedule = resolve_schedule(paths['schedules_dir'], rw)
    if not result.schedule:
        result.warnings.append("No 3-week look-ahead schedule found")

    # Minutes
    result.minutes = resolve_minutes(paths['minutes_dir'], rw)
    if not result.minutes:
        result.warnings.append("No meeting minutes found")

    # Photos
    result.candidate_photos = resolve_photos(paths['photos_dir'], rw)
    if len(result.candidate_photos) < 2:
        result.warnings.append(f"Only {len(result.candidate_photos)} candidate photos found")

    return result
