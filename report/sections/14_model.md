## 1.4 Model specification

| Field | Baseline [1] reproduced | Ours | Taiwan |
| --- | --- | --- | --- |
| Algorithm | Balanced LR and XGB. All eligible encoded features, scaling and PCA at 95% variance. The PCA setting is our reproduction assumption. LR applies signed log1p before scaling. | Balanced LR and XGB. Drop numeric drift features at KS D ≥ 0.15. Keep original coordinates for SHAP. LR uses signed log1p and scaling. | XGB on de-identified credit features after dropping SEX and MARRIAGE. No temporal KS screen. |
| Hyperparameters and search space | Fixed pilot LR C=0.1 and max_iter=2000. XGB learning rate 0.05, depth 6, min_child_weight 5, row and column subsampling 0.8, up to 1,000 rounds. Planned LR C log-uniform 0.001–10. Planned XGB learning rate 0.01–0.2 log-uniform, depth 3–8, min_child_weight 1–10, and row and column subsampling 0.6–1.0. | Same pilot settings and planned search space as baseline. | Same XGB pilot setting and planned search space. |
| Tuning method and budget | Pilot hyperparameters fixed from Week 3. Early stop XGB after 50 rounds without inner-val AUC gain. Planned Optuna budget is 50 trials per variant, scored on inner-val only. | Same budget and selection metric. | Planned Optuna budget is 50 trials on a stratified inner fold within training. Pilot trained on 16,200 records and used 1,800 for early stopping. |
| Loss | Logistic log loss for LR. Binary logistic objective for XGB. | Same objectives. Use Brier for probability evaluation. | Binary logistic objective. |
| Class imbalance | LR class_weight balanced. XGB scale_pos_weight equals training negatives divided by positives. | Same. | Same XGB weighting from its own fit fold. |
| Threshold choice | AUC uses continuous scores. Any decision threshold uses validation only. | Fit isotonic and D1 tiers on validation only. Freeze for test. | Pilot reports held-out AUC. Any later threshold uses the reserved validation fold. |
| Leakage controls | Training-only scaling and PCA. Chronological D5 folds with purges. Test only for evaluation and bootstrap. | KS uses train_core versus inner-val. Vocabularies and scaling use train_core. Test SHAP uses a frozen model. | Stratify once at seed 11. Tune within training. Reserve validation and test separately. |

Table 8. Models and validation controls.

Pilot date 2026-11-19. The baseline test AUCs were 0.6145 for LR and 0.7020 averaged over XGB seeds. Compare with the paper's 0.723 and 0.732 [1]. The reported pilot configurations and seed-level scores are in results/pilot_model.json. Taiwan O_XGB test AUC was 0.7834 on 2026-11-19, compared with the chart-derived range of approximately 0.68–0.71 [3].
