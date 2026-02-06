# Bennett-Kew Weekly Progress Report Generator

## Project Overview
Programmatic PDF report generator for the Bennett-Kew P-8 Academy New Classroom Building project (Inglewood USD). Produces branded weekly construction progress reports matching the Fonder-Salari Inc. template exactly.

## Architecture
- **`src/generate_report.py`** — Core report generator using ReportLab. Takes a Python dict (or JSON file) of report data and produces a branded PDF. Every field in the template is a variable.
- **`run_report.py`** — CLI wrapper that resolves asset paths (logos, photos) automatically relative to project root.
- **`assets/logos/`** — Fonder-Salari, Bennett-Kew, and IUSD logo files (extracted from original PDF).
- **`assets/photos/sample/`** — Sample construction photos for testing.
- **`templates/`** — Original PDF templates from Canva (v1 and r1) for visual reference.
- **`examples/`** — Sample JSON data file and sample generated PDF output.

## Key Design Decisions
1. **ReportLab over fillable PDF** — Template is code, not a static form. This means every field is a variable, colors/badges are dynamic, and automation is trivial.
2. **JSON data interface** — All report content comes from a single flat JSON dict. This makes it easy to pipe data in from Procore, Notion, n8n, or voice dictation.
3. **Logo/photo paths** — The `run_report.py` wrapper auto-resolves paths relative to project root so you don't need to copy assets into the working directory.

## r1 Corrections Applied
- Banner: no curly braces around report number (was `{##}`, now `##`)
- Project Report Details: 2-column layout (dates left, GC/CM right side-by-side)
- Activities/Milestones/Critical Items: wider fields allowing longer text per bullet
- Planned Activities & Special Considerations: full-width lines

## How to Generate a Report
```bash
# With sample data
python run_report.py

# With custom JSON data
python run_report.py examples/sample_data.json

# With custom output path
python run_report.py examples/sample_data.json --output my_report.pdf

# With custom photos directory
python run_report.py examples/sample_data.json --photos /path/to/this/weeks/photos/
```

## Data Schema
See `examples/sample_data.json` for the complete field reference. Key sections:
- **Report ID**: report_number, report_week, issued_date
- **Project static info**: project_name, architect, etc. (rarely changes)
- **This week**: phase, overall_progress, schedule_status, activities_completed[], milestones_achieved[], critical_items[]
- **3-week forecast**: week1_dates/level/activities, week2_*, week3_*
- **Next week**: planned_activities[], noise_index, special_considerations[]
- **Photos**: photos[] (list of file paths), photo_captions[]

## Automation Next Steps (TODO)
- [ ] Procore API integration — pull daily logs, RFIs, schedule data
- [ ] n8n workflow — weekly trigger, data assembly, PDF generation, email distribution
- [ ] Notion database backend — maintain weekly data in Notion, script pulls and generates
- [ ] Voice input pipeline — dictate summary during commute, parse to JSON, generate report
- [ ] Photo auto-pull from Procore or Google Drive folder

## Dependencies
- Python 3.10+
- reportlab (pip install reportlab)
