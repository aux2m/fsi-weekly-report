You are extracting structured data from a 3-week construction look-ahead schedule PDF for the Bennett-Kew P-8 Academy project.

The schedule shows planned activities for the next 3 weeks. Extract:

1. For each of 3 weeks:
   - Date range (MM/DD format with em dash)
   - Activity level: LOW, MODERATE, or HIGH
   - Top 3 activities (brief, abbreviated)

2. Planned activities for next week (3-5 items)

3. Noise assessment based on planned work:
   - LOW (1/5): Office work, deliveries, quiet activities
   - MODERATE (3/5): Excavation, compaction, trenching
   - HIGH (5/5): Major equipment, concrete pours, continuous heavy ops

4. Special considerations: any items that would affect the school campus

Use construction abbreviations: bldg, w/, ops, geotech, UG, SWPMP, SPED, over-ex

Return a JSON object with:
- week1_dates, week1_level, week1_activities (array of 3)
- week2_dates, week2_level, week2_activities (array of 3)
- week3_dates, week3_level, week3_activities (array of 3)
- planned_activities: array of 3-5 strings
- noise_index: "Low" or "Moderate" or "High"
- noise_level: "1/5" or "3/5" or "5/5"
- special_considerations: array of strings
