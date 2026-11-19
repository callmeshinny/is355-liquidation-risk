## 1.2 Procedure

### Step 1 · Data collection

| Field | Specification |
| --- | --- |
| Purpose | Assemble loan-level features and survival outcomes, plus an external credit-default dataset for I4. |
| Input | FinSurvival Borrow RDS feature parts and Account Liquidated RDS labels [1]. UCI credit defaults, dataset 350 [3]. |
| Processing | Concatenate four benchmark training X parts and three test X parts. Remove missing IDs, all-null feature columns and columns starting with exo. Join each y to the matching X by ID and align the shared columns. Load Taiwan features and binary default outcome through ucimlrepo. |
| Parameters | Use the Borrow → Account Liquidated benchmark cohort and UCI dataset ID 350. |
| Libraries / tools | pandas, pyreadr, pyarrow and ucimlrepo. |
| Output | Three interim parquet files and counts with schemas in results/pilot_data.json. |
| Runs | One load per input snapshot. Pilot date 2026-11-19. Loading has no random operations. |
| Correctness check | Compare label coverage and matched counts with Week 3. Check the RDS columns and record the Taiwan target rate. |
| Errors & edge cases | Missing parts stop the load. Unmatched IDs are counted by source split. Repeated IDs are handled in Step 2. |
| Est. run time | Pilot wall time 26.4 s including the UCI fetch and parquet writes. |
| Improvement | I4 adds a separate credit-default dataset using the same input and reporting conventions. |

```text
for each benchmark source split:
    concatenate X parts, clean columns and join to y by id
align train and test schemas
fetch dataset 350 and save all three frames and their counts
```

The pilot loaded 259,886 FinSurvival label rows, of which 259,886 matched a feature ID. The join produced 269,546 rows with 116 shared feature columns excluding ID and target fields. Repeated matches can yield more joined rows than matched label rows. The label files contained 0 training and 0 test label rows without features. Week 3 recorded 264,536 label rows, 259,886 with features and 4,650 unmatched test labels. The local snapshot contains 4,650 fewer label rows and has complete ID coverage, which accounts for the label-count difference.

| Source split | Raw features | All-null removed | Exogenous removed | Non-shared removed |
| --- | ---: | ---: | ---: | ---: |
| train | 128 | 12 | 0 | 0 |
| test | 128 | 12 | 0 | 0 |

Table 1. FinSurvival feature counts before and after loader checks.

The feature-count difference from Week 3's 128 is shown by these loader checks. The Taiwan load yielded 30,000 clients, 23 features and 22.12% defaults.

### Step 2 · Labelling and feature preparation

| Field | Specification |
| --- | --- |
| Purpose | Build a binary outcome and temporally separated model inputs with train-only encoding. |
| Input | Step 1 interim parquet files and the D5 calendar. |
| Processing | Remove repeated transaction IDs and rows with insufficient follow-up. Split on loan start in UTC. On train_core and inner-val compute KS D for numeric features. Record D ≥ 0.15 for removal in the O branch. Fit top-ten categorical vocabularies on train_core. Map other levels to a fallback column and fill missing numerics with zero. |
| Parameters | 17.43-day horizon [1]. D5 purge windows of 18 days. KS D ≥ 0.15. Taiwan 60/10/30 stratified with seed 11. |
| Libraries / tools | pandas, SciPy, scikit-learn and pyarrow. |
| Output | Split parquet files with encoded features and a manifest of feature rules in results/pilot_data.json. |
| Runs | One fixed calendar split and one Taiwan stratified split. Pilot date 2026-11-19. |
| Correctness check | tests/test_data.py checks disjoint IDs, D5 date bounds and train-only categorical fitting. |
| Errors & edge cases | Keep observed early liquidations. Drop short censored outcomes and exclude IDs and label fields from modelling. |
| Est. run time | Pilot wall time 9.7 s including the split parquet writes. |
| Improvement | I2 uses an inner validation window and KS drift removal. I4 applies the pipeline to Taiwan without a time-based drift test. |

```text
discard all rows whose transaction ID repeats
if status is 1 and duration <= 17.43 days: label = 1
else if duration > 17.43 days: label = 0
else: discard insufficient follow-up
split on UTC start date and drop the two D5 purge windows
fit categories and identify empty columns using train_core
compare numeric features between train_core and inner-val
transform each fold with the fitted feature rules
```

D5 replaces the Week 3 moving validation cutoff. Train_core ends before 2021-11-27. Inner validation spans 2021-12-15 through 2022-03-14. Calibration and tier selection use 2022-04-02 through 2022-06-30. The test window begins 2022-07-01. The date gaps are purged before fitting. The local test snapshot ends on 2024-05-07, leaving no rows in 2024Q3. Mark that quarter as empty in the calibration and tier tables. Taiwan omits SEX and MARRIAGE and uses stratification without a calendar.

| FinSurvival split | Rows | Positive rate | Observed UTC dates |
| --- | ---: | ---: | --- |
| train_core | 118,055 | 7.67% | 2020-12-01 to 2021-11-26 |
| inner_val | 10,638 | 5.99% | 2021-12-15 to 2022-03-14 |
| val | 19,305 | 4.33% | 2022-04-02 to 2022-06-28 |
| test | 96,345 | 1.31% | 2022-07-01 to 2024-05-07 |

Table 2. FinSurvival pilot split counts.

| Taiwan split | Rows | Positive rate |
| --- | ---: | ---: |
| train_core | 18,000 | 22.12% |
| val | 3,000 | 22.13% |
| test | 9,000 | 22.12% |

Table 3. Taiwan pilot split counts.

The FinSurvival pilot removed 13,819 joined rows with repeated IDs, corresponding to 4,159 source feature rows before the join, and 4,556 rows during labelling. The resulting 251,171 rows had a positive rate of 4.81% before D5 excluded 6,828 rows. The pre-purge count and rounded rate match the Week 3 totals of 251,171 and 4.81%. The KS screen flagged 46 numeric features.

In one pilot row, the loan started on 2020-12-01. Its event status was 0, observed duration was 576.465 days and the label was 0.

### Step 3 · Train baseline and proposed models

| Field | Specification |
| --- | --- |
| Purpose | Compare all-feature PCA models with drift-filtered models under the D5 split and evaluate H1. |
| Input | Step 2 encoded FinSurvival splits and the KS drop list. Taiwan provides an external cohort. |
| Processing | For LR, apply signed log1p and standardize. For baseline XGB, standardize before PCA. Fit all transforms on train_core. Train two LR and two XGB variants. Use inner-val AUC for XGB early stopping. Score all held-out folds after fitting. |
| Parameters | Baseline PCA retains 95% variance as our assumption about [1]. LR uses C=0.1 and balanced weights. XGB uses learning rate 0.05, depth 6 and patience 50. |
| Libraries / tools | scikit-learn, XGBoost, NumPy and pandas. |
| Output | AUC and fit time per run in results/pilot_model.json. Save proposed XGB trees and held-out scores locally. |
| Runs | Pilot 2026-11-19. XGB seeds 11, 22 and 33. LR uses seed 11 with 1,000 stratified test bootstrap samples. Taiwan uses seed 11. |
| Correctness check | Check the complete model-by-seed matrix and AUCs on inner-val, val and test. Pair XGB runs by seed for H1. |
| Errors & edge cases | Convert nonfinite features to zero consistently. Compare paper reproduction using ±0.02 AUC tolerance. |
| Est. run time | Mean fit time by variant is shown below. It includes scaling and PCA where used. |
| Improvement | I2 drops variables flagged for drift and keeps the original feature space for explanation. I4 checks transfer to a separate credit dataset. |

```text
fit scaling and PCA on train_core for each baseline branch
fit LR on train_core and early-stop XGB using inner-val
evaluate frozen models on inner-val, calibration val and test
pair XGB test AUC by seed and bootstrap LR test AUC
```

| Model | Seeds | Mean inner-val AUC | Mean val AUC | Mean test AUC | Mean fit (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| B_XGB | 11, 22, 33 | 0.7885 | 0.6870 | 0.7020 | 3.61 |
| O_XGB | 11, 22, 33 | 0.8089 | 0.8113 | 0.8033 | 3.10 |
| B_LR | 11 | 0.7931 | 0.7519 | 0.6145 | 2.45 |
| O_LR | 11 | 0.8053 | 0.7974 | 0.7861 | 3.92 |

Table 4. FinSurvival pilot fits on 2026-11-19.

The B_LR test AUC differs from [1] by -0.1085 and the B_XGB mean differs by -0.0300. Both exceed the ±0.02 reproduction tolerance in absolute difference. The paired XGB AUC difference has seed SD 0.00566. Using a t interval with five seeds, its estimated 95% half-width is 0.00703. Taiwan O_XGB achieved test AUC 0.7834 on 2026-11-19 with seed 11.

### Step 4 · Calibrate and explain probabilities

| Field | Specification |
| --- | --- |
| Purpose | Test probability calibration under changing base rates and rank features by model contribution. |
| Input | Frozen O_XGB seed 11 scores on validation and chronological test. |
| Processing | Fit isotonic using validation labels. Apply the frozen monotone mapping to test. Compute Brier before and after, overall and by quarter. For SHAP, use the trees through the selected early-stopping iteration and rank mean absolute contributions. |
| Parameters | Clip isotonic predictions outside the fitted score range. Reliability uses ten fixed equal-width bins. XGBoost native TreeSHAP (vector intercept compatibility) uses 2,000 distinct test rows. |
| Libraries / tools | scikit-learn, SHAP, XGBoost and pandas. |
| Output | results/pilot_calib.json and results/pilot_reliability.csv. |
| Runs | Pilot 2026-11-19, seed 11. The multi-seed H2 test is planned, not yet run. |
| Correctness check | Verify validation-only calibration and Brier on identical raw and calibrated test pools. |
| Errors & edge cases | Empty quarters have undefined Brier. Empty reliability bins retain their zero counts. SHAP describes raw model output. |
| Est. run time | Pilot wall time 2.1 s. |
| Improvement | I1 adds an interpretable probability mapping and feature attributions. D4 evaluates quarterly reliability. |

```text
fit isotonic(raw_val, label_val)
score test with the frozen mapping
compute raw and calibrated Brier on each test quarter
rank contributions on a seeded sample using TreeSHAP
```

Overall Brier changed from 0.06409 to 0.01636. The SHAP ranking is `userLiquidationCount`, `userDepositAvgAmountUSD`, `cosDayOfQuarter`, `userBorrowCount`, `userDepositAvgAmountETH`, `priceInUSD`, `userActiveDaysYearly`, `userActiveDaysWeekly`, `dayOfMonth`, `userBorrowAvgAmountETH`.

| Quarter | Loans | Raw Brier | Calibrated Brier |
| --- | ---: | ---: | ---: |
| 2022Q3 | 25,953 | 0.05696 | 0.01548 |
| 2022Q4 | 23,787 | 0.07139 | 0.02295 |
| 2023Q1 | 17,899 | 0.06410 | 0.01162 |
| 2023Q2 | 9,292 | 0.05658 | 0.01161 |
| 2023Q3 | 6,354 | 0.05910 | 0.01346 |
| 2023Q4 | 6,808 | 0.06096 | 0.00959 |
| 2024Q1 | 5,005 | 0.09185 | 0.02532 |
| 2024Q2 | 1,247 | 0.06032 | 0.02844 |
| 2024Q3 | 0 | — | — |

Table 5. FinSurvival test Brier by quarter.

### Step 5 · Assign risk tiers

| Field | Specification |
| --- | --- |
| Purpose | Convert calibrated risk to A/B/C and compare fixed D1 thresholds with a validation percentile rule. |
| Input | Calibrated scores, validation labels, held-out cohort and the locally saved model. |
| Processing | Group validation scores by distinct value. Use cumulative lower and upper tail counts to select the feasible D1 cutoffs. Freeze these and the comparison quantiles. Compute held-out shares and liquidation rates for both rules. Take maximum risk across each wallet's input loans. |
| Parameters | A uses a lower tail rate ≤ 0.5 times validation prevalence. C uses an upper tail rate ≥ 3 times prevalence and at least 30 positives. Comparison uses the validation 70th and 90th percentiles. |
| Libraries / tools | pandas, NumPy and hashlib. |
| Output | results/pilot_tiers.json, a hashed 20-wallet percentile sample and a local tiers_percentile.csv for the comparison. |
| Runs | Pilot 2026-11-19 using model seed 11 and the two frozen validation rules. |
| Correctness check | Check ordering of the thresholds, model SHA-256, and partition totals for each rule and cohort. |
| Errors & edge cases | The snapshot lacks point-in-time open-loan membership. Use the observed cohort for the wallet pilot. Live D2 aggregation takes open loans as input. |
| Est. run time | Measure end-to-end tier and export latency in the planned chain integration test. |
| Improvement | I1 replaces percentile buckets with validation-derived fixed thresholds for the main policy. |

```text
choose D1 thresholds and comparison quantiles using validation only
for each test cohort and rule:
    assign loan tiers
    aggregate maximum score per wallet and assign wallet tiers
    publish shares, realized rates and Wilson intervals
hash the fitted model and export wallet tiers
```

Validation prevalence was 4.33%. The independent D1 extrema were τ_A = 0.106122 and τ_C = 0.043348. D1 produces overlapping A/C regions on validation. The fixed-tier pilot is planned, not yet run. The comparison cutoffs were 0.020427 and 0.106122. The test cohort has 96,345 loans from 21,641 wallet groups. Quarterly loan and wallet summaries for the percentile rule are in results/pilot_tiers.json. Wallet rates indicate whether any observed loan for the wallet liquidated.

| Rule | Tier | Test loans | Share | Liquidation rate | 95% Wilson CI |
| --- | --- | ---: | ---: | ---: | --- |
| percentile | A | 62,092 | 64.45% | 0.45% | 0.40%–0.51% |
| percentile | B | 19,203 | 19.93% | 1.58% | 1.41%–1.76% |
| percentile | C | 15,050 | 15.62% | 4.54% | 4.22%–4.88% |

Table 6. Percentile tiers on the held-out loan cohort.

The fixed-rule D3a pilot is planned, not yet run because D1 yields overlapping regions. The percentile sensitivity pilot on 2026-11-19 used the contemporaneous loan score and its observed outcome. The historical data lacks open-loan membership, so the pilot uses each loan's origination score for acceptance. “Liquidations avoided” counts rejected loans that later liquidated. This is a counterfactual proxy. The price-shock simulation is planned, not yet run. Capital totals use 95,596 loans with positive finite USD amounts. Capital freed is uniform minus tiered capital, or USD 1,941,823,554.74. The tier-A subset frees USD 1,665,763,650.49.

| Policy | Accepted | Rejected | Liquidations avoided | Good loans rejected | Capital locked (USD) |
| --- | ---: | ---: | ---: | ---: | ---: |
| uniform | 96,345 | 0 | 0 | 0 | 44,218,089,861.50 |
| tiered | 81,295 | 15,050 | 683 | 14,367 | 42,276,266,306.76 |

Table 7. D3a percentile sensitivity and uniform policy on the same test loans.
