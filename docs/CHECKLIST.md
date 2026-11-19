# CHECKLIST — IS355 Week 4
Legend: `[ ]` todo · `[x]` done → evidence · `[⚠]` failed/skipped + reason · 👤 = human task (agent skips, but reminds).
Time boxes are hard limits (deadline 20/11/2026). If exceeded: ⚠, write "planned, not yet run", move on.

## STATUS (agent updates after every item)
- Next item: P4.5
- Last gate: P3 PASS (24 tests passed; sections 1.2 and 1.3 each 0 FAIL, 0 WARN)
- Blockers: D1 validation extrema overlap. Historical open-loan membership unavailable. 2024Q3 has no test rows.

---
## P0 · Setup (human first, then agent) — 30 min
- [ ] 👤 P0.1 Create GitHub repo `is355-liquidation-risk` (private), add teammate as collaborator, clone, copy this kit in, first commit.
- [ ] 👤 P0.2 Run `bash tools/setup_env.sh`; then `bash tools/push_initial.sh <Khanh folder> <Khanh email>` (copies legacy code + local data, pushes safely); run `bash tools/get_data.sh` only if `data/raw/finsurvival/Data` is missing.
- [x] P0.3 Folders: `src/ tests/ contracts/ scripts/ results/ logs/ figures/ out/ data/`; `.gitignore` per AGENTS.md; README stub (purpose, setup, run commands). → verify command passed; README.md
  verify: `grep -q '^data/' .gitignore && test -f README.md`
- [x] P0.4 `tools/env_report.py` → `results/env.json` (OS, CPU, RAM, python, pandas, sklearn, xgboost, shap, optuna, vyper, eth-ape, anvil version). → results/env.json
  verify: `.venv/bin/python -c "import json;d=json.load(open('results/env.json'));assert d['python'].startswith('3.11') and d['vyper'].startswith('0.4')"`
- [x] P0.5 Write `report/sections/15_env.md` (1.5): hardware, OS, versions table, networks (Anvil: function+gas; Sepolia: latency + E2E, RPC provider = Alchemy, planned), seeds, repo link, end-to-end command (`make all` or script list). → report/sections/15_env.md
- [x] P0.6 Inventory `legacy/` (Week 3 code by Khanh): for each notebook list cells/functions reusable for Steps 1–5 and any printed results with their config → `results/legacy_inventory.md` (≤ 40 lines). Reuse this logic in P1–P2; do not rewrite from scratch. Week 3 numbers from legacy outputs may be cited as "Week 3 pilot (Oct 2026, legacy/<file>)" only if the config is visible. Local data already copied: `data/raw/finsurvival/`, `data/raw/taiwan/`, `data/processed/` (skip downloads that already exist). → results/legacy_inventory.md
  verify: `test -f results/legacy_inventory.md`
- **Gate P0:** `.venv/bin/python tools/check_report.py --only 1.5`

## P1 · Data pilot + Steps 1–2 — 1.5 h
- [x] P1.1 `src/step1_load.py`: read all X parts + y (Borrow → Account Liquidated), join by `id`, mirror relevant `dataLoader.R` cleaning; Taiwan via `ucimlrepo` (id 350). Save `data/interim/*.parquet`. Write counts + schema (name, dtype) to `results/pilot_data.json`. → results/pilot_data.json (259,886 matched FinSurvival labels, 30,000 Taiwan clients)
  verify: `.venv/bin/python -c "import json;d=json.load(open('results/pilot_data.json'));print({k:d[k] for k in d if 'n_' in k})"` (compare with CONTEXT §3; explain any difference in the report)
- [x] P1.2 `src/step2_prepare.py`: label (17.43 d), drop short-observed + duplicate tx ids, D5 split with purges, KS drift (D ≥ 0.15) on train_core vs inner-val, encoding fitted on train_core only. Taiwan 60/10/30 stratified seed 11. Save splits; append to `results/pilot_data.json`: per-split n, positive rate, date range, dropped columns (+KS D). → results/pilot_data.json; 3 data tests passed
  verify: `.venv/bin/python -m pytest -p no:ape_test -q -s tests/test_data.py` (asserts: no id overlap between splits; date ranges match D5; no test row used in fitting encoders; label rates printed; Ape plugin disabled for data-only checks)
- [x] P1.3 Write `12_steps.md` Step 1 and Step 2 cards (11 fields each, pseudo-code for Step 2, one real example row, real counts). Note the D5 change. → report/sections/12_steps.md; Gate P1 PASS
- **Gate P1:** `.venv/bin/python tools/check_report.py --only 1.2 --steps 1,2`

## P2 · Model pilot + Steps 3–5 + 1.4 — 2.5 h
- [x] P2.1 `src/step3_train.py --model {B_LR,B_XGB,O_LR,O_XGB} --seed S`: B_* = all features + PCA (95% variance; state as our assumption about [1]); O_* = drift-removed, no PCA. Week 3 fixed params for the pilot (no Optuna yet). Early stopping on inner-val. XGB seeds 11,22,33; LR once (seed-insensitive → variance via 1,000 test bootstrap). Log fit time. → results/pilot_model.json (8 fits across 4 model variants)
  verify: `results/pilot_model.json` has AUC (inner-val, val, test) for 4 models and fit_seconds.
- [x] P2.2 `src/step4_calibrate.py`: isotonic on val; Brier uncal vs cal on test overall + per quarter (2022Q3…2024Q3); reliability bins CSV; SHAP top-10 (TreeExplainer, 2,000 test rows, seed 11). → results/pilot_calib.json and pilot_reliability.csv; native TreeSHAP used because TreeExplainer 0.49 cannot load XGBoost 3.2 vector intercepts
  verify: `results/pilot_calib.json` has brier_uncal, brier_cal, per_quarter list.
- [⚠] P2.3 `src/step5_tiers.py`: D1 fixed thresholds (τ_A, τ_C) + percentile comparison; wallet aggregation = max over open loans (D2); tier share + liquidation rate (Wilson CI) per tier, overall and per test quarter, both rules; model SHA-256; `data/processed/tiers.csv` (wallet, p, tier, model_version) + 20-row sample in `results/`. → results/pilot_tiers.json; independent D1 extrema overlap, so only the percentile comparison and cohort wallet proxy were run
  verify: `results/pilot_tiers.json` has tau_A, tau_C, both rules, per-quarter shares.
- [x] P2.4 `src/power.py`: s per model across seeds, s_d for (O_XGB − B_XGB) paired; n ≈ (2.8·s_d/Δ)² for Δ ∈ {0.01, 0.02}; CI half-width for n=5. → `results/pilot_power.json`. → results/pilot_power.json (3 paired XGB seeds and 5-seed CI estimate)
- [x] P2.5 Taiwan: O_XGB seed 11, test AUC → `results/pilot_taiwan.json`. → results/pilot_taiwan.json (O_XGB seed 11 on 9,000 test clients)
- [⚠] P2.6 `src/sim_policy.py` (D3a counterfactual with real labels, tiered vs uniform) → `results/pilot_policy.json`. If loan USD amount column is missing, use count-based metrics and say so. → results/pilot_policy.json; verified uniform and percentile sensitivity. Fixed-rule counterfactual unavailable due to D1 overlap
- [x] P2.7 Write Steps 3–5 cards + `14_model.md` (columns: Baseline [1] reproduced · Ours · Taiwan; rows: algorithm, hyperparameters & search space, tuning method & budget (Optuna 50 trials each, inner-val), loss, class imbalance, threshold choice (val only), leakage controls). Mark pilot numbers with date. → report/sections/12_steps.md and 14_model.md; both Gate P2 checks passed
- **Gate P2:** `.venv/bin/python tools/check_report.py --only 1.2 --steps 1,2,3,4,5 && .venv/bin/python tools/check_report.py --only 1.4`

## P3 · Contracts + T3/T4 pilot + gas + Steps 6–8 + 1.3 — 2.5 h
- [x] P3.1 `contracts/`: MockERC20.vy, PriceOracle.vy, ScoreOracle.vy, LendingPool.vy (constructor takes policy params so the same code deploys as Tiered or Uniform). Loan stores `tier_at_borrow`. `get_tier` returns 2 (B) if unscored or stale > 30 days. `@nonreentrant` on state-changing functions. Exact assert messages. → Ape compiled four Vyper 0.4.3 contracts
  verify: `.venv/bin/ape compile`
- [x] P3.2 `tests/test_t3_functions.py`: every function in CONTEXT §9 → 1 valid + 1 revert (match message). → 11 passed on Anvil, with valid calls and exact guard messages
  verify: `.venv/bin/ape test tests/test_t3_functions.py -q`
- [x] P3.3 `tests/test_t4_security.py` (≥6): unauthorized set_score; version mismatch; stale score → B terms; liquidate healthy loan; repay > 50% in liquidation; zero / max uint amounts; Sybil fresh wallet gets B (documents limitation); Hypothesis ≥200 examples: borrow never exceeds tier limit. → 10 defensive tests passed on Anvil, including 200 Hypothesis examples
  verify: `.venv/bin/ape test tests/test_t4_security.py -q`
- [x] P3.4 Gas pilot: `ape test --gas` + `scripts/gas_batch.py` (set_scores_batch with 1/10/100 wallets) → `results/pilot_gas.json`; put EVM estimate (CONTEXT §11) next to measured; flag > 2×. → results/pilot_gas.json; 30 Anvil batch receipts and 10 T3 gas-profile tests passed. Reverting view calls verified separately without Ape tracing.
- [x] P3.5 Write `13_contract.md` (state vars; function table with role, asserts+messages, state change, event, est. + measured gas; loan state machine figure `figures/state_machine.png` + transition table incl. forbidden; events table with reader; off-chain ↔ on-chain: Ape scripts sign with Ape keystore account `oracle`, never a raw key in code; failed/stuck tx: wait 3 blocks, resend same nonce with +20% fee, max 3 tries, log; blockchain guarantees vs not; oracle trust & key-leak risk) + Steps 6–8 cards. → section 1.3, Steps 6–8 and state machine figure; Gate P3 passed
- **Gate P3:** `.venv/bin/ape test -q && .venv/bin/python tools/check_report.py --only 1.2 && .venv/bin/python tools/check_report.py --only 1.3`

## P4 · Test plan sections — 2 h (write from results/*.json)
- [x] P4.1 `21_hypotheses.md`: H1–H7 from CONTEXT §6, each with primary metric and acceptance criterion. → report/sections/21_hypotheses.md; verified seven primary metrics and acceptance criteria
- [x] P4.2 `22_overview.md`: table of all scenarios (ID, name, group, H/I link, env, runs). → report/sections/22_overview.md; verified 37 unique scenarios across T1–T7
- [x] P4.3 `23_scenarios.md`: T1 (reproduce baseline; H1; H2; H3 tiers both rules; H4 policy tiered vs uniform; H6 Taiwan) · T2 (drift on/off, PCA on/off, isotonic/Platt/none, KS threshold, tier rule) · T3 compact table (all 11 functions) · T4 ≥ 8 incl. edge-of-design (oracle key leak, owner price manipulation, front-run of tier downgrade, Sybil) with "not blocked" stated · T5 gas sizes + Sepolia latency · T6 ×2 (data→tiers→chain with hash/count match; price drop→liquidation via Streamlit) · T7 (per-quarter calibration; Taiwan; 1,000-run Monte Carlo price shocks for D3b). → report/sections/23_scenarios.md; 37 scenario IDs match Section 2.2 and the 2.3 checker passed
- [x] P4.4 `24_runs.md`: unit of repetition per scenario; runs vs minimum; CI + n formula with pilot s, s_d; Sepolia ETH budget = Σ(gas × tx) × gas price (state assumed gwei) vs faucet amount; summary table (scenario, unit, runs, reason, aggregation, est. time). → Section 2.4 verified against pilot power and gas JSON
- [ ] P4.5 `25_expected.md`: per H: Expected | Basis | Reject if | If rejected; gas estimate vs pilot; latency expectation (Sepolia ~12 s blocks; median 7–15 s, p95 24–36 s) labelled expected; baseline reproduction tolerance ±0.02 AUC.
- [ ] P4.6 `26_schedule.md`: Week 5…Week 9 table (task, weeks, duration calc, owner Khanh/Ngoc, depends on, output), M1–M4, ≥20% buffer; `figures/gantt.png` (matplotlib).
- [ ] P4.7 `27_risks.md`: ≥4 risks (faucet ETH, RPC limits, baseline not reproducible, prior shift breaks calibration, 2-person team) with likelihood, impact, backup.
- **Gate P4:** `.venv/bin/python tools/check_report.py --only 2`

## P5 · Part A, figures, assembly, final review — 1 h
- [ ] P5.1 `00_info.md`: info table (Repository = GitHub URL), members table (`[to fill by group]` for tasks/shares), Response-to-feedback table (6 rows = CONTEXT §5, with section numbers), Changes since Week 3.
- [ ] P5.2 `11_workflow.md` + `figures/workflow.png` (graphviz): Steps 1–8 exactly as 1.2, I1–I4 marks, off-chain/on-chain boundary, data name on every arrow; change table.
- [ ] P5.3 `30_next.md`, `90_refs.md` (CONTEXT §12), `95_appendix.md` (pilot table).
- [ ] P5.4 `bash tools/build_docx.sh` → `out/6_BC_IS355_Week4_Project.docx`.
- [ ] P5.5 Full check + self-review: `.venv/bin/python tools/check_report.py` → 0 FAIL. Then write `results/rubric_review.md`: per rubric row (CONTEXT §7) score 0–100% with the weakest point; fix the 2 weakest; rebuild.
- [ ] 👤 P5.6 Open docx in Word: fill members' tasks/shares, check 12–18 pages, figures readable, export PDF if wanted, submit on Moodle (Exercise 4). Push repo; make it visible to the lecturer.
- **Gate P5:** `.venv/bin/python tools/check_report.py && test -f out/6_BC_IS355_Week4_Project.docx`
