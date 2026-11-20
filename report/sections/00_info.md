# A. INFORMATION

| Field | Value |
| --- | --- |
| Course | IS355 – Blockchain Technology |
| Project title | Calibrated and Explainable Liquidation-Risk Scoring for DeFi Lending with an On-chain Risk-Tiered Lending Pool |
| Group | 6 – BC (3H2N52) |
| Class | IS355.R11.CTTT.1 |
| Repository | [is355-liquidation-risk](https://github.com/callmeshinny/is355-liquidation-risk) |
| Submission date | 20 November 2026 |

**Members and Week 4 contribution**

| No. | Full name | Student ID | Week 4 tasks | Share |
| --- | --- | --- | --- | --- |
| 1 | Tran Quang Khanh (Leader) | 23520724 | Checked the ML pilot results against the Week 3 code; wrote Steps 1–5 and model details (1.4); designed hypotheses H1–H3, H7 and scenarios T1, T2, T7; wrote the schedule and risks; assembled the report | 50% |
| 2 | Nguyen Le Nhu Ngoc | 23521031 | Set up the repository and environment; ran the ML pilots on both datasets (split, baseline vs. ours, calibration, tiers); wrote the smart contracts, T3/T4 pilot tests and gas pilot; wrote Steps 6–8 and the contract spec (1.3); designed H4–H6 and scenarios T3–T6 | 50% |

### Response to Week 3 feedback

| No. | Feedback | Week 4 response | Section |
| --- | --- | --- | --- |
| 1 | Percentiles assign high-risk tiers even when prevalence falls | Fixed cutoffs are selected on validation and compared with percentile tiers. To resolve the overlapping extrema, the pilot searches ordered cutoffs on validation and uses A ≤0.75× and C ≥2× prevalence. | 1.2 Step 5, 2.3 |
| 2 | Specify loan-to-wallet aggregation and new-wallet terms | The wallet uses its highest open-loan score, with B terms for an unscored or stale wallet. Document the cohort proxy and Sybil limitation. | 1.2 Step 5, 1.3, 2.3 |
| 3 | Add policy comparison alongside gas | The tiered pool is compared with an Aave V2 launch-style uniform policy using actual outcomes and simulated price shocks. | 1.2 Step 5, 1.3, 2.3 |
| 4 | Report calibration outside the validation window | Test Brier scores and reliability are measured by quarter. Record the empty local 2024Q3 cohort. | 1.2 Step 4, 2.3 |
| 5 | Resolve conflicting validation descriptions | Calendar gaps separate training, early-stopping validation and calibration validation. | 1.2 Step 2, 1.4 |
| 6 | Avoid an absolute discrimination claim for filtered models | The paired test uses a non-inferiority margin of 0.02 AUC (area under the receiver operating characteristic curve). | 2.1, 2.5 |

Table 1. Response to Week 3 feedback.

### Protocol decisions

- **D1** Choose ordered fixed cutoffs on calibration validation and compare with validation percentiles.
- **D2** Use the highest open-loan score per wallet and tier B for unscored or stale wallets.
- **D3** Compare tiered and uniform collateral using observed labels and paired simulated price shocks.
- **D4** Evaluate calibration by test quarter.
- **D5** Freeze chronological folds and purge gaps before early-stopping and calibration validation.
- **D6** Test paired AUC non-inferiority with a 0.02 margin.

### Changes since the Week 3 report

- Use 2021-12-15 through 2022-03-14 for early stopping and begin calibration validation on 2022-04-02. The last observed calibration loan was on 2022-06-28.
- Select ordered fixed risk cutoffs on calibration validation and compare them with validation percentiles.
- Take the maximum score across open loans for each wallet. Use tier B for missing or stale scores.
- Compare tiered collateral with a uniform 125% requirement using observed labels and paired simulated price shocks.
- Test H1 with a paired non-inferiority margin of 0.02 AUC.
