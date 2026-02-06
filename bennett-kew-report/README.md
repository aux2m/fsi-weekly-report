# Bennett-Kew Weekly Construction Progress Report Generator

Programmatic PDF report generator for the **Bennett-Kew P-8 Academy New Classroom Building** project (Inglewood USD / Fonder-Salari Inc.).

Generates pixel-perfect branded weekly progress reports from JSON data — no Canva, no PDF editors, fully automatable.

## Quick Start

```bash
# Install dependency
pip install reportlab

# Generate a sample report
python run_report.py

# Generate from your data
python run_report.py my_week_data.json --output Report_04.pdf

# Auto-grab photos from a folder
python run_report.py my_data.json --photos ./site_photos/
```

## Project Structure

```
bennett-kew-report/
├── CLAUDE.md              ← Project context for Claude Code
├── README.md
├── requirements.txt
├── run_report.py          ← CLI entry point (use this)
├── src/
│   └── generate_report.py ← Core PDF generator
├── assets/
│   ├── logos/             ← FS, BK, IUSD logos
│   └── photos/
│       └── sample/        ← Sample construction photos
├── examples/
│   ├── sample_data.json   ← Complete data schema reference
│   └── sample_output.pdf  ← What the generated report looks like
└── templates/
    ├── original_template_v1.pdf  ← Original Canva template
    └── original_template_r1.pdf  ← Revised template (corrections)
```

## Data Format

Create a JSON file with your weekly report data. See `examples/sample_data.json` for all fields. Only the fields you want to change need to be included — everything else uses sensible defaults.

### Minimal weekly update example:

```json
{
    "report_number": "04",
    "report_week": "02/10—02/14",
    "issued_date": "Friday, February 14, 2025",
    "countdown_days": "340",
    "phase": "Foundations & Underground",
    "overall_progress": "12",
    "schedule_status": "On Schedule",
    "activities_completed": [
        "Formed and poured stem walls Grid 1-5",
        "Underground electrical conduit complete",
        "Anchor bolt installation Grid A-D"
    ],
    "milestones_achieved": [
        "Stem wall inspection passed (DSA)"
    ],
    "critical_items": [
        "RFI #012 response received — no design change required"
    ],
    "planned_activities": [
        "Begin SOG gravel base Grid 1-10",
        "Vapor barrier installation",
        "Rebar mat placement for SOG"
    ]
}
```

## Automation Paths

This generator is designed as the **output layer** of an automation pipeline. Data can flow in from:

| Source | Method | Status |
|--------|--------|--------|
| Manual JSON | Edit `sample_data.json` | ✅ Ready |
| Voice dictation | Whisper → Claude parse → JSON | Planned |
| Procore API | Daily logs + schedule → JSON | Planned |
| Notion database | Weekly entry → API pull → JSON | Planned |
| n8n workflow | Scheduled trigger → assemble → generate → email | Planned |
