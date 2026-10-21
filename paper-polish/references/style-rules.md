# 学术文体与去 AI 痕迹规范（规则全文）

本文件是 `paper-polish` 的规则正本，也是 `opt-paper-*` / `ml-paper-*` 两组写稿、回复信、投稿包技能引用的
同一份规则。模式与交付格式在 SKILL.md；正例库在 `style-rewrite-examples.md`；机检实现在 `stylecheck.md`。
条款后括号里的数字是 `stylecheck.py` 的项号。

顶刊评审对文体敏感，机器写作的默认习惯会显著降低稿件可信度。它有两层。**表层**是标点与词汇指纹：
连接词链、分号、句中冒号、破折号插入语、突然加粗、造词与缩写通胀、等长句、三连排比、强化副词、
分段摘要。**深层**是内容空洞：面向泛读者解释常识、段落里没有一个具体物、只报结果不给因果、引用成簇
不评价。表层靠纪律与机检拦，深层靠"事实清单先行"与读者模型。

**执行时机**：写稿时本规范在**起草时即生效**——每节动笔前先过一遍本规范与正例库，每写完一节立即跑
`stylecheck.py`，超标当场改；修订轮的文体审读只是 final sweep。润色已有文本时，先跑机检拿基线报告，
改完复跑到零 FAIL。起草时就写成合规文风的成本远低于事后清理，事后清理往往只改表面。

## 1. 表层纪律：标点、强调、命名、节奏

- **连接词纪律**（15）：句首显式连接词（Moreover / Furthermore / Additionally / In addition / Notably /
  Consequently / Specifically / Overall / Meanwhile / Nevertheless / 句首的 Thus；中文"此外/而且/另外/
  值得注意的是/综上所述/首先/其次/最后/总之/与此同时"）全文限量——每节至多 1–2 处，口径为**句首
  （段首或句号后）出现才计数**；删掉后语义不变的连接词一律删。逻辑关系优先靠**内容顺序与 given-new
  衔接**（新句开头承接旧句已知信息）表达，不靠连接词标签。
- **分号纪律**（14）：正文散文**不用分号**——拆成短句或重组。豁免：数学环境、算法伪代码、参考文献
  （豁免处加 `% style-exempt` 注释便于核查）。
- **冒号纪律**（19）：正文散文**句中不用冒号**。冒号只允许出现在行尾，引出显示公式、列表或算法伪代码
  （中文"："同）。"three components: A, B, and C" 改写为完整句子逐个展开。
- **破折号纪律**（20）：正文散文**不用破折号**（`---`、`—`、两侧带空格的 `--`；中文"——"）。插入语改成
  从句或拆成独立句；数字范围 `20--50` 不受限。
- **强调纪律**（21）：**句中不加粗、不斜体强调**。`\textbf` 只出现在表格最优值、算法关键字与定义环境；
  术语首次定义可用一次 `\emph`。段首引导词（Setup. / 状态）一律写成 `\paragraph{Setup}`，每节
  ≤4 个，不写成 `\textbf{Setup.}`——机检靠这个区分结构与强调。Markdown 文本里的 `**加粗**` 按句中
  强调计。
- **命名与缩写纪律（不造词）**（18）：
  - 命名预算 = 方法总名 1 个 + **每个进消融表的机制各 1 个名字**（与贡献数对齐，通常 2–4 个），此外
    不再命名；名字首次出现处定义，此后固定用法。
  - 命名风格 = 由**既有术语组合**（以该方向 SOTA 表与相邻论文用词为准）、**描述机制**而非宣称效果
    （Efficient / Robust / Novel / Smart / Adaptive 不入名）、≤3 个词、禁"形容词堆叠 + 名词"链
    （Context-aware Hierarchical Adaptive …）；正文中机制名作**小写普通名词**使用，只有方法总名可
    专有名词化。
  - 缩写预算 = 方法总名可有 1 个缩写（≤5 字母）；子机制不起缩写，除非全文用 ≥10 次且展开 ≥3 词；
    任一句子至多 1 个自造缩写；标题不含自造缩写，摘要定义后可用 1 次。机检输出缩写清单：定义处与
    使用次数，用 ≤2 次的缩写展开后删掉。
  - 中文同理：不造"××感知/××驱动/××增强"式新词，方法名用既有术语组合。
- **禁用/替换表**（16）：It is worth noting that → 直接陈述；plays a crucial/pivotal role in → 写出
  具体作用；leverage / utilize → use；delve into → examine / analyze；aims to + 动词 → 直接用该动词；
  showcase / underscore → show / highlight 且限量；In this section, we will → 删（结构自明）；
  comprehensive / novel / remarkable 无证据不用。中文：值得注意的是、综上所述、旨在、"本文所提出的"
  反复出现（>2 次）都在表内。
- **节奏与密度纪律**（23、24）：句长有长有短（每节句长变异系数 ≥0.35）；三连排比（"X, Y, and Z"）每节
  ≤2；段落不等长；**段尾不写 "This design ensures …" 式小结句**，段落以最后一个事实结束。强化副词
  （significantly / effectively / seamlessly / comprehensively / remarkably）无数字不用；泛动词
  （facilitate / enable / ensure / enhance / demonstrate）与抽象名词（framework / paradigm / mechanism /
  scheme / module）限密度；"not only … but also""respectively"每节 ≤2。
- **摘要单段**（22）：摘要是**一个段落**，六句逻辑（问题与动机、缺口、想法、证据、结果、影响）。顶会、
  Elsevier/IEEE、Nature 子刊一律单段；只有期刊明确要求 structured abstract 时才分段。
- **正向文体纪律**：每段单一论点，主题句是**论断**不是预告（"The mask design dominates the
  contribution" 而非 "We now discuss the mask design"）；具体动词优先于名词化堆叠；主动语态与 we
  优先；**定量声明必须带数字与出处**（"substantially better" → "reduces the mean gap by 2.1 pp
  (Table 4)"，数字用宏或原表）。
- **时态惯例**：方法与模型描述用现在时；实验执行与观察用过去时；结论性陈述用现在时——按目标 venue
  相邻论文校准并全文统一。
- **词汇纪律：领域相邻论文用什么词就用什么词**（30）。机器写作偏爱书面化的生僻词，SCI 论文用的是
  领域内的平实词。替换表（左 → 右；`stylecheck.py` 逐词报出，目标刊物语料里出现过两次以上的词放行）：
  elucidate → explain；delineate → describe；underpin → support；salient → main；myriad / plethora → many；
  intricate → complex；nuanced / holistic / multifaceted → 删掉或写出具体差异；synergistic → combined；
  harness / leverage / utilize → use；bolster → support；foster → encourage；garner → gain；pertinent →
  relevant；endeavor → effort；ameliorate → improve；expedite → speed up；necessitate → require；
  encompass → include；albeit → although；whilst → while；hitherto / heretofore → so far；vis-à-vis →
  compared with；in lieu of → instead of；paramount → most important；quintessential → typical；
  meticulously → carefully；pivotal / cornerstone → key / basis；landscape / realm → field；testament →
  evidence；underscore / showcase / unveil → show；unravel → explain；embark → begin；pave the way → enable；
  shed light on → explain；cutting-edge → recent；groundbreaking / transformative / tapestry / usher /
  intriguing / elegant / noteworthy / profound / sheer → 删；commence → begin；ascertain → determine；
  exemplify → show；posit → propose；purport → claim；substantiate → support；corroborate → confirm；
  amalgamate → combine；juxtapose → compare；hinges on → depends on；boils down to → reduces to；akin to →
  similar to；wherein → where；whereby → by which；thereof / therein / hereinafter → 改写；aforementioned →
  these；burgeoning → growing；ubiquitous → common；seminal → early；immense / vast → large。判据不是
  "词难不难"，而是目标刊物的论文用不用：拿不准就查语料，语料用的词即使在表里也保留。
- **符号与连字符纪律**（31）：
  - 正文散文与表头**不用箭头和运算符代替词语**：`A → B`、`$\to$`、`↑`/`↓`、`3×`、`+2.1%`、`≈`、`/` 表示
    "或"，都改成词（leads to、higher is better、three times faster、an increase of 2.1 points、about）。
    表格里"越低越好"写进表注，不在表头挂箭头；增减量给自己一列并带单位，不用 `(+)`/`(−)` 标记。
    豁免：均值±标准差的 `±`、数学环境内的全部运算符。
  - 连字符只用于领域惯用的复合词与消歧，**不叠两个以上**（feasibility-mask-guided、graph-attention-based-
    decoder 改写成短语或已定义的术语）；前缀词按领域拼法（nonlinear、subproblem、preprocessing、
    multiobjective 等不加连字符；目标刊物语料里出现过的连字符拼法照用）；连字符复合词密度每千词 ≤25。
  - **CamelCase 自造名只许一个**（方法总名，如 FeasiSched），其余机制一律小写普通名词；
    `stylecheck.py --method-name` 声明那一个。

## 2. 深层纪律：读者模型与具体性（质量的主体）

- **读者模型**：目标读者是熟悉全部基线的审稿人。背景只为定义记号服务，能引用就不解释——不讲
  PPO 是什么、transformer 是什么；该读者已知的句子一律删。
- **段落具体性**（25）：方法与实验节**每段至少含一项具体物**——数字、公式引用、表图引用或具体例子；
  四者全无的段落是填充，删；无法删的留"待补事实"占位交作者。
- **因果解释**：结果段不止于"A 优于 B 2.1 pp"，必须有一句**机制解释**（"因为掩码进入 softmax 归一化项，
  梯度只在可行集内比较，所以…"）并指向背书它的消融或探针（Table 5）。
- **引用有评价**（26）：一处引用 ≤4 篇；引用某工作就给它一句具体评价（做了什么、缺什么），不写
  "several works [3–9] have explored"。
- **事实清单先行**（写法本身）：每节动笔前先列纯事实条目——数字、公式号、引用、表图号、结论——再据此
  成文；**每句话都能回指某条事实，回指不到的句子即填充**。润色已有文本时，事实清单从文本自身反推。
- **反向大纲**（27）：每段首句连读必须自己讲得通论证；讲不通的地方是段序或主题句的问题，不是措辞问题。

## 2.5 证明与推导的排版（32）

机器写作把证明写成一段散文，把等式链塞在句子里。数学领域的惯例是**分行连续推导**：

- 定理类环境之后用 `proof` 环境；推导用 `align` / `align*`，**每行一步**，步与步之间的依据写在行末
  `&& \text{(by Lemma 2)}`、`\text{(by the triangle inequality)}`，或引用式号；只给后文要引用的行编号
  （`align*` + `\tag` 或 `\notag`）；以 `\end{proof}` 收尾，不写"which completes the proof"。
- 正文里的推导同理：一个行内公式只放**一个关系式**（`$a = b$`），`$a = b = c = d$` 一律改成 `align`；
  一个证明超过约 120 词却没有任何 display 数学，就是段落式证明，重排。
- 文字只做三件事：说明要证什么、交代每步用了什么、指出结论；不复述公式已经写明的内容。

段落式 → 分行式（内容不变）：

```latex
% 段落式（机器写作）
We have $\nabla J = \mathbb{E}[\nabla \log \pi\, A] = \mathbb{E}[g]$ by the log-derivative trick, and since the
mask keeps the distribution valid on the feasible set the estimator is unbiased, which completes the proof.

% 分行式
\begin{proof}
By the log-derivative trick,
\begin{align*}
\nabla J &= \mathbb{E}[\nabla \log \pi(a \mid s)\, A(s,a)]      && \text{(policy gradient theorem)} \\
         &= \mathbb{E}[g]                                        && \text{(definition of $g$ in (7))}
\end{align*}
and $\pi$ remains a distribution on the feasible set under the mask, so $g$ is unbiased.
\end{proof}
```

## 3. 反防御性写作（与 AI 痕迹并列的第二类文体病）

防御性写作 = 为预防审稿人挑刺而堆砌的对冲、免责与过度限定；顶刊的实际文风是**论断干净、边界集中
声明**。五条纪律（17）：

1. 每个结论句**至多一个限定词**，禁止双重对冲（"may potentially""可能在某些情况下或许"）。
2. 限定必须**可判定**——"on instances up to $n=100$"合规，"in some cases / 在某些情况下"不合规。
3. 禁止无信息免责句（删掉后论文没有任何损失的句子一律删）。
4. **修复过度声称的唯一正确动作是收窄到证据边界并给出数字，禁止用软化词修复**。润色时本技能只标出
   过度声称处并留待补事实占位，收窄由作者决定。
5. 结论句写干净，适用边界统一进 limitations 节（引用研究边界表），不在每个结论后重复挂限定尾巴。

hedge 检测词表：may / might / could potentially / to some extent / relatively / arguably / 可能 / 或许 /
在一定程度上——每节 >2 即回改。界限：统计不确定性与明确适用条件是**合法限定**，本条款禁的是模糊、
堆叠、无判定条件的对冲。

## 3.5 脚手架（33）

机器写作用结构标签代替结构本身。以下都是脚手架，叙述顺序对了它们就多余：

- **枚举标签**：段内 "(i) … (ii) … (iii)"、"First, … Second, … Finally" 每节至多 1 组；贡献列表之外
  的 itemize / enumerate 不进正文节。
- **总结段与路线图段**："In summary / To summarize / Taken together / 综上 / 总之" 开头的段落只许在结论节；
  "The remainder of this section is organized as follows / 本节其余部分安排如下" 只许在引言（且仅当
  venue 惯例需要）。
- **句首提示词**："Note that / Importantly / Interestingly / Crucially / In particular / In other words /
  To this end" 并入句首连接词预算（15），每节 1–2 处；删掉后语义不变的一律删。
- **括号插入**：散文括号每百词 ≤1.5 个（引用与年份不计）；"i.e. / e.g. / etc." 每节 ≤4，能点名就点名。

## 4. 机检、校准与豁免

- **机检**：`stylecheck.py` 项 14–27（实现与阈值表见 `stylecheck.md`）。无脚本时的 grep 粗查：
  `grep -c ";" sections/*.tex`、`grep -cE -- "---|: [a-z]" sections/*.tex`、`grep -c "textbf" sections/*.tex`、
  `grep -cin "moreover\|furthermore\|delve\|leverage" sections/*.tex`——粗查噪声大，准数以脚本为准。
- **语料校准**：阈值用 `style_baseline.py` 从目标刊物 **2–3 篇已发表论文**统计（`style_baseline.json`
  存在即生效，容差 ±20%）；有作者旧稿时同法提取作者基线，稿件向作者靠而不向通用学术腔靠。
- **豁免**：合法例外在该行加 `% style-exempt`——数学与伪代码里的分号冒号、引用他人原文、术语首次
  定义的强调、Harvard 多引文列表的分号。

## 5. 体裁规则

- **论文正文、摘要、研究方案**：全部条款。
- **rebuttal 回复信**：礼节句式、编号冒号与加粗定位是体裁结构，不受标点与强调条款约束；命名与缩写
  纪律、禁用词、对冲、节奏同样适用；回复信沿用稿件已定义的机制名与缩写，不另起新名。
- **cover letter**：首末段礼节句豁免标点与加粗条款；期刊名用斜体宏（不计入 `\emph` 预算）；其余与正文
  同标准——句长有长有短、无 novel/significantly、无句中冒号与破折号。
- **中文文本**：标点与词表自动切换——正文不用"——"与句中"："，连接词与对冲按中文词表，不造
  "××感知/××驱动/××增强"式新词；段首引导词用 `\paragraph{}` 而非 `\textbf{状态。}`。空话与生僻词
  （赋能、抓手、底层逻辑、闭环、颗粒度、擘画、彰显、凸显、阐释、诠释、赋予、不可或缺、举足轻重、行之有效、
  深度融合、全方位、多维度、层层递进、应运而生）改成具体动作或删；"（一）（二）"枚举每节至多 1 组，"综上"
  段只在结论；证明同样分行推导。

## 6. 诚实边界

文体规则显著降低但不能消除 AI 痕迹——终稿建议作者人工通读定稿；AI 辅助的披露按目标 venue 政策如实
处理。目标是写出资深学者水准的文章，不是规避检测。
