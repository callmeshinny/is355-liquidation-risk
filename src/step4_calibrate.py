"""Fit isotonic on validation and evaluate seed-11 O_XGB on the held-out test set."""

import argparse
import json
from datetime import date
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from scipy.special import logit
from xgboost import DMatrix, XGBClassifier

from step3_train import INTERIM, MODELS, feature_names

RESULT = Path("results/pilot_calib.json")
QUARTERS = pd.period_range("2022Q3", "2024Q3", freq="Q")


def scored_split(split, seed):
    frame = pd.read_parquet(INTERIM / f"fin_{split}.parquet")
    scores = pd.read_parquet(INTERIM / f"o_xgb_{seed}_{split}_scores.parquet")
    return frame.merge(scores, on="id", validate="one_to_one")


def brier(frame):
    n = len(frame)
    return dict(n=n,
                brier_uncal=float(brier_score_loss(frame.label, frame.p_raw)) if n else None,
                brier_cal=float(brier_score_loss(frame.label, frame.p)) if n else None,
                brier_platt=float(brier_score_loss(frame.label, frame.p_platt)) if n else None)


def raw_margins(frame):
    eps = np.finfo(np.float32).eps
    return logit(np.clip(frame.p_raw.to_numpy(), eps, 1 - eps)).reshape(-1, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", default=11, type=int)
    args = parser.parse_args()
    started = perf_counter()
    val, test = (scored_split(s, args.seed) for s in ("val", "test"))
    calibrator = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(val.p_raw, val.label)
    platt = LogisticRegression(C=np.inf).fit(raw_margins(val), val.label)
    for split, frame in (("val", val), ("test", test)):
        frame["p"] = calibrator.predict(frame.p_raw)
        frame["p_platt"] = platt.predict_proba(raw_margins(frame))[:, 1]
        columns = ["id", "label", "timestamp", "user", "p_raw", "p"]
        if "amountUSD" in frame:
            columns.append("amountUSD")
        frame[columns].to_parquet(INTERIM / f"calibrated_{split}.parquet", index=False)
    test["quarter"] = test.timestamp.dt.tz_localize(None).dt.to_period("Q")
    reliability = []
    cohorts = [("overall", test), *((str(q), test.loc[test.quarter.eq(q)]) for q in QUARTERS)]
    for cohort, frame in cohorts:
        for name, col in (("raw", "p_raw"), ("isotonic", "p"), ("platt", "p_platt")):
            bins = pd.cut(frame[col], np.linspace(0, 1, 11), include_lowest=True)
            for interval, group in frame.groupby(bins, observed=False):
                reliability.append(dict(cohort=cohort, score=name, bin=str(interval), n=len(group),
                                        mean_probability=group[col].mean(), observed_rate=group.label.mean()))
    pd.DataFrame(reliability).to_csv("results/pilot_reliability.csv", index=False)
    model = XGBClassifier()
    model.load_model(MODELS / f"O_XGB_{args.seed}.ubj")
    booster = model.get_booster()[:model.best_iteration + 1]
    sample = test.sample(n=2000, random_state=args.seed)
    cols = feature_names(pd.read_parquet(INTERIM / "fin_train_core.parquet").columns, "O")
    matrix = sample[cols].replace([np.inf, -np.inf], 0)
    import shap

    method = "shap.TreeExplainer"
    try:
        values = shap.TreeExplainer(booster).shap_values(matrix)
    except ValueError as error:
        # SHAP 0.49 reads the XGBoost 3.2 vector intercept as a scalar.
        if "could not convert string to float: '[" not in str(error):
            raise
        dm = DMatrix(matrix.to_numpy())
        contributions = booster.predict(dm, pred_contribs=True)
        np.testing.assert_allclose(contributions.sum(axis=1), booster.predict(dm, output_margin=True),
                                   rtol=1e-5, atol=1e-5)
        values = contributions[:, :-1]
        method = "XGBoost native TreeSHAP (vector intercept compatibility)"
    ranking = pd.Series(np.abs(values).mean(axis=0), index=cols).nlargest(10)
    report = dict(date=date.today().isoformat(), seed=args.seed, model="O_XGB",
                  fit_split="val", platt_method="Unpenalized logistic regression on clipped raw logits", **brier(test),
                  per_quarter=[dict(quarter=name, **brier(frame)) for name, frame in cohorts[1:]],
                  shap_rows=len(sample), shap_method=method, shap_top10=ranking.to_dict(),
                  elapsed_seconds=round(perf_counter() - started, 3))
    RESULT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(brier(test), "SHAP rows:", len(sample))


if __name__ == "__main__":
    main()
