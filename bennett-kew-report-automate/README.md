# Bennett-Kew Weekly Report Automation

Automated pipeline for generating weekly construction progress reports for the **Bennett-Kew P-8 Academy** project (Inglewood Unified School District).

## What It Does

Takes raw construction data from your Synology NAS and produces:
- **PDF Report** - Branded weekly progress report (via ReportLab)
- **Email Draft** - Plain-language email to Principal Appleton
- **Audit Trail** - JSON data file for verification

## Pipeline

```
Daily Reports (5 PDFs) ──┐
3-Week Schedule PDF ─────┤── AI Extraction ── JSON Assembly ── PDF
Meeting Minutes PDF ─────┤
Construction Photos ─────┘── Photo Selection + Captioning
```

## Setup

```bash
pip install -r requirements.txt
```

Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api...
```

## Usage

```bash
python run.py                                    # This Friday
python run.py --date 2026-02-06 --report-num 21  # Specific week
python run.py --debug                             # Save intermediates
python run.py --dry-run                           # JSON only, no PDF
python run.py --skip-photos --skip-email          # Minimal run
```

## Scheduled Run

Set up Windows Task Scheduler to run `schedule_task.bat` every Friday at 8:00 AM.

## Output

All outputs go to `output/`:
- `Weekly_Progress_Report_XX.pdf`
- `report_data_XX.json` (audit trail)
- `principal_email_XX.txt` (review before sending)
- `photo_selections_XX.json` (photo scoring log)

## Cost

~$0.50-$1.00 per report using mixed Sonnet/Haiku model allocation.

## Multi-Project

Each project is a JSON config file in `config/`. Copy `_template.json` and customize for new projects.
