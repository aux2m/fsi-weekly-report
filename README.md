# FSI Weekly Report

Programmatic PDF report generator for construction weekly progress reports. Built for **Fonder-Salari, Inc.** project management — generates pixel-perfect branded reports from JSON data using ReportLab.

No Canva, no PDF editors, fully automatable.

## Projects

### Bennett-Kew Report (`bennett-kew-report/`)

Weekly progress reports for the **Bennett-Kew P-8 Academy New Classroom Building** project (Inglewood USD).

## Quick Start

```bash
pip install reportlab

# Generate a sample report
python bennett-kew-report/run_report.py

# Generate from your data
python bennett-kew-report/run_report.py my_week_data.json --output Report_04.pdf

# Auto-grab photos from a folder
python bennett-kew-report/run_report.py data.json --photos ./site_photos/
```

## How It Works

1. Create a JSON file with your weekly report data (see `bennett-kew-report/examples/sample_data.json`)
2. Run the generator — it produces a branded PDF matching the FSI template exactly
3. Every field in the template is a variable: phase, progress, activities, photos, milestones, etc.

### Data Format (minimal example)

```json
{
    "report_number": "04",
    "report_week": "02/10—02/14",
    "issued_date": "Friday, February 14, 2025",
    "phase": "Foundations & Underground",
    "overall_progress": "12",
    "schedule_status": "On Schedule",
    "activities_completed": [
        "Formed and poured stem walls Grid 1-5",
        "Underground electrical conduit complete"
    ],
    "planned_activities": [
        "Begin SOG gravel base Grid 1-10",
        "Vapor barrier installation"
    ]
}
```

## Architecture

- **ReportLab over fillable PDF** — Template is code, not a static form. Every field is a variable, colors and badges are dynamic, and automation is trivial.
- **JSON data interface** — All report content comes from a single flat JSON dict, making it easy to pipe data from Procore, Notion, n8n, or voice dictation.
- **Auto-resolved assets** — The CLI wrapper resolves logo and photo paths relative to the project root automatically.

## Automation Roadmap

| Source | Method | Status |
|--------|--------|--------|
| Manual JSON | Edit data file directly | Ready |
| Procore API | Daily logs + schedule → JSON | Planned |
| Voice dictation | Whisper → Claude parse → JSON | Planned |
| n8n workflow | Scheduled trigger → assemble → generate → email | Planned |

## Requirements

- Python 3.10+
- reportlab >= 4.0
