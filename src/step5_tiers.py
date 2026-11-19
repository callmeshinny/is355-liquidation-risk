"""Choose D1 thresholds on validation and apply both rules to held-out cohorts."""

import argparse
import hashlib
import json
from datetime import date
from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd

from step4_calibrate import QUARTERS
from step3_train import INTERIM, MODELS

RESULT = Path("results/pilot_tiers.json")


def fixed_thresholds(val):
    groups = val.groupby("p").label.agg(["count", "sum"]).sort_index()
    rate = val.label.mean()
    below_n = groups["count"].cumsum().shift(fill_value=0)
    below_pos = groups["sum"].cumsum().shift(fill_value=0)
    above_n = groups["count"].iloc[::-1].cumsum().iloc[::-1]
    above_pos = groups["sum"].iloc[::-1].cumsum().iloc[::-1]
    a = groups.index[(below_n > 0) & ((below_pos / below_n) <= 0.5 * rate)]
    c = groups.index[(above_pos >= 30) & ((above_pos / above_n) >= 3 * rate)]
    return (float(a.max()) if len(a) else None, float(c.min()) if len(c) else None)


def assign(probability, thresholds):
    a, c = thresholds
    return np.select([probability < a, probability >= c], [1, 3], default=2)


def wilson(positives, n):
    if not n:
        return None
    p = positives / n
    z = 1.959963984540054
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    radius = z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
    return [max(0, center - radius), min(1, center + radius)]


def summarize(frame):
    rows = []
    for tier in (1, 2, 3):
        labels = frame.loc[frame.tier.eq(tier), "label"]
        n, positives = len(labels), int(labels.sum())
        rows.append(dict(tier=tier, n=n, share=n / len(frame) if len(frame) else None,
                         liquidation_rate=positives / n if n else None,
                         liquidation_ci95=wilson(positives, n)))
    return rows


def aggregate_wallets(observed_loans):
    """Take max over the loans supplied for each wallet."""
    return observed_loans.groupby("user", as_index=False).agg(p=("p", "max"), label=("label", "max"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()
    val = pd.read_parquet(INTERIM / "calibrated_val.parquet")
    test = pd.read_parquet(INTERIM / "calibrated_test.parquet")
    if json.loads(Path("results/pilot_calib.json").read_text())["seed"] != args.seed:
        raise ValueError("Run calibration for this seed first")
    candidates = fixed_thresholds(val)
    fixed = candidates if None not in candidates and candidates[0] < candidates[1] else None
    percentile = tuple(float(v) for v in val.p.quantile([0.7, 0.9]))
    if percentile[0] >= percentile[1]:
        raise ValueError("Validation quantile scores do not define three ordered tiers")
    model_hash = hashlib.sha256((MODELS / f"O_XGB_{args.seed}.ubj").read_bytes()).hexdigest()
    test["quarter"] = test.timestamp.dt.tz_localize(None).dt.to_period("Q")
    cohorts = [("overall", test), *((str(q), test.loc[test.quarter.eq(q)]) for q in QUARTERS)]
    rules = {"fixed": {"status": "unavailable", "overall": None, "per_quarter": []}}
    for name, thresholds in (("fixed", fixed), ("percentile", percentile)):
        if thresholds is None:
            continue
        rows = []
        for cohort, frame in cohorts:
            wallets = aggregate_wallets(frame).assign(tier=lambda w: assign(w.p, thresholds))
            loans = frame.assign(tier=assign(frame.p, thresholds))
            rows.append(dict(cohort=cohort, wallets=summarize(wallets), loans=summarize(loans)))
        rules[name] = dict(status="measured", tau_A=thresholds[0], tau_C=thresholds[1], overall=rows[0],
                           per_quarter=rows[1:])

    wallets = aggregate_wallets(test).rename(columns={"user": "wallet"})
    export_rule, export_thresholds = ("fixed", fixed) if fixed else ("percentile", percentile)
    wallets["tier"] = assign(wallets.p, export_thresholds)
    wallets["model_version"] = 1
    export = wallets[["wallet", "p", "tier", "model_version"]]
    suffix = "" if fixed else "_percentile"
    export_path = Path(f"data/processed/tiers{suffix}.csv")
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export.to_csv(export_path, index=False)
    sample = export.sample(n=min(len(export), 20), random_state=args.seed).copy()
    sample["wallet"] = sample.wallet.map(lambda wallet: hashlib.sha256(str(wallet).encode()).hexdigest())
    sample.to_csv(f"results/pilot_tiers_sample{suffix}.csv", index=False)
    report = dict(date=date.today().isoformat(), seed=args.seed, tau_A=fixed[0] if fixed else None, tau_C=fixed[1] if fixed else None,
                  fixed_validation_candidates={"tau_A": candidates[0], "tau_C": candidates[1]},
                  export_rule=export_rule,
                  fit_split="val", validation_liquidation_rate=float(val.label.mean()),
                  model_version=1, model_sha256=model_hash, rules=rules,
                  n_wallets=len(wallets), n_test_loans=len(test),
                  wallet_scope="Retrospective cohort proxy. Loan open status is unavailable.")
    RESULT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print({key: report[key] for key in ("tau_A", "tau_C", "n_wallets", "n_test_loans")})


if __name__ == "__main__":
    main()
