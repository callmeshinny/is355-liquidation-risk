"""Load FinSurvival and UCI credit defaults into the interim parquet files."""

import argparse
import json
from datetime import date
from pathlib import Path
from time import perf_counter

import pandas as pd
import pyreadr
from ucimlrepo import fetch_ucirepo

BORROW = Path("data/raw/finsurvival/Data/Survival_Data/Borrow")
INTERIM = Path("data/interim")
RESULT = Path("results/pilot_data.json")


def read_rds(path):
    # Same single-data-frame loader as the Week 3 EDA.
    return next(iter(pyreadr.read_r(path).values()))


def load_borrow(root, split, part_count):
    prefix = f"X_{split}"
    parts = [read_rds(root / prefix / f"{prefix}_{i}.rds")
             for i in range(1, part_count + 1)]
    x = pd.concat(parts, ignore_index=True).dropna(subset=["id"])
    raw_feature_count = x.shape[1] - 1
    empty = x.columns[x.isna().all()].tolist()
    x = x.drop(columns=empty)
    exogenous = x.columns[x.columns.str.lower().str.startswith("exo")].tolist()
    x = x.drop(columns=exogenous)
    y = read_rds(root / "Account Liquidated" / f"y_{split}.rds")
    label_columns = ["id", "timeDiff", "status"]
    y = y.loc[:, label_columns].dropna(subset=["id"])
    joined = y.merge(x, on="id", how="inner", validate="many_to_many")
    counts = {
        "n_parts": part_count,
        "n_features_rows": len(x),
        "n_raw_features": raw_feature_count,
        "dropped_all_null": empty,
        "dropped_exogenous": exogenous,
        "n_labels": len(y),
        "n_labels_without_features": int((~y.id.isin(x.id)).sum()),
        "n_features_without_labels": int((~x.id.isin(y.id)).sum()),
        "n_joined": len(joined),
        "n_duplicate_id_rows": int(joined.id.duplicated(keep=False).sum()),
    }
    return joined, counts


def schema(frame):
    return [{"name": name, "dtype": str(dtype)} for name, dtype in frame.dtypes.items()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--borrow-root", type=Path, default=BORROW)
    args = parser.parse_args()
    started = perf_counter()
    train, train_counts = load_borrow(args.borrow_root, "train", 4)
    test, test_counts = load_borrow(args.borrow_root, "test", 3)
    shared = train.columns.intersection(test.columns)
    train_counts["dropped_nonshared"] = train.columns.difference(shared).tolist()
    test_counts["dropped_nonshared"] = test.columns.difference(shared).tolist()
    datasets = {"finsurvival_train": train[shared], "finsurvival_test": test[shared]}

    uci = fetch_ucirepo(id=350)
    target = uci.data.targets.squeeze(axis=1).rename("label")
    taiwan = uci.data.features.join(target, validate="one_to_one")
    datasets["taiwan"] = taiwan
    INTERIM.mkdir(parents=True, exist_ok=True)
    RESULT.parent.mkdir(exist_ok=True)
    for name, frame in datasets.items():
        frame.to_parquet(INTERIM / f"{name}.parquet", index=False)

    report = {
        "load_date": date.today().isoformat(),
        "n_labels": train_counts["n_labels"] + test_counts["n_labels"],
        "n_joined": len(train) + len(test),
        "n_labels_with_features": sum(c["n_labels"] - c["n_labels_without_features"]
                                      for c in (train_counts, test_counts)),
        "load_seconds": round(perf_counter() - started, 3),
        "n_shared_features": len(shared) - 3,
        "n_taiwan": len(taiwan),
        "n_taiwan_features": len(uci.data.features.columns),
        "taiwan_positive_rate": float(target.mean()),
        "source_splits": {"train": train_counts, "test": test_counts},
        "schema": {name: schema(frame) for name, frame in datasets.items()},
    }
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    print({key: value for key, value in report.items() if key.startswith("n_")})


if __name__ == "__main__":
    main()
