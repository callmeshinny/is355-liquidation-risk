"""Audit D5 baseline preprocessing and origination availability on validation."""
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from xgboost import DMatrix, XGBClassifier

from step2_prepare import label_loans, split_loans
from step3_train import INTERIM, MODELS, RESULT, feature_names
from step4_calibrate import scored_split

SEED = 11
DEFINITIONS = {
    "userBorrowCount": "Number of prior borrows",
    "userLiquidationCount": "Number of prior liquidations",
    "cosDayOfQuarter": "Cosine of the origination day within its quarter",
    "userBorrowSumUSD": "Prior borrow amounts summed in USD",
    "userDepositAvgAmountUSD": "Mean prior deposit amount in USD",
    "priceInUSD": "Reserve price in USD at origination",
    "userActiveDaysYearly": "Active days in the trailing 365 days",
    "userActiveDaysWeekly": "Active days in the trailing seven days",
    "userDepositAvgAmountETH": "Mean prior deposit amount in ETH",
    "dayOfMonth": "Day of month at origination",
    "userLiquidationSumETH": "Prior liquidation amounts summed in ETH",
    "userLiquidationSumUSD": "Prior liquidation amounts summed in USD",
    "userBorrowSum": "Amount of this coin summed over prior borrows",
    "amount": "Amount borrowed at origination",
    "userBorrowAvgAmountETH": "Mean prior borrow amount in ETH",
}


def main():
    source = pd.concat([pd.read_parquet(INTERIM / f"finsurvival_{s}.parquet")
                        for s in ("train", "test")], ignore_index=True)
    splits = split_loans(label_loans(source.loc[~source.id.duplicated(keep=False)]))
    train = pd.read_parquet(INTERIM / "fin_train_core.parquet")
    columns = feature_names(train.columns, "B")
    nonfinite = {}
    for split, source_frame in splits.items():
        encoded = pd.read_parquet(INTERIM / f"fin_{split}.parquet")[columns]
        nonfinite[split] = {
            "n": len(encoded),
            "encoded_nonfinite_share": (~np.isfinite(encoded)).mean().to_dict(),
            "source_numeric_nonfinite_share": {
                col: float((~np.isfinite(source_frame[col])).mean())
                for col in columns if col in source_frame
            },
        }

    xgb_input = train[columns].replace([np.inf, -np.inf], 0).to_numpy()
    for values in (xgb_input, np.sign(xgb_input) * np.log1p(np.abs(xgb_input))):
        standardized = StandardScaler().fit_transform(values)
        sd = standardized.std(axis=0)
        np.testing.assert_allclose(standardized.mean(axis=0), 0, atol=1e-7)
        np.testing.assert_allclose(sd[sd > 1e-7], 1, atol=1e-7)

    sample = scored_split("val", SEED).sample(n=2000, random_state=SEED)
    features = feature_names(train.columns, "O")
    model = XGBClassifier()
    model.load_model(MODELS / f"O_XGB_{SEED}.ubj")
    booster = model.get_booster()[:model.best_iteration + 1]
    matrix = DMatrix(sample[features].replace([np.inf, -np.inf], 0).to_numpy())
    contributions = booster.predict(matrix, pred_contribs=True)
    np.testing.assert_allclose(contributions.sum(axis=1), booster.predict(matrix, output_margin=True),
                               rtol=1e-5, atol=1e-5)
    ranking = pd.Series(np.abs(contributions[:, :-1]).mean(axis=0), index=features).nlargest(15)
    audit = [dict(feature=feature, mean_abs_shap=float(value), known_at_loan_start=True,
                  definition=DEFINITIONS[feature]) for feature, value in ranking.items()]
    fits = json.loads(RESULT.read_text())
    report = dict(date=date.today().isoformat(), split="D5", baseline_no_pca=fits["B_XGB_noPCA"],
                  test_auc={name: float(np.mean([v["auc"]["test"] for v in runs.values()]))
                            for name, runs in fits.items()},
                  pca=dict(fit_split="train_core", standardized=True, variance_retained=0.95,
                           handling="Numeric NaN filled with zero at encoding. Infinities replaced "
                                    "with zero before model preprocessing. Missing categorical "
                                    "values use the other indicator. LR applies signed log1p before scaling.",
                           per_split=nonfinite),
                  shap=dict(model="O_XGB", seed=SEED, split="val", rows=len(sample),
                            method="Native TreeSHAP, raw margin", top15=audit, leakage_features=[],
                            sources=["legacy/make_dataset_figures.py identifies past liquidations and borrows",
                                     "dataLoader.R loads precomputed X and joins outcomes by id",
                                     "FinSurvival Appendix B.4 and Tables 10, 12 and 14 define origins and history windows"]))
    Path("results/pilot_audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["test_auc"])


if __name__ == "__main__":
    main()
