## 2.2 Scenario overview

| ID | Scenario | Group | Hypothesis or improvement | Environment | Planned runs |
| --- | --- | --- | --- | --- | --- |
| T1-01 | Reproduce the all-feature PCA baselines from [1] | Model | H1, I2 | Python, FinSurvival | 5 seeds per model. For deterministic LR, one fit and 1,000 test bootstrap draws |
| T1-02 | Test drift-filtered model non-inferiority | Model | H1, I2 | Python/D5 | 5 paired XGBoost seeds |
| T1-03 | Compare raw and isotonic probability scores | Model | H2, I1 | Python/D5 | 5 paired seeds |
| T1-04 | Compare fixed and percentile risk tiers | Model | H3, I1 | Python/D5 | 5 seeds per rule. The fixed rule requires ordered D1 cutoffs |
| T1-05 | Compare tiered and uniform acceptance and collateral | Model | H4, I3 | Python/D5 | 5 paired score seeds. The fixed policy requires ordered D1 cutoffs |
| T1-06 | Evaluate Taiwan test ROC AUC | Model | H6, I4 | Python, Taiwan | 5 seeds on the same stratified split |
| T2-01 | Turn drift removal on and off | Ablation | H1, I2 | Python/D5 | 5 paired seeds/setting |
| T2-02 | Turn PCA on and off | Ablation | H1, I2 | Python/D5 | 5 paired seeds/setting |
| T2-03 | Compare isotonic, Platt and raw scores | Ablation | H2, H7, I1 | Python/D5 | 5 paired seeds/setting |
| T2-04 | Vary the KS drift threshold | Ablation | H1, I2 | Python/D5 | 5 paired seeds per threshold |
| T2-05 | Vary the tier assignment rule | Ablation | H3, H4, I1 | Python/D5 | 5 paired seeds/rule. Fixed results depend on D1 feasibility |
| T3-01 | Register model hash and version | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-02 | Change the score writer | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-03 | Write a single tier score | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-04 | Write a batch of tier scores | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-05 | Read the effective tier | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-06 | Deposit collateral | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-07 | Withdraw collateral | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-08 | Borrow against collateral | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-09 | Repay debt | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-10 | Liquidate unhealthy debt | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T3-11 | Update the collateral price | Functions | I3 | Ape/Anvil | 1 valid + 1 guard |
| T4-01 | Score-writer authorization and model version | Safeguards | H5, I3 | Ape/Anvil | 1 per guard |
| T4-02 | Default B terms for stale scores | Safeguards | H5, I3 | Ape/Anvil | 1 deterministic case |
| T4-03 | Healthy-position and close-factor guards | Safeguards | H5, I3 | Ape/Anvil | 1 per guard |
| T4-04 | Amount bounds, tier C and borrowing invariant | Safeguards | H5, I3 | Ape, Anvil and Hypothesis | 1 deterministic case per boundary and 200 generated examples |
| T4-05 | New-wallet identity and default-tier limitation | Design review | H5, I3 | Threat model and Anvil default-tier check | 1 review and 1 default-tier check |
| T4-06 | Compromised oracle key exposure | Design review | H5, I3 | Threat model and role review | 1 design review |
| T4-07 | Trusted owner price-setting exposure | Design review | H5, I3 | Threat model and role review | 1 design review |
| T4-08 | Tier-downgrade transaction-ordering exposure | Design review | H5, I3 | Threat model and contract review | 1 design review |
| T5-01 | Measure single and batched score-write gas | Performance | H5, I3 | Ape/Anvil | 10 single writes and 10 batches at each size of 1, 10 and 100 |
| T5-02 | Measure public testnet confirmation latency | Performance | I3 | Sepolia via Alchemy, planned | Target 100 confirmations per main function across at least two windows, with at least 30 per window |
| T6-01 | Reconcile the tier export, model hash and chain events | End-to-end | I1, I3 | Python, Ape/Anvil | 3 full runs on fresh deployments. Fixed-tier inputs depend on D1 feasibility |
| T6-02 | Show price drop and liquidation in the dashboard | End-to-end | H4, I3 | Streamlit, Ape/Anvil | 3 full runs on fresh deployments |
| T7-01 | Measure calibration and prevalence by quarter | Robustness | H2, H7, I1 | Python/D5 | 5 model seeds across all non-empty quarters |
| T7-02 | Check stability on the Taiwan cohort | Robustness | H6, I4 | Python, Taiwan | Reuse the 5 T1-06 fits and summarize seed spread |
| T7-03 | Compare both lending policies under price shocks | Robustness | H4, I3 | Python, paired Monte Carlo | At least 1,000 runs per shock. Compare both policies on the same draws and report CI precision |

Table 16. Scenario IDs, environments and planned repetitions.

Pilots used three FinSurvival XGB seeds, Taiwan seed 11 and ten Anvil batches per size. Optuna uses 50 inner-validation trials per variant. Test 2024Q3 is empty. Sepolia, dashboard integration and Monte Carlo are planned, not yet run.
