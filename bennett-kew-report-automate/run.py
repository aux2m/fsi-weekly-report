#!/usr/bin/env python3
"""
Bennett-Kew Weekly Report Automation
=====================================
End-to-end pipeline: NAS inputs -> AI extraction -> PDF + email draft.

Usage:
  python run.py                                    # Normal Friday run
  python run.py --date 2026-02-06 --report-num 22  # Specific week
  python run.py --config another_project           # Different project
  python run.py --skip-email --debug               # Dev mode
  python run.py --dry-run                          # Assemble JSON only
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Bennett-Kew Weekly Report Automation"
    )
    parser.add_argument("--config", "-c", default="bennett_kew",
                        help="Project config name (default: bennett_kew)")
    parser.add_argument("--date", "-d", default=None,
                        help="Target Friday date YYYY-MM-DD (default: this Friday)")
    parser.add_argument("--report-num", "-n", type=int, default=None,
                        help="Override report number")
    parser.add_argument("--skip-email", action="store_true",
                        help="Don't generate principal email")
    parser.add_argument("--skip-photos", action="store_true",
                        help="Skip AI photo selection")
    parser.add_argument("--dry-run", action="store_true",
                        help="Extract and assemble but don't generate PDF")
    parser.add_argument("--debug", action="store_true",
                        help="Save intermediate outputs for debugging")

    args = parser.parse_args()

    result = asyncio.run(run_pipeline(
        config_name=args.config,
        target_date=args.date,
        report_number=args.report_num,
        skip_email=args.skip_email,
        skip_photos=args.skip_photos,
        dry_run=args.dry_run,
        debug=args.debug,
    ))

    if result.get("error"):
        print(f"\nERROR: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
