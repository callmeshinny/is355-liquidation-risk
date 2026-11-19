#!/usr/bin/env python3
"""Rubric linter for the IS355 Week 4 report (report/sections/*.md).

Usage:
  python tools/check_report.py                  # all checks
  python tools/check_report.py --only 1.2 --steps 1,2
  python tools/check_report.py --only 2         # all Part 2 checks
Prints only FAIL/WARN lines and a summary. Exit 1 if any FAIL.
"""
import argparse, glob, os, re, sys

SEC = "report/sections"
FILES = {
    "A": "00_info.md", "1.1": "11_workflow.md", "1.2": "12_steps.md", "1.3": "13_contract.md",
    "1.4": "14_model.md", "1.5": "15_env.md", "2.1": "21_hypotheses.md", "2.2": "22_overview.md",
    "2.3": "23_scenarios.md", "2.4": "24_runs.md", "2.5": "25_expected.md", "2.6": "26_schedule.md",
    "2.7": "27_risks.md", "3": "30_next.md", "refs": "90_refs.md", "appx": "95_appendix.md",
}
STEP_FIELDS = ["Purpose", "Input", "Processing", "Parameters", "Libraries / tools", "Output", "Runs",
               "Correctness check", "Errors & edge cases", "Est. run time", "Improvement"]
CARD_FIELDS = ["Objective", "Preconditions", "Input data", "Steps", "Expected result", "Pass criterion",
               "Runs & environment"]
H_FIELDS = ["Expected", "Basis", "Reject if", "If rejected"]
FUNCS = ["register_model", "set_oracle", "set_score", "set_scores_batch", "get_tier", "deposit_collateral",
         "withdraw_collateral", "borrow", "repay", "liquidate", "set_price"]
VAGUE = ["works well", "runs stably", "run stably", "low gas", "high accuracy", "many times", "good performance"]
PLACEHOLDER = re.compile(r"\[(e\.g\.|…|\.\.\.|dd/mm|x+\]|Full name)|\bTODO\b|\bTBD\b|\[insert", re.I)

out = {"FAIL": [], "WARN": []}


def read(key):
    p = os.path.join(SEC, FILES[key])
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def fail(group, msg): out["FAIL"].append(f"[{group}] {msg}")
def warn(group, msg): out["WARN"].append(f"[{group}] {msg}")


def need(group, key):
    t = read(key)
    if t is None:
        fail(group, f"missing file {FILES[key]}")
    return t


def has_all(group, text, labels, where):
    miss = [l for l in labels if l.lower() not in text.lower()]
    if miss:
        fail(group, f"{where}: missing {', '.join(miss)}")


def blocks(text, pattern):
    """Split text into {id: body} by heading regex with one capture group."""
    ms = list(re.finditer(pattern, text, re.M))
    return {m.group(1): text[m.end(): (ms[i + 1].start() if i + 1 < len(ms) else len(text))]
            for i, m in enumerate(ms)}


def check_A():
    t = need("A", "A")
    if not t: return
    has_all("A", t, ["Response to Week 3 feedback", "Changes since", "Repository"], "Part A")
    if "github.com" not in t: fail("A", "no GitHub link in Repository row")
    rows = re.findall(r"^\|\s*([1-9])\s*\|", t, re.M)
    if len(set(rows)) < 6: fail("A", f"feedback table needs 6 rows (found {len(set(rows))})")


def check_11():
    t = need("1.1", "1.1")
    if not t: return
    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", t)
    if not imgs: fail("1.1", "no workflow figure")
    for i in imgs:
        if not (os.path.exists(i) or os.path.exists(os.path.join("report", i))): fail("1.1", f"image not found: {i}")
    if "Figure 1" not in t: fail("1.1", "caption 'Figure 1.' missing")
    for k in ["I1", "I2", "I3", "I4"]:
        if k not in t: warn("1.1", f"{k} not mentioned near diagram")


def check_12(steps):
    t = need("1.2", "1.2")
    if not t: return
    bl = blocks(t, r"^#{2,5}\s*Step\s+(\d+)\b.*$")
    for s in steps:
        b = bl.get(str(s))
        if b is None:
            fail("1.2", f"Step {s} card missing (heading 'Step {s} · …')"); continue
        has_all("1.2", b, STEP_FIELDS, f"Step {s}")
        if len(b.split()) < 120: warn("1.2", f"Step {s} is short ({len(b.split())} words) — 'exactly how' level?")
    code = len(re.findall(r"^```", t, re.M)) // 2
    if code < min(4, len(steps)): warn("1.2", f"only {code} pseudo-code blocks")


def check_13():
    t = need("1.3", "1.3")
    if not t: return
    has_all("1.3", t, ["State variables", "Functions", "State machine", "Events", "forbidden",
                       "private key", "stuck", "guarantee"], "1.3")
    miss = [f for f in FUNCS if f not in t]
    if miss: fail("1.3", f"functions not specified: {', '.join(miss)}")
    if not re.search(r"!\[[^\]]*\]\([^)]*state", t): warn("1.3", "no state-machine figure")


def check_14():
    t = need("1.4", "1.4")
    if not t: return
    has_all("1.4", t, ["Optuna", "trials", "validation", "PCA", "leakage", "class"], "1.4")


def check_15():
    t = need("1.5", "1.5")
    if not t: return
    has_all("1.5", t, ["Python 3.11", "Vyper 0.4", "Ape 0.8", "Anvil", "Sepolia", "seed", "RAM"], "1.5")
    if not re.search(r"11.*22.*33.*44.*55", t): fail("1.5", "seed list [11,22,33,44,55] not stated")


def check_2():
    t = need("2.1", "2.1")
    if t:
        for h in range(1, 8):
            if f"H{h}" not in t: fail("2.1", f"H{h} missing")
        if t.lower().count("accept") + t.lower().count("criterion") < 7: warn("2.1", "acceptance criterion per H?")
    t = need("2.2", "2.2")
    t3 = need("2.3", "2.3")
    if t3:
        ids = re.findall(r"\bT([1-7])-(\d{2})\b", t3)
        cnt = {g: len({n for gg, n in ids if gg == g}) for g in "1234567"}
        mins = {"1": 5, "2": 1, "4": 5, "5": 1, "6": 2, "7": 1}
        for g, m in mins.items():
            if cnt[g] < m: fail("2.3", f"T{g}: {cnt[g]} scenarios < {m}")
        cards = blocks(t3, r"^#{3,5}\s*(T[1-7]-\d{2})\b.*$")
        for cid, body in cards.items():
            if cid[1] in "12456": has_all("2.3", body, CARD_FIELDS, cid)
        need_cards = {f"T{g}-{n}" for g, n in ids if g in "12456"}
        nocard = sorted(need_cards - set(cards))
        if nocard: fail("2.3", f"no full card (#### heading) for {', '.join(nocard[:8])}")
        miss = [f for f in FUNCS if f not in t3]
        if miss: fail("2.3", f"T3 table lacks {', '.join(miss)}")
        for kw in ["Sybil", "key", "front-run", "price manipulation"]:
            if kw.lower() not in t3.lower(): warn("2.3", f"edge-of-design T4 '{kw}' not found")
        if "not blocked" not in t3.lower() and "cannot block" not in t3.lower():
            fail("2.3", "state which T4 attacks the design does NOT block")
    t = need("2.4", "2.4")
    if t:
        has_all("2.4", t, ["unit of repetition", "n ≈", "Sepolia", "budget", "p95", "seed"], "2.4")
        if "pilot" not in t.lower(): warn("2.4", "s / s_d should come from pilot runs")
    t = need("2.5", "2.5")
    if t:
        hb = blocks(t, r"^#{3,5}\s*(H\d)\b.*$")
        for h in [f"H{i}" for i in range(1, 8)]:
            if h not in hb: fail("2.5", f"{h} block missing (#### H{h[1]} …)")
            else: has_all("2.5", hb[h], H_FIELDS, h)
        if "anvil" in t.lower() and "latency" in t.lower() and "not" not in t.lower():
            warn("2.5", "make clear Anvil latency is not real-chain latency")
    t = need("2.6", "2.6")
    if t:
        has_all("2.6", t, ["M1", "M2", "M3", "M4", "buffer", "Owner", "Depends"], "2.6")
        if not re.search(r"!\[[^\]]*\]\([^)]*gantt", t, re.I): fail("2.6", "Gantt figure missing")
    t = need("2.7", "2.7")
    if t:
        risks = re.findall(r"^\|\s*R\d+\s*\|", t, re.M)
        if len(risks) < 3: fail("2.7", f"{len(risks)} risks < 3 (rows '| R1 | …')")
        has_all("2.7", t, ["Likelihood", "Impact", "Backup"], "2.7")


def check_global():
    texts = {k: read(k) for k in FILES}
    alltxt = "\n".join(v for v in texts.values() if v)
    for k, v in texts.items():
        if not v: continue
        for m in PLACEHOLDER.finditer(v): fail("text", f"{FILES[k]}: placeholder '{m.group(0)}'")
        for p in VAGUE:
            if p in v.lower(): fail("text", f"{FILES[k]}: vague phrase '{p}'")
    if "pilot" in alltxt.lower():
        ap = texts.get("appx") or ""
        if "Appendix A" not in ap: fail("appx", "pilot results used but Appendix A missing")
        for p in set(re.findall(r"results/[\w\-/]+\.json", alltxt)):
            if not os.path.exists(p): fail("appx", f"cited {p} does not exist")
    for n in re.findall(r"\[(\d+)\]", alltxt):
        if int(n) > 6: warn("refs", f"citation [{n}] not in reference list")
    tabs = len(re.findall(r"^Table \d+\.", alltxt, re.M)); figs = len(re.findall(r"^Figure \d+\.", alltxt, re.M))
    if tabs < 10: warn("text", f"only {tabs} 'Table n.' captions")
    if figs < 3: warn("text", f"only {figs} 'Figure n.' captions (need workflow, state machine, Gantt)")
    body = "\n".join(texts[k] or "" for k in FILES if k not in ("refs", "appx"))
    words = len(re.sub(r"[|\-:]+", " ", body).split())
    pages = words / 430
    print(f"INFO body ≈ {words} words ≈ {pages:.1f} pages (target 12–18; check in Word)")
    if pages > 20: warn("text", "likely over 18 pages — cut prose, keep tables")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="A,1.1,1.2,1.3,1.4,1.5,2 (comma list)")
    ap.add_argument("--steps", default="1,2,3,4,5,6,7,8")
    a = ap.parse_args()
    steps = [int(x) for x in a.steps.split(",")]
    groups = a.only.split(",") if a.only else ["A", "1.1", "1.2", "1.3", "1.4", "1.5", "2", "global"]
    run = {"A": check_A, "1.1": check_11, "1.2": lambda: check_12(steps), "1.3": check_13,
           "1.4": check_14, "1.5": check_15, "2": check_2, "global": check_global}
    for g in groups:
        run[g]()
    for k in ("FAIL", "WARN"):
        for m in out[k]: print(k, m)
    print(f"SUMMARY {len(out['FAIL'])} FAIL, {len(out['WARN'])} WARN ({','.join(groups)})")
    sys.exit(1 if out["FAIL"] else 0)


if __name__ == "__main__":
    main()
