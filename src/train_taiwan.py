"""Run the external Taiwan O_XGB pilot with a training-only early-stopping fold."""

import argparse
import json
from datetime import date
from pathlib import Path
from time import perf_counter

import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from step3_train import INTERIM, XGB_PARAMS, xgb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()
    training = pd.read_parquet(INTERIM / "taiwan_train_core.parquet")
    test = pd.read_parquet(INTERIM / "taiwan_test.parquet")
    cols = training.columns.difference(["id", "label"], sort=False).tolist()
    train, inner = train_test_split(training, test_size=0.10, stratify=training.label,
                                    random_state=args.seed)
    model = xgb(args.seed, train.label)
    start = perf_counter()
    model.fit(train[cols], train.label, eval_set=[(inner[cols], inner.label)], verbose=False)
    result = dict(date=date.today().isoformat(), seed=args.seed, model="O_XGB",
                  test_auc=float(roc_auc_score(test.label, model.predict_proba(test[cols])[:, 1])),
                  n_fit=len(train), n_inner_val=len(inner), n_test=len(test), n_features=len(cols),
                  fit_seconds=round(perf_counter() - start, 3), best_iteration=model.best_iteration,
                  config=dict(XGB_PARAMS, scale_pos_weight=model.scale_pos_weight))
    Path("results/pilot_taiwan.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Taiwan test AUC:", result["test_auc"])


if __name__ == "__main__":
    main()
