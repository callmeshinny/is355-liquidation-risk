# Appendix A — Pilot runs

Run from the repository root with the Python 3.11 environment active. Use Anvil on PATH for Ape. The recorded pilot date is 2026-11-19. Seeds apply where random sampling or model estimation uses them.

| Work | Configuration and seed | Command | Evidence |
| --- | --- | --- | --- |
| Environment | Apple Silicon native, no random seed | `python tools/env_report.py` | `results/env.json` |
| Data load | FinSurvival Borrow and UCI 350, no random seed | `python src/step1_load.py` | `results/pilot_data.json` |
| D5 and Taiwan splits | D5 calendar, Taiwan seed 11 | `python src/step2_prepare.py --seed 11` | `results/pilot_data.json` |
| Model fits | B_LR and O_LR seed 11. B_XGB and O_XGB seeds 11, 22, 33 | `python src/step3_train.py --model MODEL --seed SEED`, once per listed pair | `results/pilot_model.json` |
| Calibration and explanation | Isotonic fit on validation, XGBoost TreeSHAP with 2,000 test rows, seed 11 | `python src/step4_calibrate.py --seed 11` | `results/pilot_calib.json`, `results/pilot_reliability.csv` |
| Tier evaluation | D1 feasibility and percentile comparator, seed 11 | `python src/step5_tiers.py --seed 11` | `results/pilot_tiers.json`, `results/pilot_tiers_sample_percentile.csv` |
| Repetition planning | Paired XGB seeds 11, 22, 33 and LR bootstrap SD | `python src/power.py` | `results/pilot_power.json` |
| Taiwan AUC | O_XGB, stratified inner validation, seed 11 | `python src/train_taiwan.py --seed 11` | `results/pilot_taiwan.json` |
| Real-label policy sensitivity | Uniform versus percentile tiers, seed 11 | `python src/sim_policy.py` | `results/pilot_policy.json` |
| Anvil checks | Local T3 and T4 checks and deterministic Hypothesis settings | `ape test -q` | `tests/test_t3_functions.py`, `tests/test_t4_security.py` |
| Anvil gas | Ten fresh synthetic batches per size 1, 10 and 100. Deterministic identifiers | `ape run gas_batch --network ethereum:local:foundry` | `results/pilot_gas.json` |

Table 22. Pilot configurations, commands and evidence.

For the supplementary Ape gas profile, run `ape test tests/test_t3_functions.py --gas -q -k 'not test_get_tier'`. View gas uses an estimate query. Revert assertions are verified with the ordinary test runner.
