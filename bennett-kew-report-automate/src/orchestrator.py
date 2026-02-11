"""
Orchestrator: Main async pipeline tying all stages together.
"""

import os
import sys
import json
import time
import shutil
import asyncio
from pathlib import Path
from anthropic import AsyncAnthropic

from .calendar_utils import get_report_week, ReportWeek
from .file_resolver import resolve_all_files, ResolvedFiles
from .pdf_extractor import extract_daily_report, extract_schedule_table, extract_meeting_minutes
from .daily_report_agent import process_daily_reports
from .schedule_agent import process_schedule, empty_schedule
from .minutes_agent import process_minutes, empty_minutes
from .photo_selector import select_photos
from .json_assembler import assemble_json
from .email_drafter import draft_email

PROJECT_ROOT = Path(__file__).parent.parent
PDF_GENERATOR_DIR = None  # Set from config


def _load_config(config_name: str) -> dict:
    """Load project config from config/ directory."""
    config_path = PROJECT_ROOT / "config" / f"{config_name}.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def _print_header(rw: ReportWeek):
    print("=" * 56)
    print(f"  Bennett-Kew Weekly Report #{rw.report_number:02d}")
    print(f"  Week: {rw.report_week_str}")
    print(f"  Issued: {rw.issued_date_str}")
    print(f"  Countdown: {rw.countdown_days} calendar days")
    print("=" * 56)


def _print_files(files: ResolvedFiles):
    print(f"\nInput files resolved:")
    print(f"  Daily reports: {len(files.daily_reports)}/5 found")
    for d, p in files.daily_reports:
        print(f"    {d.strftime('%A %m/%d')}: {os.path.basename(p)}")
    print(f"  Schedule: {'Found' if files.schedule else 'MISSING'}")
    if files.schedule:
        print(f"    {os.path.basename(files.schedule)}")
    print(f"  Minutes: {'Found' if files.minutes else 'MISSING'}")
    if files.minutes:
        print(f"    {os.path.basename(files.minutes)}")
    print(f"  Candidate photos: {len(files.candidate_photos)}")
    if files.warnings:
        print(f"\n  WARNINGS:")
        for w in files.warnings:
            print(f"    ! {w}")


def _generate_pdf(config: dict, report_data: dict, rw: ReportWeek,
                  output_dir: Path) -> str:
    """Import and run the existing PDF generator."""
    pdf_gen_dir = Path(config["paths"]["pdf_generator_dir"])
    sys.path.insert(0, str(pdf_gen_dir / "src"))
    from generate_report import generate_report, SAMPLE_DATA

    merged = {**SAMPLE_DATA, **report_data}
    output_path = output_dir / f"Weekly_Progress_Report_{rw.report_number:02d}.pdf"
    generate_report(merged, str(output_path))
    return str(output_path)


async def run_pipeline(config_name: str = "bennett_kew",
                       target_date: str = None,
                       report_number: int = None,
                       skip_email: bool = False,
                       skip_photos: bool = False,
                       dry_run: bool = False,
                       debug: bool = False,
                       backend: str = "api") -> dict:
    """
    Main pipeline entry point.
    backend: "api" (direct Anthropic API) or "cli" (Claude CLI subprocess)
    Returns dict with generated file paths and summary.
    """
    start_time = time.time()

    # ── Stage 0: Load config + calendar validation ───────────────────────
    config = _load_config(config_name)
    constants = config["constants"]

    rw = get_report_week(
        target_date=target_date,
        report_number=report_number,
        start_date=constants.get("report_start_date"),
        completion_date=constants.get("substantial_completion_date"),
    )
    _print_header(rw)
    print(f"  Backend: {backend.upper()}")

    # ── Stage 1: File resolution ─────────────────────────────────────────
    print("\nStage 1: Resolving input files...")
    files = resolve_all_files(config, rw)
    _print_files(files)

    if not files.daily_reports:
        print("\nFATAL: No daily reports found. Cannot generate report.")
        return {"error": "No daily reports found"}

    # ── Stage 2: PDF text extraction ─────────────────────────────────────
    print("\nStage 2: Extracting PDF text...")
    daily_texts = []
    for d, path in files.daily_reports:
        print(f"  Extracting {d.strftime('%A')}: {os.path.basename(path)}")
        daily_texts.append(extract_daily_report(path))

    schedule_text = None
    if files.schedule:
        print(f"  Extracting schedule: {os.path.basename(files.schedule)}")
        schedule_text = extract_schedule_table(files.schedule)

    minutes_text = None
    if files.minutes:
        print(f"  Extracting minutes: {os.path.basename(files.minutes)}")
        minutes_text = extract_meeting_minutes(files.minutes)

    # ── Stage 3: AI content extraction (parallel where possible) ─────────
    print(f"\nStage 3: AI content extraction ({backend.upper()})...")

    if backend == "cli":
        from .cli_agents import (
            process_daily_reports_cli,
            process_schedule_cli, empty_schedule_cli,
            process_minutes_cli, empty_minutes_cli,
            select_photos_cli,
            draft_email_cli,
        )
        print("  Starting parallel CLI agents...")

        async def _get_schedule():
            if schedule_text:
                return await process_schedule_cli(schedule_text, rw.report_week_str)
            return empty_schedule_cli()

        async def _get_minutes():
            if minutes_text:
                return await process_minutes_cli(minutes_text)
            return empty_minutes_cli()

        daily_result, schedule_result, minutes_result = await asyncio.gather(
            process_daily_reports_cli(daily_texts, rw.report_week_str),
            _get_schedule(),
            _get_minutes(),
        )
    else:
        client = AsyncAnthropic()
        print("  Starting parallel API agents...")

        async def _get_schedule():
            if schedule_text:
                return await process_schedule(client, schedule_text, rw.report_week_str)
            return empty_schedule()

        async def _get_minutes():
            if minutes_text:
                return await process_minutes(client, minutes_text)
            return empty_minutes()

        daily_result, schedule_result, minutes_result = await asyncio.gather(
            process_daily_reports(client, daily_texts, rw.report_week_str),
            _get_schedule(),
            _get_minutes(),
        )
    print("  AI extraction complete.")

    if debug:
        _save_debug(daily_result, "daily_result", rw)
        _save_debug(schedule_result, "schedule_result", rw)
        _save_debug(minutes_result, "minutes_result", rw)

    # ── Stage 4: Photo selection ─────────────────────────────────────────
    photo_result = {"photos": [], "photo_captions": [], "photo_scores": [], "mismatch_warning": None}
    if not skip_photos and files.candidate_photos:
        print(f"\nStage 4: Photo selection ({backend.upper()})...")
        activities = daily_result.get("activities_completed", [])
        num_photos = config["constants"].get("photos_per_report", 2)
        if backend == "cli":
            photo_result = await select_photos_cli(
                files.candidate_photos, activities, num_photos=num_photos
            )
        else:
            photo_result = await select_photos(
                client, files.candidate_photos, activities, num_photos=num_photos
            )
        if photo_result.get("mismatch_warning"):
            print(f"  PHOTO WARNING: {photo_result['mismatch_warning']}")
        else:
            for i, cap in enumerate(photo_result.get("photo_captions", [])):
                print(f"  Photo {i+1}: {cap}")
    else:
        print("\nStage 4: Skipping photo selection")

    # ── Stage 5: JSON assembly ───────────────────────────────────────────
    print("\nStage 5: Assembling report data...")
    report_data = assemble_json(config, rw, daily_result, schedule_result,
                                minutes_result, photo_result)

    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)

    # Save assembled JSON (audit trail)
    json_path = output_dir / f"report_data_{rw.report_number:02d}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, default=str)
    print(f"  Saved: {json_path.name}")

    # Save photo selections
    if photo_result.get("photo_scores"):
        photo_log = output_dir / f"photo_selections_{rw.report_number:02d}.json"
        with open(photo_log, "w", encoding="utf-8") as f:
            json.dump(photo_result, f, indent=2, default=str)

    if dry_run:
        print("\nDRY RUN: Skipping PDF generation and email.")
        return {"report_data": report_data, "json_path": str(json_path)}

    # ── Stage 6: PDF generation ──────────────────────────────────────────
    print("\nStage 6: Generating PDF...")
    pdf_path = _generate_pdf(config, report_data, rw, output_dir)
    print(f"  Generated: {os.path.basename(pdf_path)}")

    # ── Stage 7: Email draft ─────────────────────────────────────────────
    email_path = None
    if not skip_email:
        print(f"\nStage 7: Drafting principal email ({backend.upper()})...")
        if backend == "cli":
            email_result = await draft_email_cli(report_data, config)
        else:
            email_result = await draft_email(client, report_data, config)
        email_path = output_dir / f"principal_email_{rw.report_number:02d}.txt"
        with open(email_path, "w", encoding="utf-8") as f:
            f.write(f"Subject: {email_result['subject']}\n\n")
            f.write(email_result['body'])
        print(f"  Saved: {email_path.name}")
    else:
        print("\nStage 7: Skipping email draft")

    # ── Stage 8: Summary ─────────────────────────────────────────────────
    elapsed = time.time() - start_time
    print("\n" + "=" * 56)
    print(f"  REPORT GENERATION COMPLETE")
    print(f"  Duration: {elapsed:.1f} seconds")
    print("=" * 56)
    print(f"\nGenerated files:")
    print(f"  PDF:   {pdf_path}")
    print(f"  Data:  {json_path}")
    if email_path:
        print(f"  Email: {email_path}")

    if photo_result.get("photo_captions"):
        print(f"\nPhoto selections:")
        for i, cap in enumerate(photo_result["photo_captions"]):
            score = photo_result["photo_scores"][i] if i < len(photo_result.get("photo_scores", [])) else {}
            s = score.get("total_score", "N/A")
            print(f"  Photo {i+1}: {os.path.basename(photo_result['photos'][i])}  [Score: {s}]")
            print(f"           Caption: \"{cap}\"")

    if files.warnings:
        print(f"\nWarnings:")
        for w in files.warnings:
            print(f"  ! {w}")
    if photo_result.get("mismatch_warning"):
        print(f"  ! PHOTOS: {photo_result['mismatch_warning']}")

    print(f"\nNext steps:")
    print(f"  1. Review PDF for accuracy")
    if email_path:
        print(f"  2. Review {email_path.name}")
        print(f"  3. Send email when ready")
    print()

    return {
        "pdf_path": pdf_path,
        "json_path": str(json_path),
        "email_path": str(email_path) if email_path else None,
        "report_number": rw.report_number,
        "duration": elapsed,
        "warnings": files.warnings,
    }


def _save_debug(data: dict, name: str, rw: ReportWeek):
    """Save intermediate result for debugging."""
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    path = output_dir / f"debug_{name}_{rw.report_number:02d}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  [debug] Saved: {path.name}")
