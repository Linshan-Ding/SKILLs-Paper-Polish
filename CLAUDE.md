# SKILLs-Paper-Polish

领域无关的学术文本润色与去 AI 味技能 `paper-polish`：输入已写好的文本，输出意思不变、像资深学者手笔的版本，
附改动清单与文体机检前后对比。三种模式（体检 / 润色 / 深度去 AI 味）与四条不变量见 `paper-polish/SKILL.md`。

## 技能在哪里

- 技能就是根目录的 `paper-polish/SKILL.md` 加 `paper-polish/references/`（规则全文 `style-rules.md`、正例库、
  `stylecheck.md` 里的 `stylecheck.py` 与 `style_baseline.py`、交付协议），**不在 `.claude/skills/` 下**。
  在本仓库开的会话里直接 Read SKILL.md 即可使用；装到别的项目是整目录拷贝到 `.claude/skills/` 或
  `~/.claude/skills/`，单独使用不依赖其它技能。
- 本仓库是 `SKILLs-OP-Paper`（`opt-paper-*`）与 `SKILLs-ML-Paper`（`ml-paper-*`）两组流水线的文体层：
  两组的写稿、rebuttal、投稿包技能用 `../paper-polish/references/...` 引用这里，生成的 `check.py` 导入
  这里的 `stylecheck.py`（文体项 14–27、30–33）。改规则、词表或阈值只改本仓库。

## 维护纪律

- 每条规则配正例与机检；改 `stylecheck.py` 后用埋点夹具与干净稿各跑一次，再重新嵌入 `stylecheck.md`
  （脚本里不能出现三个连续反引号）。
- 改动在 `claude/*` 分支上提交并推送，经 PR 合入 `main`。
