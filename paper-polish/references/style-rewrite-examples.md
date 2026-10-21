# 文体改写对照（AI 腔 → 期刊腔）

本文件是 `paper-polish` 规则 `style-rules.md` 的正例库：起草前读一遍，润色与改写时对照校准。
八组对照覆盖表层指纹（连接词链、分号、造词与缩写、破折号/冒号/加粗、分段摘要、等长段落）与深层
空洞（只报结果不给因果）。规则记不全没关系，**照着"改写后"的样子写**。

## 对照一：连接词链 → given-new 衔接

**改写前（AI 腔，每句靠段首连接词粘合）：**

> Moreover, the mask participates in the policy gradient. Furthermore, this
> changes what the policy has to learn. Additionally, the learning target
> becomes a comparison among feasible actions. Consequently, sample
> efficiency improves.

**改写后（期刊腔，新句开头承接旧句已知信息，删光连接词，也不借冒号接续）：**

> The mask participates in the policy gradient, which changes what the
> policy has to learn. Instead of telling feasible from infeasible actions,
> the policy only compares actions inside the feasible set. This smaller
> learning target is where the sample-efficiency gain comes from (Section 5.3).

要领：删掉连接词后若句子接不上，问题不在连接词而在**句序**。把上一句的宾语变成下一句的主语，
逻辑自然接续；额外收益是逼出"增益从哪来"这类实质内容。

## 对照二：分号长句 → 拆短句

**改写前：**

> The encoder maps the disjunctive graph to node embeddings; the decoder
> scores ready operation--machine pairs; infeasible pairs are masked out;
> the resulting distribution is used both for sampling during training and
> for greedy decoding at test time.

**改写后（独立成句）：**

> The encoder maps the disjunctive graph to node embeddings. The decoder
> scores ready operation--machine pairs and masks out the infeasible ones.
> The resulting distribution serves training (by sampling) and testing
> (by greedy decoding).

另一种拆法是**主从重组**（把并列分句改成主句 + which/that 从句，见对照一）。真正的并列项不用
"three components: A, B, and C" 引出，而是用完整句子逐个展开（见对照五）。分号与句中冒号的合法
住所只有数学环境、伪代码与参考文献。

## 对照三：防御性对冲 → 论断 + 可判定边界

**改写前（双重对冲 + 模糊限定 + 免责句）：**

> The proposed mask may potentially improve sample efficiency in some
> cases. It should be noted that we do not claim optimality in all
> settings, and results might vary depending on the instance distribution.

**改写后（论断干净，边界可判定且集中声明）：**

> The mask reduces the steps to reach a 5\% validation gap by \SpeedupVsBase{}
> (Table 5). All results are on instances of up to $50\times20$ drawn from the distribution in Table 1. Larger scales and other distributions are outside
> this study's scope (Section 7).

要领：(1) 结论句给数字与出处，一个限定词都不留；(2) 适用范围写成**可判定条件**（规模、分布、
表号），不写 "in some cases"；(3) 免责内容集中到 limitations 节，正文不挂尾巴。

## 对照四：造词与缩写通胀 → 既有术语、一个缩写

**改写前（每个模块一个专有名词一个缩写，名字宣称效果）：**

> We propose the Adaptive Context-Aware Feasibility Gating Module (ACFGM),
> coupled with a Dynamic Graph Encoder (DGE) and a Prioritised Sampling
> Scheme (PSS). The ACFGM-DGE-PSS framework is efficient and robust.

**改写后（方法总名一个缩写，机制名是小写普通名词，说的是机制做什么）：**

> We propose masked constructive scheduling (\textsc{MCS}), a constructive policy that applies a
> feasibility mask before the softmax at every decoding step. The mask is
> computed from the two precedence constraints in Eq.~(3); the encoder is a
> graph attention network and the sampler follows Kool et al.\ unchanged.

要领：一篇论文的命名预算是方法总名加每个进消融表的机制各一个名字，缩写只给方法总名。机制名由
既有术语组合（feasibility mask、graph attention encoder），描述它做什么，不带 adaptive / dynamic /
efficient 这类效果词，正文里当普通名词小写使用。审稿人看到三个自造缩写串成的 framework，读到的是
包装而不是贡献。

## 对照五：破折号、句中冒号、突然加粗 → 平实句法

**改写前：**

> Our approach has three components: an encoder, a decoder, and a critic ---
> each of which is \textbf{fully differentiable}. The key insight --- that
> constraints belong in the action space --- drives the design: \emph{feasibility
> is structural, not learned}.

**改写后：**

> The policy consists of an encoder, a decoder and a critic, all trained end
> to end. The design rests on one observation. Feasibility in this problem is a
> property of the action space, so it is encoded there rather than learned
> from a penalty. Section 4.2 gives the encoding.

要领：破折号插入语改成从句或独立句；句中冒号改成"X 有三部分。第一部分…"或直接一句话列全；
想加粗的那句话，通常是段落真正的主题句，把它放到段首用陈述语气写出来即可，不需要字体帮忙。
`\textbf` 只出现在表格最优值与算法关键字，`\paragraph{Setup}` 才是段首引导词的写法。

## 对照六：分段摘要 → 单一段落、六句逻辑

**改写前（三段，像一份小引言）：**

> Scheduling is important in manufacturing. Existing methods have limits.
>
> We propose a new mask-based framework and evaluate it on benchmarks.
>
> Results show improvements. The method has broad applicability.

**改写后（一段，句句有内容）：**

> Constructive scheduling policies trained with reinforcement learning handle
> precedence and machine constraints through reward penalties, which wastes samples on infeasible
> actions and degrades on instances larger than those seen in training. We
> encode the constraints as a feasibility mask that is updated at every decoding
> step and enters the policy gradient. The mask needs no penalty weight and
> keeps every sampled solution feasible by construction. On 59 benchmark instances the
> method reduces the mean gap by \ImpvOverBase{} against the strongest baseline
> (Wilcoxon $p<0.001$) and retains feasibility on instances four times larger
> than the training range. The design transfers to other constraint-dense
> problems where feasibility is decidable from the partial solution.

要领：摘要是一个段落。分段的摘要在期刊系统里会被合并成一段，而分段本身暴露出作者是按"背景/
方法/结果"模板填空。六句各有分工，每句都能被正文的某张表或某个公式支撑。

## 对照七：只报结果 → 因果解释 + 证据落点

**改写前：**

> Our method outperforms all baselines by 2.1 pp on average, demonstrating
> the effectiveness and superiority of the proposed framework.

**改写后：**

> The method lowers the mean gap by \ImpvOverBase{} (Table 4). The gain comes
> from the gradient rather than from filtering. Masking only at sampling time,
> which leaves the gradient untouched, closes 0.4 pp of the 2.1 pp (Table 5,
> row 2), so the remaining 1.7 pp is attributable to the mask entering the
> softmax normalisation.

要领：结果句之后必须跟一句"为什么"，而且这句"为什么"要指向一张能证明它的表（消融、探针、行为
统计）。没有证据落点的因果解释是猜测，写成"we hypothesise"放到 discussion。

## 对照八：等长段落与段尾小结 → 节奏变化

**改写前（三段各五句、句长相仿、段尾都来一句总结）：**

> The encoder maps the graph to embeddings. The decoder scores the pairs. The
> critic reads the same embedding. The policy samples actions. This design
> ensures stable training.
>
> The buffer stores transitions. The advantage uses GAE. The update follows
> PPO. The entropy term aids exploration. This approach guarantees convergence.

**改写后（长短交替，段落以最后一个事实结束）：**

> The encoder maps the disjunctive graph to node embeddings that the decoder and the
> critic both read, so the three modules share one representation of the
> partial solution (Fig.~2). Transitions go to a rollout buffer of 512
> instances. Advantages use GAE with $\lambda=0.95$, and the clipped PPO
> objective in Eq.~(12) updates the weights for three epochs per rollout.

要领：段尾的 "This design ensures…" 是模板句，删掉后段落只会更紧；句长变化让读者知道哪句是
重点。机检第 23、25 项分别量这两件事。

## 使用方式

- 起草：每节先落事实清单（`paper/facts/<section>.md`），再读本文件 30 秒，按"改写后"的密度与
  句法写，每句回指清单里的一条事实。
- 机检：写完一节跑 `stylecheck.py`（项 14–27）；阈值可用 `style_baseline.py` 从目标刊物已发表论文
  校准。
- 中文写作同样适用：连接词（此外/而且/值得注意的是）、对冲（可能/或许/在一定程度上）、标点
  （——/句中：）、造词（××感知/××驱动）的对应规则见 `style-rules.md` 的中文条款。
