### 1.2. Step-by-step specification

#### Step 1 · Data collection

**Purpose** Load standardized loan and credit records. **Input** RDS features and liquidation labels [1]. UCI 350 [5]. **Processing** Concatenate X parts. Drop empty columns and external covariates. Inner join y by ID. Align schemas. **Parameters** Borrow → Account Liquidated. UCI dataset 350.

**Libraries / tools** pandas, pyreadr, pyarrow, ucimlrepo. **Output** Interim parquet. Example: finsurvival_train.parquet and taiwan.parquet. **Runs** One load, 2026-11-19.

**Correctness check** Check IDs, source row counts and schema. **Errors & edge cases** Missing parts stop loading. Record unmatched and duplicate IDs. **Est. run time** 26.4 s pilot including UCI and writes. **Improvement** I4 adds Taiwan.

```text
concat FinSurvival X parts by benchmark split
drop all-null and external covariates
join X and y by loan id
align train and test feature columns
fetch UCI 350 and write interim parquet and schema counts
```

All 259,886 local labels matched features, yielding 269,546 joined rows after repeat matches. The source has 4,650 fewer test labels than Week 3, which reported those labels as unmatched.

| Source split | Raw features | All-null removed | External covariates removed | Non-shared removed |
| --- | ---: | ---: | ---: | ---: |
| train | 128 | 12 | 0 | 0 |
| test | 128 | 12 | 0 | 0 |

Table 3. FinSurvival feature counts before and after loader checks.

After loader checks, 116 features remain. Taiwan loaded 30,000 clients, 23 features and 22.12% defaults.

#### Step 2 · Labelling and feature preparation

**Purpose** Prepare leak-resistant inputs. **Input** Interim parquet and D5 calendar. **Processing** Deduplicate transactions, label, purge and encode. Record proposed-model drops using the Kolmogorov–Smirnov (KS) statistic. **Parameters** 17.43 days, D5 windows, D ≥ 0.15, Taiwan seed 11.

**Libraries / tools** pandas, SciPy, scikit-learn, pyarrow. **Output** Split parquet (example: fin_train_core.parquet) and feature-rule manifest. **Runs** One split per dataset, 2026-11-19.

**Correctness check** Test date boundaries, ID disjointness and train-only vocabularies. **Errors & edge cases** Keep observed early liquidations. Drop insufficient follow-up. **Est. run time** 9.7 s pilot including writes. **Improvement** I2 freezes chronological feature preparation.

```text
drop repeated IDs
label observed events within 17.43 days as positive
label later observations as negative and discard short censored records
split by UTC start date and purge D5 gaps
fit categories on train_core
flag numeric features with train_core versus inner validation KS D at or above the cutoff
transform all folds with frozen rules
```

D5 purges two gaps. Calibration eligibility ends 2022-06-30. Taiwan excludes sex and marital status before stratification.

| FinSurvival fold | Rows | Positive rate | Observed UTC dates |
| --- | ---: | ---: | --- |
| train_core | 118,055 | 7.67% | 2020-12-01 to 2021-11-26 |
| inner_val | 10,638 | 5.99% | 2021-12-15 to 2022-03-14 |
| val | 19,305 | 4.33% | 2022-04-02 to 2022-06-28 |
| test | 96,345 | 1.31% | 2022-07-01 to 2024-05-07 |

Table 4. FinSurvival pilot split counts.

| Taiwan split | Rows | Positive rate |
| --- | ---: | ---: |
| train_core | 18,000 | 22.12% |
| val | 3,000 | 22.13% |
| test | 9,000 | 22.12% |

Table 5. Taiwan pilot split counts.

Removed 13,819 joined rows with repeated IDs, representing 4,159 source rows, and 4,556 rows during labelling. Before purging 6,828 rows, 251,171 remained with 4.81% positives, matching Week 3. KS flagged 46 numeric features.

| Dropped feature (D) | Dropped feature (D) | Dropped feature (D) |
| --- | --- | --- |
| borrowRate (0.40481) | userSecondsSinceFirstTransaction (0.32442) | userBorrowAvgAmountUSD (0.16052) |
| marketCollateralCount (0.95954) | marketDepositCount (0.96822) | marketDepositAvgAmount (0.95278) |
| marketDepositSum (0.39857) | marketDepositAvgAmountUSD (0.93619) | marketDepositSumUSD (0.35849) |
| marketDepositAvgAmountETH (0.95650) | marketDepositSumETH (0.30556) | marketWithdrawCount (0.86506) |
| marketWithdrawAvgAmount (0.91356) | marketWithdrawSum (0.64778) | marketWithdrawAvgAmountUSD (0.88221) |
| marketWithdrawSumUSD (0.40575) | marketWithdrawAvgAmountETH (0.91647) | marketWithdrawSumETH (0.37987) |
| marketBorrowCount (0.95595) | marketBorrowAvgAmount (0.60867) | marketBorrowSum (0.64386) |
| marketBorrowAvgAmountUSD (0.69632) | marketBorrowSumUSD (0.64375) | marketBorrowAvgAmountETH (0.42474) |
| marketBorrowSumETH (0.69006) | marketRepayCount (0.58686) | marketRepayAvgAmount (0.84588) |
| marketRepaySum (0.38776) | marketRepayAvgAmountUSD (0.83307) | marketRepaySumUSD (0.38448) |
| marketRepayAvgAmountETH (0.46280) | marketRepaySumETH (0.31501) | marketSwapCount (0.88608) |
| marketLiquidationCount (0.70087) | marketLiquidationAvgAmount (0.22057) | marketLiquidationSum (0.51510) |
| marketLiquidationAvgAmountUSD (0.22807) | marketLiquidationSumUSD (0.51465) | marketLiquidationAvgAmountETH (0.53013) |
| marketLiquidationSumETH (0.38131) | dayOfYear (0.57617) | quarter (0.54472) |
| sinDayOfYear (0.32774) | cosDayOfYear (0.67497) | sinQuarter (0.54472) |
| cosQuarter (0.60419) | — | — |

Table 6. Numeric feature exclusions from the training-to-inner-validation KS check.

Example loan: 2020-12-01, event status 0, observed 576.465 days, label 0.

#### Step 3 · Train baseline and proposed models

The B prefix identifies baseline variants and O identifies proposed variants. LR denotes logistic regression and XGB denotes XGBoost.

**Purpose** Compare drift-filtered and all-feature XGBoost without PCA for H1. **Input** Split parquet and feature-rule manifest. **Processing** Fit LR or XGB. Scale as needed. Fit PCA in training for the paper reproduction only. Early-stop XGB on inner validation. **Parameters** 95% PCA assumption, LR C=0.1, XGB learning rate 0.05, depth 6, patience 50.

**Libraries / tools** scikit-learn, XGBoost. **Output** Frozen XGBoost model artifact, validation and test score parquet, AUC and fit time. **Runs** 2026-11-19. XGB seeds 11/22/33. LR seed 11 and 1,000 bootstrap draws.

**Correctness check** Check model/seed coverage and paired test AUC. **Errors & edge cases** Replace nonfinite features with zero. Paper reproduction tolerance ±0.02 AUC. **Est. run time** Mean XGBoost fit times were 3.61 s baseline, 3.10 s proposed and 2.66 s without PCA. **Improvement** I2 tests non-inferiority and the validation-to-test AUC gap. I4 checks Taiwan.

```text
select eligible features and apply the drift list for proposed variants
replace nonfinite values with zero and apply signed log1p for LR
fit required scaling and baseline PCA on train_core only
fit LR on train_core or early-stop XGBoost on inner validation
freeze the model and score validation and test
record fit time, AUC, paired seed differences and LR bootstrap intervals
```

| Model | Seeds | Mean inner validation AUC | Mean val AUC | Mean test AUC | Mean fit (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| B_XGB | 11, 22, 33 | 0.7885 | 0.6870 | 0.7020 | 3.61 |
| B_XGB_noPCA | 11, 22, 33 | 0.8367 | 0.8348 | 0.8091 | 2.66 |
| O_XGB | 11, 22, 33 | 0.8089 | 0.8113 | 0.8033 | 3.10 |
| B_LR | 11 | 0.7931 | 0.7519 | 0.6145 | 2.45 |
| O_LR | 11 | 0.8053 | 0.7974 | 0.7861 | 3.92 |

Table 6. FinSurvival fits from 2026-11-19 and 2026-11-20. B_XGB is the PCA reproduction. B_XGB_noPCA is the H1 baseline.

PCA reproduction missed the [1] tolerance for LR and XGBoost. For the primary H1 comparison and both validation-to-test gaps, see Section 2.5.

#### Step 4 · Calibrate and explain probabilities

**Purpose** Calibrate risk and explain model output. **Input** Frozen XGB artifact and validation/test score parquet. **Processing** Fit isotonic and Platt on calibration validation. Compare frozen maps and raw probabilities on test. Rank TreeSHAP. **Parameters** Ten reliability bins, 2,000 test loans, seed 11.

**Libraries / tools** scikit-learn, XGBoost TreeSHAP, pandas. **Output** Calibrated score parquet (example: calibrated_test.parquet), Brier, reliability bins and SHAP top ten. **Runs** 2026-11-20, seed 11. Multi-seed H2 planned, not yet run.

**Correctness check** Verify matching pools and validation-only fit. **Errors & edge cases** Empty quarters have undefined Brier. TreeSHAP describes raw output. **Est. run time** 34.82 s measured including isotonic, Platt, reliability and SHAP. **Improvement** I1 and D4 add calibration, interpretation and quarterly checks.

```text
fit isotonic and Platt on validation and freeze both maps
score test quarters and record Brier and reliability
rank TreeSHAP on the seeded sample
```

Overall test Brier was 0.06409 raw, 0.01636 isotonic and 0.01549 Platt. The SHAP ranking is `userLiquidationCount`, `userDepositAvgAmountUSD`, `cosDayOfQuarter`, `userBorrowCount`, `userDepositAvgAmountETH`, `priceInUSD`, `userActiveDaysYearly`, `userActiveDaysWeekly`, `dayOfMonth`, `userBorrowAvgAmountETH`.

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

Table 7. FinSurvival test Brier by quarter.

#### Step 5 · Assign risk tiers

**Purpose** Convert scores to A/B/C. **Input** Calibrated score parquet, outcomes and frozen XGB artifact. **Processing** Fit D1 and percentile rules on validation. Apply feasible rules to test. Aggregate wallet maximum. **Parameters** Validation grid step 0.005. A ≤0.75× prevalence, C ≥2× prevalence, ≥30 positives and ≤20% validation share. Relax the C rate to 1.5× only if the strict grid has no feasible pair. Require all tiers. Compare p70/p90.

**Libraries / tools** pandas, NumPy, hashlib. **Output** Wallet tiers and model SHA-256/version. The pilot exports fixed tiers.csv and reports the percentile comparator. **Runs** 2026-11-20, seed 11.

**Correctness check** Verify cutoff order, hash and partition totals. **Errors & edge cases** The wallet cohort proxy takes the maximum score across a wallet’s observed loans in each cohort because historical open-loan membership is unavailable. **Est. run time** 0.36 s measured for cutoff search, test summaries and export. **Improvement** I1 adds fixed-risk tier rules.

**Procedure** search ordered validation grid for the maximum C/A rate ratio → calculate comparison quantiles on validation → freeze feasible rules and score test cohorts → take wallet maximum across available input loans → compute shares, outcome rates and Wilson intervals → hash model artifact and export wallet tiers.

Validation prevalence was 4.33%. Ordered cutoffs 0.005 and 0.065 met the strict rule. On validation, C was 16.21% of loans with 541 positives and a 17.28% liquidation rate. The search maximizes C/A, treating zero A rate as infinite. Ties favor combined tail coverage, then smaller cutoffs. Percentile cutoffs were 0.020427 and 0.106122.

| Test cohort | Rule | Tier A | Tier B | Tier C |
| --- | --- | --- | --- | --- |
| overall | Fixed | 4.58% / 0.02% [0.00%, 0.13%] | 77.73% / 0.72% [0.67%, 0.79%] | 17.70% / 4.23% [3.94%, 4.55%] |
| overall | Percentile | 64.45% / 0.45% [0.40%, 0.51%] | 19.93% / 1.58% [1.41%, 1.76%] | 15.62% / 4.54% [4.22%, 4.88%] |
| 2022Q3 | Fixed | 2.52% / 0.00% [0.00%, 0.58%] | 82.42% / 0.67% [0.57%, 0.79%] | 15.06% / 6.14% [5.43%, 6.94%] |
| 2022Q3 | Percentile | 68.37% / 0.45% [0.36%, 0.55%] | 18.19% / 1.59% [1.27%, 1.99%] | 13.43% / 6.60% [5.82%, 7.47%] |
| 2022Q4 | Fixed | 3.70% / 0.11% [0.02%, 0.64%] | 77.29% / 1.56% [1.39%, 1.75%] | 19.01% / 3.80% [3.28%, 4.40%] |
| 2022Q4 | Percentile | 63.25% / 0.89% [0.75%, 1.05%] | 19.88% / 3.64% [3.14%, 4.21%] | 16.87% / 3.84% [3.29%, 4.48%] |
| 2023Q1 | Fixed | 6.10% / 0.00% [0.00%, 0.35%] | 75.63% / 0.26% [0.19%, 0.36%] | 18.27% / 1.56% [1.19%, 2.04%] |
| 2023Q1 | Percentile | 63.58% / 0.24% [0.16%, 0.34%] | 20.38% / 0.25% [0.13%, 0.47%] | 16.03% / 1.74% [1.32%, 2.29%] |
| 2023Q2 | Fixed | 6.48% / 0.00% [0.00%, 0.63%] | 77.25% / 0.35% [0.24%, 0.51%] | 16.27% / 3.51% [2.69%, 4.56%] |
| 2023Q2 | Percentile | 65.44% / 0.28% [0.17%, 0.45%] | 20.24% / 0.69% [0.40%, 1.18%] | 14.31% / 3.61% [2.73%, 4.75%] |
| 2023Q3 | Fixed | 8.56% / 0.00% [0.00%, 0.70%] | 72.43% / 0.28% [0.17%, 0.48%] | 19.01% / 4.72% [3.66%, 6.06%] |
| 2023Q3 | Percentile | 65.74% / 0.12% [0.05%, 0.28%] | 18.04% / 0.70% [0.35%, 1.37%] | 16.23% / 5.53% [4.29%, 7.10%] |
| 2023Q4 | Fixed | 6.77% / 0.00% [0.00%, 0.83%] | 76.78% / 0.21% [0.12%, 0.38%] | 16.45% / 1.61% [1.02%, 2.53%] |
| 2023Q4 | Percentile | 60.85% / 0.07% [0.02%, 0.21%] | 24.69% / 0.48% [0.24%, 0.94%] | 14.45% / 1.83% [1.16%, 2.87%] |
| 2024Q1 | Fixed | 2.66% / 0.00% [0.00%, 2.81%] | 71.15% / 0.39% [0.23%, 0.66%] | 26.19% / 7.48% [6.17%, 9.03%] |
| 2024Q1 | Percentile | 54.65% / 0.33% [0.17%, 0.62%] | 22.04% / 0.73% [0.37%, 1.42%] | 23.32% / 8.14% [6.71%, 9.85%] |
| 2024Q2 | Fixed | 3.61% / 0.00% [0.00%, 7.87%] | 80.51% / 1.29% [0.76%, 2.20%] | 15.88% / 16.67% [12.12%, 22.48%] |
| 2024Q2 | Percentile | 62.95% / 0.64% [0.27%, 1.48%] | 23.50% / 3.41% [1.86%, 6.17%] | 13.55% / 18.34% [13.23%, 24.86%] |
| 2024Q3 | Fixed | — | — | — |
| 2024Q3 | Percentile | — | — | — |

Table 8. Held-out loan tier share / liquidation rate [95% Wilson interval]. The JSON includes Wilson intervals for shares and results for the wallet cohort proxy. 2024Q3 has no test loans.

| Policy | Accepted | Liquidations avoided | Good loans rejected | Collateral locked (USD) |
| --- | ---: | ---: | ---: | ---: |
| uniform | 96,345 | 0 | 0 | 44,218,089,861.50 |
| tiered | 79,296 | 722 | 16,327 | 49,281,618,994.69 |

Table 9. Uniform and fixed-tier D3a on the same loans. USD totals use 95,596 loans with valid origination USD.

The cap reduced good-loan rejections from 33,267 to 16,327. Labelled liquidations avoided fell from 986 to 722. For every avoided liquidation, the capped policy rejected about 22.6 good loans, compared with 33.7 before the cap.

#### Step 6 · Register model and write scores

**Purpose** Attach tiers to a registered model. **Input** Wallet tiers, model SHA-256 and version. **Processing** Register digest as owner. Write tiers as approved signer. Reconcile receipts. **Parameters** Tiers 1–3, batch ≤100, age ≤30 days.

**Libraries / tools** Vyper, Ape, Anvil and planned oracle keystore. **Output** Registered digest, version, effective tier lookup and ScoreUpdated receipts. **Runs** 2026-11-19. Ten batches each for 1, 10 and 100 synthetic wallets.

**Correctness check** Check version, hash, reads and guard messages. **Errors & edge cases** Missing/stale tiers fall back to B. Check receipt before retry. **Est. run time** Expected seconds = (1 registration + batches) × seconds per receipt, plus upload and reconciliation. Use the Sepolia median planning range in Section 2.5 for serial receipts. **Improvement** I3 stores tier and model identifiers.

**Procedure** verify digest and proposed model version → register with owner on the selected local network → validate wallet and tier inputs → submit each approved writer batch → reconcile receipts and effective tier lookups.

#### Step 7 · Execute the lending policy

**Purpose** Enforce collateral policy. **Input** Effective tier lookup, collateral balance, debt request and scaled oracle price. **Processing** Check debt limits, freeze original tier and evaluate health at current price. **Parameters** A 120%/110%, B 150%/130%, C ineligible. Uniform 125%/121.2%. Close 50%, bonus 5%.

**Libraries / tools** Vyper, Ape, Anvil, MockERC20, Hypothesis. **Output** Position balances and loan receipts, such as Liquidated(wallet, liquidator, repaid, seized). **Runs** T3/T4 plus 200 generated boundary cases.

**Correctness check** Match balances, snapshots and guard messages. **Errors & edge cases** Reject unsafe amounts and transitions. Bad-debt settlement planned. **Est. run time** Expected seconds = serial transactions × seconds per receipt, plus scenario setup. Measure local and Sepolia receipts separately. **Improvement** I3 enforces policy on-chain.

**Procedure** read effective tier and scaled collateral value → apply origination collateral requirement → store tier at first borrow → check current health using stored tier at liquidation → apply close factor and bonus → reconcile balances and emit the position event.

#### Step 8 · Demonstrate and evaluate

**Purpose** Verify end-to-end evidence. **Input** Position balances, loan receipts, score receipts and committed pilot metrics. **Processing** Reconcile export, hash and receipts. Show local price change and liquidation in Streamlit. **Parameters** Seed 11 model. Fresh local deployment per run.

**Libraries / tools** Ape, Anvil, pytest, Streamlit. **Output** Scenario evidence package. Example: local gas JSON plus deployment and dashboard logs for T6. **Runs** Local pilots measured. Three full runs planned, not yet run.

**Correctness check** Match counts, digest, price, health and events. **Errors & edge cases** Keep synthetic and percentile inputs labelled. **Est. run time** Expected seconds = deployment + score upload + loan and price receipts + dashboard checks. Sum these durations across fresh runs. **Improvement** I3 links model outputs to contract evidence.

**Procedure** start a fresh local deployment → compare model version, digest and wallet counts → apply the planned local price change → reconcile dashboard values against loan receipts → attach metrics and logs to the scenario run.
