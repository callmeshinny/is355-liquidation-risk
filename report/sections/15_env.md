## 1.5 Environment and reproducibility

The pilot host uses Apple M2 with 8 GiB RAM and macOS-27.0.1-arm64-arm-64bit. The runtime uses the Python 3.11 virtual environment at `.venv`, Vyper 0.4 and Ape 0.8. The measured versions are recorded in `results/env.json`.

| Tool | Installed version |
| --- | --- |
| Python | 3.11.18 |
| pandas | 2.3.3 |
| scikit-learn | 1.9.1 |
| XGBoost | 3.2.0 |
| SHAP | 0.49.1 |
| Optuna | 5.1.0 |
| Vyper | 0.4.3 |
| Ape | 0.8.54 |
| Anvil | anvil Version: 1.9.0 |

Anvil is the local network for functional tests and gas measurements. Sepolia with the Alchemy RPC provider is planned for confirmation latency and end-to-end deployment checks. The Week 4 run uses local test tokens.

The planned seed list is 11, 22, 33, 44, 55. The model pilot uses 11, 22, 33. Taiwan's stratified split uses seed 11.

Repository [is355-liquidation-risk](https://github.com/callmeshinny/is355-liquidation-risk).

Run `bash tools/setup_env.sh` and, if FinSurvival is missing, `bash tools/get_data.sh`. Run the data scripts `src/step1_load.py` and `src/step2_prepare.py --seed 11` with `.venv/bin/python`, followed by the planned Step 3–5 scripts. Use `.venv/bin/ape test --gas` for the planned local chain checks and `bash tools/build_docx.sh` to assemble the report.
