### 2.5. Expected results and reasoning

#### H1 · Non-inferiority

- **Expected** Paired XGBoost ΔAUC has a lower 95% confidence bound above −0.02.
- **Basis** D5 mean test AUC was 0.8033 for proposed XGBoost, 0.7020 with PCA and 0.8091 with all eligible features and PCA disabled. This matched ablation implicates PCA in the local gap, and the top 15 validation TreeSHAP features were available at origination. Local PCA LR scored 0.6145, versus 0.723 in [1], which uses R glm and a different training and preprocessing protocol. The paper's XGBoost AUC of 0.732 also uses a different fit protocol [1].
- **Reject if** The lower paired bound is at or below −0.02.
- **If rejected** Report the result and inspect split, PCA and drift-filter differences using the planned ablations. Keep baseline reproduction status visible.

#### H2 · Calibration

- **Expected** Calibrated test Brier is smaller than raw Brier.
- **Basis** The seed-11 pilot measured 0.01636 after calibration and 0.06409 before it.
- **Reject if** The upper bound of the paired 95% interval for calibrated minus raw Brier is zero or positive.
- **If rejected** Report raw, isotonic and Platt results by quarter and examine validation-to-test prevalence shift.

#### H3 · Tier separation

- **Expected** Rates increase from A to C with disjoint adjacent 95% Wilson intervals. C share falls when risk falls.
- **Basis** The ordered validation grid yields 0.005 and 0.015. Fixed test rates are 0.02%, 0.48% and 2.88%, with disjoint overall 95% Wilson intervals. Step 5 reports quarterly comparisons and the empty 2024Q3 cohort.
- **Reject if** With a feasible fixed rule, any adjacent ordering or interval condition fails. Treat infeasible thresholds as an unevaluable hypothesis.
- **If rejected** Report the observed tiers or infeasibility and retain the comparator as labelled evidence. Any future threshold revision requires approval and validation-only selection.

#### H4 · Policy

- **Expected** Tier A saves 0.05 USD in required collateral per USD of debt versus uniform. Rejection effectiveness is measurable where both denominators are positive.
- **Basis** 125% minus 120% yields a five-point reduction. Percentile sensitivity saw 683 rejected loans with a liquidation label and 14,367 rejected good loans. Fixed-policy D3a is planned, not yet run.
- **Reject if** For a feasible comparison, the tiered rejection ratio fails to exceed uniform or tier-A capital freed is nonpositive. The ratio is undefined for the all-accept uniform case.
- **If rejected** Report counts, ratio availability and collateral effects separately. Use the planned price-shock analysis to inspect trade-offs.

#### H5 · Gas and guards

- **Expected** Single updates use ≤100,000 gas and 100-wallet batches use ≤75,000 gas per wallet. Designed guards return their exact messages.
- **Basis** Estimate versus Anvil pilot was 93,000 versus 94,739 gas for a single write and 69,034 versus median 69,252 gas per wallet at size 100. Sepolia is planned with approximately 12 s blocks, expected median 7–15 s and expected p95 24–36 s. Anvil gas does not measure Sepolia latency.
- **Reject if** A guard check fails or any measured receipt exceeds its H5 bound. Assess Sepolia latency against its expected range separately.
- **If rejected** Inspect the storage and receipt breakdown or the failing guard. If gas exceeds twice the estimate, investigate the storage and calldata assumptions. Report testnet timeouts and window differences.

#### H6 · Taiwan transfer

- **Expected** ROC AUC is in the 0.760–0.810 planning range.
- **Basis** The seed-11 pilot measured 0.7834. The chart-based range in [3] is approximately 0.68–0.71 and uses its own evaluation setup.
- **Reject if** The full estimate falls outside the expected range on the frozen evaluation protocol.
- **If rejected** Audit the split, feature exclusions and training variance. Document differences from the paper protocol.

#### H7 · Quarterly drift

- **Expected** The later populated quarter has lower prevalence and a positive calibration gap greater than the earlier quarter.
- **Basis** The validation map remains fixed as test prevalence can change. Brier and reliability by quarter will show where the discrepancy occurs. The final planned quarter, 2024Q3, is empty in this snapshot.
- **Reject if** The directional conditions in Section 2.1 are unmet across the first and last populated quarters.
- **If rejected** Report the quarterly trajectory and bin counts. Assess score mix and base-rate shifts before proposing a prospective calibration update.
