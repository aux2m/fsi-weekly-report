# BENNETT-KEW WEEKLY REPORT SOP
**Standard Operating Procedure | Report Generation**

---

## WORKFLOW

1. **Start metrics tracking**
2. **Receive 4 files:**
   - Weekly summary (from archive project)
   - Meeting minutes/agenda
   - 3-week look-ahead
   - (Baseline schedule if needed)
3. **Generate dynamic content only**
4. **Assemble with static templates**
5. **Save markdown to /mnt/user-data/outputs/**
6. **Display metrics**

**NO WORD CONVERSION** (user handles if needed)

---

## CRITICAL FORMAT LOCKS

### ACTIVITIES COMPLETED - THE #1 RULE

**ALWAYS:**
- 5-7 narrative bullets covering ENTIRE WEEK
- Use `*` for bullets (NEVER dashes `-` or checkmarks)
- Max 2 lines per bullet
- Combine related activities
- Focus on key events only

**NEVER:**
- Day-by-day breakdown ("Monday: ... Tuesday: ...")
- More than 7 bullets
- Bullets longer than 2 lines
- Every minor task listed

**Example:**
```
Activities Completed:
* Completed bldg pad corner surveying and commenced over-excavation for foundation footprint.
* During excavation, discovered significant moisture infiltration from existing PVC sewer line—extensive root intrusion at pipe joints causing water seepage.
* Conducted investigation w/ geotech & design team; approved soil replacement strategy using on-site material.
* Completed additional site fencing per principal's security request.
* Maintained dust control & SWPMP compliance throughout ops.
```

---

## MANDATORY ABBREVIATIONS

| Full Term | Use This |
|-----------|----------|
| building | bldg |
| with | w/ |
| operations | ops |
| geotechnical | geotech |
| underground | UG |
| Storm Water Pollution Prevention | SWPMP |
| special education | SPED |
| over-excavation | over-ex |

---

## STATIC SECTIONS (COPY VERBATIM - NEVER REGENERATE)

### Report Header
```
Bennett-Kew P-8 Academy
New Classroom Building Project
Project Address: 11710 S Cherry Ave, Inglewood, CA 90303

Inglewood Unified School District
General Contractor: PCN3, Inc.
Construction Manager: Fonder-Salari, Inc.
Architect: HED Design
Project Duration: September 2025 - September 2026
Prepared by: Adam Wentworth, PM
```

### Project Description
```
The project generally consists of the construction of: a single story building consisting of 6 classrooms, restrooms, utility spaces and a large multipurpose space. Site work includes new asphalt play field, courts, solar installation, fire lane striping and modifications to fencing. Play structures and soft surface materials are owner furnished, contractor coordinated and installed along with minor landscaping. Project is on an active school site, all work will be coordinated with the District to cause the least disruption to class, particularly for special education programming.
```

### Commitment Section
```
Community Promise: Our construction team completed this week's activities with zero educational disruptions while maintaining the highest safety standards. Moving into higher-impact phases, we remain committed to advance communication, flexible scheduling around special programs, and immediate response to any campus concerns. Direct Contact for Immediate Issues:
Adam Wentworth, Construction Manager (661) 204-1154 | adam.wentworth@fonder-salari.com
```

---

## DYNAMIC SECTIONS (GENERATE WEEKLY)

### 1. Report Week & Phase
```
Report Week: [Monday] - [Friday], 2025
Weekly Progress Report #[X]
Issued: [Friday of report week]

Phase: [Current Phase Name]
Overall Progress: X% Complete
Schedule Status: [On Track / On Track w/ minor delays—recoverable / Behind Schedule]
```

### 2. Activities Completed
**Format:** 5-7 bullets, `*` bullets, max 2 lines each, narrative style

### 3. Milestones Achieved
**Format:** 3-4 bullets, bold title + one sentence
```
Milestones Achieved:
* **Bold Title**: One sentence explanation maximum.
* **Bold Title**: One sentence explanation maximum.
* **Bold Title**: One sentence explanation maximum.
```

### 4. Critical Items (If Applicable)
**Format:** 0-3 bullets, bold title + 2-3 sentence summary
```
Critical Items:
* **Issue Title**: Executive summary showing status and resolution—2-3 sentences maximum.
```
**Skip entire section if no critical items**

### 5. Next Week Activity Projection
```
Week of [Date Range], 2025

PLANNED ACTIVITIES
Monday-Wednesday (MM/DD-MM/DD)
* [Activity 1]
* [Activity 2]
* [Activity 3]

Thursday-Friday (MM/DD-MM/DD)
* [Activity 1]
* [Activity 2]

ANTICIPATED IMPACT LEVELS
NOISE INDEX: [LOW/MODERATE/HIGH] (Level X/3)
Peak Impact Times: [Days] [Hours] ([equipment/activity type])

SPECIAL CONSIDERATIONS
* [Consideration 1—brief]
* [Consideration 2—brief]
```

**Noise Levels:**
- LOW (1/3): Office work, deliveries, quiet activities
- MODERATE (2/3): Excavation, compaction, trenching
- HIGH (3/3): Major equipment, concrete pours, continuous heavy ops

### 6. 3-Week Construction Impact Matrix

| Week | Dates | Activities | Impact | Summary |
|------|-------|------------|--------|---------|
| 1 | [Dates] | [Brief list w/ abbrev] | **MODERATE** | [8-12 word summary] |
| 2 | [Dates] | [Brief list w/ abbrev] | **MODERATE** | [8-12 word summary] |
| 3 | [Dates] | [Brief list w/ abbrev] | **LOW** | [8-12 word summary] |

**Rules:** Activities = comma-separated, Impact = bold, Summary = ultra-concise

### 7. Substantial Completion Countdown
```
[Report Friday Date] - August 9, 2026 = XXX Calendar Days
```
**Always August 9, 2026** (never changes)

### 8. Photo Captions
```
Photo 1: [3-5 words - current week activity]
Photo 2: [3-5 words - safety/site conditions]
```

---

## DATE ACCURACY RULE

**ONLY include activities from exact 5-day report week (Mon-Fri)**

Validate:
- All activities within report week dates?
- No activities from previous/future weeks?
- Weekday names match calendar?

---

## WRITING STYLE

**DO:**
- Use construction abbreviations extensively
- Write concise, technical statements
- Combine related activities
- Keep 1-2 lines per bullet

**DON'T:**
- Use transitional phrases ("Additionally," "Furthermore")
- Write verbose explanations
- List every minor task
- Repeat information across sections

---

## PERFORMANCE METRICS

**Start of report:**
```bash
echo "REPORT_START=$(date +%s)" > /tmp/report_metrics.txt
echo "Report #[X] generation started at $(date '+%Y-%m-%d %H:%M:%S')"
```

**End of report:**
```bash
REPORT_END=$(date +%s)
REPORT_START=$(grep REPORT_START /tmp/report_metrics.txt | cut -d'=' -f2)
DURATION=$((REPORT_END - REPORT_START))

echo ""
echo "=== REPORT #[X] METRICS ==="
echo "Duration: ${DURATION} seconds"
echo "Input tokens: [from conversation stats]"
echo "Output tokens: [from conversation stats]"
echo "==========================="
```

---

## PRINCIPAL EMAIL (When Requested)

```
Subject: IUSD: Week #[X] Construction Update - Bennett-Kew Project

Hi Principal Appleton,

Happy Friday! Here's your weekly update on the classroom building project.

**This Week's Progress:**
* [Key accomplishment - plain language, NO jargon]
* [Problem discovered and resolution]
* [Progress percentage]
* Zero educational disruptions throughout the week

**Next Week Preview:** [2-3 sentences covering Mon-Wed and Thu-Fri activities with noise levels. Plain language.]

**Good News:** [1-2 sentences: positive framing, on-track messaging, collaborative relationship]

Have a great weekend!

All the best,

Adam Wentworth
Senior Project Manager

adam.wentworth@fonder-salari.com
661-204-1154

25101 The Old Rd, #112
Santa Clarita, CA 91381-2206
fonder-salari.com
```

**Tone:** Professional-friendly, concise, reassuring. NO jargon for principal.

---

## FINAL CHECKLIST

Before delivery:
- [ ] Activities = 5-7 narrative bullets (NO day-by-day)
- [ ] All bullets use `*` (no dashes/checkmarks)
- [ ] Each bullet max 2 lines
- [ ] Used mandatory abbreviations
- [ ] All dates within exact report week
- [ ] Countdown from Friday to Aug 9, 2026
- [ ] Static sections copied verbatim (not regenerated)
- [ ] Metrics displayed

---

## PROJECT CONSTANTS

- **Owner:** Inglewood Unified School District
- **Key Contact:** Principal Sarah Appleton
- **GC:** PCN3, Inc.
- **CM:** Fonder-Salari, Inc. (Adam Wentworth, PM)
- **Substantial Completion:** August 9, 2026
- **School Start:** August 10, 2026 (1-day buffer)
- **Critical Constraint:** Zero educational disruptions
- **Sensitive Area:** Room 19 (SPED) requires noise mitigation

---

**NO DEVIATIONS FROM THIS FORMAT**

*SOP v4.0 | Locked Format | November 2025*