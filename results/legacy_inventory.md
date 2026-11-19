# Week 3 code inventory

| Notebook | Reuse for Week 4 | Results and configuration |
| --- | --- | --- |
| finsurvival_borrow_liquidated_eda.ipynb | Step 1 cells 2–5, RDS part loader and ID join. Step 2 cell 6, make_label with 17.43 days (seconds). | Code prints sizes, event counts and duration quantiles. Saved outputs were excluded from inspection. |
| check_finsurvival_data.ipynb | Steps 1–2, X/y ID coverage, remove all duplicate IDs, validated one-to-one merge, label_of and censor audit. | Code prints retained counts and positive rates before and after deduplication. Saved outputs were excluded from inspection. |
| 02_model_finsurvival.ipynb | Step 2 cell 4, train-fitted top-ten categorical encoding and zero-fill numerics. Replace its trailing validation split with D5. Step 3 cell 5, balanced LR (C=0.1) and XGB (depth 6, learning rate 0.05, early stopping 50). Step 4 metrics and isotonic fit on validation. | Code prints split and metric tables and best XGB iteration. Paper AUC constants are citations. Saved outputs were excluded from inspection. |

The Week 3 workflow plans SHAP and tier assignment. The first 200 lines of the model export establish the model and calibration inputs. Step 5 uses the finalized D1 thresholds and D2 wallet aggregation in Week 4.
