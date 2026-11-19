# A. Information

| Field | Value |
| --- | --- |
| Project | Calibrated and Explainable Liquidation-Risk Scoring for DeFi Lending with an On-chain Risk-Tiered Lending Pool |
| Group and class | 6 – BC (3H2N52), IS355.R11.CTTT.1 |
| Repository | [is355-liquidation-risk](https://github.com/callmeshinny/is355-liquidation-risk) |
| Submission date | 20 November 2026 |

| Name | Student ID | Role | Week 4 tasks | Share |
| --- | --- | --- | --- | --- |
| Tran Quang Khanh | 23520724 | Leader | [to fill by group] | [to fill by group] |
| Nguyen Le Nhu Ngoc | 23521031 | Member | [to fill by group] | [to fill by group] |

### Response to Week 3 feedback

| No. | Feedback | Week 4 response | Section |
| --- | --- | --- | --- |
| 1 | Percentiles assign high-risk tiers even when prevalence falls | D1 sets validation-only fixed cutoffs and keeps percentile sensitivity. The pilot records overlapping fixed cutoffs as infeasible. | 1.2 Step 5, 2.3 |
| 2 | Specify loan-to-wallet aggregation and new-wallet terms | D2 takes the maximum score over open loans and uses B terms for unscored or stale wallets. Document the cohort proxy and Sybil limitation. | 1.2 Step 5, 1.3, 2.3 |
| 3 | Add policy comparison alongside gas | D3 compares the tiered pool with the Aave V2 launch-style uniform policy under real labels and planned simulated price shocks. | 1.2 Step 5, 1.3, 2.3 |
| 4 | Report calibration outside the validation window | D4 measures test Brier and reliability by quarter. Record the empty local 2024Q3 cohort. | 1.2 Step 4, 2.3 |
| 5 | Resolve conflicting validation descriptions | D5 supplies calendar cutoffs, purges and distinct inner validation and calibration roles. | 1.2 Step 2, 1.4 |
| 6 | Avoid an absolute AUC claim for filtered models | D6 uses paired non-inferiority with a 0.02 margin. | 2.1, 2.5 |

Table 1. Response to Week 3 feedback.

### Changes since Week 3

Week 4 fixes the split and tuning protocol, measures local model and contract pilots, and specifies robustness and integration tests. The planned policy evaluation now includes collateral and realized outcome trade-offs. The protocol records fixed-rule infeasibility, data coverage and trusted on-chain roles.
