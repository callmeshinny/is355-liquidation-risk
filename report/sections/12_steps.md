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
