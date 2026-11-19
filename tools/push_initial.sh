#!/usr/bin/env bash
# Push only what the group needs to GitHub; keep data, models and secrets local.
# Usage (from the repo root):
#   bash tools/push_initial.sh "<path to Khanh's Drive folder>" "<Khanh's GitHub email>"
# Example:
#   bash tools/push_initial.sh ~/Downloads/drive-download "khanh@example.com"
set -euo pipefail

SRC="${1:?Give the path to the Khanh folder (the one with taiwan/, processed/, Data/ ...)}"
KHANH_EMAIL="${2:?Give Khanh GitHub email (or <ID>+quangkhanh1029@users.noreply.github.com)}"
KHANH="Tran Quang Khanh <${KHANH_EMAIL}>"

[ -d .git ] || { echo "Run this from the repo root (is355-liquidation-risk)."; exit 1; }
git remote get-url origin >/dev/null 2>&1 || { echo "No 'origin' remote. Run: git remote add origin https://github.com/<you>/is355-liquidation-risk.git"; exit 1; }
[ -d "$SRC" ] || { echo "Folder not found: $SRC"; exit 1; }

# 1) Make sure private things are ignored ------------------------------------------
for p in ".venv/" "data/" "models/" ".env" ".env.*" "*.key" "*.pem" "*keystore*" "*.parquet" "*.rds" \
         "*.pkl" "*.joblib" "*.ubj" "*.xls" "*.xlsx" "*.csv" ".DS_Store" ".ipynb_checkpoints/" "logs/" \
         "__pycache__/" ".pytest_cache/" ".hypothesis/" ".build/" "out/report.md"; do
  grep -qxF "$p" .gitignore 2>/dev/null || echo "$p" >> .gitignore
done
# small result tables we DO want in git
grep -qxF '!results/*.csv' .gitignore || echo '!results/*.csv' >> .gitignore

# 2) Copy files ----------------------------------------------------------------------
mkdir -p legacy legacy/figures data/raw data/processed
CODE=(check_finsurvival_data.ipynb 02_model_finsurvival.ipynb finsurvival_borrow_liquidated_eda.ipynb
      inspect_borrow_liquidated.py make_dataset_figures.py)
for f in "${CODE[@]}"; do
  if [ -f "$SRC/$f" ]; then cp "$SRC/$f" legacy/; else echo "WARN missing $f"; fi
done
# figures: only small images go to git
if [ -d "$SRC/figures" ]; then
  find "$SRC/figures" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.svg' \) -size -3M \
    -exec cp {} legacy/figures/ \;
fi
# data stays local (ignored by data/)
[ -d "$SRC/processed" ] && cp -R "$SRC/processed/." data/processed/
[ -d "$SRC/taiwan" ]    && mkdir -p data/raw/taiwan && cp -R "$SRC/taiwan/." data/raw/taiwan/
if [ -d "$SRC/Data" ] && [ ! -d data/raw/finsurvival/Data ]; then
  mkdir -p data/raw/finsurvival && cp -R "$SRC/Data" data/raw/finsurvival/
  for r in dataLoader.R dataPreprocessing.R; do [ -f "$SRC/$r" ] && cp "$SRC/$r" data/raw/finsurvival/; done
fi
[ -d "$SRC/models" ] && mkdir -p data/legacy_models && cp -R "$SRC/models/." data/legacy_models/

# 3) Safety checks before anything is committed -----------------------------------
SECRET_RE='(PRIVATE_KEY|private_key|api[_-]?key|alchemy\.com/v2/[A-Za-z0-9_-]{10,}|infura\.io/v3/[a-f0-9]{20,}|0x[a-fA-F0-9]{64}|BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{20,})'
if grep -rIlE "$SECRET_RE" legacy/ docs/ tools/ AGENTS.md 2>/dev/null | grep -v 'tools/push_initial.sh'; then
  echo "STOP: possible secret found in the files above. Remove it, then run again."; exit 1
fi
BIG=$(find legacy docs tools report -type f -size +5M 2>/dev/null || true)
[ -z "$BIG" ] || { echo "STOP: files > 5 MB would be pushed:"; echo "$BIG"; exit 1; }

# 4) Commits: kit as you, Week 3 code as Khanh ---------------------------------------
git add -A -- . ':!legacy'
git diff --cached --quiet || git commit -m "P0.1: add agent kit (AGENTS, checklist, context, tools) and gitignore"
git add legacy
git diff --cached --quiet || git commit --author="$KHANH" -m "Week 3 code by Khanh (moved from Google Drive to legacy/)"

# 5) Show exactly what is tracked, then push -----------------------------------------
echo "---- Files that will be on GitHub ----"; git ls-files
echo "---- Kept local (ignored) ----"; git status --ignored --short | grep '^!!' | head -n 20
git log --format='%h  author=%an  committer=%cn  %s' -n 3
read -r -p "Push to GitHub now? [y/N] " ok
[ "$ok" = "y" ] && git push -u origin "$(git branch --show-current)" && echo "Pushed."
