"""Assemble the canonical report sections and number tables in reading order."""

import re
from pathlib import Path

REPORT = Path("report")
PAGE_BREAK = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```'


def main():
    sections = [path.read_text().strip() for path in sorted((REPORT / "sections").glob("*.md"))]
    parts = [(REPORT / "cover.md").read_text().strip(), PAGE_BREAK, *sections]
    table = 0

    def renumber(match):
        nonlocal table
        table += 1
        return f"Table {table}."

    return re.sub(r"(?m)^Table \d+\.", renumber, "\n\n".join(parts) + "\n")


if __name__ == "__main__":
    print(main(), end="")
