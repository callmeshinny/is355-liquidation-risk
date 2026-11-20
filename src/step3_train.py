"""Run one fixed-parameter FinSurvival model and record its pilot metrics."""

import argparse
import json
from datetime import date
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from step2_prepare import INTERIM, NON_FEATURES

RESULT = Path("results/pilot_model.json")
MODELS = Path("models")
SPLITS = ("train_core", "inner_val", "val", "test")
XGB_PARAMS = dict(n_estimators=1000, learning_rate=0.05, max_depth=6,
                  min_child_weight=5, subsample=0.8, colsample_bytree=0.8,
                  eval_metric="auc", early_stopping_rounds=50, n_jobs=4)


def xgb(seed, y):
    weight = int((y == 0).sum()) / int((y == 1).sum())
    return XGBClassifier(**XGB_PARAMS, scale_pos_weight=weight, random_state=seed)


def bootstrap_auc(y, p, seed, runs=1000):
    rng = np.random.default_rng(seed)
    positive = np.flatnonzero(y == 1)
    negative = np.flatnonzero(y == 0)
    labels = y[np.r_[positive, negative]]
    estimates = [
        roc_auc_score(labels, p[np.r_[rng.choice(positive, len(positive)),
                                      rng.choice(negative, len(negative))]])
        for _ in range(runs)
    ]
    return dict(runs=runs, sd=float(np.std(estimates, ddof=1)),
                ci95=np.quantile(estimates, [0.025, 0.975]).tolist())


def feature_names(columns, branch):
    drift = json.loads(Path("results/pilot_data.json").read_text())["dropped_drift"]
    excluded = NON_FEATURES | (set(drift) if branch == "O" else set())
    return [name for name in columns if name not in excluded]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=["B_LR", "B_XGB", "O_LR", "O_XGB", "B_XGB_noPCA"])
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()
    branch, algorithm = args.model.split("_")[:2]
    frames = {s: pd.read_parquet(INTERIM / f"fin_{s}.parquet") for s in SPLITS}
    cols = feature_names(frames["train_core"].columns, branch)
    x = {s: frames[s][cols].replace([np.inf, -np.inf], 0).to_numpy() for s in SPLITS}
    y = {s: frames[s].label.to_numpy() for s in SPLITS}
    started = perf_counter()
    if algorithm == "LR":
        x = {s: np.sign(a) * np.log1p(np.abs(a)) for s, a in x.items()}
    use_pca = branch == "B" and args.model != "B_XGB_noPCA"
    if use_pca or algorithm == "LR":
        scaler = StandardScaler().fit(x["train_core"])
        x = {s: scaler.transform(a) for s, a in x.items()}
    if use_pca:
        pca = PCA(n_components=0.95, svd_solver="full").fit(x["train_core"])
        x = {s: pca.transform(a) for s, a in x.items()}
    if algorithm == "LR":
        model = LogisticRegression(C=0.1, class_weight="balanced", max_iter=2000)
        model.fit(x["train_core"], y["train_core"])
    else:
        model = xgb(args.seed, y["train_core"])
        model.fit(x["train_core"], y["train_core"], eval_set=[(x["inner_val"], y["inner_val"])],
                  verbose=False)
    elapsed = perf_counter() - started
    scores = {s: model.predict_proba(x[s])[:, 1] for s in SPLITS[1:]}
    run = dict(date=date.today().isoformat(), seed=args.seed,
               n_features_in=len(cols), n_features_model=x["train_core"].shape[1],
               fit_seconds=round(elapsed, 3),
               auc={s: float(roc_auc_score(y[s], p)) for s, p in scores.items()},
               config=({"C": 0.1, "class_weight": "balanced", "max_iter": 2000}
                       if algorithm == "LR" else {**XGB_PARAMS, "scale_pos_weight": model.scale_pos_weight}))
    if algorithm == "LR":
        run["test_bootstrap"] = bootstrap_auc(y["test"], scores["test"], args.seed)
    else:
        run["best_iteration"] = model.best_iteration
    if args.model == "O_XGB":
        MODELS.mkdir(exist_ok=True)
        model.save_model(MODELS / f"O_XGB_{args.seed}.ubj")
        for split, p in scores.items():
            pd.DataFrame({"id": frames[split].id, "p_raw": p}).to_parquet(
                INTERIM / f"o_xgb_{args.seed}_{split}_scores.parquet", index=False
            )
    report = json.loads(RESULT.read_text()) if RESULT.exists() else {}
    report.setdefault(args.model, {})[str(args.seed)] = run
    RESULT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(args.model, args.seed, run["auc"], run["fit_seconds"])


if __name__ == "__main__":
    main()
