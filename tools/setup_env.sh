#!/usr/bin/env bash
# One-time setup on macOS (Apple Silicon). Run from the repo root: bash tools/setup_env.sh
set -euo pipefail
command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
brew install uv pandoc graphviz libomp git
if ! command -v anvil >/dev/null; then
  curl -L https://foundry.paradigm.xyz | bash
  export PATH="$HOME/.foundry/bin:$PATH"
  foundryup
fi
uv venv -p 3.11 .venv
source .venv/bin/activate
# chain stack first (lets Ape choose its own web3 version)
uv pip install "eth-ape==0.8.54" "ape-vyper==0.8.13" "ape-foundry==0.8.13" "vyper==0.4.3"
# ML / data / test / report
uv pip install pandas pyarrow pyreadr xlrd ucimlrepo scikit-learn xgboost shap optuna scipy nbconvert \
  matplotlib streamlit hypothesis pytest python-dotenv
cat > ape-config.yaml <<'YAML'
name: is355-liquidation-risk
plugins:
  - name: vyper
  - name: foundry
vyper:
  version: 0.4.3
default_ecosystem: ethereum
ethereum:
  default_network: local
  local:
    default_provider: foundry
YAML
ape plugins list
anvil --version
python -c "import xgboost, sklearn, vyper; print('OK', xgboost.__version__, sklearn.__version__, vyper.__version__)"
echo "Setup done. Next: bash tools/get_data.sh"
