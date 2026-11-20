### 2.3. Test scenario details

#### T1 · Model comparisons

##### T1-01 · Reproduce baseline AUC

**Objective** Reproduce paper AUC. **Preconditions** Frozen D5 folds. **Input data** FinSurvival labels and features.

**Steps** Fit scaling and PCA (95%) on train_core. Fit LR and XGB. Early-stop XGB on inner-val AUC. **Expected result** Paper targets 0.723 LR and 0.732 XGB [1].

**Pass criterion** Each test AUC within ±0.02 of its target. **Runs & environment** Python. Five XGB seeds. One LR fit and 1,000 stratified bootstrap draws.


##### T1-02 · Test model non-inferiority

**Objective** Test H1. **Preconditions** Matched D5 folds and seeds. **Input data** All-feature and drift-filtered XGBoost inputs without PCA. **Steps** Fit both variants on matched seeds. Subtract B_XGB_noPCA test AUC from proposed test AUC and compute the paired 95% t interval. **Expected result** Proposed model within margin. **Pass criterion** Lower endpoint > −0.02. Report both validation-to-test gaps. **Runs & environment** Python. Five paired seeds. **Evidence** Pilot model and audit JSON.

##### T1-03 · Compare raw and isotonic scores

**Objective** Test H2. **Preconditions** Frozen XGB fits. **Input data** Validation and test scores and labels. **Steps** Fit isotonic on calibration validation. Compute the calibrated-minus-raw Brier difference on identical test rows. **Expected result** Negative calibrated-minus-raw Brier. **Pass criterion** Upper paired 95% bound < 0. **Runs & environment** Python. Five paired seeds. Seed 11 measured. **Evidence** Pilot calibration JSON.

##### T1-04 · Compare fixed and percentile tiers

**Objective** Test H3. **Preconditions** Frozen scores and ordered D1 cutoffs. **Input data** Scores, outcomes, quarters and wallet IDs. **Steps** Fit ordered cutoffs on the validation grid and compute validation p70/p90. Freeze both rules. Compute overall and quarterly test shares, rates and Wilson intervals. **Expected result** Fixed rates rise A to C. C share tracks prevalence. **Pass criterion** Apply H3. Leave fixed outputs missing for unordered cutoffs. **Runs & environment** Python. Five seeds per rule. The seed-11 pilot measured both rules. **Evidence** Pilot tiers JSON.

##### T1-05 · Compare lending policies using realized labels

**Objective** Evaluate D3a. **Preconditions** Frozen scores and feasible D1 cutoffs. **Input data** Origination scores, labels and valid loan USD. **Steps** Apply tiered 120%/150% and reject C. Apply uniform 125%. Tabulate acceptance, avoided liquidations, rejected good loans and collateral. **Expected result** Tier A needs less collateral. Tiering avoids more liquidations without increasing total collateral. **Pass criterion** Apply H4. Report acceptance, avoided liquidations, good loans rejected and locked collateral for both policies. **Runs & environment** Python. Five paired seeds. The seed-11 fixed-policy pilot is measured. **Evidence** Pilot policy v2 JSON.

##### T1-06 · Evaluate Taiwan test AUC

**Objective** Test H6. **Preconditions** Frozen 60/10/30 split. **Input data** Taiwan UCI 350, excluding SEX and MARRIAGE. **Steps** Exclude sex and marital status, including coded duplicates. Early-stop XGBoost on the stratified inner training fold. Score test and summarize AUC across seeds. **Expected result** AUC 0.7828–0.7847. **Pass criterion** Compare with the expected range and [3]. **Runs & environment** Python. Five seeds planned. Three measured. **Evidence** Pilot Taiwan JSON.

#### T2 · Ablations

##### T2-01 · Drift removal ablation

**Objective** Isolate KS filtering. **Preconditions** Fix PCA and learner. **Input data** D5 folds and inner KS statistics. **Steps** Fit matched XGBoost runs without PCA, with and without the D ≥ 0.15 drop list. Compare held-out AUC. **Expected result** Discrimination remains within margin. **Pass criterion** Report paired AUC interval against H1 margin. **Runs & environment** Python. Five seeds per setting. **Evidence** Planned five-seed comparison.

##### T2-02 · PCA ablation

**Objective** Isolate PCA. **Preconditions** Same feature set. **Input data** D5 folds. **Steps** Enable or disable 95%-variance PCA fitted on train_core. Early-stop both fits on inner-val. **Expected result** Matched AUC isolates the effect of the PCA pipeline. **Pass criterion** Verify matched settings and report paired 95% interval. **Runs & environment** Python. Five seeds per setting. **Evidence** Pilot audit JSON.

##### T2-03 · Calibration ablation

**Objective** Compare calibration maps. **Preconditions** Freeze raw model. **Input data** Validation and test scores and outcomes. **Steps** Fit both maps on calibration validation. Evaluate raw, isotonic and Platt probabilities on the same frozen test rows. **Expected result** Lower Brier indicates improvement. **Pass criterion** Report paired Brier, intervals and reliability. Apply H2 to isotonic. **Runs & environment** Python. Five seeds per setting. **Evidence** Pilot calibration JSON covers all three settings.

##### T2-04 · KS threshold sensitivity

**Objective** Vary KS threshold. **Preconditions** Prespecify cutoffs. **Input data** Train_core and inner-val distributions. **Steps** Derive each drop list on training and inner validation. Compare D = 0.10, 0.15, 0.20 and 0.30 with matched XGBoost settings. **Expected result** Feature counts change. **Pass criterion** Report drops, paired AUC and gaps. Keep 0.15 primary. **Runs & environment** Python. Five seeds per cutoff. **Evidence** Planned cutoff sweep.

##### T2-05 · Tier rule sensitivity

**Objective** Isolate tier rule. **Preconditions** Freeze both rules on validation. **Input data** Same calibrated test scores. **Steps** Compare fixed and percentile tier shares, Wilson intervals and D3a outputs. **Expected result** Rules can give different allocations. **Pass criterion** Report paired coverage and explicit D1 infeasibility. **Runs & environment** Python. Five seeds per rule. **Evidence** Pilot tiers JSON.

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

**Objective** Verify stale fallback. **Preconditions** Scored local fixture. **Input data** Tier A more than 30 days old. **Steps** Advance the local clock past the freshness limit. Read the tier and check the resulting borrow terms. **Expected result** Stale score resolves to B. **Pass criterion** Tier = 2 and B collateral terms apply. **Runs & environment** Ape/Anvil. One case. **Evidence** Local safeguard test.

##### T4-03 · Verify liquidation guards

**Objective** Check liquidation guards. **Preconditions** Known local positions. **Input data** Healthy and eligible fixtures. **Steps** Check guard behavior for a healthy position and a request above the close factor. **Expected result** Out-of-policy requests revert. **Pass criterion** Match healthy loan and exceeds close factor. **Runs & environment** Ape/Anvil. One case per guard. **Evidence** Local safeguard tests.

##### T4-04 · Verify amount bounds and borrowing invariant

**Objective** Check borrowing invariant. **Preconditions** Local tier policy fixtures. **Input data** Zero, max uint256, C and generated A/B cases. **Steps** Assert invalid amount and tier guards. For generated A/B cases compare proposed borrowing with the policy limit. **Expected result** Only eligible within-limit values pass. **Pass criterion** Match exact guards and confirm all generated cases. **Runs & environment** Ape/Anvil/Hypothesis. One per boundary and 200 generated cases. **Evidence** Local safeguard tests.

##### T4-05 · Review Sybil exposure and default tier

**Objective** Assess fresh-wallet Sybil exposure. **Preconditions** Wallet-keyed tiers. **Input data** Unscored wallet fixture. **Steps** Review identity assumptions and verify the B fallback. **Expected result** A Sybil new wallet is not blocked by the design. A borrower can regain B terms under a new identity. **Pass criterion** Record exposure and verify default B. Consider verified identity or conservative admission controls. **Runs & environment** One design review and one Anvil check. **Evidence** Local fallback test.

##### T4-06 · Review oracle key leak exposure

**Objective** Assess oracle key compromise. **Preconditions** Registered model and writer role. **Input data** Writer permissions and score event schema. **Steps** Review authorization, monitoring and rotation controls. **Expected result** A compromised authorized oracle is not blocked by the design. It can publish false tiers and change borrowing eligibility. **Pass criterion** Record exposure. Monitor score events and rotate or revoke the writer promptly. **Runs & environment** One design review. **Evidence** Role and event specification.

##### T4-07 · Review owner price manipulation exposure

**Objective** Assess owner price manipulation. **Preconditions** Owner-controlled price oracle. **Input data** Price authority and event schema. **Steps** Review the maintenance checks and oracle trust boundary. **Expected result** Owner price manipulation is not blocked by the design. A false price can trigger wrongful liquidations or hide unsafe debt. **Pass criterion** Record exposure. Use an independent price feed, multisig administration and deviation alerts. **Runs & environment** One design review. **Evidence** Price role specification.

##### T4-08 · Review front-run exposure for tier downgrades

**Objective** Assess front-running a tier downgrade. **Preconditions** Scores apply when confirmed and tiers are stored at borrow. **Input data** Score and loan state specifications. **Steps** Review ordering assumptions and existing-loan terms. **Expected result** Front-running a downgrade is not blocked by the design. A loan can retain earlier, less restrictive terms. **Pass criterion** Record exposure. Consider private submission and fail-closed borrowing during authorized refresh windows. **Runs & environment** One design review. **Evidence** Borrow and score specifications.

#### T5 · Performance

##### T5-01 · Profile score-write gas

**Objective** Check H5 gas. **Preconditions** Fresh local deployment. **Input data** Synthetic single and batch inputs.

**Steps** Capture gas receipts, normalize by wallet count and compare EVM estimates. **Expected result** Per-wallet cost falls with batch size.

**Pass criterion** ≤100,000 gas for singles and ≤75,000 per wallet for size 100. Flag >2× estimate. **Runs & environment** Ape/Anvil. Ten singles and ten per batch size 1, 10, 100. Thirty batches measured.


##### T5-02 · Measure Sepolia confirmation latency

**Objective** Measure median and p95 confirmations. **Preconditions** Funded testnet account and approved RPC. **Input data** Synthetic main-function calls. **Steps** Log submission and receipt timestamps. Report median and p95 by function and window. Count timeouts separately. **Expected result** Expected median 7–15 s and p95 24–36 s. **Pass criterion** ≥30 confirmations per function per window. Target 100 overall per function. **Runs & environment** Sepolia via Alchemy. At least two windows, planned, not yet run. **Evidence** Planned funded Sepolia run.

#### T6 · End-to-end checks

##### T6-01 · Reconcile score export and model registration

**Objective** Reconcile export and chain. **Preconditions** Fresh local deployment. **Input data** Model SHA-256, version and wallet tiers. **Steps** Register the hash, publish scores, reconcile unique wallets and versions in receipts, and read back tiers. **Expected result** Chain records match inputs. **Pass criterion** Exact hash, version and unique counts match. **Runs & environment** Python/Ape/Anvil. Three fresh runs, planned, not yet run. Fixed tiers depend on D1. **Evidence** Planned integration run.

##### T6-02 · Show price drop and liquidation in the dashboard

**Objective** Verify dashboard liquidation. **Preconditions** Fresh local pool and healthy loan. **Input data** Synthetic price and loan receipts. **Steps** Display initial health, apply a local price drop, and reconcile the liquidation receipt with the updated dashboard balances. **Expected result** Dashboard reflects chain transitions. **Pass criterion** Price, debt and collateral agree with receipts. **Runs & environment** Streamlit/Ape/Anvil. Three fresh runs, planned, not yet run. **Evidence** Planned dashboard run.

#### T7 · Robustness

| ID | Unit | Runs & environment | Metric |
| --- | --- | --- | --- |
| T7-01 | Test quarter within a model seed | Five seeds, Python. Seed 11 measured. | Count, prevalence, mean score, raw and calibrated Brier, and reliability. Apply H7. Report empty 2024Q3. |
| T7-02 | Taiwan model seed | Reuse five T1-06 fits, Python. | Mean and sample SD of test ROC AUC on the same population. |
| T7-03 | Paired draw at each shock | Python. One simulated pilot draw per shock. At least 1,000 planned. | At −10%, −20%, −30% and −40%, report liquidation count, seized USD and bad debt using common borrower buffers. |
