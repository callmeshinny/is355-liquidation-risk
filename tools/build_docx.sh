#!/usr/bin/env bash
# Assemble report/sections/*.md into the Week 4 docx using the course template styles.
set -euo pipefail
mkdir -p out
OUT=out/6_BC_IS355_Week4_Project.docx
.venv/bin/python tools/assemble_report.py > out/report.md
pandoc out/report.md -f markdown+pipe_tables+grid_tables-implicit_figures -o "$OUT" \
  --reference-doc=docs/ref/template.docx --resource-path=.:report:figures
.venv/bin/python tools/compact_docx.py "$OUT"

echo "Built $OUT ($(wc -w < out/report.md) words in markdown)"
