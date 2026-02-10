# Changelog

All notable changes to the Bennett-Kew Weekly Report Automation will be documented here.

## [0.1.0] - 2026-02-09

### Initial Release - "First Pipeline"

**Architecture**
- Python-orchestrated async pipeline with direct Anthropic API calls
- 8-stage pipeline: Calendar -> File Resolution -> PDF Extraction -> AI Extraction -> Photo Selection -> JSON Assembly -> PDF Generation -> Email Draft
- Multi-project config system (JSON-based, one config per project)
- Designed for Windows Task Scheduler (Friday 8am)

**Pipeline Stages**
- `calendar_utils.py`: Date calculation, week validation, countdown to Aug 9, 2026
- `file_resolver.py`: Auto-discovers daily reports, schedules, minutes, photos from Synology NAS
- `pdf_extractor.py`: PyMuPDF text extraction with ZIP-wrapped PDF handling
- `daily_report_agent.py`: Sequential 5-day extraction + weekly synthesis (Sonnet)
- `schedule_agent.py`: 3-week look-ahead parsing (Haiku)
- `minutes_agent.py`: Meeting minutes extraction (Haiku)
- `photo_selector.py`: Vision API photo scoring + caption generation (Sonnet)
- `json_assembler.py`: Merges all outputs, applies abbreviations, validates
- `email_drafter.py`: Principal email generation (Haiku)
- `orchestrator.py`: Async pipeline runner with parallel agent execution

**AI Agents**
| Agent | Model | Purpose |
|-------|-------|---------|
| Daily Report Extractor | claude-sonnet-4-20250514 | Extract activities/equipment/issues from each daily PDF |
| Weekly Synthesizer | claude-sonnet-4-20250514 | Combine 5 days into 5-7 narrative bullets with abbreviations |
| Schedule Parser | claude-haiku-4-5-20251001 | Parse 3-week look-ahead into impact matrix |
| Minutes Parser | claude-haiku-4-5-20251001 | Extract critical items and milestones |
| Photo Scorer | claude-sonnet-4-20250514 | Vision API: score photos, generate captions |
| Email Drafter | claude-haiku-4-5-20251001 | Generate plain-language principal email |

**Data Sources (Synology NAS)**
- Daily Reports: `...\12 Gen Corresp and Misc\Daily Reports`
- 3-Week Schedules: `...\13 Schedules\SIS`
- Meeting Minutes: `...\14 Meetings\Weekly OAC Coordination Meeting_Minutes`
- Photos: `...\18 Photos`

**SOP Rules Encoded**
- 5-7 narrative bullets (never day-by-day)
- Mandatory abbreviations: bldg, w/, ops, geotech, UG, SWPMP, SPED, over-ex
- Max 2 lines per bullet
- Photo captions 3-5 words matching actual photo content
- Countdown always to August 9, 2026
- Static sections never regenerated

**Outputs**
- `Weekly_Progress_Report_XX.pdf` (via existing generate_report.py)
- `report_data_XX.json` (audit trail)
- `principal_email_XX.txt` (review before sending)
- `photo_selections_XX.json` (photo decision transparency)

### Known Limitations
- Requires Anthropic API key (not Claude Code OAuth)
- Photo scoring may vary with image quality
- Schedule date parsing handles 2 formats (YY-MM-DD, MM-DD-YY) but not all edge cases
- Daily report extraction quality depends on Procore PDF format consistency

---

## Continuous Improvement Log

### How to Improve This Report

After each run, review these areas and update this log:

1. **Activity Extraction Quality**: Are the 5-7 bullets accurate? Do they capture the right level of detail?
2. **Abbreviation Coverage**: Are all construction terms being abbreviated correctly? Add new ones to `config/bennett_kew.json`.
3. **Photo Selection**: Are the AI-selected photos the best choices? Adjust scoring weights in `photo_selector.py`.
4. **Caption Quality**: Do captions match photos? Refine the `photo_selection_system.md` prompt.
5. **Schedule Parsing**: Is the 3-week impact matrix accurate? Check `schedule_extraction_system.md`.
6. **Email Tone**: Does the principal email sound right? Adjust `email_draft_system.md`.
7. **Missing Data Handling**: How does the pipeline handle missing inputs? Document edge cases.

### Improvement Actions Taken

| Date | Area | Change | Result |
|------|------|--------|--------|
| 2026-02-09 | Initial | First pipeline build | Pending first run |

### Future Enhancements Planned

- [ ] Procore API integration for automatic daily report fetching
- [ ] Webhook trigger (FastAPI endpoint)
- [ ] Multi-project support (duplicate config for new projects)
- [ ] Email sending via SMTP (with review gate)
- [ ] Streamlined SOP instructions (replace Step 01/02 with optimized prompts)
- [ ] Historical report comparison (diff against previous week)
- [ ] Cost tracking per run (API token usage logging)
