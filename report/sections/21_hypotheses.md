## 2. Test Plan

### 2.1. Research questions and hypotheses

| ID | Hypothesis | Primary metric | Acceptance criterion |
| --- | --- | --- | --- |
| H1 · I2, D6 | Drift-filtered XGBoost is non-inferior to all-feature PCA. | Test ΔAUC = proposed − baseline, paired by seed. | Accept if lower 95% bound > −0.02. Report validation-to-test AUC gaps as secondary. |
| H2 · I1 | Isotonic improves test probabilities. | Test ΔBrier = calibrated − raw, paired by seed. | Accept if upper 95% bound < 0. |
| H3 · I1, D1 | Fixed tiers separate risk and C share falls with prevalence. | Tier rates, 95% Wilson intervals, quarterly C share and prevalence. | Accept if A < B < C with disjoint adjacent intervals. Check that C share falls when prevalence falls. Compare the percentile rule's expected ~10% C share and report ties. Use the ordered validation grid with A ≤0.75× and C ≥2× validation prevalence. |
| H4 · I3, D3 | Tiering reduces liquidation losses while conserving collateral. | Accepted loans, avoided liquidations, rejected good loans and collateral locked. Under shocks, liquidated loans, seized collateral and bad debt. | See the H4 decision rule below. |
| H5 · I3 | Score writes meet gas limits and guards hold. | Single receipt gas, 100-wallet batch gas per wallet and exact T4 messages. | Accept if single ≤100,000. Every size-100 batch ≤75,000 per wallet. Every planned guard returns its message. Document identity and key exposure. |
| H6 · I4 | The proposed XGBoost transfers to Taiwan credit prediction. | Held-out ROC AUC. | Accept within expected 0.760–0.810 on the fixed protocol. Compare with the chart range of 0.68–0.71 [3]. Independent confirmation is planned, not yet run. |
| H7 · D4 | Calibration overpredicts as test prevalence falls. | Quarterly gap = mean calibrated score − observed rate, plus Brier and reliability. | Accept if the last populated quarter has lower prevalence and a positive gap larger than in the first populated quarter. Report intermediate quarters and empty cohorts. |

Table 15. Primary measures and decision rules for H1–H7.

| Expected | Basis | Reject if | If rejected |
| --- | --- | --- | --- |
| Tiering avoids more historically liquidating loans, lowers tier-A collateral per dollar of debt, and holds total collateral and simulated bad debt at or below uniform. | Tier A requires 120% versus 125% uniform. D3a uses observed labels. D3b uses paired simulated shocks. | Reject if tiering fails to avoid more labelled liquidations or to lower tier-A collateral per debt dollar, raises total locked collateral, or raises bad debt at any specified shock. | Report the acceptance and good-loan rejection trade-off and the shock results separately. The pilot fails the total collateral and −20% bad debt conditions. |

Table 16. H4 decision rule.

The seed-11 fixed pilot has disjoint overall tier intervals. Test 2024Q3 is empty.

H5 uses the 2026-11-19 Anvil pilot. Take the greater of estimate and measurement, add a 5% allowance and round up to 5,000 gas. The single calculation uses 94,739 versus 93,000. The batch calculation uses 69,252 versus 69,034 gas per wallet. See `results/pilot_gas.json`.

H6 uses the seed-11 pilot of 0.7834 from `results/pilot_taiwan.json`. The planning range adds and subtracts 0.025 AUC and rounds each endpoint to the nearest 0.005.
