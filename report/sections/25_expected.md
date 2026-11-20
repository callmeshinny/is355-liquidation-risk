### 2.5. Expected results and reasoning

#### H1 · Non-inferiority

- **Expected** Paired XGBoost ΔAUC has a lower 95% confidence bound above −0.02.
- **Basis** Across seeds 11, 22 and 33, proposed minus all-feature no-PCA test AUC was -0.00583 (paired 95% t interval -0.04285 to 0.03118). Mean validation minus test AUC was 0.00807 proposed and 0.02567 baseline. The gap narrowed, but the interval crosses the −0.02 non-inferiority margin.
- **Reject if** The lower paired bound is at or below −0.02.
- **If rejected** Report the result and complete the planned matched runs and report the validation-to-test gap. Keep baseline reproduction status visible.

#### H2 · Calibration

- **Expected** Calibrated test Brier is smaller than raw Brier.
- **Basis** Seed 11 test Brier was 0.06409 raw, 0.01636 isotonic and 0.01549 Platt. Class weighting emphasizes positives during training, which pushes raw probabilities upward relative to the observed event prevalence and inflates raw Brier. Both maps were fitted on validation.
- **Reject if** The upper bound of the paired 95% interval for calibrated minus raw Brier is zero or positive.
- **If rejected** Report raw, isotonic and Platt results by quarter and examine validation-to-test prevalence shift.

#### H3 · Tier separation

- **Expected** Rates increase from A to C with disjoint adjacent 95% Wilson intervals. C share falls when risk falls.
- **Basis** The ordered validation grid yields 0.005 and 0.015. Fixed test rates are 0.02%, 0.48% and 2.88%, with disjoint overall 95% Wilson intervals. The quarterly C share does not consistently fall with prevalence. From 2023Q3 to 2023Q4, prevalence fell from 1.10% to 0.43% while fixed C share rose from 34.26% to 39.15%. Step 5 reports all quarters, including the empty 2024Q3 cohort.
- **Reject if** With a feasible fixed rule, any adjacent ordering or interval condition fails, or the quarterly C share does not consistently fall with prevalence. Treat infeasible thresholds as an unevaluable hypothesis.
- **If rejected** Report the observed tiers or infeasibility and retain the comparator as labelled evidence. Any future threshold revision requires approval and validation-only selection.

#### H4 · Policy

- **Expected** Tiering avoids more historically liquidating loans, lowers tier-A collateral per dollar of debt, and holds total collateral and simulated bad debt at or below uniform.
- **Basis** Uniform accepted 96,345 and tiering accepted 62,092. Tiering avoided 986 historically labelled liquidations and rejected 33,267 good loans. Uniform had zero for both. Collateral locked was USD 44.22 billion uniform and USD 47.13 billion tiered. At −20%, simulated bad debt was USD 64.56 million uniform and USD 121.47 million tiered.
- **Reject if** Reject if tiering fails to avoid more labelled liquidations or to lower tier-A collateral per debt dollar, raises total locked collateral, or raises bad debt at any specified shock.
- **If rejected** Report the acceptance and good-loan rejection trade-off and the shock results separately. The pilot fails the total collateral and −20% bad debt conditions.

The simulated pilot draws one shared borrower buffer per loan from Uniform(0, 0.20), seed 11, and adds it to each policy's initial collateral ratio. Debt stays fixed. It evaluates accepted loans with valid USD amounts (95,596 uniform and 61,695 tiered), applies one liquidation call below the maintenance ratio, and uses the 50% close factor and 5% bonus. Bad debt is the positive gap between remaining debt and remaining marked collateral after the call. The same buffer draw is used for every shock.

| Shock | Policy | Liquidated loans | Seized collateral (USD m) | Bad debt (USD m) |
| --- | --- | ---: | ---: | ---: |
| -10% | Uniform | 46,237 | 9,015.35 | 0.00 |
| -10% | Tiered | 475 | 510.94 | 0.00 |
| -20% | Uniform | 95,596 | 18,571.60 | 64.56 |
| -20% | Tiered | 39,660 | 12,203.87 | 121.47 |
| -30% | Uniform | 95,596 | 18,571.60 | 2,833.23 |
| -30% | Tiered | 61,695 | 17,490.52 | 1,085.32 |
| -40% | Uniform | 95,596 | 18,571.60 | 7,608.31 |
| -40% | Tiered | 61,695 | 17,490.52 | 3,877.05 |

Table 21. Paired simulated shocks on the priced subset of test loans. See `results/pilot_policy_v2.json`.

#### H5 · Gas and guards

- **Expected** Single updates use ≤100,000 gas and 100-wallet batches use ≤75,000 gas per wallet. Designed guards return their exact messages.
- **Basis** Estimate versus Anvil pilot was 93,000 versus 94,739 gas for a single write and 69,034 versus median 69,252 gas per wallet at size 100. Sepolia is planned with approximately 12 s blocks, expected median 7–15 s and expected p95 24–36 s. Anvil gas does not measure Sepolia latency.
- **Reject if** A guard check fails or any measured receipt exceeds its H5 bound. Assess Sepolia latency against its expected range separately.
- **If rejected** Inspect the storage and receipt breakdown or the failing guard. If gas exceeds twice the estimate, investigate the storage and calldata assumptions. Report testnet timeouts and window differences.

#### H6 · Taiwan transfer

- **Expected** ROC AUC is in the 0.760–0.810 planning range.
- **Basis** The seed-11 pilot measured 0.7834 on the local stratified Taiwan split with sex and marital status excluded, class-weighted XGBoost and early stopping within training. These choices can change the fitted ranking and evaluated cases relative to the random-forest AutoML pipeline reported in [3]. A matched replication would be needed to attribute the gap.
- **Reject if** The full estimate falls outside the expected range on the frozen evaluation protocol.
- **If rejected** Audit the split, feature exclusions and training variance. Document differences from the paper protocol.

#### H7 · Quarterly drift

- **Expected** The later populated quarter has lower prevalence and a positive calibration gap greater than the earlier quarter.
- **Basis** The validation map remains fixed as test prevalence can change. Brier and reliability by quarter will show where the discrepancy occurs. The final planned quarter, 2024Q3, is empty in this snapshot.
- **Reject if** The directional conditions in Section 2.1 are unmet across the first and last populated quarters.
- **If rejected** Report the quarterly trajectory and bin counts. Assess score mix and base-rate shifts before proposing a prospective calibration update.
