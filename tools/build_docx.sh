#!/usr/bin/env bash
# Assemble report/sections/*.md into the Week 4 docx using the course template styles.
set -euo pipefail
mkdir -p out
OUT=out/6_BC_IS355_Week4_Project.docx
{ cat report/cover.md; printf '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n';
  for f in report/sections/*.md; do cat "$f"; printf '\n\n'; done; } > out/report.md
pandoc out/report.md -f markdown+pipe_tables+grid_tables -o "$OUT" \
  --reference-doc=docs/ref/template.docx --resource-path=.:report:figures
echo "Built $OUT ($(wc -w < out/report.md) words in markdown)"
