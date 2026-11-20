<!-- 12_steps -->
### 1.2. Step-by-step specification

Appendix B records input and output examples, pseudocode, parameters and checks for each step.

| Step | Procedure and handoff |
| --- | --- |
| 1. Data collection | Join FinSurvival features and labels by ID and load Taiwan UCI 350. Write interim parquet. The pilot matched 259,886 FinSurvival labels and loaded 30,000 Taiwan records. |
| 2. Labelling and feature preparation | Label liquidations within 17.43 days. Drop repeated IDs and short censored records. Purge the two D5 gaps. Learn the encoder on training and flag drift at KS D ≥ 0.15. Write split parquet and feature rules. |
| 3. Train baseline and proposed models | Compare LR and XGBoost on all eligible PCA features versus drift-filtered inputs without PCA. Early-stop XGBoost on inner validation. Save frozen models and scores. Mean pilot XGBoost test AUC was 0.7020 for baseline and 0.8033 for proposed. |
| 4. Calibrate and explain probabilities | Fit isotonic on validation. Evaluate Brier and reliability on test, and rank TreeSHAP on a seeded sample. Seed-11 test Brier moved from 0.06409 to 0.01636. |
| 5. Assign risk tiers | Freeze feasible validation cutoffs, then aggregate maximum risk per wallet. D1 cutoffs overlapped, so the pilot exported percentile comparison tiers and model SHA-256. Historical open-loan membership is unavailable. |
| 6. Register model and write scores | Register the hash and version and write wallet tiers through the authorized oracle. Match receipt events to input. |
| 7. Execute the lending policy | Apply borrowing and maintenance limits using the effective tier and collateral price. Record debt, collateral and loan events. |
| 8. Demonstrate and evaluate | Reconcile registered hash, wallet counts, receipts and dashboard state. Local checks and gas are measured. Full integration is planned, not yet run. |

<!-- 13_contract -->
### 1.3. Smart contract specification

ScoreOracle stores the writer, model version and digest, and each wallet's tier, version and timestamp. Missing, stale or old-version scores fall back to B. PriceOracle stores a scaled owner-set collateral price. LendingPool stores collateral, debt and the original borrowing tier. MockERC20 supplies balances and allowances for local tests.

| Policy | Origination collateral | Maintenance collateral |
| --- | --- | --- |
| Tiered | A 120%, B 150%, C ineligible | A 110%, B 130% |
| Uniform | 125% | Approximately 121.2% [6] |

The close factor is 50% and the seizure bonus is 5% [4]. Liquidation requires health below maintenance. Full repayment clears the tier snapshot. Appendix B lists function roles, exact guards, events and gas.

![Loan state machine](figures/state_machine.png)

Figure 2. Loan state transitions at the current collateral price.

The planned writer signs with the Ape keystore account `oracle`. Check the receipt after three pending blocks. If needed, resend using the same nonce and a 20% higher fee, up to three retries. Keep the private key out of source and results. The chain enforces roles and atomic writes and records accepted changes. Score quality and oracle inputs depend on trusted off-chain actors.

<!-- 22_overview -->
### 2.2. Test scenario overview

| Group | Scope | Environment and planned units |
| --- | --- | --- |
| T1 | Reproduction, H1–H4, Taiwan H6 | Python. Five matched seeds, with one deterministic LR fit and bootstrap. |
| T2 | Drift, PCA, calibration, KS threshold and tier rule | Python. Five paired seeds per setting. |
| T3 | Eleven contract functions | Ape and Anvil. One valid and one guard case per function. |
| T4 | Defensive guards and residual trust or identity risks | Ape, Anvil, Hypothesis and design review. One deterministic case per guard and 200 generated cases. |
| T5 | Score-write gas and testnet latency | Anvil and planned Sepolia. Ten transactions per batch size and 100 confirmations per main function. |
| T6 | Tier reconciliation and dashboard liquidation | Three fresh Anvil deployments per scenario. |
| T7 | Quarterly calibration, Taiwan sensitivity and price shocks | Five seeds and at least 1,000 paired Monte Carlo runs per shock. |

Appendix C maps all 37 scenario IDs to hypotheses, environments and run counts.

<!-- 23_scenarios -->
### 2.3. Test scenario details

- **T1 and T2.** Freeze D5 and common seeds. Compare reproduction tolerance, paired AUC and Brier, tier allocation and counterfactual policy outcomes. Change one factor per ablation. Fit every calibration map and threshold on validation.
- **T3 and T4.** Check state and guard messages on fresh local fixtures. Record authorization, version, freshness, collateral and liquidation results. Document owner price control, writer compromise, Sybil exposure and ordering assumptions as residual design risks.
- **T5 and T6.** Profile score writes at 1, 10 and 100 wallets. Measure confirmation time only on Sepolia. Reconcile the hash, score events and wallet count on fresh Anvil deployments, then compare dashboard state with liquidation receipts.
- **T7.** Report Brier, prevalence and reliability by populated quarter. Reuse Taiwan fits for stability. Simulate shared price shocks of −10%, −20%, −30% and −40% and report liquidations, collateral seized and residual unsecured debt. Test 2024Q3 is empty.

Appendix C supplies inputs, prerequisites, procedures, expected outcomes and pass criteria. Fixed-tier policy outcomes remain unavailable because the pilot D1 cutoffs overlap.

<!-- 25_expected -->
### 2.5. Expected results and reasoning

| Hypothesis | Expected and evidence | Reject condition and response |
| --- | --- | --- |
| H1 | Paired lower AUC bound > −0.02. Pilot means 0.8033 proposed, 0.7020 with PCA, and 0.8091 without PCA on all eligible features. | At or below −0.02, inspect matched feature and PCA ablations. |
| H2 | Lower calibrated Brier. Seed 11 measured 0.01636 versus 0.06409 raw. | If the upper difference bound is nonnegative, compare quarterly calibration maps. |
| H3 | Ordered tier liquidation rates and disjoint intervals. D1 pilot extrema overlap. | If feasible cutoffs fail separation, report results. For infeasible cutoffs, mark the test unevaluable. |
| H4 | Tier A requires five percentage points less collateral than uniform. | If savings fail or rejection efficiency is undefined, report counts and collateral separately. |
| H5 | Single gas ≤100,000 and 100-wallet gas ≤75,000 per wallet. Pilot measured 94,739 and 69,252 respectively. | Investigate any exceeded limit or guard failure. Sepolia latency remains planned. |
| H6 | AUC 0.760–0.810 around the 0.7834 Taiwan pilot. | If outside range, review exclusions, split and seed variation. |
| H7 | Positive calibration gap rises as prevalence falls. | If the directional criteria fail, inspect the quarterly series and coverage. |

Appendix D gives the full reasoning, including the ±0.02 reproduction tolerance and expected Sepolia median 7–15 s and p95 24–36 s.
