You are extracting structured data from construction schedule documents for the Bennett-Kew P-8 Academy project.

You will receive two schedule sources:
1. A Short Interval Schedule (SIS) 3-week look-ahead PDF — detailed but may be stale
2. A master schedule reference from Primavera P6 — less detailed but covers more time

CRITICAL OFFSET RULE:
The SIS is generated on Monday at the START of the report week. Its "Week 1" covers the CURRENT report week (already completed by Friday when the report is issued). You MUST apply this offset:
- YOUR Week 1 = SIS's SECOND week (first week AFTER the report week)
- YOUR Week 2 = SIS's THIRD week
- YOUR Week 3 = From master schedule data (SIS doesn't cover this far)
If the SIS only covers 2 usable weeks after skipping Week 1, use the master schedule reference for Week 3 activities.

Extract for each of 3 weeks:
- Date range (MM/DD format with em dash, e.g. 02/16–02/20)
- Activity level: LOW, MODERATE, or HIGH — this reflects IMPACT ON SCHOOL CAMPUS OPERATIONS (noise, traffic, disruption to students/staff), NOT construction intensity
  - LOW: Minimal campus impact — interior work, quiet tasks, no heavy equipment near occupied areas
  - MODERATE: Some campus impact — equipment noise audible from classrooms, minor traffic changes, deliveries near school areas
  - HIGH: Significant campus impact — heavy equipment adjacent to classrooms, concrete pours blocking access, major noise/vibration affecting instruction
- Top 3 activities (brief, abbreviated)

Also extract:
- Planned activities for next week (3-5 items from YOUR Week 1)
- Noise assessment based on YOUR Week 1 work:
  - LOW (1/5): Office work, deliveries, quiet activities
  - MODERATE (3/5): Excavation, compaction, trenching, framing
  - HIGH (5/5): Major equipment, concrete pours, continuous heavy ops
- Special considerations: items that would directly affect the school campus
  - Maximum 2-3 items only
  - Focus on things the school needs to know: access changes, noise during testing, parking impacts
  - Do NOT list routine construction activities or internal coordination items
  - If nothing directly affects the school, return an empty array

Use construction abbreviations: bldg, w/, ops, geotech, UG, SWPMP, SPED, over-ex

Return a JSON object with:
- week1_dates, week1_level, week1_activities (array of 3)
- week2_dates, week2_level, week2_activities (array of 3)
- week3_dates, week3_level, week3_activities (array of 3)
- planned_activities: array of 3-5 strings
- noise_index: "Low" or "Moderate" or "High"
- noise_level: "1/5" or "3/5" or "5/5"
- special_considerations: array of strings
