# CLAUDE.md - Bennett-Kew Report Automation

## Project Overview

Automated pipeline for generating weekly construction progress reports for the Bennett-Kew P-8 Academy project (Inglewood USD). Replaces a manual two-step Claude.ai workflow with a single Python command.

## Quick Start

```bash
cd bennett-kew-report-automate

# Add your API key to .env
# ANTHROPIC_API_KEY=sk-ant-api...

# Install deps
pip install -r requirements.txt

# Run for this Friday
python run.py

# Run for specific week
python run.py --date 2026-02-06 --report-num 21

# Debug mode (saves intermediate outputs)
python run.py --date 2026-02-06 --debug

# Dry run (no PDF, no email)
python run.py --date 2026-02-06 --dry-run
```

## Architecture

8-stage async pipeline using direct Anthropic API calls:
1. Calendar validation (always first)
2. File resolution (auto-discover from Synology NAS)
3. PDF text extraction (PyMuPDF)
4. AI extraction (3 parallel agents: daily reports + schedule + minutes)
5. Photo selection (Vision API, runs after stage 4)
6. JSON assembly (merge all outputs)
7. PDF generation (existing `bennett-kew-report/src/generate_report.py`)
8. Email draft (saved for review, never auto-sent)

## Key Files

- `run.py` - CLI entry point
- `src/orchestrator.py` - Main pipeline
- `config/bennett_kew.json` - Project paths, static data, constants
- `prompts/` - System prompts for each AI agent
- `output/` - Generated PDFs, JSON audit trail, email drafts

## Data Sources (Synology NAS)

All inputs are on locally-synced Synology NAS folders. Paths configured in `config/bennett_kew.json`.

## Critical Rules

- Daily reports processed ONE AT A TIME (token management)
- Activities: ALWAYS 5-7 narrative bullets, never day-by-day
- Mandatory abbreviations: bldg, w/, ops, geotech, UG, SWPMP, SPED, over-ex
- Static sections (description, commitment) copied from config, never regenerated
- Photo captions MUST match actual photo content
- Countdown always to August 9, 2026
- Email NEVER auto-sent

## PDF Generator

The PDF generator at `bennett-kew-report/src/generate_report.py` is production-proven and should NOT be modified. The automation pipeline produces the JSON data dict it expects.

## Adding a New Project

1. Copy `config/_template.json` to `config/new_project.json`
2. Fill in project-specific paths, static data, constants
3. Run: `python run.py --config new_project`
