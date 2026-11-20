"""Evaluate D3a on held-out labels and simulate D3b on paired loan amounts."""

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
    if collateral is not None:
        report["capital_locked_usd"] = float(collateral[accepted].sum())
    return report


def shocks(debt, initial_ratio, maintenance_ratio, buffers):
    collateral = debt * (initial_ratio + buffers)
    outcomes = []
    for shock in (-0.10, -0.20, -0.30, -0.40):
        mark = collateral * (1 + shock)
        triggered = mark < debt * maintenance_ratio
        # One liquidation call, capped by both the close factor and collateral.
        repay = np.minimum(0.5 * debt[triggered], mark[triggered] / 1.05)
        seized = repay * 1.05
        bad_debt = np.maximum(debt[triggered] - repay - (mark[triggered] - seized), 0)
        outcomes.append(dict(shock=shock, liquidated_loans=int(triggered.sum()),
                             liquidated_collateral_usd=float(seized.sum()),
                             bad_debt_usd=float(bad_debt.sum())))
    return outcomes


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
    if rule != "fixed" or not capital_available:
        raise ValueError("D3b requires fixed tiers and loans with valid USD amounts")
    # Stable loan order makes the shared draw reproducible across policy runs.
    test_order = np.argsort(test.id.to_numpy(), kind="stable")
    priced = test_order[valid_amount.to_numpy()[test_order]]
    buffers = np.random.default_rng(11).uniform(0, 0.20, size=len(priced))
    for name, mask, initial, maintenance in (
        ("uniform", uniform, np.full(len(test), 1.25), np.full(len(test), 1.212)),
        ("tiered", accepted, ratios, np.where(tier == 1, 1.10, 1.30)),
    ):
        keep = mask[priced]
        indices = priced[keep]
        policies[name]["n_priced_accepted"] = len(indices)
        policies[name]["simulated_shocks"] = shocks(
            usd.to_numpy()[indices], initial[indices], maintenance[indices], buffers[keep]
        )
    report["simulation"] = dict(
        label="simulated", seed=11, borrower_buffer="Uniform(0, 0.20) added to collateral/debt ratio",
        pairing="Same origination-id-ordered draw for both policies and all price shocks",
        debt="Stable USD debt; exclude loans with missing or nonpositive USD amounts",
        liquidation="One call for each breached maintenance ratio; 50% close factor and 5% bonus",
        maintenance_ratios={"uniform": 1.212, "A": 1.10, "B": 1.30},
        bad_debt="Positive residual debt minus remaining marked collateral after the liquidation call",
    )
    Path("results/pilot_policy_v2.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    print({name: [row["liquidated_loans"] for row in policy["simulated_shocks"]]
           for name, policy in policies.items()})


if __name__ == "__main__":
    main()
