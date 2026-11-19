## 1.2 Procedure

### Step 1 · Data collection

| Field | Specification |
| --- | --- |
| Purpose | Load standardized loan and credit records. |
| Input | RDS features and liquidation labels [1]. UCI 350 [5]. |
| Processing | Concatenate X parts. Drop empty/exo columns. Inner join y by ID. Align schemas. |
| Parameters | Borrow → Account Liquidated. UCI dataset 350. |
| Libraries / tools | pandas, pyreadr, pyarrow, ucimlrepo. |
| Output | Interim parquet. Example: finsurvival_train.parquet and taiwan.parquet. |
| Runs | One load, 2026-11-19. |
| Correctness check | Check IDs, source row counts and schema. |
| Errors & edge cases | Missing parts stop loading. Record unmatched and duplicate IDs. |
| Est. run time | 26.4 s pilot including UCI and writes. |
| Improvement | I4 adds Taiwan. |

```text
concat FinSurvival X parts by benchmark split
drop all-null and exogenous columns
join X and y by loan id
align train and test feature columns
fetch UCI 350 and write interim parquet and schema counts
```

All 259,886 local labels matched features, yielding 269,546 joined rows after repeat matches. The source has 4,650 fewer test labels than Week 3, which reported those labels as unmatched.

| Source split | Raw features | All-null removed | Exogenous removed | Non-shared removed |
| --- | ---: | ---: | ---: | ---: |
| train | 128 | 12 | 0 | 0 |
| test | 128 | 12 | 0 | 0 |

Table 3. FinSurvival feature counts before and after loader checks.

After loader checks, 116 features remain. Taiwan loaded 30,000 clients, 23 features and 22.12% defaults.

### Step 2 · Labelling and feature preparation

| Field | Specification |
| --- | --- |
| Purpose | Prepare leak-resistant inputs. |
| Input | Interim parquet and D5 calendar. |
| Processing | Deduplicate transactions, label, purge and encode. Record KS drops for O variants. |
| Parameters | 17.43 days, D5 windows, D ≥ 0.15, Taiwan seed 11. |
| Libraries / tools | pandas, SciPy, scikit-learn, pyarrow. |
| Output | Split parquet (example: fin_train_core.parquet) and feature-rule manifest. |
| Runs | One split per dataset, 2026-11-19. |
| Correctness check | Test date boundaries, ID disjointness and train-only vocabularies. |
| Errors & edge cases | Keep observed early liquidations. Drop insufficient follow-up. |
| Est. run time | 9.7 s pilot including writes. |
| Improvement | I2 freezes chronological feature preparation. |

```text
drop repeated IDs
label observed events within 17.43 days as positive
label later observations as negative and discard short censored records
split by UTC start date and purge D5 gaps
fit categories on train_core
compare train_core and inner-val with KS
transform all folds with frozen rules
```

D5 replaces the Week 3 moving cutoff with two purged gaps. Inner-val ends 2022-03-14, calibration val ends 2022-06-30 and test starts 2022-07-01. The actual test ends 2024-05-07. Taiwan drops SEX and MARRIAGE before stratified splitting.

| FinSurvival split | Rows | Positive rate | Observed UTC dates |
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

Example loan: 2020-12-01, event status 0, observed 576.465 days, label 0.

### Step 3 · Train baseline and proposed models

| Field | Specification |
| --- | --- |
| Purpose | Compare baseline and proposed models. |
| Input | Split parquet and feature-rule manifest. |
| Processing | Fit LR or XGB. Scale as needed. Fit baseline PCA in training. Early-stop XGB on inner-val. |
| Parameters | 95% PCA assumption, LR C=0.1, XGB learning rate 0.05, depth 6, patience 50. |
| Libraries / tools | scikit-learn, XGBoost. |
| Output | Frozen XGB artifact (example: O_XGB_11.ubj), validation and test score parquet, AUC and fit time. |
| Runs | 2026-11-19. XGB seeds 11/22/33. LR seed 11 and 1,000 bootstrap draws. |
| Correctness check | Check model/seed coverage and paired test AUC. |
| Errors & edge cases | Replace nonfinite features with zero. Paper reproduction tolerance ±0.02 AUC. |
| Est. run time | Measured mean fit times below. |
| Improvement | I2 isolates the proposed feature pipeline. I4 checks Taiwan. |

```text
fit scaling and PCA for baseline using train_core
fit LR on train_core
early-stop XGB on inner-val
score frozen models on evaluation folds
compare paired XGB seeds and bootstrap LR test AUC
```

| Model | Seeds | Mean inner-val AUC | Mean val AUC | Mean test AUC | Mean fit (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| B_XGB | 11, 22, 33 | 0.7885 | 0.6870 | 0.7020 | 3.61 |
| O_XGB | 11, 22, 33 | 0.8089 | 0.8113 | 0.8033 | 3.10 |
| B_LR | 11 | 0.7931 | 0.7519 | 0.6145 | 2.45 |
| O_LR | 11 | 0.8053 | 0.7974 | 0.7861 | 3.92 |

Table 6. FinSurvival pilot fits on 2026-11-19.

Paper deviations were −0.1085 (LR) and −0.0300 (XGB), both outside ±0.02 [1]. Taiwan test AUC was 0.7834 at seed 11. Section 2.4 summarizes paired precision.

### Step 4 · Calibrate and explain probabilities

| Field | Specification |
| --- | --- |
| Purpose | Calibrate risk and explain model output. |
| Input | Frozen XGB artifact and validation/test score parquet. |
| Processing | Fit isotonic on val. Compare raw and frozen mapped scores on test. Rank TreeSHAP. |
| Parameters | Ten reliability bins, 2,000 test loans, seed 11. |
| Libraries / tools | scikit-learn, XGBoost TreeSHAP, pandas. |
| Output | Calibrated score parquet (example: calibrated_test.parquet), Brier, reliability bins and SHAP top ten. |
| Runs | 2026-11-19, seed 11. Multi-seed H2 planned, not yet run. |
| Correctness check | Verify matching pools and validation-only fit. |
| Errors & edge cases | Empty quarters have undefined Brier. TreeSHAP describes raw output. |
| Est. run time | 2.1 s pilot. |
| Improvement | I1 and D4 add calibration, interpretation and quarterly checks. |

```text
fit isotonic(raw_val, label_val)
apply frozen mapping to validation and test scores
compare raw and calibrated Brier by quarter
sample 2,000 test loans at seed 11
rank mean absolute TreeSHAP contributions
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

Table 7. FinSurvival test Brier by quarter.

### Step 5 · Assign risk tiers

| Field | Specification |
| --- | --- |
| Purpose | Convert scores to A/B/C. |
| Input | Calibrated score parquet, outcomes and frozen XGB artifact. |
| Processing | Fit D1 and percentile rules on validation. Apply feasible rules to test. Aggregate wallet maximum. |
| Parameters | A tail ≤0.5× prevalence. C tail ≥3× and ≥30 positives. Compare p70/p90. |
| Libraries / tools | pandas, NumPy, hashlib. |
| Output | Wallet tiers and model SHA-256/version. The pilot emits tiers_percentile.csv as a labelled comparator. |
| Runs | 2026-11-19, seed 11. |
| Correctness check | Verify cutoff order, hash and partition totals. |
| Errors & edge cases | Pilot uses cohort wallets because open-loan status is unavailable. |
| Est. run time | Measure export latency during integration. |
| Improvement | I1 adds fixed-risk tier rules. |

```text
calculate D1 extrema and comparison quantiles on validation
check fixed cutoffs are ordered
freeze feasible rules and score test cohorts
take wallet maximum across available input loans
compute shares, outcome rates and Wilson intervals
hash model artifact and export wallet tiers
```

Validation prevalence was 4.33%. D1 extrema τ_A = 0.106122 and τ_C = 0.043348 overlap. Fixed tiers are planned, not yet run. Percentile cutoffs were 0.020427 and 0.106122. The pilot covered 96,345 loans in 21,641 wallet groups.

| Rule | Tier | Test loans | Share | Liquidation rate | 95% Wilson CI |
| --- | --- | ---: | ---: | ---: | --- |
| percentile | A | 62,092 | 64.45% | 0.45% | 0.40%–0.51% |
| percentile | B | 19,203 | 19.93% | 1.58% | 1.41%–1.76% |
| percentile | C | 15,050 | 15.62% | 4.54% | 4.22%–4.88% |

Table 8. Percentile tiers on the held-out loan cohort.

D3a percentile sensitivity used origination scores on 2026-11-19. Rejected loans that later liquidated count as the avoidance proxy. Capital uses 95,596 positively priced loans. Uniform minus tiered capital is USD 1,941,823,554.74, including USD 1,665,763,650.49 for tier A. Fixed D3a and price shocks are planned, not yet run.

| Policy | Accepted | Rejected | Liquidations avoided | Good loans rejected | Capital locked (USD) |
| --- | ---: | ---: | ---: | ---: | ---: |
| uniform | 96,345 | 0 | 0 | 0 | 44,218,089,861.50 |
| tiered | 81,295 | 15,050 | 683 | 14,367 | 42,276,266,306.76 |

Table 9. D3a percentile sensitivity and uniform policy on the same test loans.

### Step 6 · Register model and write scores

| Field | Specification |
| --- | --- |
| Purpose | Attach tiers to a registered model. |
| Input | Wallet tiers, model SHA-256 and version. Fixed-rule export remains blocked. |
| Processing | Register digest as owner. Write tiers as approved signer. Reconcile receipts. |
| Parameters | Tiers 1–3, batch ≤100, age ≤30 days. |
| Libraries / tools | Vyper, Ape, Anvil and planned oracle keystore. |
| Output | Registered digest, version, effective tier lookup and ScoreUpdated receipts. |
| Runs | 2026-11-19. Ten batches each for 1, 10 and 100 synthetic wallets. |
| Correctness check | Check version, hash, reads and guard messages. |
| Errors & edge cases | Missing/stale tiers fall back to B. Check receipt before retry. |
| Est. run time | Sepolia timing planned, not yet run. |
| Improvement | I3 stores tier and model identifiers. |

```text
verify digest and proposed model version
register with owner on the selected local network
validate wallet and tier inputs
submit each approved writer batch
reconcile receipts and effective tier lookups
```

### Step 7 · Execute the lending policy

| Field | Specification |
| --- | --- |
| Purpose | Enforce collateral policy. |
| Input | Effective tier lookup, collateral balance, debt request and scaled oracle price. |
| Processing | Check debt limits, freeze original tier and evaluate health at current price. |
| Parameters | A 120%/110%, B 150%/130%, C ineligible. Uniform 125%/121.2%. Close 50%, bonus 5%. |
| Libraries / tools | Vyper, Ape, Anvil, MockERC20, Hypothesis. |
| Output | Position balances and loan receipts, such as Liquidated(wallet, liquidator, repaid, seized). |
| Runs | T3/T4 plus 200 generated boundary cases. |
| Correctness check | Match balances, snapshots and guard messages. |
| Errors & edge cases | Reject unsafe amounts and transitions. Bad-debt settlement planned. |
| Est. run time | Record local gas and future Sepolia latency separately. |
| Improvement | I3 enforces policy on-chain. |

```text
read effective tier and scaled collateral value
apply origination collateral requirement
store tier at first borrow
check current health using stored tier at liquidation
apply close factor and bonus
reconcile balances and emit the position event
```

### Step 8 · Demonstrate and evaluate

| Field | Specification |
| --- | --- |
| Purpose | Verify end-to-end evidence. |
| Input | Position balances, loan receipts, score receipts and committed pilot metrics. |
| Processing | Reconcile export, hash and receipts. Show local price change and liquidation in Streamlit. |
| Parameters | Seed 11 model. Fresh local deployment per run. |
| Libraries / tools | Ape, Anvil, pytest, Streamlit. |
| Output | Scenario evidence package. Example: local gas JSON plus deployment and dashboard logs for T6. |
| Runs | Local pilots measured. Three full runs planned, not yet run. |
| Correctness check | Match counts, digest, price, health and events. |
| Errors & edge cases | Keep synthetic and percentile inputs labelled. Fixed export unavailable. |
| Est. run time | Log wall time and future testnet median/p95. |
| Improvement | I3 links model outputs to contract evidence. |

```text
start a fresh local deployment
compare model version, digest and wallet counts
apply the planned local price change
reconcile dashboard values against loan receipts
attach metrics and logs to the scenario run
```
