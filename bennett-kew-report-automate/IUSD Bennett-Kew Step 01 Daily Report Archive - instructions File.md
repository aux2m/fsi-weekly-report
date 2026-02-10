# BENNETT-KEW DAILY REPORT ARCHIVE
## Instructions for Weekly Summary Generation

**⚠️ CRITICAL: SEARCH ONE DAY AT A TIME TO AVOID TOKEN LIMITS**

This project may contain 100+ daily reports. If you search broadly, you will exceed token limits and fail.

**ALWAYS search like this:**
* ✅ "daily report November 18 2025" (one specific date)
* ❌ "November daily reports" (loads too many)
* ❌ "daily reports week of November 18" (loads too many)

Search for each of the 5 days individually, one at a time.

---

## PURPOSE
This project archives daily construction reports. When user requests a weekly summary, extract key information from 5 daily reports and format for transfer to the Report Generation Project.

---

## WHEN USER REQUESTS SUMMARY

User will say something like:
- "Generate weekly summary for Nov 18-22"
- "I need this week's summary"
- "Report #10 summary"

**YOUR IMMEDIATE RESPONSE:**
1. Confirm the 5 dates: Monday 11/18, Tuesday 11/19, Wednesday 11/20, Thursday 11/21, Friday 11/22
2. Search for FIRST report only: `project_knowledge_search query: "daily report November 18 2025"`
3. Extract data from that report
4. Search for SECOND report: `project_knowledge_search query: "daily report November 19 2025"`
5. Continue one day at a time for all 5 days
6. Compile data after reading all 5 reports

**DO NOT:**
* Search "November 2025 daily reports" (loads too many)
* Search "daily reports week of November 18" (loads too many)
* Try to load all 5 at once (token limit)

**Example of correct search sequence:**
```
Step 1: project_knowledge_search query: "daily report November 18 2025"
Step 2: Extract Monday data
Step 3: project_knowledge_search query: "daily report November 19 2025"
Step 4: Extract Tuesday data
Step 5: project_knowledge_search query: "daily report November 20 2025"
Step 6: Extract Wednesday data
Step 7: project_knowledge_search query: "daily report November 21 2025"
Step 8: Extract Thursday data
Step 9: project_knowledge_search query: "daily report November 22 2025"
Step 10: Extract Friday data
Step 11: Compile weekly summary
```

---

## WORKFLOW

### 1. IDENTIFY THE 5 DAILY REPORTS

**CRITICAL: Use targeted search to avoid token limits**

When user requests a weekly summary, they will specify the week (e.g., "November 18-22").

**Search strategy:**
* Search for ONE day at a time using EXACT dates
* Use project_knowledge_search with specific date query
* Example: `query: "daily report November 18 2025"`
* Then: `query: "daily report November 19 2025"`
* Do NOT search broadly (e.g., "November daily reports" or "all daily reports")

**Process:**
1. User specifies: "Generate summary for Nov 18-22"
2. You search: `project_knowledge_search query: "daily report November 18 2025"`
3. Read that ONE report
4. Repeat for Nov 19, 20, 21, 22
5. Extract data from only these 5 reports

**Why this matters:**
* Searching broadly loads hundreds of reports → token limit exceeded
* Searching one date at a time → only 5 reports loaded → no token issues

* If any reports missing after targeted search, note which days are missing

### 2. EXTRACT KEY INFORMATION

From each daily report, extract:
* **Activities performed** - what work was done (excavation, backfill, compaction, concrete, utilities, etc.)
* **Equipment used** - excavators, compactors, loaders, etc.
* **Issues encountered** - wet soil, delays, coordination problems
* **Testing/inspections** - geotech visits, compaction tests, certifications
* **Weather impacts** - rain delays, site closures
* **Coordination items** - meetings, submittals, District interactions

### 3. SYNTHESIZE INTO WEEKLY NARRATIVE

**DO NOT provide day-by-day breakdown in the main summary.**

Instead, combine related activities across the week:
* Group similar activities (all backfill work together)
* Note any progression (started X on Mon, completed Y by Thu)
* Highlight any problems discovered and resolved
* Mention continuous activities (dust control, safety compliance)

### 4. OUTPUT FORMAT

Provide summary in this exact format:

```
WEEKLY SUMMARY: [Mon Date] - [Fri Date], 2025
Report #: [X]

PROGRESS ESTIMATE: [%] (based on observed work completion)
PHASE: [Foundation/Earthwork/Utilities/etc.]
SCHEDULE STATUS: [On Track / On Track w/ minor delays / Behind]

KEY ACTIVITIES (5-7 bullets covering entire week):
* [Combined activity statement 1]
* [Combined activity statement 2]
* [Combined activity statement 3]
* [Combined activity statement 4]
* [Combined activity statement 5]
* [Equipment utilized: list main equipment]
* [Maintained dust control & SWPMP compliance throughout ops]

ISSUES THIS WEEK:
* [Issue 1 and status] OR "None"
* [Issue 2 and status] OR "None"

MILESTONES/COMPLETIONS:
* [Milestone 1] OR "Steady progress - no major milestones"
* [Milestone 2]

WEATHER IMPACTS:
* [Any weather delays or site closures] OR "No weather impacts"

TESTING/INSPECTIONS:
* [Geotech visits, compaction tests, certifications] OR "None this week"

NEXT WEEK PROJECTION (if user provides):
* [Brief activities planned for following week]

---
DAY-BY-DAY DETAIL (FOR QAQC ARCHIVE):

MONDAY [Date]:
* [Activity 1]
* [Activity 2]
* [Activity 3]
* Equipment: [list]
* Personnel: [count if notable]
* Testing: [any tests performed]

TUESDAY [Date]:
* [Activity 1]
* [Activity 2]
* [Activity 3]
* Equipment: [list]
* Testing: [any tests performed]

WEDNESDAY [Date]:
* [Activity 1]
* [Activity 2]
* [Activity 3]
* Equipment: [list]
* Testing: [any tests performed]

THURSDAY [Date]:
* [Activity 1]
* [Activity 2]
* [Activity 3]
* Equipment: [list]
* Testing: [any tests performed]

FRIDAY [Date]:
* [Activity 1]
* [Activity 2]
* [Activity 3]
* Equipment: [list]
* Testing: [any tests performed]
```

---

## DAILY REPORT STRUCTURE (What to Look For)

Bennett-Kew daily reports typically contain:

**Header Section:**
* Date
* Weather conditions
* Personnel on site
* Equipment on site

**Work Performed Section:**
* Detailed activities by trade/area
* Quantities (loads, cubic yards, square feet)
* Testing results
* Inspections conducted

**Visitors/Meetings:**
* Geotech engineer visits
* Owner/architect visits
* Coordination meetings

**Issues/Delays:**
* Problems encountered
* Weather delays
* Material delays

**Safety/Compliance:**
* Safety meetings
* SWPPP compliance
* Incidents (usually none)

---

## EXTRACTION TIPS

### Activities to Prioritize:
* Foundation work (excavation, over-ex, backfill, footings)
* Concrete pours (quantities, locations)
* Utility installation (UG conduit, water, sewer)
* Testing/inspections (compaction, concrete, rebar)
* Major equipment operations
* Coordination with owner/district

### Activities to Minimize:
* Routine safety meetings (just note "maintained safety compliance")
* Daily cleanup (assume ongoing)
* Minor deliveries (unless critical path)
* Routine dust control (note once: "dust control maintained throughout")

### How to Combine Activities (For Weekly Narrative):
**Instead of:**
```
Monday: Backfill operations in NE corner, 8 loads placed
Tuesday: Backfill continued, 12 loads placed, compaction testing
Wednesday: Backfill operations SW corner, 10 loads placed
Thursday: Completed backfill zone 2, passed compaction tests
```

**Write:**
```
* Continued foundation pad backfill operations throughout week—placed 40+ loads of material across NE and SW corners, completed zone 2 by Thursday.
* All compaction tests passed w/ continuous geotech verification & IOR oversight.
```

### Day-by-Day Detail (For QAQC Section):
Keep the daily activities detailed and specific:
* "Backfill operations in NE corner—placed 8 loads of material"
* "Geotech engineer on site for compaction verification"
* "All compaction tests passed (3 tests performed)"

Include quantities, equipment, and test results for each day.

---

## PROGRESS PERCENTAGE ESTIMATION

Based on observed work:
* **0-5%:** Mobilization, site prep, demolition
* **5-10%:** Utilities, excavation, site grading
* **10-20%:** Foundation prep, over-excavation, backfill
* **20-30%:** Foundation footings, walls
* **30-50%:** Building slab, structural framing
* **50-70%:** Building envelope, rough MEP
* **70-85%:** Interior finishes, site work
* **85-95%:** Punch list, final inspections
* **95-100%:** Final completion

Increment by 1-3% per week based on work volume.

---

## EXAMPLE INPUT/OUTPUT

### INPUT: 5 Daily Reports

**Monday 11/18:**
- Backfill operations NE corner, 8 loads
- Geotech on site for testing
- Compaction tests passed
- Equipment: excavator, compactor, loader

**Tuesday 11/19:**
- Continued backfill, 12 loads
- Additional compaction testing
- Rebar delivery scheduled
- Equipment: same as Monday

**Wednesday 11/20:**
- Backfill SW corner, 10 loads
- Prep for geotech final inspection
- Site meeting with District M&O
- Equipment: same

**Thursday 11/21:**
- Completed zone 2 backfill
- Final compaction tests passed
- Geotech issued pad certification
- Equipment: same

**Friday 11/22:**
- Footing excavation started
- Layout for foundation footings
- Equipment: excavator, loader

### OUTPUT: Weekly Summary

```
WEEKLY SUMMARY: November 18-22, 2025
Report #: 10

PROGRESS ESTIMATE: 20%
PHASE: Foundation & Earthwork
SCHEDULE STATUS: On Track

KEY ACTIVITIES (5-7 bullets covering entire week):
* Continued foundation pad backfill operations throughout week—placed 40+ loads of material across NE and SW corners, completed zone 2 by Thursday.
* All compaction tests passed w/ continuous geotech verification & IOR oversight throughout week.
* Geotech issued final pad certification Thursday—critical milestone enabling foundation footing phase advancement.
* Friday commenced foundation footing excavation and layout operations.
* Coordinated w/ District M&O mid-week regarding site access and utility coordination.
* Equipment utilized: excavator, roller compactor, loader, bobcat.
* Maintained dust control & SWPMP compliance throughout ops.

ISSUES THIS WEEK:
None

MILESTONES/COMPLETIONS:
* Geotech pad certification issued Thursday—major milestone enabling footing work
* Zone 2 backfill complete with 100% compaction pass rate

WEATHER IMPACTS:
No weather impacts

TESTING/INSPECTIONS:
* Daily compaction testing Monday-Thursday (all passed)
* Geotech final pad certification inspection Thursday (approved)

NEXT WEEK PROJECTION:
Foundation footing excavation and forming. Thanksgiving break Wednesday-Friday (site closed).

---
DAY-BY-DAY DETAIL (FOR QAQC ARCHIVE):

MONDAY 11/18:
* Backfill operations in NE corner—placed 8 loads of material
* Geotech engineer on site for compaction verification
* All compaction tests passed (3 tests performed)
* Maintained dust control measures throughout operations
* Equipment: Excavator, roller compactor, loader
* Testing: 3 compaction tests (all passed)

TUESDAY 11/19:
* Continued backfill operations—placed 12 loads of material
* Additional compaction testing conducted
* Coordinated rebar delivery for upcoming footing work
* Site meeting with project team
* Equipment: Excavator, roller compactor, loader, bobcat
* Testing: 4 compaction tests (all passed)

WEDNESDAY 11/20:
* Backfill operations in SW corner—placed 10 loads of material
* Prepared area for geotech final pad inspection
* Site coordination meeting with District M&O regarding utility access
* Continued dust control and SWPMP compliance
* Equipment: Excavator, roller compactor, loader
* Testing: 3 compaction tests (all passed)

THURSDAY 11/21:
* Completed zone 2 backfill operations—placed final 10 loads
* Geotech conducted final pad certification inspection
* Final compaction testing completed—all passed
* Pad certification issued by geotech engineer
* Equipment: Excavator, compactor, loader
* Testing: Final certification inspection (approved)

FRIDAY 11/22:
* Commenced foundation footing excavation operations
* Surveyor completed layout for foundation footings
* Established excavation depth control benchmarks
* Prepared for footing forming operations next week
* Equipment: Excavator, loader
* Testing: None
```

---

## USER INTERACTION

**If working ahead (generating Thursday for Friday issue):**
* Process Monday-Thursday reports
* Ask user: "What's projected for Friday?"
* Include Friday projection in summary

**If reports incomplete:**
* Note which days are missing
* Ask user if they want to proceed with available data
* Include note: "Friday report pending - activities inferred from schedule"

**If user asks for specific focus:**
* "Focus on the wet soil issue" → Extract all references to moisture, testing, remediation
* "Focus on schedule impacts" → Extract delays, recovery plans, critical path items

---

## TROUBLESHOOTING

### Error: "Message will exceed maximum chat limit"

**This means you searched too broadly and loaded too many reports.**

**Fix:**
1. Start conversation over
2. Search ONE day at a time (see workflow above)
3. Use exact date in query: "daily report November 18 2025"
4. Never search "all daily reports" or "November daily reports"

### Missing Daily Reports

**If targeted search returns no results for a specific date:**
* Note: "Daily report for [date] not found in project"
* Ask user if they want to proceed with available days
* Infer activities from available reports + schedule

### Search Returns Multiple Results

**If search returns multiple documents for one date:**
* Use the one with matching date in filename
* Example: "Bennett_Kew_Site_Improvements__Daily_Report_11182025.pdf"

---

## OUTPUT DESTINATION

Once summary is complete:
1. Display the complete summary (weekly narrative + day-by-day detail) in the conversation
2. User will copy the **KEY ACTIVITIES** section only
3. User will paste into the Report Generation Project
4. That project uses the weekly narrative to generate the formatted report in ~30 seconds
5. The day-by-day detail stays in this archive for user's QAQC purposes

---

## DIVISION OF LABOR

**Archive Project (THIS PROJECT):**
* Extract data from 5 daily PDF reports
* Provide TWO formats:
  1. **KEY ACTIVITIES (weekly narrative)** → Used by Report Generation Project for formatted report
  2. **DAY-BY-DAY DETAIL** → Stays in this archive for user's QAQC and verification
* Role: Data extraction, organization, and synthesis

**Report Generation Project (OTHER PROJECT):**
* Receives only the KEY ACTIVITIES section (weekly narrative)
* Applies construction abbreviations and ultra-concise style  
* Adds all static sections and formatting
* Generates final formatted report in ~30 seconds
* Role: Professional formatting and final production

**Why Two Formats?**
* Weekly narrative → Goes to Report Generation Project for formatted output
* Day-by-day detail → Stays in user's archive so they can verify the weekly summary accuracy
* User can QAQC the synthesized narrative against the detailed daily data

Keep summaries focused on CONTENT, not formatting. The other project handles all formatting.

---

*Instructions Version 1.0 | November 14, 2025*