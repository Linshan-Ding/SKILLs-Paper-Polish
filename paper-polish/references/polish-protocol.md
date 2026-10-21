# 润色交付协议（改动清单、diff、机检对比、待补事实）

本文件是 `paper-polish` 的交付格式细则。模式与不变量在 SKILL.md；本文件只放格式与一段示例。

## 1. 交付物清单（按模式）

| 交付物 | 体检 | 润色 | 深度 |
|---|---|---|---|
| 机检报告（`stylecheck.py` 原始输出 + 逐项解释） | 必有 | 前后各一份 | 前后各一份 |
| 反向大纲（`reverse-outline.md`，每段首句连读） | 必有 | 有 | 必有，且附连读是否成立的判断 |
| 改后文本 | 无 | 必有 | 必有 |
| diff 或逐段对照 | 无 | 必有 | 必有 |
| 改动清单（表 2 格式） | 无 | 必有 | 必有 |
| 待补事实清单 | 无 | 有则列 | 必有（可为空，要写"无"） |
| 未改之处与理由 | 无 | 必有 | 必有 |
| 删减记录（删了哪些句、为何是填充） | 无 | 无 | 必有，含删减比例 |
| 证明重排（段落式证明 → `align` 分行推导，内容不变；改动清单标 32） | 无 | 有则列 | 必有 |

## 2. 改动清单格式

| # | 位置 | 原文 | 改后 | 规则 | 理由 |
|---|---|---|---|---|---|
| 1 | §3 第 2 段 第 1 句 | Moreover, the framework leverages … | The decoder masks … | 15, 16 | 句首连接词超预算；leverage → use，并把"框架"落到具体组件 |

"位置"用节号加段落序号加句序号，`.tex` 另给行号。"规则"填 `style-rules.md` 的条款名或 `stylecheck.py`
的项号。一条改动涉及多条规则就都列上。改动清单按原文顺序排，不按规则分组，作者才能顺着稿子核对。

## 3. diff 约定

- `.tex` 与 Markdown：统一 diff（`diff -u`），改后文件名加 `-polished`；作者在 Overleaf 上改时附逐段
  对照表而不是 diff。
- 粘贴段落：逐段对照，左原文右改后，段落编号对齐。
- 任何改动都不跨段合并、不拆段、不调段序（深度模式允许删整段，但要在删减记录里列出）。

## 4. 待补事实占位

格式固定为 `〔待补事实：此处需要 ___〕`，英文稿用 `[FACT NEEDED: ___]`。只在以下三种情形使用：

1. 原句是定量声明但没有数字与出处（"substantially better"），改成中性表述后留占位要数字与表号。
2. 结果段没有机制解释句，留占位要作者给因果与背书证据（消融表号或探针图号）。
3. 整段没有任何具体物又不能删（承担结构功能），留占位说明这一段缺什么。

占位是给作者的待办，不是交付的终态；清单里每条写清需要什么、从哪里能拿到（表号、附录、代码日志）。

## 5. 不变量核对表（交付前逐条打勾）

- [ ] 原文与改后的数字逐个相同（含百分号、单位、置信区间）。
- [ ] 引用键与引用位置相同，没有新增或删除引用。
- [ ] 每条 claim 的强度相同或由作者决定收窄；本技能只标出过度声称处。
- [ ] 没有新增句子；深度模式的删减都在删减记录里。
- [ ] 改动清单每条有规则编号。
- [ ] 机检复跑零 FAIL，豁免行有 `% style-exempt`。

## 6. 示例（英文，润色模式，节选）

原文：

> Moreover, the proposed framework significantly enhances scheduling performance; it leverages a novel
> adaptive masking mechanism. Furthermore, it is worth noting that the **masking module** plays a crucial
> role in the pipeline: it effectively prunes infeasible actions. Additionally, the results may potentially
> generalize to larger instances to some extent.

改后：

> The decoder masks infeasible operations before the softmax, so the policy compares only feasible actions.
> On the main tier the mean gap falls from 4.1 to 2.0 percentage points (Table 4). Whether the gain holds
> on instances larger than those seen in training is tested in Section 5.6.

改动清单（节选）：

| # | 位置 | 原文 | 改后 | 规则 | 理由 |
|---|---|---|---|---|---|
| 1 | 句 1 | Moreover, … significantly enhances … | The decoder masks … | 15, 24, 命名 | 句首连接词；无数字的强化副词；"novel adaptive masking mechanism"是效果形容词造名，改为描述机制 |
| 2 | 句 1 | ; it leverages | （拆句） | 14, 16 | 散文分号；leverage → 直接写动作 |
| 3 | 句 2 | it is worth noting that the **masking module** plays a crucial role …: it … | On the main tier the mean gap falls … (Table 4) | 16, 21, 19, 具体性 | 禁用句式；句中加粗；句中冒号；"crucial role"换成数字与表号——数字来自作者附的表 4 |
| 4 | 句 3 | may potentially … to some extent | Whether the gain holds … is tested in Section 5.6 | 17 | 三重对冲改成可判定的指向；claim 强度由作者在 5.6 节的结果决定 |

机检对比：改前 FAIL 8（14/15/16×2/17/19/21/24），改后 FAIL 0。待补事实：无（表 4 的数字由作者提供）。
未改之处：无。
