"""Evaluate the D3a loan-level counterfactual on held-out outcomes."""

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from step5_tiers import RESULT as TIER_RESULT, assign
from step3_train import INTERIM


def summarize(accepted, labels, collateral=None):
    rejected = ~accepted
    report = dict(accepted=int(accepted.sum()), rejected=int(rejected.sum()),
                  liquidations_avoided=int((rejected & labels.eq(1)).sum()),
                  good_loans_rejected=int((rejected & labels.eq(0)).sum()))
    good_rejected = report["good_loans_rejected"]
    report["avoided_per_good_rejected"] = (
        report["liquidations_avoided"] / good_rejected if good_rejected else None
    )
    if collateral is not None:
        report["capital_locked_usd"] = float(collateral[accepted].sum())
    return report


def main():
    tiers = json.loads(TIER_RESULT.read_text())
    test = pd.read_parquet(INTERIM / "calibrated_test.parquet")
    rule = tiers["export_rule"]
    cutoffs = tiers["rules"][rule]
    tier = assign(test.p, (cutoffs["tau_A"], cutoffs["tau_C"]))
    uniform = np.ones(len(test), dtype=bool)
    accepted = tier != 3
    amount = test.get("amountUSD")
    valid_amount = amount.notna() & np.isfinite(amount) & amount.gt(0) if amount is not None else None
    capital_available = valid_amount is not None and bool(valid_amount.any())
    ratios = np.select([tier == 1, tier == 2], [1.20, 1.50], default=0)
    usd = amount.where(valid_amount, 0) if capital_available else None
    policies = {
        "uniform": summarize(uniform, test.label, usd * 1.25 if usd is not None else None),
        "tiered": summarize(accepted, test.label, usd * ratios if usd is not None else None),
    }
    report = dict(date=date.today().isoformat(), seed=tiers["seed"], model_sha256=tiers["model_sha256"],
                  n_loans=len(test), policies=policies,
                  rule=rule, fixed_policy_available=tiers["rules"]["fixed"]["status"] == "measured",
                  score_scope="At-origin loan score. Historical open-loan wallet membership is unavailable.",
                  n_priced=int(valid_amount.sum()) if valid_amount is not None else 0,
                  collateral_ratios={"uniform": 1.25, "A": 1.20, "B": 1.50})
    if capital_available:
        report["capital_freed_tier_a_usd"] = float((usd[tier == 1] * (1.25 - 1.20)).sum())
        report["capital_freed_usd"] = (policies["uniform"]["capital_locked_usd"]
                                      - policies["tiered"]["capital_locked_usd"])
    Path("results/pilot_policy.json").write_text(json.dumps(report, indent=2) + "\n")
    print(policies)


if __name__ == "__main__":
    main()
