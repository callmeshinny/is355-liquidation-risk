"""Assemble the concise report and preserve detailed specifications in appendices."""

import re
from pathlib import Path

REPORT = Path("report")
SECTIONS = REPORT / "sections"
DETAILS = {
    "B": ("Method specifications", ("12_steps", "13_contract")),
    "C": ("Test scenario specifications", ("22_overview", "23_scenarios")),
    "D": ("Result criteria and rationale", ("25_expected",)),
}
PAGE_BREAK = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```'


def main():
    blocks = re.split(r"(?m)^<!-- (\w+) -->\s*\n", (REPORT / "concise_sections.md").read_text())
    concise = dict(zip(blocks[1::2], blocks[2::2]))
    originals = {path.stem: path.read_text().strip() for path in sorted(SECTIONS.glob("*.md"))}
    parts = [(REPORT / "cover.md").read_text(), PAGE_BREAK]
    parts.extend(concise.get(name, text).strip() for name, text in originals.items())
    for letter, (title, names) in DETAILS.items():
        parts.extend((PAGE_BREAK, f"# Appendix {letter} — {title}"))
        for name in names:
            text = re.sub(r"(?m)^!\[Loan state machine\]\([^\n]+\)\n\nFigure 2\.[^\n]*\n\n",
                          "", originals[name])
            parts.append(text)
    table = 0

    def renumber(match):
        nonlocal table
        table += 1
        return f"Table {table}."

    return re.sub(r"(?m)^Table \d+\.", renumber, "\n\n".join(parts) + "\n")


if __name__ == "__main__":
    print(main(), end="")
