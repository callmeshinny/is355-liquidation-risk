"""Summarize seed dispersion and approximate the paired AUC run budget."""

import json
from datetime import date
from math import ceil, sqrt
from pathlib import Path

import numpy as np
from scipy.stats import t

from step3_train import RESULT


def main():
    models = json.loads(RESULT.read_text())
    baseline = "B_XGB_noPCA"
    seeds = sorted(set(models[baseline]) & set(models["O_XGB"]), key=int)
    if len(seeds) < 2:
        raise ValueError("At least two paired XGB seeds are required")
    auc = {name: np.array([models[name][s]["auc"]["test"] for s in seeds])
           for name in (baseline, "O_XGB")}
    differences = auc["O_XGB"] - auc[baseline]
    sd = float(differences.std(ddof=1))
    mean_delta = float(differences.mean())
    observed_width = float(t.ppf(0.975, df=len(seeds) - 1)) * sd / sqrt(len(seeds))
    gaps = {
        name: [models[name][s]["auc"]["val"] - models[name][s]["auc"]["test"] for s in seeds]
        for name in auc
    }
    n = 5
    critical = float(t.ppf(0.975, df=n - 1))
    calculations = [{"delta": delta, "n_approx": (2.8 * sd / delta) ** 2,
                     "n_rounded_up": ceil((2.8 * sd / delta) ** 2)}
                    for delta in (0.01, 0.02)]
    report = dict(date=date.today().isoformat(), seeds=[int(s) for s in seeds],
                  baseline=baseline, test_auc_mean={name: float(x.mean()) for name, x in auc.items()},
                  paired_mean_delta=mean_delta,
                  paired_ci95=[mean_delta - observed_width, mean_delta + observed_width],
                  val_minus_test_by_seed=gaps,
                  val_minus_test_mean={name: float(np.mean(values)) for name, values in gaps.items()},
                  s_by_model={name: float(values.std(ddof=1)) for name, values in auc.items()},
                  lr_bootstrap_sd={name: next(iter(models[name].values()))["test_bootstrap"]["sd"]
                                   for name in ("B_LR", "O_LR")},
                  paired_differences=differences.tolist(), s_d=sd, power_approx=calculations,
                  n_for_ci=n, t_critical=critical, ci95_half_width=critical * sd / sqrt(n))
    Path("results/pilot_power.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Paired SD", sd, "95% CI half-width", report["ci95_half_width"])


if __name__ == "__main__":
    main()
