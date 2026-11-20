# Appendix A — Pilot runs

Run from the repository root with the Python 3.11 environment active. Use Anvil on PATH for Ape. The original pilot date is 2026-11-19. The review audit ran on 2026-11-20. Seeds apply where random sampling or model estimation uses them.

| Work | Configuration and seed | Command | Evidence |
| --- | --- | --- | --- |
| Environment | Apple Silicon native, no random seed | `python tools/env_report.py` | `results/env.json` |
| Data load | FinSurvival Borrow and UCI 350, no random seed | `python src/step1_load.py` | `results/pilot_data.json` |
| D5 and Taiwan splits | D5 calendar, Taiwan seed 11 | `python src/step2_prepare.py --seed 11` | `results/pilot_data.json` |
| Model fits | B_LR and O_LR seed 11. B_XGB and O_XGB seeds 11, 22, 33 | `python src/step3_train.py --model MODEL --seed SEED`, once per listed pair | `results/pilot_model.json` |
| Baseline and leakage audit | All eligible features without PCA, seeds 11, 22, 33. Validation TreeSHAP, seed 11 | `python src/step3_train.py --model B_XGB_noPCA --seed SEED`, then `python src/audit_pilot.py` | `results/pilot_audit.json` |
| Calibration and explanation | Isotonic fit on validation, XGBoost TreeSHAP with 2,000 test rows, seed 11 | `python src/step4_calibrate.py --seed 11` | `results/pilot_calib.json`, `results/pilot_reliability.csv` |
| Tier evaluation | Revised D1 grid and percentile comparator, seed 11 | `python src/step5_tiers.py --seed 11` | `results/pilot_tiers.json`, `results/pilot_tiers_sample.csv` |
| Repetition planning | Paired XGB seeds 11, 22, 33 and LR bootstrap SD | `python src/power.py` | `results/pilot_power.json` |
| Taiwan AUC | O_XGB, stratified inner validation, seed 11 | `python src/train_taiwan.py --seed 11` | `results/pilot_taiwan.json` |
| Policy counterfactual and simulated shocks | 2026-11-20, fixed tiers versus uniform, shared Uniform(0, 0.20) borrower buffer, seed 11 | `python src/sim_policy.py` | `results/pilot_policy_v2.json` |
| Anvil checks | Local T3 and T4 checks and deterministic Hypothesis settings | `ape test -q` | `tests/test_t3_functions.py`, `tests/test_t4_security.py` |
| Anvil gas | Ten fresh synthetic batches per size 1, 10 and 100. Deterministic identifiers | `ape run gas_batch --network ethereum:local:foundry` | `results/pilot_gas.json` |

Table 22. Pilot configurations, commands and evidence.

D5 mean test AUC was 0.8033 for proposed XGBoost, 0.7020 with PCA and 0.8091 with all eligible features and PCA disabled. This matched ablation implicates PCA in the local gap, and the top 15 validation TreeSHAP features were available at origination. Local PCA LR scored 0.6145, versus 0.723 in [1], which uses R glm and a different training and preprocessing protocol. The paper's XGBoost AUC of 0.732 also uses a different fit protocol [1].

For the supplementary Ape gas profile, run `ape test tests/test_t3_functions.py --gas -q -k 'not test_get_tier'`. View gas uses an estimate query. Revert assertions are verified with the ordinary test runner.
