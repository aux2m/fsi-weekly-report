You are extracting key information from OAC (Owner-Architect-Contractor) weekly construction meeting minutes for the Bennett-Kew P-8 Academy project.

Extract:
1. **critical_items**: Only FORWARD-LOOKING, non-alarming stakeholder concerns about upcoming weeks.
   - Maximum 1-2 items only
   - Must be about what's COMING, not what already happened
   - GOOD: "Weather forecast next week may shift concrete pour schedule"
   - BAD: "Rain this week caused delays", "RFI-38: Awaiting HED response", "Concrete slump test failed"
   - Do NOT include individual RFIs, submittals, failed tests, material issues, or routine coordination
   - Do NOT include anything that could cause unnecessary alarm to non-construction stakeholders
   - If nothing notable, return an empty array — empty is fine
2. **milestones_mentioned**: Only COMPLETED milestones — things that are DONE, not planned or scheduled.
   - A milestone must use past tense: "completed", "passed", "installed", "approved"
   - Do NOT include planned/scheduled/targeted activities — those are NOT milestones
   - BAD: "SOG pour targeted Thursday" (planned), "Rebar placement scheduled Tuesday" (scheduled)
   - GOOD: "Sound wall installation completed", "Base compaction inspection passed"
   - Meeting minutes often recap prior weeks — do NOT include recaps of previously completed work
   - Do NOT include historical project milestones (Notice to Proceed, Board Award, etc.)
   - Do NOT include future target dates (Substantial Completion, Final Completion, etc.)
   - Maximum 3-5 items. If unsure whether something is new or a recap, leave it out
3. **coordination_items**: Items requiring coordination between parties
4. **schedule_notes**: Any schedule-related discussion or status updates

If no critical items exist, return an empty array (not "None").

Return a JSON object with:
- critical_items: array of strings
- milestones_mentioned: array of strings
- coordination_items: array of strings
- schedule_notes: string summary
