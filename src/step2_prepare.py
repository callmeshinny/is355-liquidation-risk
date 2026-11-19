"""Apply the label horizon and D5 split, then fit feature rules on training only."""

import argparse
import json
from datetime import date
from pathlib import Path
from time import perf_counter

import pandas as pd
from scipy.stats import ks_2samp
from sklearn.model_selection import train_test_split

INTERIM = Path("data/interim")
RESULT = Path("results/pilot_data.json")
HORIZON = 17.43 * 86400
KS_THRESHOLD = 0.15
WINDOWS = {
    "train_core": (None, "2021-11-27"),
    "inner_val": ("2021-12-15", "2022-03-15"),
    "val": ("2022-04-02", "2022-07-01"),
    "test": ("2022-07-01", None),
}
METADATA = {"id", "timestamp", "timeDiff", "status", "label", "user", "amountUSD"}
NON_FEATURES = METADATA - {"amountUSD"}


def label_loans(frame):
    positives = frame.status.eq(1) & frame.timeDiff.le(HORIZON)
    negatives = frame.timeDiff.gt(HORIZON)
    keep = positives | negatives
    return frame.loc[keep].assign(label=positives.loc[keep].astype("int8"))


def within(timestamp, start, end):
    mask = timestamp.notna()
    if start is not None:
        mask &= timestamp.ge(pd.Timestamp(start, tz="UTC"))
    if end is not None:
        mask &= timestamp.lt(pd.Timestamp(end, tz="UTC"))
    return mask


def split_loans(frame):
    values = frame.timestamp
    if pd.api.types.is_numeric_dtype(values):
        timestamp = pd.to_datetime(values, unit="s", utc=True)
    else:
        timestamp = pd.to_datetime(values, utc=True)
    return {name: frame.loc[within(timestamp, *bounds)].assign(timestamp=timestamp)
            for name, bounds in WINDOWS.items()}


def fit_features(train_core, inner_val):
    candidates = train_core.drop(columns=list(NON_FEATURES), errors="ignore")
    empty = candidates.columns[candidates.isna().all()].tolist()
    candidates = candidates.drop(columns=empty)
    numeric = candidates.select_dtypes(include="number").columns.tolist()
    categories = {name: candidates[name].dropna().astype(str).value_counts().head(10).index.tolist()
                  for name in candidates.columns.difference(numeric)}
    drift = {}
    for name in numeric:
        left, right = train_core[name].dropna(), inner_val[name].dropna()
        if not left.empty and not right.empty:
            statistic = float(ks_2samp(left, right, method="asymp").statistic)
            if statistic >= KS_THRESHOLD:
                drift[name] = statistic
    return numeric, categories, empty, drift


def encode(frame, numeric, categories):
    # Week 3's top-ten encoding with a dedicated fallback column.
    features = {name: frame[name].fillna(0).astype(float) for name in numeric}
    for name, levels in categories.items():
        values = frame[name].astype("string")
        for position, level in enumerate(levels):
            features[f"{name}__level_{position}"] = values.eq(level).fillna(False).astype("float32")
        features[f"{name}__other"] = (~values.isin(levels)).astype("float32")
    return pd.DataFrame(features, index=frame.index)


def summarize(frame):
    summary = {"n": len(frame), "positive_rate": float(frame.label.mean())}
    if "timestamp" in frame:
        summary.update(first_date=str(frame.timestamp.min().date()),
                       last_date=str(frame.timestamp.max().date()))
    return summary


def split_taiwan(frame, seed):
    frame = frame.drop(columns=["X2", "X4", "SEX", "MARRIAGE"], errors="ignore")
    frame.insert(0, "id", range(len(frame)))
    rest, test = train_test_split(frame, test_size=0.3, stratify=frame.label, random_state=seed)
    train, val = train_test_split(rest, test_size=1 / 7, stratify=rest.label, random_state=seed)
    return {"train_core": train, "val": val, "test": test}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()

    started = perf_counter()
    frame = pd.concat([pd.read_parquet(INTERIM / f"finsurvival_{s}.parquet")
                       for s in ("train", "test")], ignore_index=True)
    unique = frame.loc[~frame.id.duplicated(keep=False)]
    labeled = label_loans(unique)
    splits = split_loans(labeled)
    numeric, categories, empty, drift = fit_features(splits["train_core"], splits["inner_val"])
    for name, split in splits.items():
        cols = [col for col in split if col in METADATA and col not in numeric]
        features = encode(split, numeric, categories)
        split[cols].join(features).to_parquet(INTERIM / f"fin_{name}.parquet", index=False)
    taiwan = split_taiwan(pd.read_parquet(INTERIM / "taiwan.parquet"), args.seed)
    for name, split in taiwan.items():
        split.to_parquet(INTERIM / f"taiwan_{name}.parquet", index=False)

    summary = json.loads(RESULT.read_text())
    summary.update(
        prepare_date=date.today().isoformat(), seed=args.seed, horizon_days=17.43,
        n_duplicate_id_rows_removed=len(frame) - len(unique),
        n_short_or_invalid_removed=len(unique) - len(labeled),
        n_purged=len(labeled) - sum(map(len, splits.values())),
        n_labeled=len(labeled), positive_rate=float(labeled.label.mean()),
        finsurvival_splits={name: summarize(split) for name, split in splits.items()},
        taiwan_splits={name: summarize(split) for name, split in taiwan.items()},
        feature_fit_split="train_core", numeric_features=numeric, categorical_levels=categories,
        dropped_empty=empty, excluded_metadata=sorted(NON_FEATURES),
        ks_threshold=KS_THRESHOLD, dropped_drift=drift,
    )
    example = splits["train_core"].iloc[0]
    summary["prepare_seconds"] = round(perf_counter() - started, 3)
    summary["label_example"] = {
        "loan_start_date": str(example.timestamp.date()), "status": int(example.status),
        "time_diff_days": round(float(example.timeDiff) / 86400, 6), "label": int(example.label),
    }
    RESULT.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(summary["finsurvival_splits"])
    print(summary["taiwan_splits"])


if __name__ == "__main__":
    main()
