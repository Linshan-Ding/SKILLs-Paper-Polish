# 润色交付协议（改动清单、diff、机检对比、待补事实）

本文件是 `paper-polish` 的交付格式细则。模式与不变量在 SKILL.md；本文件只放格式与一段示例。

## 1. 交付物清单（按模式）

| 交付物 | 体检 | 润色 | 深度 | 去防御 |
|---|---|---|---|---|
| 机检报告（`stylecheck.py` 原始输出 + 逐项解释） | 必有 | 前后各一份 | 前后各一份 | 前后各一份，项 17 单列 |
| 反向大纲（`reverse-outline.md`，每段首句连读） | 必有 | 有 | 必有，且附连读是否成立的判断 | 无 |
| 改后文本 | 无 | 必有 | 必有 | 必有 |
| diff 或逐段对照 | 无 | 必有 | 必有 | 必有 |
| 改动清单（表 2 格式） | 无 | 必有 | 必有 | 必有 |
| 待补事实清单 | 无 | 有则列 | 必有（可为空，要写"无"） | 有则列 |
| 未改之处与理由 | 无 | 必有 | 必有 | 必有 |
| 删减记录（删了哪些句、为何是填充） | 无 | 无 | 必有，含删减比例 | 无 |
| 证明重排（段落式证明 → `align` 分行推导，内容不变；改动清单标 32） | 无 | 有则列 | 必有 | 无 |
| 迁移记录（免责与范围声明迁入局限节，§6.2） | 无 | 有则列 | 有则列 | 必有（可为空，要写"无"） |
| 交作者清单（要作者加强或收窄 claim 的句子，§6.3） | 无 | 有则列 | 有则列 | 必有（可为空，要写"无"） |

## 2. 改动清单格式

| # | 位置 | 原文 | 改后 | 规则 | 理由 |
|---|---|---|---|---|---|
| 1 | §3 第 2 段 第 1 句 | Moreover, the framework leverages … | The decoder masks … | 15, 16 | 句首连接词超预算；leverage → use，并把"框架"落到具体组件 |

"位置"用节号加段落序号加句序号，`.tex` 另给行号。"规则"填 `style-rules.md` 的条款名或 `stylecheck.py`
的项号；项 17 在括号里写形态，如"17（元评论）"。一条改动涉及多条规则就都列上。改动清单按原文顺序排，不按规则分组，作者才能顺着稿子核对。

## 3. diff 约定

- `.tex` 与 Markdown：统一 diff（`diff -u`），改后文件名加 `-polished`；作者在 Overleaf 上改时附逐段
  对照表而不是 diff。
- 粘贴段落：逐段对照，左原文右改后，段落编号对齐。
- 任何改动都不跨段合并、不拆段、不调段序（深度模式允许删整段，但要在删减记录里列出）。唯一的例外是项 17
  的迁移：免责与范围声明整句移进局限节，逐句写进迁移记录（§6.2）。

## 4. 待补事实占位

格式固定为 `〔待补事实：此处需要 ___〕`，英文稿用 `[FACT NEEDED: ___]`。只在以下四种情形使用：

1. 原句是定量声明但没有数字与出处（"substantially better"），改成中性表述后留占位要数字与表号。
2. 结果段没有机制解释句，留占位要作者给因果与背书证据（消融表号或探针图号）。
3. 整段没有任何具体物又不能删（承担结构功能），留占位说明这一段缺什么。
4. 限定说不出条件（项 17 的不可判定限定，或局限节里没有可判定条件的免责），留占位要条件：规模、参数范围、
   表号或假设编号。

占位是给作者的待办，不是交付的终态；清单里每条写清需要什么、从哪里能拿到（表号、附录、代码日志）。机检把
两种写法的占位都当作非正文跳过，占位里的冒号不报项 19。

## 5. 不变量核对表（交付前逐条打勾）

- [ ] 原文与改后的数字逐个相同（含百分号、单位、置信区间）。
- [ ] 引用键与引用位置相同，没有新增或删除引用。
- [ ] 每条 claim 的强度相同或由作者决定收窄；本技能只标出过度声称处。
- [ ] 没有靠删对冲加强 claim：删掉的只有引导语、借口、堆叠里多余的限定与重复的优先权声明。
- [ ] 迁入局限节的句子在迁移记录里逐句可查，原意不变。
- [ ] 没有新增句子；深度模式的删减都在删减记录里。
- [ ] 改动清单每条有规则编号。
- [ ] 机检复跑零 FAIL，豁免行有 `% style-exempt`（Markdown 里是 `<!-- style-exempt -->`）。

## 6. 防御性写作的修正（项 17）

润色与深度模式顺带处理项 17；用户只要求处理防御性写作时走"去防御性写作"模式，只动本节这些句子。每条命中
先定动作，动作决定 claim 强度会不会变，会变的一律交作者。规则全文与九种形态见 `style-rules.md` 第 3 节。

### 6.1 命中 → 动作

| 机检报告 | 先看什么 | 动作 | claim 强度 | 记在哪 |
|---|---|---|---|---|
| `meta-comment` | — | 删引导语，直接陈述后面的内容 | 不变 | 改动清单 |
| `apology or excuse` | — | 删借口，留指向（"证明见附录 B"）与其中的事实 | 不变 | 改动清单 |
| `pre-emptive defence` | 假想反方之后有没有证据句 | 有：删反方，证据句直接陈述；没有：原样保留，交作者 | 不变 / 交作者 | 改动清单 / 交作者清单 |
| `stacked hedge` | 几个限定里哪个可判定 | 只留一个，优先留可判定的那个 | 不变 | 改动清单 |
| `vague qualifier` | 原文或附带材料里有没有条件 | 有：换成条件（规模、参数范围、表号、假设编号）；没有：留 `〔待补事实：此处需要 ___〕` | 不变 | 改动清单 / 待补事实清单 |
| `N hedges in section` | 逐个看对冲有没有证据 | 有：换成数字与出处；没有：保留并交作者（删掉就是加强 claim） | 不变 / 交作者 | 改动清单 / 交作者清单 |
| 局限节外的 `disclaimer`、`scope caveat` | 稿件里有没有局限、讨论或结论节 | 有：整句迁入，原处不留尾巴；没有：原处保留，交作者（新增一节属于新增内容） | 不变 | 迁移记录 / 交作者清单 |
| `novelty hedge … times` | 哪一处挂着主要的优先权声明 | 那一处保留；重复同一声明的删重复句；另一条声明交作者 | 不变 / 交作者 | 改动清单 / 交作者清单 |
| 局限节内的 note | 边界是不是可判定条件 | 是：不动；不是：留待补事实要条件 | 不变 | 待补事实清单 |
| 合法限定被报（统计不确定性、明确条件、引文、表示"允许"的 may） | 是不是真的合法 | 表示允许的 may 改成 can；其余加 `% style-exempt`，写进"未改之处与理由" | 不变 | 改动清单 / 未改之处 |

### 6.2 迁移记录

| # | 原位置 | 原句 | 迁入位置 | 迁入后 | 规则 |
|---|---|---|---|---|---|
| 1 | §5 第 1 段 第 7 句 | Larger models are beyond the scope of this paper. | §7 第 1 段末 | 原句不变 | 17（范围声明） |

迁入后能改的只有两处：并入同一条边界背后的事实句（"because the 13B model did not fit in memory"），以及把
不可判定的说法换成条件或留占位。原处不留尾巴，也不补"see Section 7"一类新句。

### 6.3 交作者清单

| # | 位置 | 原句 | 需要作者决定什么 | 现有证据 |
|---|---|---|---|---|
| 1 | §5 第 1 段 第 5 句 | The filter may help on harder benchmarks. | 无证据的推测：补一组结果，或删句 | 无 |

收窄与加强 claim 都在这里交给作者，润色不代劳。

### 6.4 剩余 FAIL

改完复跑。项 17 的剩余 FAIL 必须逐条对得上交作者清单，并写进"未改之处与理由"。不为清零机检而删对冲（那是
替作者加强 claim），也不给防御句加 `% style-exempt`；豁免只给 6.1 末行的合法限定。

### 6.5 示例（英文，去防御性写作，节选）

原文（第 5 节第 1 段与第 7 节）：

> **5 Experiments.** It should be noted that the reference set contains only 64 samples. One might argue that
> this is too few. However, accuracy changes by less than 0.3 points between 32 and 128 samples (Table 6). Due to
> space limitations, the full sensitivity study is in Appendix C. The filter may potentially help on harder
> benchmarks to some extent. We believe the gain may shrink at higher noise rates. Larger models are beyond the
> scope of this paper.
>
> **7 Limitations.** All results use models of up to 7B parameters.

改后：

> **5 Experiments.** The reference set contains 64 samples. Accuracy changes by less than 0.3 points between 32
> and 128 samples (Table 6), and the full sensitivity study is in Appendix C. The filter may help on harder
> benchmarks. The gain may shrink at higher noise rates.
>
> **7 Limitations.** All results use models of up to 7B parameters. Larger models are beyond the scope of this paper.

改动清单：

| # | 位置 | 原文 | 改后 | 规则 | 理由 |
|---|---|---|---|---|---|
| 1 | §5 句 1 | It should be noted that the reference set contains only 64 samples. | The reference set contains 64 samples. | 17（元评论） | 删引导语；only 是替作者先认错，数字不变 |
| 2 | §5 句 2–3 | One might argue that this is too few. However, accuracy changes … (Table 6). | Accuracy changes … (Table 6), | 17（预先辩护） | 删假想反方，证据句直接陈述 |
| 3 | §5 句 4 | Due to space limitations, the full sensitivity study is in Appendix C. | and the full sensitivity study is in Appendix C. | 17（道歉与借口） | 删借口，指向留下，并入上一句 |
| 4 | §5 句 5 | may potentially … to some extent | may | 17（堆叠、超预算） | 三个限定留一个 |
| 5 | §5 句 6 | We believe the gain may shrink | The gain may shrink | 17（堆叠、超预算） | 两个限定留一个 |

迁移记录与交作者清单见 6.2 与 6.3 的示例行；交作者清单另有一条：§5 句 6 "The gain may shrink at higher
noise rates."，表 5 若已有更高噪声率的结果，作者可以改成那一列的数字，删 may 就等于断言增益缩小。

机检对比：改前 FAIL 8（17×7：对冲超预算、两处堆叠、元评论、预先辩护、道歉与借口、局限节外的范围声明；
23×1：句长过于整齐），改后 FAIL 0，项 17 剩一条 note（局限节里的范围声明）。项 23 随删句消失，没有单独处理。
待补事实：无。未改之处：交作者清单两句各保留一个对冲，仍在预算内。

## 7. 示例（英文，润色模式，节选）

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
| 4 | 句 3 | may potentially … to some extent | Whether the gain holds … is tested in Section 5.6 | 17（堆叠、超预算） | 三重对冲改成可判定的指向；claim 强度由作者在 5.6 节的结果决定 |

机检对比：改前 FAIL 9（14/15/16×2/17×2/19/21/24），改后 FAIL 0。待补事实：无（表 4 的数字由作者提供）。
未改之处：无。
