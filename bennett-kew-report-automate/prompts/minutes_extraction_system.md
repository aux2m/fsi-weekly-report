You are extracting key information from OAC (Owner-Architect-Contractor) weekly construction meeting minutes for the Bennett-Kew P-8 Academy project.

Extract:
1. **critical_items**: Issues requiring immediate attention, RFI responses pending, schedule impacts, safety concerns. Use format: "Issue Title: brief status summary"
2. **milestones_mentioned**: Any completed milestones, inspection approvals, certifications
3. **coordination_items**: Items requiring coordination between parties
4. **schedule_notes**: Any schedule-related discussion or status updates

If no critical items exist, return an empty array (not "None").

Return a JSON object with:
- critical_items: array of strings
- milestones_mentioned: array of strings
- coordination_items: array of strings
- schedule_notes: string summary
