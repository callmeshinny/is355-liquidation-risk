## 2.2 Scenario overview

| ID | Scenario | Group | Hypothesis or improvement | Environment | Planned runs |
| --- | --- | --- | --- | --- | --- |
| T1-01 | Reproduce the all-feature PCA baselines from [1] | Model comparison | H1, I2 | Python, FinSurvival | 5 seeds per model. For deterministic LR, one fit and 1,000 test bootstrap draws |
| T1-02 | Test drift-filtered model non-inferiority | Model comparison | H1, I2 | Python, FinSurvival D5 | 5 paired XGBoost seeds |
| T1-03 | Compare raw and isotonic probability scores | Model comparison | H2, I1 | Python, FinSurvival D5 | 5 paired seeds |
| T1-04 | Compare fixed and percentile risk tiers | Model comparison | H3, I1 | Python, FinSurvival D5 | 5 seeds per rule. The fixed rule requires ordered D1 cutoffs |
| T1-05 | Compare tiered and uniform acceptance and collateral | Model comparison | H4, I3 | Python, FinSurvival D5 | 5 paired score seeds. The fixed policy requires ordered D1 cutoffs |
| T1-06 | Evaluate Taiwan test ROC AUC | Model comparison | H6, I4 | Python, Taiwan | 5 seeds on the same stratified split |
| T2-01 | Turn drift removal on and off | Ablation | H1, I2 | Python, FinSurvival D5 | 5 paired seeds per setting |
| T2-02 | Turn PCA on and off | Ablation | H1, I2 | Python, FinSurvival D5 | 5 paired seeds per setting |
| T2-03 | Compare isotonic, Platt and raw scores | Ablation | H2, H7, I1 | Python, FinSurvival D5 | 5 paired seeds per setting |
| T2-04 | Vary the KS drift threshold | Ablation | H1, I2 | Python, FinSurvival D5 | 5 paired seeds per threshold |
| T2-05 | Vary the tier assignment rule | Ablation | H3, H4, I1 | Python, FinSurvival D5 | 5 paired seeds per rule. Fixed results depend on D1 feasibility |
| T3-01 | Register model hash and version | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-02 | Change the score writer | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-03 | Write a single tier score | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-04 | Write a batch of tier scores | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-05 | Read the effective tier | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-06 | Deposit collateral | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-07 | Withdraw collateral | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-08 | Borrow against collateral | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-09 | Repay debt | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-10 | Liquidate unhealthy debt | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T3-11 | Update the collateral price | Contract functions | I3 | Ape and Anvil | 1 valid call and 1 guard case |
| T4-01 | Score-writer authorization and model version | Contract safeguards | H5, I3 | Ape and Anvil | 1 deterministic case per guard |
| T4-02 | Default B terms for stale scores | Contract safeguards | H5, I3 | Ape and Anvil | 1 deterministic case |
| T4-03 | Healthy-position and close-factor guards | Contract safeguards | H5, I3 | Ape and Anvil | 1 deterministic case per guard |
| T4-04 | Amount bounds, tier C and borrowing invariant | Contract safeguards | H5, I3 | Ape, Anvil and Hypothesis | 1 deterministic case per boundary and 200 generated examples |
| T4-05 | New-wallet identity and default-tier limitation | Design review | H5, I3 | Threat model and Anvil default-tier check | 1 review and 1 default-tier check |
| T4-06 | Compromised oracle key exposure | Design review | H5, I3 | Threat model and role review | 1 design review |
| T4-07 | Trusted owner price-setting exposure | Design review | H5, I3 | Threat model and role review | 1 design review |
| T4-08 | Tier-downgrade transaction-ordering exposure | Design review | H5, I3 | Threat model and contract review | 1 design review |
| T5-01 | Measure single and batched score-write gas | Performance | H5, I3 | Ape and Anvil | 10 single writes and 10 batches at each size of 1, 10 and 100 |
| T5-02 | Measure public testnet confirmation latency | Performance | I3 | Sepolia via Alchemy, planned | Target 100 confirmations per main function across at least two windows, with at least 30 per window |
| T6-01 | Reconcile the tier export, model hash and chain events | End-to-end | I1, I3 | Python, Ape and Anvil | 3 full runs on fresh deployments. Fixed-tier inputs depend on D1 feasibility |
| T6-02 | Show price drop and liquidation in the dashboard | End-to-end | H4, I3 | Streamlit, Ape and Anvil | 3 full runs on fresh deployments |
| T7-01 | Measure calibration and prevalence by quarter | Robustness | H2, H7, I1 | Python, FinSurvival D5 | 5 model seeds across all non-empty quarters |
| T7-02 | Check stability on the Taiwan cohort | Robustness | H6, I4 | Python, Taiwan | Reuse the 5 T1-06 fits and summarize seed spread |
| T7-03 | Compare both lending policies under price shocks | Robustness | H4, I3 | Python, paired Monte Carlo | At least 1,000 runs per shock. Compare both policies on the same draws and report CI precision |

Table 14. Scenario IDs, environments and planned repetitions.

The counts describe the full design. The FinSurvival model pilot used three XGBoost seeds, the Taiwan pilot used seed 11 and the Anvil gas pilot used ten fresh batches per size. Measured results appear in `results/pilot_model.json`, `results/pilot_taiwan.json` and `results/pilot_gas.json`. Planned Optuna comparisons use 50 trials per variant on inner validation. The 2024Q3 test cohort is empty. Sepolia, the full dashboard runs and the Monte Carlo study are planned, not yet run.
