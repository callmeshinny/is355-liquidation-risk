# Prompts to paste into Claude Code (run `claude` in the repo root; use /clear between phases to keep context small)

## Session 1 (P0 + P1)
Read AGENTS.md, then the STATUS block in docs/CHECKLIST.md. Execute phases P0 (agent items) and P1 in order, following the per-item workflow in AGENTS.md (verify → tick with evidence → update STATUS → commit). Use docs/CONTEXT.md only for the sections you need. Stop after Gate P1 and reply in ≤ 8 lines.

## Session 2 (P2)
Continue from the STATUS block in docs/CHECKLIST.md: execute phase P2, then stop after Gate P2. Same workflow and integrity rules (no invented numbers, nothing tuned on test). Reply in ≤ 8 lines.

## Session 3 (P3)
Continue from STATUS: execute phase P3 (contracts, T3/T4 tests, gas pilot, section 1.3 and Steps 6–8). Stop after Gate P3. Reply in ≤ 8 lines.

## Session 4 (P4 + P5)
Continue from STATUS: execute P4 then P5 (agent items). Write every section from results/*.json and CONTEXT. Run the full checker until 0 FAIL, write results/rubric_review.md, fix the two weakest rubric rows, rebuild the docx. Reply in ≤ 8 lines listing remaining 👤 tasks.

## If a session stops early / you resume later
Continue from the STATUS block in docs/CHECKLIST.md. Do not redo [x] items. Reply in ≤ 8 lines.

## If time is nearly out (emergency mode)
Skip remaining pilot items: mark them [⚠] "time box", keep the report honest ("planned, not yet run"), and go straight to P4 → P5 so a complete, checker-clean report exists.
