# Appendix A — Pilot runs

Run from the repository root with Python 3.11 active and Anvil on PATH for Ape. Execute commands containing SEED once per listed seed.

| Pilot | Date | Seed | Command | Results file |
| --- | --- | --- | --- | --- |
| Data load | 2026-11-19 | None | `python src/step1_load.py` | `results/pilot_data.json` |
| D5 and Taiwan split | 2026-11-19 | 11 | `python src/step2_prepare.py --seed 11` | `results/pilot_data.json` |
| B_XGB fit | 2026-11-19 | 11, 22, 33 | `python src/step3_train.py --model B_XGB --seed SEED` | `results/pilot_model.json` |
| O_XGB fit | 2026-11-19 | 11, 22, 33 | `python src/step3_train.py --model O_XGB --seed SEED` | `results/pilot_model.json` |
| B_LR fit | 2026-11-19 | 11 | `python src/step3_train.py --model B_LR --seed 11` | `results/pilot_model.json` |
| O_LR fit | 2026-11-19 | 11 | `python src/step3_train.py --model O_LR --seed 11` | `results/pilot_model.json` |
| B_XGB_noPCA fit | 2026-11-20 | 11, 22, 33 | `python src/step3_train.py --model B_XGB_noPCA --seed SEED` | `results/pilot_model.json` |
| Baseline preprocessing and feature audit | 2026-11-20 | 11 | `python src/audit_pilot.py` | `results/pilot_audit.json` |
| Calibration, Platt and TreeSHAP | 2026-11-20 | 11 | `python src/step4_calibrate.py --seed 11` | `results/pilot_calib.json` |
| Fixed and percentile tiers | 2026-11-20 | 11 | `python src/step5_tiers.py --seed 11` | `results/pilot_tiers.json` |
| Paired no-PCA precision | 2026-11-20 | 11, 22, 33 | `python src/power.py` | `results/pilot_power.json` |
| Taiwan XGBoost | 2026-11-19 | 11 | `python src/train_taiwan.py --seed 11` | `results/pilot_taiwan.json` |
| Fixed policy and simulated shocks | 2026-11-20 | 11 | `python src/sim_policy.py` | `results/pilot_policy_v2.json` |
| Anvil gas | 2026-11-19 | None | `ape run gas_batch --network ethereum:local:foundry` | `results/pilot_gas.json` |

Table 22. Pilot configurations, commands and evidence.

Across seeds 11, 22 and 33, proposed minus all-feature no-PCA test AUC was -0.00583 (paired 95% t interval -0.04285 to 0.03118). Mean validation minus test AUC was 0.00807 proposed and 0.02567 baseline. The gap narrowed, but the interval crosses the −0.02 non-inferiority margin. The PCA reproduction remains a separate comparison with [1].

For the supplementary Ape gas profile, run `ape test tests/test_t3_functions.py --gas -q -k 'not test_get_tier'`. View gas uses an estimate query. Revert assertions are verified with the ordinary test runner.
