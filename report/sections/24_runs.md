## 2.4 Repetition, precision and budget

The unit of repetition is a fit, guard case, transaction, fresh deployment or simulation draw. ML shares splits and seeds 11, 22, 33, 44 and 55. Optuna uses 50 inner-validation trials per variant.

| Scenarios | Unit | Plan versus minimum and reason | Aggregation | Expected elapsed time |
| --- | --- | --- | --- | --- |
| T1-01 | Baseline fit or LR bootstrap draw | Five XGB fits meet the five-seed minimum. Deterministic LR uses one fit and 1,000 stratified test bootstrap draws | Seed mean and sample SD or LR bootstrap interval | 10 min |
| T1-02–T1-05 | Paired seed | Five matched seeds meet the minimum. Reuse frozen fitted scores for calibration, tiers and policy | Mean paired difference, 95% t interval, Wilson tier intervals | 25 min with shared fits |
| T1-06, T7-02 | Taiwan fit | Five fits on the same stratified split. Reuse fits for stability | Mean AUC and seed SD | 5 min |
| T2-01–T2-05 | Seed per setting | Five seeds per setting as required. Share precomputed inputs and keep test outside selection | Paired differences and 95% t intervals | 60 min including search and setup, expected |
| T3-01–T3-11 | API assertion | One valid and one guard case per function | Exact message and state match | 10 min |
| T4-01–T4-08 | Guard check, design review or generated example | One per deterministic case and 200 generated borrowing cases meet the minimum | Pass count and documented residual exposure | 30 min with review |
| T5-01 | Transaction | Ten singles and ten batches per 1, 10 and 100 wallets. Three sizes and ten calls per size meet the minimum | Median, maximum, per-wallet gas | 20 min |
| T5-02 | Successful testnet confirmation | Target 100 per function over at least two windows, with at least 30 per window. Schedule separate windows for variability | Median, p95, timeouts and window counts | 90 min active plus window spacing |
| T6-01–T6-02 | Full fresh deployment | Three per scenario meet the minimum | Reconcile state and event evidence for every run | 60 min |
| T7-01 | Seed on fixed test quarters | Five seeds and every non-empty quarter | Quarterly Brier, reliability and prevalence | 20 min |
| T7-03 | Paired Monte Carlo draw | At least 1,000 per shock. Continue to precision target | Mean paired effect and 95% CI width | 60 min |

Table 18. Planned run counts, analysis and elapsed-time allowances.

XGB pilot SDs were 0.00224 (baseline) and 0.00411 (proposed), with paired s_d = 0.00566. LR bootstrap SDs were 0.00806 and 0.00739. The paired CI is d̄ ± t(0.975, n−1)·s_d/√n. Expected half-width at n = 5 is 0.00703. Using n ≈ (2.8·s_d/Δ)² gives 2.51 for Δ = 0.01 and 0.63 for Δ = 0.02. Round up and add 1–2. Keep the five-seed minimum because the pilot has three pairs.

### Sepolia budget (planned, not yet run)

| Main transaction | Confirmations | Anvil receipt gas proxy | Gas subtotal |
| --- | ---: | ---: | ---: |
| set_score | 100 | 94,739 | 9,473,900 |
| deposit_collateral | 100 | 83,813 | 8,381,300 |
| borrow | 100 | 119,897 | 11,989,700 |
| repay | 100 | 49,661 | 4,966,100 |
| liquidate | 100 | 96,682 | 9,668,200 |

Table 19. Confirmation sample budget using the pilot receipt gas as a planning proxy.

At an assumed 2 gwei and 25% contingency, the budget is (44,479,200 measured-call gas proxy + 5,000,000 setup allowance) × 1.25 × 2 × 10⁻⁹ = 0.1237 test ETH. Against an assumed 0.10 faucet allocation the shortfall is 0.0237. Confirm funding and stage collection if needed. Anvil provides gas estimates. Measure latency on Sepolia.
