import json
from itertools import combinations

import pandas as pd

from src.step2_prepare import INTERIM, RESULT, WINDOWS, encode, fit_features, label_loans, split_loans


def test_fin_splits_and_feature_fit():
    assert WINDOWS == {
        "train_core": (None, "2021-11-27"),
        "inner_val": ("2021-12-15", "2022-03-15"),
        "val": ("2022-04-02", "2022-07-01"),
        "test": ("2022-07-01", None),
    }
    splits = {name: pd.read_parquet(INTERIM / f"fin_{name}.parquet") for name in WINDOWS}
    for left, right in combinations(splits.values(), 2):
        assert set(left.id).isdisjoint(right.id)

    frames = [pd.read_parquet(INTERIM / f"finsurvival_{name}.parquet")
              for name in ("train", "test")]
    raw = pd.concat(frames, ignore_index=True)
    raw = raw.loc[~raw.id.duplicated(keep=False)]
    expected = split_loans(label_loans(raw))
    summary = json.loads(RESULT.read_text())
    for name, frame in splits.items():
        start, end = WINDOWS[name]
        assert frame.id.is_unique
        assert set(frame.id) == set(expected[name].id)
        if start:
            assert frame.timestamp.min() >= pd.Timestamp(start, tz="UTC")
        if end:
            assert frame.timestamp.max() < pd.Timestamp(end, tz="UTC")
        assert frame.label.mean() == summary["finsurvival_splits"][name]["positive_rate"]
        print(f"{name} n={len(frame)} positive_rate={frame.label.mean():.6f}")

    _, levels, empty, drift = fit_features(expected["train_core"], expected["inner_val"])
    assert summary["feature_fit_split"] == "train_core"
    assert summary["categorical_levels"] == levels
    assert summary["dropped_empty"] == empty
    assert summary["dropped_drift"] == drift


def test_taiwan_splits():
    splits = {name: pd.read_parquet(INTERIM / f"taiwan_{name}.parquet")
              for name in ("train_core", "val", "test")}
    assert [len(frame) for frame in splits.values()] == [18000, 3000, 9000]
    for left, right in combinations(splits.values(), 2):
        assert set(left.id).isdisjoint(right.id)
    for name, frame in splits.items():
        assert not {"SEX", "MARRIAGE", "X2", "X4"} & set(frame)
        assert {"X3", "EDUCATION"} & set(frame)

        print(f"Taiwan {name} n={len(frame)} positive_rate={frame.label.mean():.6f}")


def test_unseen_test_category_uses_existing_fallback():
    train_core = pd.DataFrame({"reserve": ["train-only", "train-only"]})
    inner_val = pd.DataFrame({"reserve": ["inner-only"]})
    test = pd.DataFrame({"reserve": ["test-only"]})
    numeric, levels, _, _ = fit_features(train_core, inner_val)
    assert levels == {"reserve": ["train-only"]}
    encoded = encode(test, numeric, levels)
    assert encoded.to_dict("records") == [{"reserve__level_0": 0.0, "reserve__other": 1.0}]
