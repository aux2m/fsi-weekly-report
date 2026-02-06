#!/usr/bin/env python3
"""
run_report.py — CLI wrapper for the Bennett-Kew Weekly Progress Report Generator.

Automatically resolves logo and photo paths relative to this project's root directory,
so you can run from anywhere without copying assets around.

Usage:
  python run_report.py                                          # Sample data, default output
  python run_report.py examples/sample_data.json                # Custom data
  python run_report.py data.json --output Report_03.pdf         # Custom data + output
  python run_report.py data.json --photos ./this_weeks_photos/  # Custom photo directory
"""

import sys
import os
import json
import glob
import argparse
from pathlib import Path

# Resolve project root (where this script lives)
PROJECT_ROOT = Path(__file__).resolve().parent

# Add src to path
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from generate_report import generate_report, SAMPLE_DATA


def resolve_asset_paths(data: dict, photos_dir: str = None) -> dict:
    """
    Resolve logo and photo paths relative to project root.
    If paths in data are relative and don't exist, try finding them in standard locations.
    """
    resolved = dict(data)
    
    # ── Resolve logo paths ──────────────────────────────────────────────
    logo_dir = PROJECT_ROOT / "assets" / "logos"
    logo_map = {
        "logo_fs": "fs_logo.png",
        "logo_bk": "bk_logo.jpg",
        "logo_iusd": "iusd_logo.jpg",
    }
    for key, default_name in logo_map.items():
        current = resolved.get(key, default_name)
        if not os.path.isabs(current) and not os.path.exists(current):
            candidate = logo_dir / default_name
            if candidate.exists():
                resolved[key] = str(candidate)
    
    # ── Resolve photo paths ─────────────────────────────────────────────
    photos_path = Path(photos_dir) if photos_dir else PROJECT_ROOT / "photos"
    if photos_path.exists():
        photo_files = (
            glob.glob(str(photos_path / "*.jpg")) +
            glob.glob(str(photos_path / "*.jpeg")) +
            glob.glob(str(photos_path / "*.png"))
        )
        # Sort by modification time, newest first
        photo_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        if photo_files:
            resolved["photos"] = photo_files[:2]  # 2 most recent
            print(f"📷 Using {min(2, len(photo_files))} most recent photos from {photos_path}")
    else:
        # Fallback: resolve paths from data against sample directory
        photos = resolved.get("photos", [])
        resolved_photos = []
        sample_dir = PROJECT_ROOT / "assets" / "photos" / "sample"
        for p in photos:
            if os.path.exists(p):
                resolved_photos.append(p)
            elif (sample_dir / os.path.basename(p)).exists():
                resolved_photos.append(str(sample_dir / os.path.basename(p)))
            else:
                resolved_photos.append(p)
        resolved["photos"] = resolved_photos
    
    return resolved


def main():
    parser = argparse.ArgumentParser(
        description="Generate Bennett-Kew Weekly Construction Progress Report PDF"
    )
    parser.add_argument(
        "data_file", nargs="?", default=None,
        help="JSON file with report data (omit for sample data)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output PDF path (default: Weekly_Progress_Report_##.pdf)"
    )
    parser.add_argument(
        "--photos", "-p", default=None,
        help="Directory containing this week's construction photos"
    )
    args = parser.parse_args()
    
    # ── Load data ───────────────────────────────────────────────────────
    if args.data_file:
        data_path = Path(args.data_file)
        if not data_path.exists():
            # Try relative to project root
            data_path = PROJECT_ROOT / args.data_file
        if not data_path.exists():
            print(f"❌ Data file not found: {args.data_file}")
            sys.exit(1)
        
        with open(data_path) as f:
            user_data = json.load(f)
        # Merge with defaults (user data overrides)
        data = {**SAMPLE_DATA, **user_data}
        print(f"📄 Loaded data from {data_path}")
    else:
        data = dict(SAMPLE_DATA)
        print("📄 Using sample data")
    
    # ── Resolve asset paths ─────────────────────────────────────────────
    data = resolve_asset_paths(data, args.photos)
    
    # ── Determine output filename ───────────────────────────────────────
    if args.output:
        output = args.output
    else:
        num = data.get("report_number", "XX")
        output = f"Weekly_Progress_Report_{num}.pdf"
    
    # ── Generate ────────────────────────────────────────────────────────
    result = generate_report(data, output)
    print(f"✅ Report generated: {os.path.abspath(result)}")
    print(f"   Report #{data['report_number']} | Week: {data['report_week']}")
    print(f"   Phase: {data['phase']} | Progress: {data['overall_progress']}%")


if __name__ == "__main__":
    main()
