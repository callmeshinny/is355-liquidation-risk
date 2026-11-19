## 2.3 Test scenario specifications

### T1 · Model comparisons

#### T1-01 · Reproduce baseline AUC

| Field | Specification |
| --- | --- |
| Objective | Check reproduction of the Borrow → Account Liquidated baselines in [1]. |
| Preconditions | D5 splits frozen and all eligible features available. |
| Input data | FinSurvival features and 17.43-day outcomes. |
| Steps | Fit scaling and 95%-variance PCA on train_core. Fit LR and XGBoost with Week 3 settings, use inner-val AUC for XGBoost early stopping, then score test once per fit. |
| Expected result | The target AUCs are 0.723 for LR and 0.732 for XGBoost [1]. |
| Pass criterion | Each respective test AUC estimate is within ±0.02 of its paper target. Record any miss and retain it in the H1 comparison. |
| Runs & environment | Python, five XGBoost seeds on the same folds. One deterministic LR fit and 1,000 stratified test bootstrap draws. |

#### T1-02 · Test model non-inferiority

| Field | Specification |
| --- | --- |
| Objective | Evaluate H1 and the validation-to-test AUC gap. |
| Preconditions | Freeze the split, features and matched seed list. |
| Input data | D5 FinSurvival splits and two XGBoost configurations. |
| Steps | Train the all-feature PCA and drift-filtered no-PCA variants per seed. Calculate the test AUC difference within each pair and its 95% t interval. |
| Expected result | The proposed model remains within the non-inferiority margin. |
| Pass criterion | The lower bound of the paired interval exceeds −0.02. Report both absolute validation-to-test gaps. |
| Runs & environment | Python, five paired seeds. |

#### T1-03 · Compare raw and isotonic scores

| Field | Specification |
| --- | --- |
| Objective | Evaluate H2 on matched test rows. |
| Preconditions | Freeze each XGBoost fit before calibration. |
| Input data | Validation scores and labels, and held-out test scores and labels. |
| Steps | Fit isotonic on validation. Apply the frozen map to test and compute raw and calibrated Brier per seed. Form a 95% t interval for calibrated minus raw Brier. |
| Expected result | Expected Brier difference is negative. |
| Pass criterion | Upper 95% confidence bound is below zero. |
| Runs & environment | Python, five paired seeds. Seed-11 comparison measured in results/pilot_calib.json. |

#### T1-04 · Compare fixed and percentile tiers

| Field | Specification |
| --- | --- |
| Objective | Evaluate H3 with D1 thresholds and the percentile comparator. |
| Preconditions | Frozen risk scores, validation-only threshold fitting and ordered D1 cutoffs for the fixed branch. |
| Input data | Calibrated scores, outcomes, UTC quarters and wallet identifiers. |
| Steps | Determine independent D1 extrema using validation tails and validate their order. Fit 70th and 90th percentile comparison cutoffs on validation. Freeze rules. Report test tier sizes, liquidation rates and Wilson intervals by quarter. |
| Expected result | Expected fixed-tier rates increase from A to C. C share falls with base rate. Percentile shares may vary with ties and drift. |
| Pass criterion | Apply H3’s ordered-rate and disjoint-interval criteria. Record overlapping or absent cutoffs and leave fixed outputs missing for such seeds. |
| Runs & environment | Python, five seeds per rule. The fixed pilot is planned, not yet run because the observed validation extrema overlap. |

#### T1-05 · Compare lending policies using realized labels

| Field | Specification |
| --- | --- |
| Objective | Measure the D3a counterfactual on the same test loans. |
| Preconditions | Frozen scores and ordered D1 cutoffs for the fixed comparison. Historical open-loan membership is unavailable. |
| Input data | Loan scores at origination, liquidation labels and positive finite loan USD amounts when available. |
| Steps | Apply tiered A/B borrowing ratios of 120%/150% and reject C. Apply 125% to all eligible loans in the uniform comparison. Count accepted, rejected, rejected liquidations and rejected good loans. Sum required collateral on the common priced subset. |
| Expected result | Tier A uses less initial collateral per USD borrowed. The tiered rejection outcome depends on the score rule. |
| Pass criterion | Apply H4 where both ratios exist. For zero denominators, mark the ratio undefined and report counts and capital. Separate percentile sensitivity from fixed results. |
| Runs & environment | Python, five paired score seeds. Fixed comparison planned, not yet run. The percentile sensitivity is recorded in results/pilot_policy.json. |

#### T1-06 · Evaluate Taiwan test AUC

| Field | Specification |
| --- | --- |
| Objective | Evaluate H6 on external credit-default data. |
| Preconditions | Use a fixed stratified 60/10/30 split and reserve the test fold. |
| Input data | UCI dataset 350 with SEX and MARRIAGE excluded. |
| Steps | Fit XGBoost with early stopping on a stratified inner fold carved from training. Compute continuous-score ROC AUC on held-out test and summarize seeds. |
| Expected result | Expected test AUC is in the planning range 0.760–0.810. |
| Pass criterion | Compare reported AUC with that range and the approximate paper chart range 0.68–0.71 [3]. Treat reuse of the pilot test split as replication evidence. |
| Runs & environment | Python, five seeds on one stratified split. Seed 11 is measured. |

### T2 · Ablations

#### T2-01 · Drift removal ablation

| Field | Specification |
| --- | --- |
| Objective | Estimate the effect of the KS feature filter. |
| Preconditions | Fix PCA, learner and calibration settings within each pair. |
| Input data | D5 features and the train_core versus inner-val KS statistics. |
| Steps | Train the same learner with the D ≥ 0.15 drop list enabled and disabled. Compute paired held-out AUC differences. |
| Expected result | The drift-filtered branch is expected to retain discrimination. |
| Pass criterion | Verify identical folds and settings within pairs. Report paired AUC and a 95% interval against the H1 margin. |
| Runs & environment | Python, five paired seeds per setting. |

#### T2-02 · PCA ablation

| Field | Specification |
| --- | --- |
| Objective | Measure the effect of PCA while holding drift filtering constant. |
| Preconditions | Fix the feature set and fit scaling within train_core. |
| Input data | D5 features and labels from the same folds. |
| Steps | Train paired XGBoost variants with 95%-variance PCA enabled or disabled. Use inner-val early stopping in both settings. |
| Expected result | Expected change is measured for the same features and seeds. |
| Pass criterion | Confirm that test rows were excluded from preprocessing. Report paired test AUC and its 95% interval. |
| Runs & environment | Python, five paired seeds per setting. |

#### T2-03 · Calibration ablation

| Field | Specification |
| --- | --- |
| Objective | Compare isotonic, Platt and raw scores. |
| Preconditions | Freeze each raw model and keep validation and test distinct. |
| Input data | Validation scores and outcomes, plus held-out test scores and outcomes. |
| Steps | Fit isotonic and a logistic mapping on validation. Evaluate raw and both mapped outputs on the same held-out rows using Brier and reliability bins. |
| Expected result | Calibration changes probability reliability. A negative Brier difference indicates improvement. |
| Pass criterion | Report paired Brier differences and intervals for each mapping versus raw. Apply the H2 criterion to isotonic. |
| Runs & environment | Python, five paired seeds per setting. |

#### T2-04 · KS threshold sensitivity

| Field | Specification |
| --- | --- |
| Objective | Measure sensitivity to the drift-screen cutoff. |
| Preconditions | Freeze the thresholds before test evaluation. |
| Input data | Numeric feature distributions on train_core and inner-val. |
| Steps | Generate drop lists for KS D cutoffs 0.10, 0.15, 0.20 and 0.30. Fit otherwise identical XGBoost configurations and score test. |
| Expected result | The cutoff changes the feature count and may affect generalization. |
| Pass criterion | Report dropped counts, paired AUC differences and validation-to-test gaps at every cutoff. Keep 0.15 as the primary cutoff. |
| Runs & environment | Python, five paired seeds per cutoff. |

#### T2-05 · Tier rule sensitivity

| Field | Specification |
| --- | --- |
| Objective | Isolate the effect of the assignment rule on the same scores. |
| Preconditions | Use validation-only thresholds. Mark infeasible fixed cutoffs per seed. |
| Input data | Identical calibrated score vectors and labels for each rule. |
| Steps | Apply D1 fixed cutoffs and validation percentile cutoffs. Compare tier shares, Wilson intervals and D3a summaries for feasible pairs. |
| Expected result | The percentile comparator provides a second allocation of the same scores. |
| Pass criterion | Report each feasible pair and its coverage. If D1 is infeasible, report the available comparator and leave its fixed counterpart missing. |
| Runs & environment | Python, five paired seeds per rule. |

### T3 · Contract functions

Run each valid case and its guard case once on a fresh local Ape/Anvil fixture. Verify state or return value for the valid call and match the exact guard message. Section 1.3 gives the full interface.

| ID | Function | Valid evidence | Guard message |
| --- | --- | --- | --- |
| T3-01 | register_model | Model hash recorded at version 1 | version not increasing |
| T3-02 | set_oracle | Writer changes to the requested address | zero address |
| T3-03 | set_score | Assigned tier resolves on lookup | invalid tier |
| T3-04 | set_scores_batch | Both fixture wallets resolve to their assigned tiers | invalid batch |
| T3-05 | get_tier | Unscored wallet resolves to B | zero address |
| T3-06 | deposit_collateral | Collateral balance increases by the deposit | invalid amount |
| T3-07 | withdraw_collateral | Remaining collateral equals the expected balance | unsafe withdrawal |
| T3-08 | borrow | Debt token transfers and initial tier is stored | insufficient collateral |
| T3-09 | repay | Full repayment clears debt and the stored tier | exceeds debt |
| T3-10 | liquidate | Debt falls and collateral seizure matches the bonus | healthy loan |
| T3-11 | set_price | Scaled collateral price updates | invalid price |

Table 15. T3 functional and guard cases.

### T4 · Contract safeguards and design review

#### T4-01 · Verify writer and model version guards

| Field | Specification |
| --- | --- |
| Objective | Check authorization and current version enforcement. |
| Preconditions | Register one model and identify designated writer in local fixtures. |
| Input data | Synthetic score records and the supported invalid inputs from the defensive suite. |
| Steps | Run the existing writer-role and current-version tests. Compare the exact guard messages. |
| Expected result | Oracle role and version checks reject invalid writes. |
| Pass criterion | Both checks pass with oracle only and version mismatch respectively. |
| Runs & environment | Ape and Anvil, one deterministic case per guard. |

#### T4-02 · Verify stale-score fallback

| Field | Specification |
| --- | --- |
| Objective | Check B borrowing terms for an expired score. |
| Preconditions | Create a scored synthetic wallet and use the Anvil clock. |
| Input data | A recorded tier A and a timestamp more than 30 days later. |
| Steps | Run the local freshness test. Check effective tier and collateral requirements. |
| Expected result | The expired score resolves to B. |
| Pass criterion | Effective tier is 2, and B borrowing terms are enforced. |
| Runs & environment | Ape and Anvil, one deterministic case. |

#### T4-03 · Verify liquidation guards

| Field | Specification |
| --- | --- |
| Objective | Check healthy-position rejection and enforcement of the 50% close factor. |
| Preconditions | Use local fixture positions with known debt and collateral. |
| Input data | A healthy position and a liquidation-eligible position. |
| Steps | Run the two existing liquidation assertions and compare their return messages. |
| Expected result | Each out-of-policy request fails its stated guard. |
| Pass criterion | Exact messages are healthy loan and exceeds close factor. |
| Runs & environment | Ape and Anvil, one deterministic case per guard. |

#### T4-04 · Verify amount bounds and borrowing invariant

| Field | Specification |
| --- | --- |
| Objective | Check that borrowing stays within the collateral and tier limits. |
| Preconditions | Use local fixtures and the documented tier policy. |
| Input data | Zero, maximum uint256, tier C and generated A/B collateral-to-debt cases. |
| Steps | Run amount and eligibility checks, then exercise the generated examples at and above the calculated borrowing boundary. |
| Expected result | Eligible within-limit values succeed and values above the limit revert. |
| Pass criterion | Match invalid amount, tier cannot borrow and insufficient collateral where applicable. Confirm all 200 generated cases satisfy the invariant. |
| Runs & environment | Ape, Anvil and Hypothesis, one deterministic case per boundary and 200 examples. |

#### T4-05 · Review Sybil exposure and default tier

| Field | Specification |
| --- | --- |
| Objective | Document how wallet-based identity limits the policy. |
| Preconditions | Review score lookup and use an unscored local fixture. |
| Input data | Contract design and an unscored wallet fixture. |
| Steps | Review the identity assumption and run the existing default-tier assertion. |
| Expected result | Sybil identity changes are not blocked. An unscored wallet gets B. |
| Pass criterion | Document the exposure and verify B eligibility and collateral terms in the fixture. |
| Runs & environment | One design review and one deterministic Anvil check. |

#### T4-06 · Review oracle key leak exposure

| Field | Specification |
| --- | --- |
| Objective | Assess the system's reliance on a trusted writer. |
| Preconditions | Review role definitions and the operator responsibility. |
| Input data | Writer authorization and key-rotation design. |
| Steps | Review authorized capabilities, rotation authority and audit events. |
| Expected result | Misuse of a compromised authorized writer key is not blocked by the contract. |
| Pass criterion | Record the trusted role, rotation control and the scope of the audit trail. |
| Runs & environment | One design review. |

#### T4-07 · Review owner price manipulation exposure

| Field | Specification |
| --- | --- |
| Objective | Assess the owner-set price trust assumption. |
| Preconditions | Review the local price-oracle design. |
| Input data | PriceOracle role definition and event specification. |
| Steps | Review who controls collateral price and how changes are logged. |
| Expected result | Owner price manipulation is not blocked by the local oracle design. |
| Pass criterion | Document the trust assumption and distinguish it from the owner-only access control. |
| Runs & environment | One design review. |

#### T4-08 · Review front-run exposure for tier downgrades

| Field | Specification |
| --- | --- |
| Objective | Assess dependence on transaction ordering. |
| Preconditions | Review score update and borrow semantics. |
| Input data | Contract design and public ordering model. |
| Steps | Review when a tier becomes effective and what the contract guarantees for accepted transactions. |
| Expected result | Front-run exposure is not blocked by the contract design. |
| Pass criterion | Document the ordering assumption and its implications for downgrade effectiveness. |
| Runs & environment | One design review. |

### T5 · Performance

#### T5-01 · Profile score-write gas

| Field | Specification |
| --- | --- |
| Objective | Check the H5 gas budget and scaling with batch size. |
| Preconditions | Deploy on fresh Anvil and register a synthetic model. |
| Input data | Fresh wallet addresses and known tiers for single writes and batches. |
| Steps | Capture receipt gas, normalize by wallet count and compare with EVM estimates. Report median and maximum and flag more than 2× the estimate. |
| Expected result | Expected per-wallet cost falls as fixed transaction overhead is shared. |
| Pass criterion | Single writes are within 100,000 gas and all 100-wallet batches are within 75,000 gas per wallet. |
| Runs & environment | Ape and Anvil, ten single writes and ten batches for each of 1, 10 and 100 wallets. Thirty batch receipts are measured in results/pilot_gas.json. |

#### T5-02 · Measure Sepolia confirmation latency

| Field | Specification |
| --- | --- |
| Objective | Estimate median and p95 from submissions to first successful confirmation. |
| Preconditions | Public testnet deployment, approved RPC access and funded test accounts. |
| Input data | Benign synthetic calls for each main function. |
| Steps | Log submission and receipt times, confirmation status and the sampling window. Report timeouts separately from confirmed latency. |
| Expected result | Expected median is 7–15 s and p95 is 24–36 s. |
| Pass criterion | Record at least 30 confirmations per function per window in at least two windows. Target 100 per function for p95 and compare observed quantiles with expected ranges. |
| Runs & environment | Sepolia via Alchemy, planned, not yet run. |

### T6 · End-to-end checks

#### T6-01 · Reconcile score export and model registration

| Field | Specification |
| --- | --- |
| Objective | Check traceability from frozen model to chain events. |
| Preconditions | Use a fresh local deployment and a validated wallet-tier export. |
| Input data | Model artifact SHA-256, assigned version and checked synthetic or comparison wallet rows. |
| Steps | Register the hash, publish batches and reconcile receipt events by wallet, tier and version. Read back recorded tiers. |
| Expected result | The registered digest and submitted rows agree with successful chain records. |
| Pass criterion | Exact digest and version match. The unique wallet count, expected rows and receipt rows reconcile. |
| Runs & environment | Python, Ape and Anvil, three full runs on fresh deployments, planned, not yet run. The fixed export depends on D1 feasibility. |

#### T6-02 · Show price drop and liquidation in the dashboard

| Field | Specification |
| --- | --- |
| Objective | Check that the dashboard matches the chain state transition. |
| Preconditions | Deploy a fresh local pool, fund test accounts and open a healthy loan. |
| Input data | Synthetic balances, initial and reduced collateral prices, and contract receipts. |
| Steps | Display the healthy position. Apply the local scenario price change. Observe the eligible position and reconcile the resulting liquidation receipt and balances in Streamlit. |
| Expected result | The displayed health and balance changes agree with contract state and events. |
| Pass criterion | Record the price update and expected debt and collateral changes. The dashboard and receipt must agree on all fields. |
| Runs & environment | Streamlit, Ape and Anvil, three fresh runs, planned, not yet run. |

### T7 · Robustness

#### T7-01 · Quarterly calibration

For each of five seeds, apply its validation-fitted probability map to test. By UTC quarter, report sample size, prevalence, mean calibrated score, Brier before and after calibration, and common-bin reliability curves. Apply the H7 directional criterion in Section 2.1. Report 2024Q3 with zero observations and undefined metrics. The seed-11 pilot is in results/pilot_calib.json.

#### T7-02 · Taiwan across seeds

Reuse the five frozen Taiwan fits from the model comparison. Report mean and sample standard deviation of test ROC AUC on the unchanged stratified split. Pass the reporting check if all five seed-level AUCs are present and the same test population is used. Apply the H6 criterion in Section 2.1.

#### T7-03 · D3b paired price shocks

For each shock of −10%, −20%, −30% and −40%, run both policies on the same simulated borrowers, with stable debt and collateral value adjusted by the shock. Use a simulated buffer set before evaluation. For planning, draw the margin above each policy's minimum collateral ratio uniformly from 0 to 0.20 ratio units. Use a reproducible PRNG initialized with seed 11 and share each draw across policies. Keep the 50% close factor and 5% bonus. Apply the maintenance ratio to identify liquidation eligibility. Record the liquidation count, collateral seized in USD and residual unsecured debt after the simulated close.

Run at least 1,000 Monte Carlo replicates per shock. Compute a 95% interval on the paired policy difference. Use a prespecified effect size for the precision decision and increase the number of replicates if the interval width remains larger than that effect. Record the distribution, seed, number of draws and whether the precision target was met. Fixed D1 tiers require feasible validation cutoffs. The simulation is planned, not yet run.
