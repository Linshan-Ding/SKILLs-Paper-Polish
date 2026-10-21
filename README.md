# SKILLs-Paper-Polish

一个领域无关的 [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills)：对**已经写好**的学术
文本做润色、去 AI 味与文体体检。输入一段或一篇稿子，输出意思一字不改、但读起来像资深学者手笔的版本，
外加能逐条核对的改动记录与机检前后对比。

适用对象：论文章节与摘要、学位论文、研究方案、基金本子、rebuttal 回复信、cover letter；中文与英文；
`.tex`、Markdown、纯文本或直接粘贴的段落。

## 三种模式

| 模式 | 做什么 | 产出 |
|---|---|---|
| 体检 | 只跑文体机检 `stylecheck.py`，按项逐条解释命中处 | 报告 + 反向大纲，不改一个字 |
| 润色 | 句级改写：连接词链、分号、句中冒号、破折号插入语、非必要连字符、正文与表头里代替词语的箭头与运算符、生僻词换领域常用词、突然加粗、造词与缩写通胀、等长句、三连排比、强化副词、对冲堆叠、枚举与总结脚手架 | 改后文本 + diff + 改动清单 |
| 深度去 AI 味 | 段级：反向大纲、从文本反推事实清单、删减配额 10–15%、每段补具体物指向、因果句、引用评价、段落式证明重排成分行推导 | 改后文本 + 改动清单 + 待补事实清单 |

四条不变量贯穿所有模式：不改事实、数字、引用与 claim 强度；不新增内容；每处改动可指到规则编号；交付
可核对。内容空洞处只留"待补事实"占位，不编。

## 仓库结构

```
SKILLs-Paper-Polish/
├── README.md
└── paper-polish/
    ├── SKILL.md                          # 决策层：模式、不变量、体裁规则、流程、自检
    └── references/
        ├── style-rules.md                # 学术文体与去 AI 痕迹规范全文（表层 / 深层 / 反防御性写作 / 中文条款）
        ├── style-rewrite-examples.md     # 改写对照正例库
        ├── stylecheck.md                 # stylecheck.py（18 项文体机检）+ style_baseline.py（语料校准）+ 阈值表
        └── polish-protocol.md            # 交付格式：改动清单、diff、机检对比、待补事实占位、示例
```

## 安装与使用

整目录 `paper-polish/` 拷贝到项目的 `.claude/skills/` 或用户级 `~/.claude/skills/`。单独使用不依赖任何
其它技能。触发示例：

- "帮我润色这一节，去掉 AI 味" → 润色模式
- "这篇稿子有没有机器写作的痕迹？先别改" → 体检模式
- "审稿人说方法节读不出贡献，太空了，重写" → 深度去 AI 味
- "把这封回复信的文风统一一下" → 润色模式，按回复信体裁豁免礼节句式

机检单独可用：

```
python paper-polish/references/stylecheck.py sections/*.tex
python paper-polish/references/stylecheck.py draft.md
python paper-polish/references/stylecheck.py --help
```

脚本以 Markdown 代码块形式放在 `references/stylecheck.md` 里，技能生成工程时把它们写到项目的
`paper_assets/scripts/` 下；想直接用，从该文件复制出 `stylecheck.py` 与 `style_baseline.py` 即可。

## 与两组科研流水线的关系

本仓库是 [`SKILLs-Generated`](https://github.com/Linshan-Ding/SKILLs-Generated)（组合优化方向 `opt-paper-*`）
与 [`SKILLs-ML-Paper`](https://github.com/Linshan-Ding/SKILLs-ML-Paper)（机器学习方向 `ml-paper-*`）共用的
**文体层**：规则、正例库、文体检查器、语料校准脚本只维护在这里，两组的写稿、rebuttal、投稿包技能用
`../paper-polish/references/...` 引用。三组装在同一个 skills 目录下即可衔接；两组的 `check.py` 直接导入
本仓库的 `stylecheck.py`，项号连续（1–13 一致性与投稿限制，14–27 与 30–33 文体，28–29 投稿包与匿名稿）。

## 诚实边界

文体规则显著降低但不能消除 AI 痕迹，终稿仍建议作者人工通读；AI 辅助的披露按目标 venue 政策如实处理。
本技能的目标是写出资深学者水准的文字，不是规避检测。
