# CONTEXT — IS355 Week 4 (single source of facts)
Read only the section you need. Do NOT open the original .docx files; everything needed is here.

## 1. Project
- Title: Calibrated and Explainable Liquidation-Risk Scoring for DeFi Lending with an On-chain Risk-Tiered Lending Pool
- Group: 6 – BC (lecturer code 3H2N52) · Class: IS355.R11.CTTT.1
- Members: Tran Quang Khanh (Leader, 23520724) · Nguyen Le Nhu Ngoc (23521031). Week 4 shares: leave `[to fill by group]` (human fills).
- Report file name: `6_BC_IS355_Week4_Project.docx`. Language: English. 12–18 A4 pages excl. cover, refs, appendix.
- Deadline: 20/11/2026. Final presentation date unknown → schedule uses "Week 5, Week 6, …" not dates.

## 2. Week 3 method (8 steps, keep numbering)
1. Data collection — FinSurvival (Borrow → Account Liquidated) .rds + Taiwan .xls → parquet.
2. Labelling & features (I2) — label = 1 if liquidated within 17.43 days (threshold from [1]); drop loans observed < 17.43 days; drop ID/empty cols; drop drifting features via KS test; encode text cols.
3. Training (I2) — LogReg (C=0.1, balanced) and XGBoost (lr 0.05, depth 6, early stop 50 rounds on AUC, class weight). No PCA.
4. Calibration & explanation (I1) — isotonic regression; Brier; SHAP.
5. Risk tiers (I1) — tier per wallet A/B/C; model file SHA-256.
6. ScoreOracle.vy (I3) — owner `register_model(hash, version)`; oracle `set_score(wallet, tier, version)`; version must match; score older than 30 days not used; event ScoreUpdated. Off-chain writer = web3.py/Ape script.
7. LendingPool.vy (I3) — deposit_collateral, borrow, repay, liquidate. Tier A needs 120% collateral, B 150%, C cannot borrow. Liquidation below 110% (A) / 130% (B). Liquidator repays ≤ 50% of debt, 5% bonus [4]. PriceOracle.set_price simulates price moves. Test tokens.
8. Demo & evaluation — Streamlit app; scripts for AUC, Brier, tier rates, gas.
On-chain data: tier (uint8), model version + hash, collateral/debt. Off-chain only: raw loan data, SHAP.
Improvements: I1 calibration+SHAP+tiers · I2 no PCA + drift removal · I3 only tier on-chain + contract sets collateral by tier · I4 same pipeline on Taiwan.

## 3. Data facts (Week 3, measured by the group)
- Repo: https://github.com/Large-Transaction-Models/DMLR_DeFi_Survival_Benchmark (Apache-2.0).
  Files: `Data/Survival_Data/Borrow/X_train/X_train_{1..4}.rds`, `X_test/X_test_{1..3}.rds`, `Borrow/Account Liquidated/y_{train,test}.rds`. Join X and y by `id`. Load all X parts and concat. Benchmark split: test from 2022-07-01. Upstream `dataLoader.R` does extra cleaning — read it (head only) and mirror the relevant steps in Python.
- 264,536 labelled loans (259,886 with features); 128 features. After cleaning: 251,171 loans; label rate 4.81% overall, 6.98% train, 1.31% test. 4,159 loans share a transaction id → removed. 4,650 test labels have no feature row.
- Taiwan: UCI id 350, 30,000 clients, 23 features, default 22.1%; drop SEX, MARRIAGE; no time order → random stratified 60/10/30 and NO drift step (state this).

## 4. Baseline numbers from papers
- [1] borrow→liquidation (4.77% liquidated): AUC 0.723 LogReg, 0.732 XGBoost, 0.750 DeepHit. [1] uses PCA for most models.
- [3] Taiwan AUC ≈ 0.68–0.71 (read from a chart; approximate).
- [4] close factor 50%, liquidation bonus ≈ 5%.
- Aave V2 WETH (launch parameters): LTV 80%, liquidation threshold 82.5%, liquidation bonus 5% [6]. Parameters changed later (e.g., LTV 82.5%/LT 85% in late 2021; LTV 81%, bonus 4% in May 2022) — say we use the launch values and why.

## 5. Lecturer feedback on Week 3 → decisions (FINAL, do not change)
| # | Prio | Feedback | Decision |
|---|---|---|---|
| 1 | High | Percentile tiers (70/20/10) always put 10% in C even when risk falls 6.98%→1.31% | D1: main = fixed probability thresholds chosen on validation; percentile kept as comparison; report tier share + liquidation rate per tier per test quarter for both |
| 2 | High | Score per loan, tier per wallet: aggregation, default tier for new wallets, risk of new-wallet creation | D2: wallet p = max p over its open loans; unscored or stale (>30 days) wallet → tier B; Sybil (new wallet to escape C) cannot be blocked, limited by B = 150%; T4 scenario + limitation |
| 3 | High | E5 only measures gas; add uniform Aave-style collateral baseline under price drops | D3: compare tiered vs uniform (Aave V2 WETH launch params) on same test loans: (a) counterfactual with real labels, (b) price-shock simulation; metrics below |
| 4 | Medium | Calibration only on 90 val days; report Brier + calibration curve per test quarter | D4: T7 scenario, quarters 2022Q3…2024Q3 |
| 5 | Medium | Two descriptions of the validation set | D5: dates below |
| 6 | Low | AUC ≥ 0.732 may not hold after removing PCA/drifting features | D6: H1 = non-inferiority (margin 0.02); main hypotheses on calibration (I1) and policy (I3) |
General lecturer notes to honour: say what blockchain guarantees (integrity, no duplicate issuance, audit trail) and does NOT (correct inputs, correct model); who writes on-chain (oracle wallet) and risk if it lies or its key leaks; Vyper + Ape; each improvement has a reasonable (not deliberately weak) baseline and a metric.

### D1 tier thresholds (fixed, chosen on validation only)
- r_val = liquidation rate on validation.
- Search ordered cutoffs on the 0.005 validation grid. Require nonempty A/B, rate(A) ≤ 0.75·r_val and rate(C) ≥ 2·r_val with ≥ 30 positives and C share ≤ 20%. If no strict pair exists, retry with C ≥ 1.5·r_val. Maximize rate(C)/rate(A), with zero A rate scored as infinity. Ties favor greater combined A+C coverage, then smaller cutoffs.
- The prior independent 0.5×/3× extrema overlapped in the pilot. The revised joint rule permits a feasible three-way split while preserving distinct validation risk targets.
- A: p < τ_A · B: τ_A ≤ p < τ_C · C: p ≥ τ_C. Comparison: percentile 70/90 on validation scores.
- Tier encoding on-chain: 0 = none, 1 = A, 2 = B, 3 = C.

### D3 policy comparison
- Tiered: A 120% / liq <110%, B 150% / liq <130%, C rejected. Uniform: 125% (LTV 80%) / liq when collateral/debt < 121.2% (LT 82.5%), bonus 5%, close factor 50% for both.
- (a) Counterfactual with real labels (no price model): per policy, count accepted loans, rejected loans, liquidations avoided (rejected & actually liquidated), good loans rejected (rejected & not liquidated), capital locked = Σ required ratio × loan USD; capital freed vs uniform.
- (b) Price-shock simulation: collateral volatile, debt stable; borrower buffer above minimum drawn from a stated distribution with seed (mark as simulated); shocks −10/−20/−30/−40%; metrics: # liquidated, liquidated collateral USD, bad debt. Planned 1,000 Monte Carlo runs; pilot = 1 deterministic run per shock.

### D5 time split (by loan start time; FinSurvival only)
- test: ≥ 2022-07-01 (benchmark split, unchanged)
- val (calibration + tier thresholds only): 2022-04-02 … 2022-06-30
- purge: 2022-03-15 … 2022-04-01 (18 days ≥ 17.43-day label window) dropped
- inner-val (early stopping, Optuna, KS drift check vs train_core): 2021-12-15 … 2022-03-14
- purge: 2021-11-27 … 2021-12-14 dropped
- train_core: < 2021-11-27
- Re-derive and print exact dates/counts in code; if counts differ from Week 3, report actual numbers.
- KS drift: numeric feature dropped if KS D(train_core, inner-val) ≥ 0.15 (T2 sensitivity: 0.10/0.15/0.20/0.30).

## 6. Hypotheses (use these IDs)
- H1 (I2, D6): ΔAUC = AUC(ours) − AUC(primary baseline, all features without PCA), paired by seed; accept if lower 95% CI bound > −0.02. Secondary: val–test AUC gap smaller for ours.
- H2 (I1): Brier(calibrated) < Brier(uncalibrated) on test; paired by seed; CI of difference excludes 0.
- H3 (I1, D1): fixed-threshold tiers give liquidation rate A < B < C on test with non-overlapping 95% Wilson CIs; share of C on test falls with base rate (percentile rule stays ≈10%).
- H4 (I3, D3): tiering avoids more labelled liquidations, lowers tier-A collateral per debt dollar and keeps total collateral and simulated bad debt at or below uniform. Record counts, USD and the paired shock results for both policies.
- H5 (I3): gas — set_score ≤ X, batch(100) per wallet ≤ Y (from EVM estimate + Anvil pilot); security — every designed-to-block T4 attack reverts with its exact message; Sybil and oracle-key compromise documented as not blocked.
- H6 (I4): Taiwan test AUC within expected range from pilot; compare [3] ≈ 0.68–0.71.
- H7 (D4): calibration drifts: Brier/curve per test quarter; expected over-prediction as base rate falls.

## 7. Week 4 rubric (lecturer) and how we score
| Criterion | Weight | Must show |
|---|---|---|
| Update after Week 3 | 5% | feedback table (6 rows above) + changes; diagram steps = 1.2 steps |
| Step-by-step spec | 20% | every step: 11 fields (§9), pseudo-code 5–15 lines or formulas with symbols, output example, correctness check; output(step k) = input(step k+1) same name/format; improved steps detailed vs baseline |
| Contract, model & env | 10% | state vars, function table (role, asserts+messages, event, gas), state machine + forbidden transitions, events + reader, Ape/web3 signing, key storage, stuck tx; model table with equal tuning budget; versions, seeds, run command |
| Test scenarios | 20% | T1–T6 (+T7, required: time data); full 8-field cards for T1,T2,T4,T5,T6; T3 compact table; T4 ≥ 5 and non-trivial (edge-of-design: oracle key leak, Sybil, owner price manipulation, front-run of tier downgrade) |
| Runs & justification | 15% | unit of repetition per scenario; minimums (§10); CI and n ≈ (2.8·s_d/Δ)² using OUR pilot s, s_d; Sepolia ETH budget; summary table |
| Expected results | 15% | number/range + basis (paper / pilot / calculation / mechanism) + reject condition + "if rejected"; realistic; labelled "expected" |
| Schedule | 10% | weekly table: task, start–end week, duration = runs × time/run + prep + analysis, owner, dependency, output; M1–M4; ≥20% buffer; Gantt figure; ≥3 risks with likelihood, impact, backup |
| Presentation & refs | 5% | template order, captions "Table n."/"Figure n.", IEEE refs |
Common errors that lose points: step = name only; only happy-path tests; uncheckable expected results ("works well", "low gas", "high accuracy"); one run or "many runs" without number; latency on Anvil presented as real; tuning/thresholds on test; baseline with different data/split/budget; expected results without basis; schedule without durations/owners or all tests in last week. Fake pilot results = cheating.
Milestones: M1 implemented (all T3 pass on Anvil) · M2 config frozen (tagged commit; test set only for evaluation) · M3 all T1–T7 runs done (raw CSV/logs) · M4 analysis + final draft.

## 8. Template order (report/sections files)
00_info.md (A. Information: info table incl. Repository; members table; Response to Week 3 feedback; Changes since Week 3) · 11_workflow.md (1.1 + Figure 1 + change table) · 12_steps.md (1.2) · 13_contract.md (1.3) · 14_model.md (1.4) · 15_env.md (1.5) · 21_hypotheses.md (2.1) · 22_overview.md (2.2 scenario overview table) · 23_scenarios.md (2.3) · 24_runs.md (2.4) · 25_expected.md (2.5) · 26_schedule.md (2.6) · 27_risks.md (2.7) · 30_next.md (3. Next Steps) · 90_refs.md · 95_appendix.md (Appendix A — Pilot runs: date, config, seed, command, results file).

## 9. Required fields
- Step card (table rows, exact labels): Purpose | Input | Processing | Parameters | Libraries / tools | Output | Runs | Correctness check | Errors & edge cases | Est. run time | Improvement
- Scenario card (T1,T2,T4,T5,T6; heading `#### T4-03 · <name>`): Objective | Preconditions | Input data | Steps | Expected result | Pass criterion | Runs & environment
- Hypothesis block (2.5): Expected | Basis | Reject if | If rejected
- Contract functions that must appear in 1.3 and T3: register_model, set_oracle, set_score, set_scores_batch, get_tier, deposit_collateral, withdraw_collateral, borrow, repay, liquidate, set_price

## 10. Minimum runs (lecturer)
ML T1/T2: 5 seeds same split (data > 5,000) · tuning: same Optuna budget for every method (50 trials), validation only · gas: ≥3 input sizes (1/10/100) × 10 calls with different data · Sepolia latency: 30 tx per main function in ≥2 time windows (median, p95; p95 needs ~100) · T3/T4: 1 deterministic run per case + Hypothesis ≥200 examples for arithmetic/permission functions · T6: 3 full runs on fresh deploy · T7 simulation: until 95% CI narrower than effect (≥1,000 Monte Carlo).
CI: x̄ ± t(0.975; n−1)·s/√n. Runs needed: n ≈ (2.8·s_d/Δ)², round up, +1–2.

## 11. EVM gas constants (for estimates before measuring)
tx base 21,000 · SSTORE 0→non-0 (cold) 22,100 · non-0→non-0 (cold) 5,000 · cold SLOAD 2,100 · warm SLOAD 100 · calldata 16/non-zero byte, 4/zero byte · LOG 375 + 375/topic + 8/byte · ERC-20 transferFrom ≈ 30k–50k. If measured > 2× estimate → storage design problem; explain.

## 12. References (IEEE; keep numbering)
[1] A. Green, Z. Nie, H. Qin, O. Seneviratne, and K. P. Bennett, "FinSurvival: A suite of large scale survival modeling tasks from finance," arXiv:2507.14160, 2025.
[2] A. M. Green, M. P. Giannattasio, J. S. Erickson, O. Seneviratne, and K. P. Bennett, "DeFi survival analysis: Insights into the emerging decentralized financial ecosystem," Distrib. Ledger Technol.: Res. Pract., vol. 3, no. 1, art. 4, 2024, doi: 10.1145/3638064.
[3] F. Yang, Y. Qiao, Y. Qi, J. Bo, and X. Wang, "BACS: Blockchain and AutoML-based technology for efficient credit scoring classification," Ann. Oper. Res., 2022, doi: 10.1007/s10479-022-04531-8.
[4] K. Qin, L. Zhou, P. Gamito, P. Jovanovic, and A. Gervais, "An empirical study of DeFi liquidations: Incentives, risks, and instabilities," in Proc. ACM IMC, 2021, doi: 10.1145/3487552.3487811.
[5] I.-C. Yeh, "Default of credit card clients," UCI Machine Learning Repository, 2016, doi: 10.24432/C55S3H.
[6] Aave, "Risk parameters (Aave V2)," Aave Risk Documentation. [Online]. Available: https://docs.aave.com/risk/v/aave-v2/asset-risk/risk-parameters
