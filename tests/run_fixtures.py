#!/usr/bin/env python3
"""Self-test for stylecheck.py and style_baseline.py, which live as code blocks in
paper-polish/references/stylecheck.md.

    python tests/run_fixtures.py                 # extract both scripts to a temp folder and run the fixtures
    python tests/run_fixtures.py --extract DIR   # only write stylecheck.py and style_baseline.py into DIR

Planted fixtures must raise every listed finding, the listed number of FAILs, and none of
the listed false alarms; clean fixtures must pass. A key may carry command-line arguments
after the file name ("en-rebuttal.md --genre rebuttal"), so one fixture can be checked
under two genres. Run it after every change to the scripts, once the new code is back in
stylecheck.md. Exit code 1 on any mismatch.
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

# fixture [arguments] -> (number of FAIL lines, patterns that must each match a line, patterns that must match none)
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
        r"FAIL .*6 hedges in section 'Method'", r"FAIL .*stacked hedge",
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
    "en-clean.tex": (0, [], [r"FAIL"]),                                    # \partial in the abstract is not \par; the colons in
                                                                           # \Cref{fig:conv,...} and \citep[..][..]{DBLP:conf/...} are not prose
    # item 17, defensive writing: every kind once, and the legitimate forms next to them
    "en-defensive.tex": (12, [
        r"FAIL   en-defensive\.tex: 3 hedges in section 'Experiments' \(budget 2\)",
        r"FAIL   en-defensive\.tex:10 meta-comment 'it should be noted'",
        r"FAIL   en-defensive\.tex:11 pre-emptive defence 'one might argue'",
        r"FAIL   en-defensive\.tex:12 disclaimer 'we do not claim' outside the limitations section",
        r"FAIL   en-defensive\.tex:13 apology or excuse 'due to space limitations'",
        r"FAIL   en-defensive\.tex:17 vague qualifier 'in some cases'",
        r"FAIL   en-defensive\.tex:20 stacked hedge in: The cost could potentially grow",
        r"FAIL   en-defensive\.tex:21 pre-emptive defence 'admittedly'",
        r"FAIL   en-defensive\.tex:22 scope caveat 'beyond the scope of this paper' outside",
        r"FAIL   en-defensive\.tex:30 apology or excuse 'unfortunately'",
        r"FAIL   en-defensive\.tex:31 scope caveat 'leave larger models to future work'",
        r"FAIL   novelty hedge 'to the best of our knowledge' 2 times outside the abstract \(en-defensive\.tex:9, en-defensive\.tex:23\)",
        r"note   en-defensive\.tex:34 disclaimer 'we do not claim' inside the limitations section",
        r"note   en-defensive\.tex:35 scope caveat 'beyond the scope of this paper' inside the limitations section",
    ], [r"en-defensive\.tex:(?:4|18|19|24|27|28)\b",                        # abstract, named condition, anchored, exempt, two hedges
        r"FAIL .*en-defensive\.tex:3[45]\b"]),                              # the limitations section
    "zh-defensive.md": (10, [
        r"FAIL   zh-defensive\.md:9 meta-comment '需要指出的是'",
        r"FAIL   zh-defensive\.md:9 pre-emptive defence '有人可能会认为'",
        r"FAIL   zh-defensive\.md:9 disclaimer '本文并不声称' outside the limitations section",
        r"FAIL   zh-defensive\.md:9 apology or excuse '限于篇幅'",
        r"FAIL   zh-defensive\.md:13 vague qualifier '在某些情况下'",
        r"FAIL   zh-defensive\.md:13 stacked hedge in: 该方法可能在一定程度上",
        r"FAIL   zh-defensive\.md:13 pre-emptive defence '诚然'",
        r"FAIL   zh-defensive\.md:13 scope caveat '超出了本文的研究范围'",
        r"FAIL   zh-defensive\.md:17 apology or excuse '遗憾的是'",
        r"FAIL   zh-defensive\.md:17 scope caveat '留待今后'",
        r"note   zh-defensive\.md:23 disclaimer '本文并不声称' inside the limitations section",
    ], [r"novelty hedge",                                                    # once in the abstract, once in the body
        r"\d+ hedges",                                                       # 尽可能 and 所有可能的 are not hedges
        r"zh-defensive\.md:(?:5|19)\b", r"FAIL .*zh-defensive\.md:23\b"]),   # abstract, exempt line, limitations
    "en-rebuttal.md": (8, [                                                  # a response letter checked as a paper
        r"FAIL   en-rebuttal\.md:7 meta-comment 'we would like to clarify'",
        r"FAIL   en-rebuttal\.md:8 disclaimer 'we acknowledge that'",
        r"FAIL   en-rebuttal\.md:9 scope caveat 'beyond the scope of this paper'",
        r"FAIL   en-rebuttal\.md:16 apology or excuse 'we apologize'",
    ], [r"en-rebuttal\.md:5\b", r"\d+ hedges"]),                             # the quoted reviewer comment is not prose
    "en-rebuttal.md --genre rebuttal": (2, [
        r"FAIL   en-rebuttal\.md:17 stacked hedge",
        r"FAIL   en-rebuttal\.md:17 vague qualifier 'in some cases'",
        r"note   en-rebuttal\.md:7 meta-comment 'we would like to clarify' -- a rebuttal may keep it",
        r"note   en-rebuttal\.md:16 apology or excuse 'we apologize' -- a rebuttal may keep it",
    ], [r"we acknowledge that", r"beyond the scope"]),                       # scope is what the letter is about
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
        for key, (n_fail, must, never) in EXPECT.items():
            name, *extra = key.split()
            r = subprocess.run([sys.executable, str(check), str(FIX / name), *extra, "--baseline", str(tmp / "none.json"),
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
            print(f"{'ok  ' if not errs else 'FAIL'}  {key}: {len(fails)} FAIL lines" + "".join(f"\n        {e}" for e in errs))
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
