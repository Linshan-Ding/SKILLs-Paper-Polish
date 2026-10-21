# 文体机检 stylecheck.py 与语料校准 style_baseline.py

本文件是 `paper-polish` 的代码层：`stylecheck.py` 对任意 `.tex` / `.md` / `.txt` 跑 14 项文体检查（项号
14–27，与家族仓库 `check.py` 的 1–13、28–29 连续；`check.py` 直接 `from stylecheck import run_style_checks`），
`style_baseline.py` 从目标刊物已发表论文统计阈值。生成工程时两者落到 `paper_assets/scripts/`；单独使用时
把代码块复制成同名文件即可。

## 用法

```
python stylecheck.py sections/*.tex                       # 每个分节文件单独计数（连接词、对冲、密度按节）
python stylecheck.py paper/zh-draft.tex --zh              # 中文；不加 --zh 时 CJK 占比 >30% 自动识别
python stylecheck.py draft.md notes.txt                   # Markdown / 纯文本：代码围栏与标题剥掉，**加粗** 计为句中强调
python stylecheck.py sections/*.tex --baseline style_baseline.json
python stylecheck.py sections/*.tex --outline-dir paper   # 反向大纲 reverse-outline.md 写到哪
python style_baseline.py --corpus ~/venue-papers          # 2–3 篇目标刊物论文（.tex/.txt）→ style_baseline.json
```

退出码：有 FAIL 为 1。合法例外在该行加 `% style-exempt` 注释（数学与伪代码里的分号冒号、引用他人原文、
术语首次定义的强调）。

## 阈值（内置默认值；`style_baseline.json` 存在时按语料 ±20% 覆盖）

| 键 | 默认 | 含义 | 语料覆盖 |
|---|---|---|---|
| `connectives` | 2 | 每节句首连接词上限 | 是（×1.2） |
| `hedges` | 2 | 每节对冲词上限；堆叠对冲无论多少都 FAIL | 否 |
| `triplets` | 2 | 每节"X, Y, and Z"三连排比上限 | 否 |
| `paragraph_leads` | 4 | 每节 `\paragraph{}` 引导词上限 | 否 |
| `sent_cv_min` | 0.35 | 句长变异系数下限（节内句数 ≥8 才算） | 是（×0.8） |
| `intensifier_per_k` | 3.0 | 强化副词每千词上限（命中 ≥3 才判） | 是 |
| `generic_verb_per_k` | 6.0 | 泛动词每千词上限 | 是 |
| `abstract_noun_per_k` | 8.0 | 抽象名词每千词上限 | 是 |
| `cluster` | 4 | 一处引用的键数上限 | 否 |
| `acronym_min_uses` | 10 | 方法总名之外的自造缩写最少使用次数 | 否 |
| `self_acronyms` | 1 | 免费的自造缩写个数（方法总名） | 否 |

词表（英文连接词、禁用句式、对冲、强化副词、泛动词、抽象名词、效果形容词、常见领域缩写白名单；中文
对应表）在脚本顶部，按领域增删后把改动记进交付说明。

## stylecheck.py

```python
#!/usr/bin/env python3
"""Prose-style checks for academic text (items 14-27 of the manuscript checker), standalone.

    python stylecheck.py sections/*.tex                  # LaTeX sections
    python stylecheck.py paper/zh-draft.tex --zh         # Chinese text (auto-detected when >30% CJK)
    python stylecheck.py draft.md notes.txt              # Markdown / plain text (**bold** counts as emphasis)
    python stylecheck.py sections/*.tex --baseline style_baseline.json

Items
 14. no semicolons survive in the running prose
 15. sentence-initial connectives stay within budget per section
 16. none of the banned stock phrases appears
 17. hedging stays within budget and never stacks
 18. coined names and self-made acronyms stay within the naming budget
 19. no mid-sentence colon in the running prose
 20. no dash used as a parenthetical in the running prose
 21. no bold or italic emphasis inside a sentence; run-in headings within budget
 22. the abstract is a single paragraph
 23. sentence length varies; triplet lists stay within budget
 24. intensifiers, generic verbs and abstract nouns stay within density limits
 25. every prose paragraph in method/experiment sections carries something concrete
 26. no citation cluster of more than four keys
 27. a reverse outline (first sentence of every paragraph) is written for review

The numbering continues the manuscript checker's items 1-13 (consistency and venue
limits, in check.py of the opt-paper-manuscript skill), which imports run_style_checks
from this file. A line that legitimately breaks a rule carries a `% style-exempt`
comment. Thresholds come from style_baseline.json when present (style_baseline.py
measures them from published papers in the target venue) and from the built-in
defaults otherwise. Exit code 1 on any FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path


def strip_comments(s: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", s)


# ---- 14-27: prose style ---------------------------------------------------
# Written drafts, not the revision pass, are where style is won: these checks
# run after every section is drafted, then once more over the whole manuscript.

MATH_ENVS = r"(?:equation|align|gather|multline|eqnarray|algorithmic|tabular|tabularx|thebibliography|center|titlepage)\*?"
# Macros whose argument is structural text (captions, placeholders, notes), not running prose.
STRUCTURAL_MACROS = {"caption": 1, "figplace": 4, "draftnote": 1, "label": 1, "includegraphics": 1,
                     "input": 1, "bibliography": 1, "cite": 1, "citep": 1, "citet": 1,
                     "ref": 1, "eqref": 1, "texttt": 1, "url": 1}


def strip_macro(t: str, name: str, nargs: int) -> str:
    """Remove \\name{...}{...} with balanced braces, keeping newlines for line numbers."""
    out, i, pat = [], 0, re.compile(r"\\" + name + r"\*?(?:\[[^\]]*\])?\s*\{")
    while True:
        m = pat.search(t, i)
        if not m:
            out.append(t[i:]); break
        out.append(t[i:m.start()])
        j, removed = m.end() - 1, 0
        while removed < nargs and j < len(t) and t[j] == "{":
            depth, k = 0, j
            while k < len(t):
                depth += t[k] == "{"
                depth -= t[k] == "}"
                k += 1
                if depth == 0:
                    break
            out.append("\n" * t[j:k].count("\n")); j, removed = k, removed + 1
            while j < len(t) and t[j] in " \t":
                j += 1
        out.append(" "); i = j
    return "".join(out)


def prose_of(text: str) -> str:
    """Strip everything that legitimately carries semicolons, colons, bold or keywords.

    Multi-line strips keep their newlines so line numbers still match the
    source file (the style-exempt lookup depends on that)."""
    keep_lines = lambda m: "\n" * m.group(0).count("\n")
    t = strip_comments(text)
    if "\\begin{document}" in t:                              # single-file sources: drop the preamble
        i = t.index("\\begin{document}")
        t = "\n" * t[:i].count("\n") + t[i:]
    t = re.sub(r"\\(?:re)?newcommand\*?\{[^}]*\}(?:\[\d\])*\{.*?\}\s*$", keep_lines, t, flags=re.M | re.S)
    t = re.sub(r"^.*(?:\\noindent\s*\\textbf\{(?:关键词|Highlights|Keywords)|通讯作者|Corresponding author)[^\n]*$", "", t, flags=re.M)
    t = re.sub(r"〔[^〕]*〕", " ", t)                              # template placeholders
    t = re.sub(r"\\begin\{(%s)\}.*?\\end\{\1\}" % MATH_ENVS, keep_lines, t, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", keep_lines, t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " ", t)
    t = re.sub(r"\\\[.*?\\\]", keep_lines, t, flags=re.S)
    for name, n in STRUCTURAL_MACROS.items():
        t = strip_macro(t, name, n)
    t = re.sub(r"\\item\[[^\]]*\]", r"\\item", t)          # list labels such as \item[\textbf{A1}]
    t = re.sub(r"\\(?:section|subsection|subsubsection|paragraph)\*?\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", t)
    return t


# ---- word lists: English -------------------------------------------------
CONNECTIVES = ("moreover", "furthermore", "additionally", "in addition", "notably",
               "consequently", "specifically", "overall", "meanwhile", "nevertheless", "thus")
BANNED = ("it is worth noting", "plays a crucial role", "plays a pivotal role",
          "delve into", "leverage", "in this section, we will", "aims to")
HEDGES = ("may ", "might ", "could potentially", "to some extent", "relatively ", "arguably")
INTENSIFIERS = ("significantly", "substantially", "remarkably", "effectively", "seamlessly",
                "comprehensively", "robustly", "dramatically", "greatly", "highly")
GENERIC_VERBS = ("facilitate", "enable", "ensure", "enhance", "demonstrate", "exhibit", "achieve", "utilize")
ABSTRACT_NOUNS = ("framework", "paradigm", "mechanism", "scheme", "module", "pipeline", "strategy")
NAME_ADJ = ("efficient", "robust", "novel", "smart", "adaptive", "dynamic", "hierarchical", "intelligent")
SUFFIX = r"(?:aware|driven|guided|enhanced|adaptive|based|oriented)"
COMMON_ACRONYMS = {"PPO", "GNN", "GAT", "GCN", "DRL", "RL", "VRP", "TSP", "JSSP", "FJSP", "CVRP", "MDP",
                   "MLP", "CNN", "RNN", "LSTM", "LLM", "GPU", "CPU", "SOTA", "MIP", "MILP", "CP", "GA",
                   "SA", "PSO", "TS", "LKH", "HV", "IGD", "OOD", "API", "CI", "SGD", "KL", "GAE",
                   "AM", "POMO", "OR", "AI", "ML", "DL", "NN", "SGD", "FIFO", "SPT", "MWKR", "LoRA"}
SUMMARY_TAIL = r"^(this|the proposed|our)\s+(design|approach|mechanism|strategy|scheme|framework|module)\s+(ensures|guarantees|enables|allows|makes)"

# ---- word lists: Chinese -------------------------------------------------
ZH_CONNECTIVES = ("此外", "而且", "另外", "值得注意的是", "综上所述", "首先", "其次", "最后", "总之", "与此同时")
ZH_BANNED = ("值得注意的是", "综上所述", "旨在", "本文所提出的")
ZH_HEDGES = ("可能", "或许", "在一定程度上", "某种程度上")
ZH_INTENSIFIERS = ("显著地", "有效地", "极大地", "大幅", "充分地", "全面地")
ZH_GENERIC_VERBS = ("实现了", "有助于", "促进了", "提升了")
ZH_ABSTRACT_NOUNS = ("框架", "范式", "策略", "模块", "体系")
ZH_SUMMARY_TAIL = r"^(这一|该|上述)(设计|机制|做法|策略)(保证|确保|使得)"

# ---- thresholds: built-in defaults, overridden by style_baseline.json ---
TH_DEFAULT = dict(connectives=2, hedges=2, triplets=2, paragraph_leads=4, sent_cv_min=0.35,
                  intensifier_per_k=3.0, generic_verb_per_k=6.0, abstract_noun_per_k=8.0,
                  cluster=4, acronym_min_uses=10, self_acronyms=1)


def load_thresholds(baseline, notes: list[str]) -> dict:
    """Built-in defaults, loosened/tightened by style_baseline.json (made by style_baseline.py)."""
    TH = dict(TH_DEFAULT)
    if baseline is not None and Path(baseline).exists():
        base = json.loads(Path(baseline).read_text(encoding="utf-8"))
        for k in ("intensifier_per_k", "generic_verb_per_k", "abstract_noun_per_k", "connectives"):
            if k in base:
                TH[k] = round(base[k] * 1.2, 2)
        if "sent_cv" in base:
            TH["sent_cv_min"] = round(base["sent_cv"] * 0.8, 2)
        notes.append(f"baseline: {Path(baseline).name} (published-paper thresholds, +/-20%)")
    return TH


def plain_to_texish(text: str) -> str:
    """Markdown / plain text -> the subset of LaTeX the checks understand: fenced code dropped
    (newlines kept), headings dropped, **bold** mapped to \\textbf{}, *italic* to \\emph{}."""
    keep_lines = lambda m: "\n" * m.group(0).count("\n")
    t = re.sub(r"`{3}.*?`{3}", keep_lines, text, flags=re.S)        # fenced code (written without literal triple backticks so the file embeds in Markdown)
    t = re.sub(r"^#{1,6} .*$", "", t, flags=re.M)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    t = re.sub(r"(?<![*\w])\*(?!\*)([^*\n]+?)\*(?![*\w])", r"\\emph{\1}", t)
    return t


def run_style_checks(sources, style_sources=None, zh: bool = False, baseline=None, root=None,
                     abstract_text=None):
    """Items 14-27 over `sources` (whole text: acronym budget, abstract) and `style_sources`
    (per-file items; defaults to `sources`). Returns (problems, notes). `root` is where the
    reverse outline is written. `abstract_text` lets check.py pass the abstract it already parsed."""
    ZH = zh
    SOURCES = [Path(s) for s in sources]
    STYLE_SOURCES = [Path(s) for s in style_sources] if style_sources is not None else SOURCES
    ROOT = Path(root) if root is not None else (SOURCES[0].resolve().parent if SOURCES else Path("."))
    problems: list[str] = []
    notes: list[str] = []
    TH = load_thresholds(baseline, notes)
    outline: list[str] = []

    def read_src(p: Path) -> str:
        t = p.read_text(encoding="utf-8")
        return plain_to_texish(t) if p.suffix.lower() in {".md", ".txt"} else t


    def sentences_of(text: str) -> list[str]:
        parts = re.split(r"(?<=[。！？])" if ZH else r"(?<=[.!?])\s+", text)
        return [s.strip() for s in parts if len(re.findall(r"\w", s)) >= (6 if ZH else 3)]


    def length_of(sentence: str) -> int:
        return len(re.findall(r"[\u4e00-\u9fff]", sentence)) if ZH else len(sentence.split())


    def per_k(count: int, total: int) -> float:
        return 1000.0 * count / max(total, 1)


    for src in STYLE_SOURCES:
        raw = read_src(src)
        raw_lines = raw.splitlines()
        prose = prose_of(raw)
        name = src.name
        low = prose.lower()
        sentences = sentences_of(prose)
        n_units = sum(length_of(s) for s in sentences)          # words (en) or characters (zh)

        # 14: prose semicolons (a "% style-exempt" comment on the line excuses it)
        semi = "；" if ZH else ";"
        for i, line in enumerate(prose.splitlines(), 1):
            if semi in line:
                orig = raw_lines[i - 1] if i <= len(raw_lines) else ""
                if "style-exempt" not in orig:
                    problems.append(f"prose semicolon at {name}:{i}")

        # 15: sentence-initial connectives
        conns = ZH_CONNECTIVES if ZH else CONNECTIVES
        hits = [s[:40] for s in sentences if s.lower().startswith(conns)]
        if len(hits) > TH["connectives"]:
            problems.append(f"{name}: {len(hits)} sentence-initial connectives "
                            f"(budget {TH['connectives']}): {hits[:3]}")

        # 16: banned stock phrases
        for phrase in (ZH_BANNED if ZH else BANNED):
            if phrase in low:
                problems.append(f"{name}: banned phrase '{phrase}'")

        # 17: hedging -- budget per section, and stacked hedges are out regardless
        hedges = ZH_HEDGES if ZH else HEDGES
        n_hedges = sum(low.count(h) for h in hedges)
        if n_hedges > TH["hedges"]:
            problems.append(f"{name}: {n_hedges} hedges (budget {TH['hedges']}) -- "
                            f"narrow the claim and cite the number instead of softening it")
        for s_ in sentences:
            sl = s_.lower()
            if ZH:
                if len(re.findall(r"可能|或许|在一定程度上", sl)) >= 2:
                    problems.append(f"{name}: stacked hedge in: {s_[:40]}")
            elif re.search(r"\b(may|might|could)\b", sl) and \
                 re.search(r"\b(potentially|possibly|perhaps|to some extent)\b", sl):
                problems.append(f"{name}: stacked hedge in: {s_[:60]}")

        # 19: colons inside a sentence (a colon that ends the line introduces a
        # display block, list or algorithm and is fine)
        colon = "：" if ZH else ":"
        for i, line in enumerate(prose.splitlines(), 1):
            if colon in line and "style-exempt" not in (raw_lines[i - 1] if i <= len(raw_lines) else ""):
                stripped = line.rstrip().rstrip("\\").rstrip()
                if stripped.endswith(colon):
                    notes.append(f"{name}:{i} line-final colon (introducing a block) -- allowed")
                elif not re.search(r"https?:|\d:\d", line):
                    problems.append(f"mid-sentence colon at {name}:{i}")

        # 20: dashes used as parentheticals (number ranges such as 20--50 are fine)
        for i, line in enumerate(prose.splitlines(), 1):
            if "style-exempt" in (raw_lines[i - 1] if i <= len(raw_lines) else ""):
                continue
            if ZH and ("——" in line or "—" in line):
                problems.append(f"dash in prose at {name}:{i}")
            if not ZH and (re.search(r"---|—", line) or re.search(r"\s--\s", line)):
                problems.append(f"dash in prose at {name}:{i}")

        # 21: emphasis inside sentences; run-in headings (\paragraph) within budget
        bold_at = [i for i, line in enumerate(prose.splitlines(), 1) if "\\textbf{" in line]
        for i in bold_at:
            if "style-exempt" not in (raw_lines[i - 1] if i <= len(raw_lines) else ""):
                problems.append(f"bold inside running text at {name}:{i} "
                                f"(use \\paragraph{{}} for a run-in heading, no bold for emphasis)")
        n_emph = len(re.findall(r"\\(?:emph|textit)\{", prose))
        if n_emph > 1:
            problems.append(f"{name}: {n_emph} italic emphases (budget 1: the first definition of a term)")
        for blk in re.split(r"\\section\*?\{", strip_comments(raw)):
            n_leads = len(re.findall(r"\\paragraph\{", blk))
            if n_leads > TH["paragraph_leads"]:
                title = blk.split("}", 1)[0][:20]
                problems.append(f"{name}: {n_leads} run-in headings in section '{title}' (budget {TH['paragraph_leads']})")
        if ZH:
            for i, line in enumerate(strip_comments(raw).splitlines(), 1):
                if re.match(r"\s*\\textbf\{[^}]{1,12}。\}", line):
                    problems.append(f"bold run-in heading at {name}:{i} -- use \\paragraph{{}} instead")

        # 23: sentence rhythm and triplet lists
        lengths = [length_of(s) for s in sentences]
        if len(lengths) >= 8:
            cv = statistics.pstdev(lengths) / max(statistics.mean(lengths), 1)
            if cv < TH["sent_cv_min"]:
                problems.append(f"{name}: sentence lengths too uniform (CV {cv:.2f} < {TH['sent_cv_min']}) "
                                f"-- vary long and short sentences")
            else:
                notes.append(f"{name}: sentence-length CV {cv:.2f}, mean {statistics.mean(lengths):.1f}")
        if not ZH:
            triplets = re.findall(r"\b\w+, \w+,? and \w+\b", prose)
            if len(triplets) > TH["triplets"]:
                problems.append(f"{name}: {len(triplets)} three-item lists (budget {TH['triplets']}): "
                                f"{triplets[:2]}")

        # 24: lexical density (per 1000 words / characters)
        if ZH:
            inten = sum(prose.count(w) for w in ZH_INTENSIFIERS)
            gener = sum(prose.count(w) for w in ZH_GENERIC_VERBS)
            abstr = sum(prose.count(w) for w in ZH_ABSTRACT_NOUNS)
            if prose.count("本文所提出的") > 2:
                problems.append(f"{name}: '本文所提出的' repeated {prose.count('本文所提出的')} times")
        else:
            inten = sum(len(re.findall(r"\b%s\b" % w, low)) for w in INTENSIFIERS)
            gener = sum(len(re.findall(r"\b%s[sd]?\b" % w, low)) for w in GENERIC_VERBS)
            abstr = sum(len(re.findall(r"\b%ss?\b" % w, low)) for w in ABSTRACT_NOUNS)
            extra = len(re.findall(r"not only .{0,60} but also|\brespectively\b", low))
            if extra > 2:
                notes.append(f"{name}: {extra} 'not only/but also' or 'respectively' (limit 2)")
        for label, cnt, key in (("intensifiers", inten, "intensifier_per_k"),
                                ("generic verbs", gener, "generic_verb_per_k"),
                                ("abstract nouns", abstr, "abstract_noun_per_k")):
            rate = per_k(cnt, n_units)
            if rate > TH[key] and cnt >= 3:
                problems.append(f"{name}: {label} at {rate:.1f}/1000 (limit {TH[key]}) -- "
                                f"replace with the specific action or the number")

        # 25: paragraph specificity (method / experiment sections) and summary tails
        lname = name.lower()
        stripped = strip_comments(raw)
        if "\\begin{document}" in stripped:
            stripped = stripped[stripped.index("\\begin{document}"):]
        # which paragraphs belong to a core (method / experiment / problem) section
        core_titles = re.compile(r"方法|实验|问题|模型|method|experiment|result|problem", re.I)
        chunks, section_core = re.split(r"(\\section\*?\{[^}]*\})", stripped), []
        current = not ZH and any(k in lname for k in ("method", "experiment", "result", "problem"))
        for c in chunks:
            if c.startswith("\\section"):
                current = bool(core_titles.search(c)); continue
            section_core.append((c, current))
        for chunk, is_core in section_core:
            for p in re.split(r"\n\s*\n", chunk):
                ptxt = prose_of(p)
                if len(re.findall(r"[\u4e00-\u9fff]" if ZH else r"[A-Za-z]{3,}", ptxt)) < (60 if ZH else 30):
                    continue
                if "〔填写" in p or "\\draftnote" in p:
                    continue
                first = sentences_of(ptxt)[:1]
                if first:
                    outline.append(f"- ({name}) {first[0][:120]}")
                if not is_core:
                    continue
                concrete = bool(re.search(r"\d", p) or re.search(r"\\(?:eq)?ref\{|\\cite|\$[^$]+\$", p)
                                or re.search(r"例如|譬如|比如|for example|e\.g\.", p))
                if not concrete:
                    problems.append(f"{name}: paragraph with nothing concrete (no number, equation, "
                                    f"table/figure reference, citation or example): '{ptxt.strip()[:50]}'")
                last = sentences_of(ptxt)[-1:] if sentences_of(ptxt) else []
                if last and re.match(ZH_SUMMARY_TAIL if ZH else SUMMARY_TAIL, last[0].strip(), re.I):
                    problems.append(f"{name}: paragraph closes on a summary sentence: '{last[0][:60]}'")

        # 26: citation clusters
        for m in re.finditer(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", stripped):
            keys = [k for k in m.group(1).split(",") if k.strip()]
            if len(keys) > TH["cluster"]:
                problems.append(f"{name}: citation cluster of {len(keys)} keys -- give each work one "
                                f"specific sentence or cite the survey")

    # 18: naming budget -- acronyms and coined compound names (whole manuscript)
    whole = strip_comments("\n".join(read_src(p) for p in SOURCES))
    defs = re.findall(r"[（(]([A-Z][A-Za-z]{1,5})[)）]", whole)
    seen: dict[str, int] = {}
    for a in defs:
        if a.upper() == a or a in COMMON_ACRONYMS:
            seen.setdefault(a, 0)
    for a in seen:
        seen[a] = len(re.findall(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(a), whole)) - 1
    self_made = {a: n for a, n in seen.items() if a not in COMMON_ACRONYMS}
    notes.append("acronyms: " + ", ".join(f"{a}({n} uses)" for a, n in sorted(seen.items())) if seen else "acronyms: none")
    if len(self_made) > TH["self_acronyms"]:
        weak = [a for a, n in self_made.items() if n < TH["acronym_min_uses"]]
        # one self-made acronym (the method's own name) is free; every further one must earn its keep
        if len(self_made) - 1 > len(self_made) - 1 - len(weak) or len(weak) >= len(self_made):
            problems.append(f"self-made acronyms {sorted(self_made)}: beyond the method's own name, an "
                            f"acronym needs >= {TH['acronym_min_uses']} uses (weak: {weak})")
    for a, n in seen.items():
        if n <= 2:
            notes.append(f"acronym {a} defined but used {n} times -- spell it out and drop it")
    if ZH:
        for m in sorted(set(re.findall(r"[\u4e00-\u9fff]{2,6}(?:感知|驱动|增强|自适应)[\u4e00-\u9fff]{0,4}(?:机制|模块|框架|策略|网络)", whole))):
            problems.append(f"coined compound name: {m} -- name the mechanism with existing terms")
    else:
        for m in sorted(set(re.findall(r"(?<![.!?]\s)(?<!\n)\b((?:[A-Z][a-z]+[- ]){2,}[A-Z][a-z]+)\b", whole))):
            if any(w.lower() in NAME_ADJ for w in re.split(r"[- ]", m)):
                problems.append(f"coined name with an effect adjective: '{m}' -- describe the mechanism, not its merit")
            else:
                notes.append(f"title-case compound '{m}' -- use lower case unless it is the method's name")
        for m in sorted(set(re.findall(r"\b\w+-%s-\w+-%s\b|\b\w+-%s\s+\w+-%s\b" % (SUFFIX, SUFFIX, SUFFIX, SUFFIX), whole))):
            problems.append(f"stacked modifier chain: '{m}'")

    # 22: the abstract is one paragraph
    if ZH:
        m = re.search(r"\\section\*\{摘要\}(.*?)(?=\\vspace|\\noindent\\textbf\{关键词|\\section)", whole, re.S)
        abstract_text = m.group(1) if m else None
    elif abstract_text is None:                                 # standalone use: find the abstract ourselves
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", whole, re.S)
        abstract_text = m.group(1) if m else None
    if abstract_text is not None:
        inner = re.sub(r"^\s*\\noindent", "", abstract_text.strip())
        if re.search(r"\n\s*\n", inner.strip()) or "\\par" in inner:
            problems.append("abstract is broken into paragraphs -- a single paragraph, six sentences")

    # 27: reverse outline for the logic pass
    if outline:
        out = (ROOT / ("reverse-outline-zh.md" if ZH else "reverse-outline.md"))
        out.write_text("# Reverse outline (first sentence of every paragraph)\n\n" + "\n".join(outline) + "\n",
                       encoding="utf-8")
        notes.append(f"reverse outline: {out} ({len(outline)} paragraphs) -- read it top to bottom; "
                     f"it must argue on its own")

    return problems, notes


def looks_chinese(paths) -> bool:
    text = "".join(Path(p).read_text(encoding="utf-8", errors="replace") for p in paths)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return cjk > 0.3 * max(len(re.findall(r"[\u4e00-\u9fffA-Za-z]", text)), 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path, help=".tex / .md / .txt files; sections are checked one by one")
    ap.add_argument("--zh", action="store_true", help="Chinese text (default: auto-detect)")
    ap.add_argument("--baseline", type=Path, default=Path(__file__).resolve().parent / "style_baseline.json")
    ap.add_argument("--outline-dir", type=Path, default=None, help="where reverse-outline.md goes (default: first file's folder)")
    a = ap.parse_args()
    zh = a.zh or looks_chinese(a.files)
    problems, notes = run_style_checks(a.files, zh=zh, baseline=a.baseline,
                                       root=a.outline_dir or a.files[0].resolve().parent)
    print(f"files   : {len(a.files)}" + (" (zh)" if zh else ""))
    for n in notes:
        print(f"  note   {n}")
    for p in problems:
        print(f"  FAIL   {p}")
    print()
    if problems:
        print(f"{len(problems)} problem(s) found.")
        sys.exit(1)
    print("all style checks passed.")
```.*?```", keep_lines, text, flags=re.S)
    t = re.sub(r"^#{1,6} .*$", "", t, flags=re.M)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    t = re.sub(r"(?<![*\w])\*(?!\*)([^*\n]+?)\*(?![*\w])", r"\\emph{\1}", t)
    return t


def run_style_checks(sources, style_sources=None, zh: bool = False, baseline=None, root=None,
                     abstract_text=None):
    """Items 14-27 over `sources` (whole text: acronym budget, abstract) and `style_sources`
    (per-file items; defaults to `sources`). Returns (problems, notes). `root` is where the
    reverse outline is written. `abstract_text` lets check.py pass the abstract it already parsed."""
    ZH = zh
    SOURCES = [Path(s) for s in sources]
    STYLE_SOURCES = [Path(s) for s in style_sources] if style_sources is not None else SOURCES
    ROOT = Path(root) if root is not None else (SOURCES[0].resolve().parent if SOURCES else Path("."))
    problems: list[str] = []
    notes: list[str] = []
    TH = load_thresholds(baseline, notes)
    outline: list[str] = []

    def read_src(p: Path) -> str:
        t = p.read_text(encoding="utf-8")
        return plain_to_texish(t) if p.suffix.lower() in {".md", ".txt"} else t


    def sentences_of(text: str) -> list[str]:
        parts = re.split(r"(?<=[。！？])" if ZH else r"(?<=[.!?])\s+", text)
        return [s.strip() for s in parts if len(re.findall(r"\w", s)) >= (6 if ZH else 3)]


    def length_of(sentence: str) -> int:
        return len(re.findall(r"[\u4e00-\u9fff]", sentence)) if ZH else len(sentence.split())


    def per_k(count: int, total: int) -> float:
        return 1000.0 * count / max(total, 1)


    for src in STYLE_SOURCES:
        raw = read_src(src)
        raw_lines = raw.splitlines()
        prose = prose_of(raw)
        name = src.name
        low = prose.lower()
        sentences = sentences_of(prose)
        n_units = sum(length_of(s) for s in sentences)          # words (en) or characters (zh)

        # 14: prose semicolons (a "% style-exempt" comment on the line excuses it)
        semi = "；" if ZH else ";"
        for i, line in enumerate(prose.splitlines(), 1):
            if semi in line:
                orig = raw_lines[i - 1] if i <= len(raw_lines) else ""
                if "style-exempt" not in orig:
                    problems.append(f"prose semicolon at {name}:{i}")

        # 15: sentence-initial connectives
        conns = ZH_CONNECTIVES if ZH else CONNECTIVES
        hits = [s[:40] for s in sentences if s.lower().startswith(conns)]
        if len(hits) > TH["connectives"]:
            problems.append(f"{name}: {len(hits)} sentence-initial connectives "
                            f"(budget {TH['connectives']}): {hits[:3]}")

        # 16: banned stock phrases
        for phrase in (ZH_BANNED if ZH else BANNED):
            if phrase in low:
                problems.append(f"{name}: banned phrase '{phrase}'")

        # 17: hedging -- budget per section, and stacked hedges are out regardless
        hedges = ZH_HEDGES if ZH else HEDGES
        n_hedges = sum(low.count(h) for h in hedges)
        if n_hedges > TH["hedges"]:
            problems.append(f"{name}: {n_hedges} hedges (budget {TH['hedges']}) -- "
                            f"narrow the claim and cite the number instead of softening it")
        for s_ in sentences:
            sl = s_.lower()
            if ZH:
                if len(re.findall(r"可能|或许|在一定程度上", sl)) >= 2:
                    problems.append(f"{name}: stacked hedge in: {s_[:40]}")
            elif re.search(r"\b(may|might|could)\b", sl) and \
                 re.search(r"\b(potentially|possibly|perhaps|to some extent)\b", sl):
                problems.append(f"{name}: stacked hedge in: {s_[:60]}")

        # 19: colons inside a sentence (a colon that ends the line introduces a
        # display block, list or algorithm and is fine)
        colon = "：" if ZH else ":"
        for i, line in enumerate(prose.splitlines(), 1):
            if colon in line and "style-exempt" not in (raw_lines[i - 1] if i <= len(raw_lines) else ""):
                stripped = line.rstrip().rstrip("\\").rstrip()
                if stripped.endswith(colon):
                    notes.append(f"{name}:{i} line-final colon (introducing a block) -- allowed")
                elif not re.search(r"https?:|\d:\d", line):
                    problems.append(f"mid-sentence colon at {name}:{i}")

        # 20: dashes used as parentheticals (number ranges such as 20--50 are fine)
        for i, line in enumerate(prose.splitlines(), 1):
            if "style-exempt" in (raw_lines[i - 1] if i <= len(raw_lines) else ""):
                continue
            if ZH and ("——" in line or "—" in line):
                problems.append(f"dash in prose at {name}:{i}")
            if not ZH and (re.search(r"---|—", line) or re.search(r"\s--\s", line)):
                problems.append(f"dash in prose at {name}:{i}")

        # 21: emphasis inside sentences; run-in headings (\paragraph) within budget
        bold_at = [i for i, line in enumerate(prose.splitlines(), 1) if "\\textbf{" in line]
        for i in bold_at:
            if "style-exempt" not in (raw_lines[i - 1] if i <= len(raw_lines) else ""):
                problems.append(f"bold inside running text at {name}:{i} "
                                f"(use \\paragraph{{}} for a run-in heading, no bold for emphasis)")
        n_emph = len(re.findall(r"\\(?:emph|textit)\{", prose))
        if n_emph > 1:
            problems.append(f"{name}: {n_emph} italic emphases (budget 1: the first definition of a term)")
        for blk in re.split(r"\\section\*?\{", strip_comments(raw)):
            n_leads = len(re.findall(r"\\paragraph\{", blk))
            if n_leads > TH["paragraph_leads"]:
                title = blk.split("}", 1)[0][:20]
                problems.append(f"{name}: {n_leads} run-in headings in section '{title}' (budget {TH['paragraph_leads']})")
        if ZH:
            for i, line in enumerate(strip_comments(raw).splitlines(), 1):
                if re.match(r"\s*\\textbf\{[^}]{1,12}。\}", line):
                    problems.append(f"bold run-in heading at {name}:{i} -- use \\paragraph{{}} instead")

        # 23: sentence rhythm and triplet lists
        lengths = [length_of(s) for s in sentences]
        if len(lengths) >= 8:
            cv = statistics.pstdev(lengths) / max(statistics.mean(lengths), 1)
            if cv < TH["sent_cv_min"]:
                problems.append(f"{name}: sentence lengths too uniform (CV {cv:.2f} < {TH['sent_cv_min']}) "
                                f"-- vary long and short sentences")
            else:
                notes.append(f"{name}: sentence-length CV {cv:.2f}, mean {statistics.mean(lengths):.1f}")
        if not ZH:
            triplets = re.findall(r"\b\w+, \w+,? and \w+\b", prose)
            if len(triplets) > TH["triplets"]:
                problems.append(f"{name}: {len(triplets)} three-item lists (budget {TH['triplets']}): "
                                f"{triplets[:2]}")

        # 24: lexical density (per 1000 words / characters)
        if ZH:
            inten = sum(prose.count(w) for w in ZH_INTENSIFIERS)
            gener = sum(prose.count(w) for w in ZH_GENERIC_VERBS)
            abstr = sum(prose.count(w) for w in ZH_ABSTRACT_NOUNS)
            if prose.count("本文所提出的") > 2:
                problems.append(f"{name}: '本文所提出的' repeated {prose.count('本文所提出的')} times")
        else:
            inten = sum(len(re.findall(r"\b%s\b" % w, low)) for w in INTENSIFIERS)
            gener = sum(len(re.findall(r"\b%s[sd]?\b" % w, low)) for w in GENERIC_VERBS)
            abstr = sum(len(re.findall(r"\b%ss?\b" % w, low)) for w in ABSTRACT_NOUNS)
            extra = len(re.findall(r"not only .{0,60} but also|\brespectively\b", low))
            if extra > 2:
                notes.append(f"{name}: {extra} 'not only/but also' or 'respectively' (limit 2)")
        for label, cnt, key in (("intensifiers", inten, "intensifier_per_k"),
                                ("generic verbs", gener, "generic_verb_per_k"),
                                ("abstract nouns", abstr, "abstract_noun_per_k")):
            rate = per_k(cnt, n_units)
            if rate > TH[key] and cnt >= 3:
                problems.append(f"{name}: {label} at {rate:.1f}/1000 (limit {TH[key]}) -- "
                                f"replace with the specific action or the number")

        # 25: paragraph specificity (method / experiment sections) and summary tails
        lname = name.lower()
        stripped = strip_comments(raw)
        if "\\begin{document}" in stripped:
            stripped = stripped[stripped.index("\\begin{document}"):]
        # which paragraphs belong to a core (method / experiment / problem) section
        core_titles = re.compile(r"方法|实验|问题|模型|method|experiment|result|problem", re.I)
        chunks, section_core = re.split(r"(\\section\*?\{[^}]*\})", stripped), []
        current = not ZH and any(k in lname for k in ("method", "experiment", "result", "problem"))
        for c in chunks:
            if c.startswith("\\section"):
                current = bool(core_titles.search(c)); continue
            section_core.append((c, current))
        for chunk, is_core in section_core:
            for p in re.split(r"\n\s*\n", chunk):
                ptxt = prose_of(p)
                if len(re.findall(r"[\u4e00-\u9fff]" if ZH else r"[A-Za-z]{3,}", ptxt)) < (60 if ZH else 30):
                    continue
                if "〔填写" in p or "\\draftnote" in p:
                    continue
                first = sentences_of(ptxt)[:1]
                if first:
                    outline.append(f"- ({name}) {first[0][:120]}")
                if not is_core:
                    continue
                concrete = bool(re.search(r"\d", p) or re.search(r"\\(?:eq)?ref\{|\\cite|\$[^$]+\$", p)
                                or re.search(r"例如|譬如|比如|for example|e\.g\.", p))
                if not concrete:
                    problems.append(f"{name}: paragraph with nothing concrete (no number, equation, "
                                    f"table/figure reference, citation or example): '{ptxt.strip()[:50]}'")
                last = sentences_of(ptxt)[-1:] if sentences_of(ptxt) else []
                if last and re.match(ZH_SUMMARY_TAIL if ZH else SUMMARY_TAIL, last[0].strip(), re.I):
                    problems.append(f"{name}: paragraph closes on a summary sentence: '{last[0][:60]}'")

        # 26: citation clusters
        for m in re.finditer(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", stripped):
            keys = [k for k in m.group(1).split(",") if k.strip()]
            if len(keys) > TH["cluster"]:
                problems.append(f"{name}: citation cluster of {len(keys)} keys -- give each work one "
                                f"specific sentence or cite the survey")

    # 18: naming budget -- acronyms and coined compound names (whole manuscript)
    whole = strip_comments("\n".join(read_src(p) for p in SOURCES))
    defs = re.findall(r"[（(]([A-Z][A-Za-z]{1,5})[)）]", whole)
    seen: dict[str, int] = {}
    for a in defs:
        if a.upper() == a or a in COMMON_ACRONYMS:
            seen.setdefault(a, 0)
    for a in seen:
        seen[a] = len(re.findall(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(a), whole)) - 1
    self_made = {a: n for a, n in seen.items() if a not in COMMON_ACRONYMS}
    notes.append("acronyms: " + ", ".join(f"{a}({n} uses)" for a, n in sorted(seen.items())) if seen else "acronyms: none")
    if len(self_made) > TH["self_acronyms"]:
        weak = [a for a, n in self_made.items() if n < TH["acronym_min_uses"]]
        # one self-made acronym (the method's own name) is free; every further one must earn its keep
        if len(self_made) - 1 > len(self_made) - 1 - len(weak) or len(weak) >= len(self_made):
            problems.append(f"self-made acronyms {sorted(self_made)}: beyond the method's own name, an "
                            f"acronym needs >= {TH['acronym_min_uses']} uses (weak: {weak})")
    for a, n in seen.items():
        if n <= 2:
            notes.append(f"acronym {a} defined but used {n} times -- spell it out and drop it")
    if ZH:
        for m in sorted(set(re.findall(r"[\u4e00-\u9fff]{2,6}(?:感知|驱动|增强|自适应)[\u4e00-\u9fff]{0,4}(?:机制|模块|框架|策略|网络)", whole))):
            problems.append(f"coined compound name: {m} -- name the mechanism with existing terms")
    else:
        for m in sorted(set(re.findall(r"(?<![.!?]\s)(?<!\n)\b((?:[A-Z][a-z]+[- ]){2,}[A-Z][a-z]+)\b", whole))):
            if any(w.lower() in NAME_ADJ for w in re.split(r"[- ]", m)):
                problems.append(f"coined name with an effect adjective: '{m}' -- describe the mechanism, not its merit")
            else:
                notes.append(f"title-case compound '{m}' -- use lower case unless it is the method's name")
        for m in sorted(set(re.findall(r"\b\w+-%s-\w+-%s\b|\b\w+-%s\s+\w+-%s\b" % (SUFFIX, SUFFIX, SUFFIX, SUFFIX), whole))):
            problems.append(f"stacked modifier chain: '{m}'")

    # 22: the abstract is one paragraph
    if ZH:
        m = re.search(r"\\section\*\{摘要\}(.*?)(?=\\vspace|\\noindent\\textbf\{关键词|\\section)", whole, re.S)
        abstract_text = m.group(1) if m else None
    elif abstract_text is None:                                 # standalone use: find the abstract ourselves
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", whole, re.S)
        abstract_text = m.group(1) if m else None
    if abstract_text is not None:
        inner = re.sub(r"^\s*\\noindent", "", abstract_text.strip())
        if re.search(r"\n\s*\n", inner.strip()) or "\\par" in inner:
            problems.append("abstract is broken into paragraphs -- a single paragraph, six sentences")

    # 27: reverse outline for the logic pass
    if outline:
        out = (ROOT / ("reverse-outline-zh.md" if ZH else "reverse-outline.md"))
        out.write_text("# Reverse outline (first sentence of every paragraph)\n\n" + "\n".join(outline) + "\n",
                       encoding="utf-8")
        notes.append(f"reverse outline: {out} ({len(outline)} paragraphs) -- read it top to bottom; "
                     f"it must argue on its own")

    return problems, notes


def looks_chinese(paths) -> bool:
    text = "".join(Path(p).read_text(encoding="utf-8", errors="replace") for p in paths)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return cjk > 0.3 * max(len(re.findall(r"[\u4e00-\u9fffA-Za-z]", text)), 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path, help=".tex / .md / .txt files; sections are checked one by one")
    ap.add_argument("--zh", action="store_true", help="Chinese text (default: auto-detect)")
    ap.add_argument("--baseline", type=Path, default=Path(__file__).resolve().parent / "style_baseline.json")
    ap.add_argument("--outline-dir", type=Path, default=None, help="where reverse-outline.md goes (default: first file's folder)")
    a = ap.parse_args()
    zh = a.zh or looks_chinese(a.files)
    problems, notes = run_style_checks(a.files, zh=zh, baseline=a.baseline,
                                       root=a.outline_dir or a.files[0].resolve().parent)
    print(f"files   : {len(a.files)}" + (" (zh)" if zh else ""))
    for n in notes:
        print(f"  note   {n}")
    for p in problems:
        print(f"  FAIL   {p}")
    print()
    if problems:
        print(f"{len(problems)} problem(s) found.")
        sys.exit(1)
    print("all style checks passed.")
```

## style_baseline.py

```python
#!/usr/bin/env python3
"""Measure the prose style of published papers and write style_baseline.json.

    python scripts/style_baseline.py                      # reads paper_assets/style_corpus/*
    python scripts/style_baseline.py --corpus ~/venue-papers

Statistics: mean sentence length, sentence-length CV, sentence-initial connective
rate, intensifier / generic-verb / abstract-noun rates per 1000 words, mean
paragraph length, acronym count. stylecheck.py (and check.py through it) loads the JSON when it exists.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

CONNECTIVES = ("moreover", "furthermore", "additionally", "in addition", "notably",
               "consequently", "specifically", "overall", "meanwhile", "nevertheless", "thus")
INTENSIFIERS = ("significantly", "substantially", "remarkably", "effectively", "seamlessly",
                "comprehensively", "robustly", "dramatically", "greatly", "highly")
GENERIC_VERBS = ("facilitate", "enable", "ensure", "enhance", "demonstrate", "exhibit", "achieve", "utilize")
ABSTRACT_NOUNS = ("framework", "paradigm", "mechanism", "scheme", "module", "pipeline", "strategy")

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--corpus", type=Path, default=Path(__file__).resolve().parents[1] / "style_corpus")
ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "style_baseline.json")
args = ap.parse_args()

files = sorted(list(args.corpus.glob("*.tex")) + list(args.corpus.glob("*.txt")))
if not files:
    raise SystemExit(f"no .tex/.txt in {args.corpus}")


def prose(t: str) -> str:
    t = re.sub(r"(?<!\\)%.*", "", t)
    t = re.sub(r"\\begin\{(equation|align|tabular|algorithmic|figure|table)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " ", t)
    t = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", t)
    return t


sent_lens, para_lens, conn, inten, gener, abstr, words, acr = [], [], 0, 0, 0, 0, 0, set()
for f in files:
    t = prose(f.read_text(encoding="utf-8", errors="replace"))
    for para in re.split(r"\n\s*\n", t):
        ss = [s for s in re.split(r"(?<=[.!?])\s+", para) if len(s.split()) >= 3]
        if ss:
            para_lens.append(len(ss))
        for s in ss:
            n = len(s.split()); sent_lens.append(n); words += n
            low = s.lower()
            conn += low.startswith(CONNECTIVES)
            inten += sum(len(re.findall(r"\b%s\b" % w, low)) for w in INTENSIFIERS)
            gener += sum(len(re.findall(r"\b%s[sd]?\b" % w, low)) for w in GENERIC_VERBS)
            abstr += sum(len(re.findall(r"\b%ss?\b" % w, low)) for w in ABSTRACT_NOUNS)
    acr.update(re.findall(r"\(([A-Z]{2,6})\)", t))

k = 1000.0 / max(words, 1)
baseline = dict(
    corpus=[f.name for f in files], words=words, sentences=len(sent_lens),
    sent_mean=round(statistics.mean(sent_lens), 1),
    sent_cv=round(statistics.pstdev(sent_lens) / statistics.mean(sent_lens), 3),
    connectives=round(conn / max(len(files), 1) / 8, 2),   # per section-sized unit (~1/8 paper)
    intensifier_per_k=round(inten * k, 2), generic_verb_per_k=round(gener * k, 2),
    abstract_noun_per_k=round(abstr * k, 2),
    para_mean_sentences=round(statistics.mean(para_lens), 1) if para_lens else None,
    acronyms_defined=len(acr),
)
args.out.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
print(json.dumps(baseline, indent=2))
print(f"\nwritten to {args.out}; stylecheck.py will use it automatically")
```

基线里的 `sent_cv`、三类词汇密度、连接词率会覆盖默认阈值；`sent_mean`、`para_mean_sentences`、
`acronyms_defined` 供起草与润色时对照。有作者自己的已发表稿件时同法提取"作者基线"，稿件向作者靠。
