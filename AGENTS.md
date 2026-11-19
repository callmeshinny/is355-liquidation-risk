# AGENTS.md — IS355 Week 4 (Group 6–BC)

## Role and goal
You are a senior blockchain (Vyper/EVM) + ML engineer and a precise technical writer.
Goal: deliver `out/6_BC_IS355_Week4_Project.docx` ("Detailed Method & Test Plan") that scores maximum on the lecturer's rubric (docs/CONTEXT.md §7), backed by small REAL pilot runs. Deadline: 20/11/2026.

## Read order (token budget matters)
1. `docs/CHECKLIST.md` — STATUS block at top tells you the next item. Work only on that.
2. `docs/CONTEXT.md` — facts, final decisions D1–D6, hypotheses, rubric, required fields. Read only the § you need.
3. Never open the original course .docx files. `docs/ref/template.docx` is used only by `tools/build_docx.sh`.
4. `legacy/` = Week 3 code by Khanh. Read notebooks via `jupyter nbconvert --to script --stdout <nb> | head -n 200` (no outputs), never the raw .ipynb JSON.

## Non-negotiable integrity rules
- Never invent results. Every number in the report is one of: (a) a paper value from CONTEXT §3–4, (b) a value in `results/*.json` produced by code in this repo, (c) a calculation shown in the text, (d) explicitly labelled "expected".
- Pilot numbers: give date, config, seed; list each pilot in Appendix A with its command and results file.
- Never fit, tune, calibrate or choose thresholds on the test set.
- If something fails or runs out of time: mark it ⚠ in the checklist with the reason and write "planned, not yet run" in the report. Do not fake it.
- Decisions D1–D6 are final. Do not redesign; if one is impossible with the data, mark ⚠ and explain.

## Workflow (do this after EVERY item)
1. Do the item. 2. Run its `verify:` command. 3. If it passes: change `[ ]` to `[x]` and append ` → <evidence path or 1-line result>`. If it fails after 2 fix attempts: `[⚠]` + reason, continue.
4. Update the STATUS block (next item, last gate result, blockers).
5. `git add -A && git commit -m "<item id>: <short summary>"`.
At the end of each phase run its **Gate**. Do not start the next phase until the gate passes or failures are marked ⚠.

## Code ↔ report in parallel
Each phase writes its report sections right after its results exist (the section files are listed in the phase). Write from `results/*.json`, not from memory. `python tools/check_report.py --only <group>` must pass for that phase's sections.

## Token economy
- Print summaries only: `head -n 20`, `wc -l`, `df.shape`, value counts. Long output → `logs/<name>.log`, then `tail -n 30`.
- One script per step: `src/stepN_<name>.py`, CLI args (`--seed`, `--config`), writes `results/<name>.json`. Reuse, don't re-explore.
- Don't re-read files you wrote in this session. Don't paste code back into chat.
- Write each report section once to the required fields; then fix only what the checker flags.
- End-of-session message ≤ 8 lines: items done, gate result, next item, blockers.

## Writing rules (report/sections/*.md → pandoc → docx)
- English, plain words, short sentences, tables over prose. Present tense for design, "expected" for predictions.
- Exact field labels from CONTEXT §9. Tables: caption line below, `Table n. …`; figures: `![…](figures/x.png)` then `Figure n. …`. IEEE citations [1]–[6].
- No placeholders left except `[to fill by group]` (members' shares). No "TODO", "TBD", "[e.g.".
- Banned vague phrases: "works well", "runs stably", "low gas", "high accuracy", "many times".

## Environment
- macOS Apple Silicon (M2), native. Python 3.11 venv at `.venv` (created by `tools/setup_env.sh`). Use `.venv/bin/python`.
- Chain: Ape 0.8 + ape-vyper + ape-foundry, Vyper 0.4.3, Anvil. Sepolia is NOT used in Week 4 (plan + budget only).
- If a tool fails on macOS, a Multipass Ubuntu VM exists: write the exact commands for the human in the checklist (⚠ HUMAN) instead of looping.
- Seeds: [11, 22, 33, 44, 55]. Pilot uses 11, 22, 33.
- Never commit: `data/`, `.env`, keystores, `*.parquet`, `*.rds`, model binaries > 5 MB.
