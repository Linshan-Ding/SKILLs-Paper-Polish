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
  这里的 `stylecheck.py`（文体项 14–27、30–33）。改规则、词表或阈值只改本仓库；项号是三个仓库共享的约定，
  新增检查并入现有项，不另起项号。

## 维护纪律

- 每条规则配正例与机检；两个脚本只以代码块形式存在 `stylecheck.md` 里（仓库里没有单独的 `.py`），
  脚本里不能出现三个连续反引号。
- 改 `stylecheck.py` 或 `style_baseline.py`：先在工作副本上改，回填进 `stylecheck.md`，再跑
  `python tests/run_fixtures.py`（从文档抽出脚本，在 `tests/fixtures/` 的埋错样例与干净样例上核对命中与误报）。
  新增检查时给埋错样例加一处、给期望表加一行；`tests/` 不属于技能目录，不随技能安装。
- 改动在 `claude/*` 分支上提交并推送，经 PR 合入 `main`。
