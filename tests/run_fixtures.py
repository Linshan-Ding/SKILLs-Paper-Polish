#!/usr/bin/env python3
"""Self-test for stylecheck.py and style_baseline.py, which live as code blocks in
paper-polish/references/stylecheck.md.

    python tests/run_fixtures.py                 # extract both scripts to a temp folder and run the fixtures
    python tests/run_fixtures.py --extract DIR   # only write stylecheck.py and style_baseline.py into DIR

Planted fixtures must raise every listed finding, the listed number of FAILs, and none of
the listed false alarms; clean fixtures must pass. Run it after every change to the
scripts, once the new code is back in stylecheck.md. Exit code 1 on any mismatch.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOC = REPO / "paper-polish" / "references" / "stylecheck.md"
FIX = Path(__file__).resolve().parent / "fixtures"

# fixture -> (number of FAIL lines, patterns that must each match a line, patterns that must match none)
EXPECT = {
    "zh-planted.md": (6, [
        r"FAIL   prose semicolon at zh-planted\.md:15$",                   # the semicolon after a literal %
        r"FAIL .*paragraph with nothing concrete.*过滤器",                   # headings are sections: item 25 applies
        r"FAIL   abstract is broken into paragraphs",
        r"FAIL   ASCII straight quotes around Chinese text at zh-planted\.md:26",
        r"FAIL .*summary paragraph outside the conclusion: '综上，过滤规则只依赖",
        r"note   half-width ',' next to a Chinese character at zh-planted\.md:28",
    ], [r"zh-planted\.md:(?:9|13|17|18|19|20)\b",                          # keywords, status line, table marker, table rows
        r"summary paragraph outside the conclusion: '综上，过滤规则在三个基准"]),
    "zh-clean.md": (0, [], [r"FAIL"]),
    "zh-planted.tex": (2, [
        r"FAIL .*banned phrase '值得注意的是'",
        r"FAIL   ASCII straight quotes around Chinese text at zh-planted\.tex:7",
        r"note   half-width ',' next to a Chinese character at zh-planted\.tex:7",
    ], [r"zh-planted\.tex:(?:8|9)\b", r"sentence-initial connectives"]),
    "en-planted.md": (6, [
        r"FAIL   prose semicolon at en-planted\.md:19$",
        r"FAIL   mid-sentence colon at en-planted\.md:33$",                # the colon inside a link text
        r"FAIL .*paragraph with nothing concrete.*The filter compares",
        r"FAIL   abstract is broken into paragraphs",
        r"FAIL   en-planted\.md:23 table uses arrow glyphs",
        r"FAIL .*summary paragraph outside the conclusion: 'In summary, the rule depends",
    ], [r"dash in prose", r"en-planted\.md:(?:1|2|3|13|17|21)\b",          # front matter, keywords, quote, thematic break
        r"summary paragraph outside the conclusion: 'In summary, the rule works"]),
    "en-clean.md": (0, [], [r"FAIL"]),
    "en-planted.tex": (15, [
        r"FAIL   prose semicolon at en-planted\.tex:16$",
        r"FAIL .*3 sentence-initial connectives",
        r"FAIL .*banned phrase 'it is worth noting'",
        r"FAIL .*5 hedges", r"FAIL .*stacked hedge",
        r"FAIL   mid-sentence colon at en-planted\.tex:19$",
        r"FAIL   dash in prose at en-planted\.tex:20$",
        r"FAIL   bold inside running text at en-planted\.tex:21",
        r"FAIL .*paragraph with nothing concrete",
        r"FAIL .*citation cluster of 5 keys",
        r"FAIL   abstract is broken into paragraphs",
        r"FAIL   operator standing in for words at en-planted\.tex:22",   # +2.1\% written the LaTeX way
        r"FAIL .*hyphen chain 'gradient-alignment-based'",
        r"FAIL   en-planted\.tex:30 proof of \d+ words with no displayed derivation",
        r"FAIL .*summary paragraph outside the conclusion",
        r"note .*obscure word\(s\) \['myriad -> many'\]",                  # one phrase, one hit
        r"note   CamelCase name \['GradSieve'\]",                           # HumanEval and HuggingFace are known names
    ], [r"self-made acronyms", r"roadmap paragraph"]),                     # BERT and RAG are standard acronyms
    "en-clean.tex": (0, [], [r"FAIL"]),                                    # \partial in the abstract is not \par
}


def extract(dest: Path) -> list[Path]:
    md = DOC.read_text(encoding="utf-8")
    out = []
    for name in ("stylecheck.py", "style_baseline.py"):
        m = re.search(r"^## " + re.escape(name) + r"[^\n]*\n\n`{3}python\n(.*?)\n`{3}\n", md, re.S | re.M)
        if not m:
            raise SystemExit(f"no code block for {name} in {DOC}")
        src = m.group(1) + "\n"
        if "`" * 3 in src:
            raise SystemExit(f"{name}: three backticks in a row would cut the code block in stylecheck.md")
        ast.parse(src)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / name).write_text(src, encoding="utf-8")
        out.append(dest / name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--extract", type=Path, default=None, help="write the two scripts into this folder and stop")
    a = ap.parse_args()
    if a.extract is not None:
        for p in extract(a.extract):
            print(f"written {p}")
        return 0
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        check, baseline = extract(tmp / "scripts")
        for name, (n_fail, must, never) in EXPECT.items():
            r = subprocess.run([sys.executable, str(check), str(FIX / name), "--baseline", str(tmp / "none.json"),
                                "--outline-dir", str(tmp / "outline")], capture_output=True, text=True)
            lines = (r.stdout + r.stderr).splitlines()
            fails = [ln for ln in lines if ln.startswith("  FAIL")]
            errs = []
            if len(fails) != n_fail:
                errs.append(f"{len(fails)} FAIL lines, expected {n_fail}")
            if (r.returncode != 0) != (n_fail > 0):
                errs.append(f"exit code {r.returncode}")
            errs += [f"missing: {p}" for p in must if not any(re.search(p, ln) for ln in lines)]
            errs += [f"false alarm: {p}" for p in never if any(re.search(p, ln) for ln in lines)]
            print(f"{'ok  ' if not errs else 'FAIL'}  {name}: {len(fails)} FAIL lines" + "".join(f"\n        {e}" for e in errs))
            if errs:
                print("\n".join("        | " + ln for ln in lines))
            bad += bool(errs)
        # the calibration script shares the checker's word lists and its output is accepted back by the checker
        corpus = tmp / "corpus"
        corpus.mkdir()
        for name in ("en-clean.tex", "en-planted.tex"):
            (corpus / name).write_text((FIX / name).read_text(encoding="utf-8"), encoding="utf-8")
        out = tmp / "style_baseline.json"
        r = subprocess.run([sys.executable, str(baseline), "--corpus", str(corpus), "--out", str(out)], capture_output=True, text=True)
        ok = r.returncode == 0 and out.exists() and {"connectives", "sent_cv", "vocabulary", "hyphenated"} <= set(json.loads(out.read_text(encoding="utf-8")))
        one = tmp / "one-connective.txt"
        one.write_text("Moreover, the filter keeps aligned samples and accuracy rises by 2.1 points in Table 2.\n", encoding="utf-8")
        r2 = subprocess.run([sys.executable, str(check), str(one), "--baseline", str(out), "--outline-dir", str(tmp / "outline")],
                            capture_output=True, text=True)
        ok2 = r2.returncode == 0 and "baseline: style_baseline.json" in r2.stdout   # a calibrated budget never drops below one
        print(f"{'ok  ' if ok and ok2 else 'FAIL'}  style_baseline.py writes a baseline the checker loads; one connective stays within budget")
        bad += not (ok and ok2)
    print(f"\n{len(EXPECT) + 1 - bad} of {len(EXPECT) + 1} passed.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
