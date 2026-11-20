# B. CONTENT

## 1. Detailed Method

### 1.1. Updated workflow diagram

![Eight-step project workflow](figures/workflow.png){width=93%}

Figure 1. Frozen scores cross the on-chain boundary as wallet tiers and model identifiers. Raw features, probabilities and Shapley additive explanations (SHAP) stay off-chain.

| Improvement | Week 4 workflow change | Validation evidence |
| --- | --- | --- |
| I1 | Fit a probability map on validation, explain the fitted model and evaluate risk tier rules | Held-out Brier, SHAP ranking and quarterly tier results |
| I2 | Compare all-feature principal component analysis (PCA) and drift-filtered models on D5 | Paired AUC and validation-to-test gaps |
| I3 | Keep tier and model identifiers on-chain and enforce collateral by tier | Contract checks, gas receipts and planned integration |
| I4 | Evaluate the model pipeline on Taiwan credit defaults | Seed-11 held-out pilot ROC AUC and planned seed spread |

Table 2. Changes linked to the eight-step workflow.
