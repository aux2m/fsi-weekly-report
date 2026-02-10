You are selecting the best construction progress photos for a weekly report for the Bennett-Kew P-8 Academy project.

For each photo, evaluate:
1. **relevance** (1-5): How well does this photo relate to the reported construction activities this week?
2. **progress_demo** (1-5): How effectively does this photo demonstrate visible construction progress?
3. **quality** (1-5): Image quality - focus, lighting, composition, professional appearance

Also provide:
- **description**: What construction activity/condition is shown (one sentence)
- **caption**: A 3-5 word caption suitable for a professional report

Score formula: relevance * 0.5 + progress_demo * 0.3 + quality * 0.2

Return a JSON object with:
- scores: array of {filename, relevance, progress_demo, quality, total_score, description, caption}
