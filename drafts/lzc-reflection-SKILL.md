---
name: lzc-reflection
description: Load during the weekly reflection cron job. Contains the self-review framework for tracking analysis output volume, ENGINE vs REALITY accuracy statistics, strongest celebrity verifications, hardest dimensions to verify, and improvement notes for the following week.
---

# Weekly Self-Review — Reflection Framework

## Purpose

Every week, step back and evaluate performance. What worked, what did not, and what to improve. This is not a formality — it directly improves the quality of future analyses.

## When to Run

Triggered by weekly reflection cron job (recommended: Sunday evening or Monday morning).

## Review Template

### 1. Output Volume

| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Full analyses completed | X | X | up/down/flat |
| Topic radar scans run | X | X | up/down/flat |
| Telegram updates sent | X | X | up/down/flat |
| Celebrities evaluated (not published) | X | X | up/down/flat |

### 2. ENGINE vs REALITY Accuracy Statistics

Across all analyses completed this week:

| Dimension | Total Checks | Match | Partial | Mismatch | Accuracy Rate |
|-----------|-------------|-------|---------|----------|---------------|
| Personality | X | X | X | X | XX% |
| Liuqin (Six Relations) | X | X | X | X | XX% |
| Dayun (Major Cycles) | X | X | X | X | XX% |
| Liunian (Annual) | X | X | X | X | XX% |
| Feeling | X | X | X | X | XX% |
| Marriage | X | X | X | X | XX% |
| **TOTAL** | X | X | X | X | **XX%** |

**Accuracy calculation:** Match = 1.0, Partial = 0.5, Mismatch = 0.0

### 3. Strongest Celebrity Verification This Week

```
Celebrity: [Name]
Born: [Date]
Overall Score: X.X / 5.0
Best Verification Point: [Dimension] — [1-sentence description of the strongest ENGINE-to-REALITY match]
Why It Works: [Why this is compelling for demos]
```

### 4. Hardest Dimension to Verify

```
Dimension: [Which of the 6 was hardest]
Why: [What made it difficult — lack of public data? Vague engine output? Ambiguous real events?]
Frequency: [How often this dimension scored Partial or Mismatch this week]
Improvement Idea: [What could be done differently next time]
```

### 5. Improvement Notes for Next Week

Specific, actionable items:

- [ ] [Improvement 1 — e.g., "Find better sources for liuqin verification in MMA fighters"]
- [ ] [Improvement 2 — e.g., "Reduce time spent on celebrities with insufficient data"]
- [ ] [Improvement 3 — e.g., "Experiment with birth time data for fighters where available"]

### 6. Patterns Observed

Any recurring patterns across this week's analyses:

- **Data gaps:** Which types of information were consistently hard to find?
- **Engine strengths:** Which dimensions consistently matched reality?
- **Engine weaknesses:** Which dimensions consistently missed?
- **Process bottlenecks:** Where did the analysis process slow down?

### 7. Cumulative Tracker

Update the running totals:

| Metric | All-Time Total |
|--------|---------------|
| Total analyses completed | X |
| Average accuracy rate | XX% |
| Best single analysis | [Celebrity name, score] |
| Total verification points checked | X |

## Output

Post the reflection summary to Telegram as a condensed message. Store the full reflection in memory for trend tracking.

## Honesty Rule

This reflection is for internal improvement, not for show. If it was a bad week — accuracy was low, candidates were weak, the process was slow — say so. The only way to improve is to see clearly.
