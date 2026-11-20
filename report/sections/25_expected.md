### 2.5. Expected results and reasoning

#### H1 · Non-inferiority

- **Expected** Paired XGBoost ΔAUC has a lower 95% confidence bound above −0.02.
- **Basis** Across seeds 11, 22 and 33, proposed minus all-feature no-PCA test AUC was -0.00583 (paired 95% t interval -0.04285 to 0.03118). Mean validation minus test AUC was 0.00807 proposed and 0.02567 baseline. The gap narrowed, but the interval crosses the −0.02 non-inferiority margin.
- **Reject if** The lower paired bound is at or below −0.02.
- **If rejected** Report the result and complete the planned matched runs and report the validation-to-test gap. Keep baseline reproduction status visible.

#### H2 · Calibration

- **Expected** Calibrated test Brier is smaller than raw Brier.
- **Basis** Seed 11 test Brier was 0.06409 raw, 0.01636 isotonic and 0.01549 Platt. Class weighting emphasizes positives during training, which pushes raw probabilities upward relative to the observed event prevalence and inflates raw Brier. Both maps used validation. Keep the prespecified isotonic map for the tier policy and retain Platt as a comparator. Switching on the lower test Brier would select the map on test.
- **Reject if** The upper bound of the paired 95% interval for calibrated minus raw Brier is zero or positive.
- **If rejected** Report raw, isotonic and Platt results by quarter and examine validation-to-test prevalence shift.

#### H3 · Tier separation

- **Expected** Rates increase from A to C with disjoint adjacent 95% Wilson intervals. C share falls when risk falls.
- **Basis** Cutoffs were 0.005 and 0.065. Fixed test rates were 0.02%, 0.72%, 4.23% for A, B and C, with disjoint overall Wilson intervals.
- **Reject if** With a feasible fixed rule, any adjacent ordering or interval condition fails, or the quarterly C share does not consistently fall with prevalence. Treat infeasible thresholds as an unevaluable hypothesis.
- **If rejected** Report the observed tiers or infeasibility and retain the comparator as labelled evidence. Any future threshold revision requires approval and validation-only selection.

#### H4 · Policy

- **Expected** Tiering avoids more historically liquidating loans, lowers tier-A collateral per dollar of debt, and holds total collateral and simulated bad debt at or below uniform.
- **Basis** Uniform accepted 96,345 and tiering accepted 79,296. Tiering avoided 722 labelled liquidations and rejected 16,327 good loans. Uniform had zero for both. Locked collateral was USD 44.22 billion uniform and USD 49.28 billion tiered.
- **Reject if** Reject if tiering fails to avoid more labelled liquidations or to lower tier-A collateral per debt dollar, raises total locked collateral, or raises bad debt at any specified shock.
- **If rejected** Report the acceptance and good-loan rejection trade-off and the shock results separately. The pilot fails the total collateral and −20% bad debt conditions.

The simulated pilot draws one shared borrower buffer per loan from Uniform(0, 0.20), seed 11, and adds it to each policy's initial collateral ratio. Debt stays fixed. It evaluates accepted loans with valid USD amounts (95,596 uniform and 78,703 tiered), applies one liquidation call below the maintenance ratio, and uses the 50% close factor and 5% bonus. Bad debt is the positive gap between remaining debt and remaining marked collateral after the call. The same buffer draw is used for every shock. Both rates use the priced accepted cohort. Its debt totals USD 35.37 billion uniform and USD 34.75 billion tiered.

| Shock | Policy | Liquidated loans | Seized collateral (USD m) | Bad debt (USD m) | Liquidated / accepted loans | Bad debt / accepted debt |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| -10% | Uniform | 46,237 | 9,015.35 | 0.00 | 48.37% | 0.000% |
| -10% | Tiered | 475 | 510.94 | 0.00 | 0.60% | 0.000% |
| -20% | Uniform | 95,596 | 18,571.60 | 64.56 | 100.00% | 0.183% |
| -20% | Tiered | 50,195 | 12,662.78 | 121.47 | 63.78% | 0.350% |
| -30% | Uniform | 95,596 | 18,571.60 | 2,833.23 | 100.00% | 8.009% |
| -30% | Tiered | 78,703 | 18,244.27 | 1,085.32 | 100.00% | 3.123% |
| -40% | Uniform | 95,596 | 18,571.60 | 7,608.31 | 100.00% | 21.508% |
| -40% | Tiered | 78,703 | 18,244.27 | 3,967.75 | 100.00% | 11.418% |

Table 21. Paired simulated shocks on the priced subset of test loans. See `results/pilot_policy_v2.json`.

Tiering reduced the share liquidated at −10% and −20%, but at −30% and −40% all priced accepted loans liquidated under both policies. At −20%, bad debt rose from USD 64.56 m under uniform to USD 121.47 m tiered, or from 0.183% to 0.350% of accepted debt. Tiering lowered the bad-debt share at −30% and −40%, but increased total locked collateral and still fails H4.

#### H5 · Gas and guards

- **Expected** Single updates use ≤100,000 gas and 100-wallet batches use ≤75,000 gas per wallet. Designed guards return their exact messages.
- **Basis** Estimate versus Anvil pilot was 93,000 versus 94,739 gas for a single write and 69,034 versus median 69,252 gas per wallet at size 100. Sepolia is planned with approximately 12 s blocks, expected median 7–15 s and expected p95 24–36 s. Anvil gas does not measure Sepolia latency.
- **Reject if** A guard check fails or any measured receipt exceeds its H5 bound. Assess Sepolia latency against its expected range separately.
- **If rejected** Inspect the storage and receipt breakdown or the failing guard. If gas exceeds twice the estimate, investigate the storage and calldata assumptions. Report testnet timeouts and window differences.

#### H6 · Taiwan transfer

- **Expected** ROC AUC is in the 0.7828–0.7847 planning range.
- **Basis** Seeds 11, 22 and 33 averaged 0.78376 AUC with sample SD 0.00048; the planning range is mean ± two seed SDs on the same test split. The higher AUC than [3] may reflect the class-weighted XGBoost model and local evaluation split versus the paper's random-forest AutoML protocol.
- **Reject if** The full estimate falls outside the expected range on the frozen evaluation protocol.
- **If rejected** Audit the split, feature exclusions and training variance. Document differences from the paper protocol.

#### H7 · Quarterly drift

- **Expected** The later populated quarter has lower prevalence and a positive calibration gap greater than the earlier quarter.
- **Basis** Reject H7 in the seed-11 pilot because from 2022Q3 to 2024Q2 prevalence rose from 1.48% to 3.69% and the positive calibration gap shrank from 2.51 to 0.78 percentage points.
- **Reject if** The directional conditions in Section 2.1 are unmet across the first and last populated quarters.
- **If rejected** Report the quarterly trajectory and bin counts. Assess score mix and base-rate shifts before proposing a prospective calibration update.
