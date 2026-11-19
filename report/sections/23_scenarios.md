### 2.3. Test scenario details

#### T1 · Model comparisons

##### T1-01 · Reproduce baseline AUC

**Objective** Reproduce paper AUC. **Preconditions** Frozen D5 folds. **Input data** FinSurvival labels and features.

**Steps** Fit scaling and PCA (95%) on train_core. Fit LR and XGB. Early-stop XGB on inner-val AUC. **Expected result** Paper targets 0.723 LR and 0.732 XGB [1].

**Pass criterion** Each test AUC within ±0.02 of its target. **Runs & environment** Python. Five XGB seeds. One LR fit and 1,000 stratified bootstrap draws.


##### T1-02 · Test model non-inferiority

**Objective** Test H1. **Preconditions** Matched D5 folds and seeds. **Input data** Baseline and proposed XGB features.

**Steps** Fit both variants and calculate paired test ΔAUC and its 95% t interval. **Expected result** Proposed model within margin.

**Pass criterion** Lower endpoint > −0.02. Report both validation-to-test gaps. **Runs & environment** Python. Five paired seeds.


##### T1-03 · Compare raw and isotonic scores

**Objective** Test H2. **Preconditions** Frozen XGB fits. **Input data** Validation and test scores and labels.

**Steps** Fit isotonic on validation. Compute raw and mapped Brier on identical test rows. **Expected result** Negative calibrated-minus-raw Brier.

**Pass criterion** Upper paired 95% bound < 0. **Runs & environment** Python. Five paired seeds. Seed 11 measured.


##### T1-04 · Compare fixed and percentile tiers

**Objective** Test H3. **Preconditions** Frozen scores and ordered D1 cutoffs. **Input data** Scores, outcomes, quarters and wallet IDs.

**Steps** Calculate D1 extrema and 70th/90th percentiles on validation. Freeze rules. Tabulate test shares and Wilson intervals. **Expected result** Fixed rates rise A to C. C share tracks prevalence.

**Pass criterion** Apply H3. Leave fixed outputs missing for unordered cutoffs. **Runs & environment** Python. Five seeds per rule. Fixed pilot planned, not yet run.


##### T1-05 · Compare lending policies using realized labels

**Objective** Evaluate D3a. **Preconditions** Frozen scores and feasible D1 cutoffs. **Input data** Origination scores, labels and valid loan USD.

**Steps** Apply tiered 120%/150% and reject C. Apply uniform 125%. Tabulate acceptance, avoided liquidations, rejected good loans and collateral. **Expected result** Tier A requires less collateral per USD.

**Pass criterion** Apply H4. Report counts and capital for undefined ratios. **Runs & environment** Python. Five paired seeds. Percentile sensitivity measured. Fixed policy planned, not yet run.


##### T1-06 · Evaluate Taiwan test AUC

**Objective** Test H6. **Preconditions** Frozen 60/10/30 split. **Input data** Taiwan UCI 350, excluding SEX and MARRIAGE.

**Steps** Early-stop XGB on stratified inner training fold. Score test and summarize AUC across seeds. **Expected result** AUC 0.760–0.810.

**Pass criterion** Compare with the expected range and [3]. **Runs & environment** Python. Five seeds. Seed 11 measured.


#### T2 · Ablations

##### T2-01 · Drift removal ablation

**Objective** Isolate KS filtering. **Preconditions** Fix PCA and learner. **Input data** D5 folds and inner KS statistics.

**Steps** Pair XGB runs with the D ≥ 0.15 drop list enabled or disabled. **Expected result** Discrimination remains within margin.

**Pass criterion** Report paired AUC interval against H1 margin. **Runs & environment** Python. Five seeds per setting.


##### T2-02 · PCA ablation

**Objective** Isolate PCA. **Preconditions** Same feature set. **Input data** D5 folds.

**Steps** Enable or disable 95%-variance PCA fitted on train_core. Early-stop both fits on inner-val. **Expected result** AUC difference is directly comparable.

**Pass criterion** Verify matched settings and report paired 95% interval. **Runs & environment** Python. Five seeds per setting.


##### T2-03 · Calibration ablation

**Objective** Compare calibration maps. **Preconditions** Freeze raw model. **Input data** Validation and test scores and outcomes.

**Steps** Fit isotonic and Platt on validation. Compare both mappings and raw scores on test. **Expected result** Lower Brier indicates improvement.

**Pass criterion** Report paired Brier, intervals and reliability. Apply H2 to isotonic. **Runs & environment** Python. Five seeds per setting.


##### T2-04 · KS threshold sensitivity

**Objective** Vary KS threshold. **Preconditions** Prespecify cutoffs. **Input data** Train_core and inner-val distributions.

**Steps** Compare D = 0.10, 0.15, 0.20 and 0.30 with the same XGB settings. **Expected result** Feature counts change.

**Pass criterion** Report drops, paired AUC and gaps. Keep 0.15 primary. **Runs & environment** Python. Five seeds per cutoff.


##### T2-05 · Tier rule sensitivity

**Objective** Isolate tier rule. **Preconditions** Fit cutoffs on validation. **Input data** Same calibrated test scores.

**Steps** Compare fixed and percentile tier shares, Wilson intervals and D3a outputs. **Expected result** Rules can give different allocations.

**Pass criterion** Report paired coverage and explicit D1 infeasibility. **Runs & environment** Python. Five seeds per rule.


#### T3 · Contract functions

Run each valid case and guard once on a fresh Ape/Anvil fixture. Assert the state, return value and precise guard message.

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

Table 17. T3 functional and guard cases.

#### T4 · Contract safeguards and design review

##### T4-01 · Verify writer and model version guards

**Objective** Verify writer and version guards. **Preconditions** Local registered model. **Input data** Synthetic score fixtures.

**Steps** Run defensive role and version tests. **Expected result** Invalid writes revert.

**Pass criterion** Match oracle only and version mismatch. **Runs & environment** Ape/Anvil. One case per guard.


##### T4-02 · Verify stale-score fallback

**Objective** Verify stale fallback. **Preconditions** Scored local fixture. **Input data** Tier A more than 30 days old.

**Steps** Run freshness and borrowing-term assertions. **Expected result** Stale score resolves to B.

**Pass criterion** Tier = 2 and B collateral terms apply. **Runs & environment** Ape/Anvil. One case.


##### T4-03 · Verify liquidation guards

**Objective** Check liquidation guards. **Preconditions** Known local positions. **Input data** Healthy and eligible fixtures.

**Steps** Run defensive health and close-factor tests. **Expected result** Out-of-policy requests revert.

**Pass criterion** Match healthy loan and exceeds close factor. **Runs & environment** Ape/Anvil. One case per guard.


##### T4-04 · Verify amount bounds and borrowing invariant

**Objective** Check borrowing invariant. **Preconditions** Local tier policy fixtures. **Input data** Zero, max uint256, C and generated A/B cases.

**Steps** Run bounds checks and compare calls at and above collateral limits. **Expected result** Only eligible within-limit values pass.

**Pass criterion** Match exact guards and confirm all generated cases. **Runs & environment** Ape/Anvil/Hypothesis. One per boundary and 200 generated cases.


##### T4-05 · Review Sybil exposure and default tier

**Objective** Review Sybil exposure. **Preconditions** Review wallet-based tiers. **Input data** Contract design and unscored fixture.

**Steps** Review identity assumptions and verify default-tier behavior. **Expected result** Sybil identity changes are not blocked.

**Pass criterion** Document exposure and verify B terms. **Runs & environment** One review and one Anvil check.


##### T4-06 · Review oracle key leak exposure

**Objective** Review oracle key leak. **Preconditions** Review trusted roles. **Input data** Writer authority and rotation design.

**Steps** Review permissions and audit events. **Expected result** A compromised authorized writer is not blocked.

**Pass criterion** Record authority, rotation and audit coverage. **Runs & environment** One design review.


##### T4-07 · Review owner price manipulation exposure

**Objective** Review owner price manipulation. **Preconditions** Review local oracle trust. **Input data** PriceOracle roles and events.

**Steps** Review ownership and logging. **Expected result** Owner price manipulation is not blocked.

**Pass criterion** Record role limits and audit coverage. **Runs & environment** One design review.


##### T4-08 · Review front-run exposure for tier downgrades

**Objective** Review front-run exposure. **Preconditions** Review tier-update timing. **Input data** Borrow and score semantics.

**Steps** Review when updated tiers become effective. **Expected result** Front-run exposure is not blocked.

**Pass criterion** Record the ordering assumption and downgrade limitation. **Runs & environment** One design review.


#### T5 · Performance

##### T5-01 · Profile score-write gas

**Objective** Check H5 gas. **Preconditions** Fresh local deployment. **Input data** Synthetic single and batch inputs.

**Steps** Capture gas receipts, normalize by wallet count and compare EVM estimates. **Expected result** Per-wallet cost falls with batch size.

**Pass criterion** ≤100,000 gas for singles and ≤75,000 per wallet for size 100. Flag >2× estimate. **Runs & environment** Ape/Anvil. Ten singles and ten per batch size 1, 10, 100. Thirty batches measured.


##### T5-02 · Measure Sepolia confirmation latency

**Objective** Measure median and p95 confirmations. **Preconditions** Funded testnet account and approved RPC. **Input data** Synthetic main-function calls.

**Steps** Measure submission-to-receipt latency and record timeouts separately. **Expected result** Expected median 7–15 s and p95 24–36 s.

**Pass criterion** ≥30 confirmations per function per window. Target 100 overall per function. **Runs & environment** Sepolia via Alchemy. At least two windows, planned, not yet run.


#### T6 · End-to-end checks

##### T6-01 · Reconcile score export and model registration

**Objective** Reconcile export and chain. **Preconditions** Fresh local deployment. **Input data** Model SHA-256, version and wallet tiers.

**Steps** Register, publish and compare receipt wallet, tier and version. Read back tiers. **Expected result** Chain records match inputs.

**Pass criterion** Exact hash, version and unique counts match. **Runs & environment** Python/Ape/Anvil. Three fresh runs, planned, not yet run. Fixed tiers depend on D1.


##### T6-02 · Show price drop and liquidation in the dashboard

**Objective** Verify dashboard liquidation. **Preconditions** Fresh local pool and healthy loan. **Input data** Synthetic price and loan receipts.

**Steps** Display initial health. Change the local price and reconcile liquidation and balances. **Expected result** Dashboard reflects chain transitions.

**Pass criterion** Price, debt and collateral agree with receipts. **Runs & environment** Streamlit/Ape/Anvil. Three fresh runs, planned, not yet run.


#### T7 · Robustness

##### T7-01 · Quarterly calibration

For five seeds, apply validation-fitted calibration to test. Report quarterly counts, prevalence, mean score, raw and calibrated Brier, and common-bin reliability. Use H7 in Section 2.1. Report 2024Q3 as empty. See results/pilot_calib.json for seed 11.

##### T7-02 · Taiwan across seeds

Reuse the five Taiwan fits. Report mean and sample SD of held-out ROC AUC. Verify the same test population and apply H6.

##### T7-03 · D3b paired price shocks

For shocks −10%, −20%, −30% and −40%, compare both policies on paired simulated borrowers with stable debt. Draw the collateral buffer uniformly from 0 to 0.20 above each policy minimum using seed 11 and common draws. Apply maintenance ratios, 50% close factor and 5% bonus. Track liquidation counts, seized USD and residual unsecured debt.

Run at least 1,000 paired draws per shock. Extend until the 95% CI width is narrower than the prespecified effect size. Record distribution, seed, draws and precision. Fixed D1 tiers require feasible cutoffs. Simulation is planned, not yet run.
