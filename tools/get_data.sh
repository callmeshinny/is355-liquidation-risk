#!/usr/bin/env bash
# Downloads only the FinSurvival Borrow→Account Liquidated files (~330 MB). Run from repo root.
set -euo pipefail
mkdir -p data/raw
if [ ! -d data/raw/finsurvival ]; then
  git clone --filter=blob:none --no-checkout --depth 1 \
    https://github.com/Large-Transaction-Models/DMLR_DeFi_Survival_Benchmark data/raw/finsurvival
fi
cd data/raw/finsurvival
git sparse-checkout init --no-cone
git sparse-checkout set '/Data/Survival_Data/Borrow/X_train/' '/Data/Survival_Data/Borrow/X_test/' \
  '/Data/Survival_Data/Borrow/Account Liquidated/' '/dataLoader.R' '/dataPreprocessing.R' '/Data/README.md'
git checkout
du -sh Data/Survival_Data/Borrow/* 
cd ../../..
.venv/bin/python -c "from ucimlrepo import fetch_ucirepo; d=fetch_ucirepo(id=350); d.data.original.to_csv('data/raw/taiwan.csv', index=False); print('Taiwan', d.data.original.shape)"
echo "Data ready in data/raw/"
