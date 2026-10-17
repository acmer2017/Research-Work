# 并行与批处理加速凝聚子图枚举：论文精读与独立选题分析

初稿：2026-10-16；更新：2026-10-17。研究目标是 **cohesive subgraph enumeration 的精确加速**，重点考察多核并行、搜索任务批处理、状态与计算复用。本文将其作为独立课题，不以 BCviz 或索引构建为前提。

**主要判断：方向可以继续研究，但“并行执行＋批量发任务”已有大量直接先例。更值得验证的是：保持每个搜索分支的唯一归属和极大性语义，在内存预算内，将相关搜索状态组成小批，减少候选状态复制、重复邻接读取和重复统计计算。** 根据用户进一步明确的设想，主线收敛为：**DFS 同父节点下，邻居相近的多个子分支，以位向量和按位 AND 联合推进搜索**。先在 maximal clique 上验证这一机制；k-plex 和 biclique 作为有条件的扩展。这个建议是基于现有证据的选题判断，不是已证实的新颖性或性能结论。

用户指定论文的 [PDF 已保存](papers/Shared-memory-Parallel-Maximal-Clique-Enumeration-from-Static-and-Dynamic-Graphs.pdf)。本专题另保存了相关作者版，见 [PDF 清单](papers/README-parallel.md) 和 [版本及 SHA-256 清单](papers/parallel-paper-manifest.json)。更广的文献分类见 [reference-enumeration.md](reference-enumeration.md)。

## 1. 阅读范围与问题边界

本文的主分析依据正文中的算法、证明、数据结构和实验，不仅依据摘要。主论文阅读涵盖 Algorithms 1–7、Lemmas 1–4、§4–6 和 Appendix A；相近论文的阅读位置在各节列出。**所有“PDF p.”均指本地文件从首页起的物理页码。** 未复现论文的大图性能实验；cuMBE 额外核对了公开源码的结果接口和计时边界。

文中的“原文”表示能定位到论文或代码的事实；“分析”表示据此作出的推论；“拟研究”表示尚需实现、测量和证明的方案。不能把本文的拟研究方案写成已有实验结论。

### 1.1 先固定输出合同

| 问题 | 需要输出什么 | 对并行化的直接影响 |
|---|---|---|
| Maximal clique enumeration，MCE | 全部包含意义下极大的团 | 必须保留 excluded 集合；局部不能继续扩展不一定是全图极大 |
| Maximal biclique enumeration，MBE | 全部极大双团，通常指二部图中的两侧点集 | 闭包、两侧扩张与规范次序共同决定去重，不能直接照搬 clique 状态 |
| Large maximal k-plex enumeration | 全部大小至少 q 的极大 k-plex | 缺边预算、候选与排除集合、大小上界均是状态；二跳限制有参数前提 |
| Maximal γ-quasi-clique enumeration | 满足相对最小度约束的全部极大准团 | 结构不具遗传性；可行候选的产生与最终极大性过滤可能是两个阶段 |
| Fixed-k clique / fixed-pattern enumeration | 固定大小团或指定模式的实例 | 可以借鉴并行原语，但没有相同的全局极大性问题 |

这里的 maximal 是“不能包含于更大的合法结果”，不是 maximum“全图规模最大”。计数、逐结果回调、完整顶点列表物化、落盘也不是同一成本。如果逐点写出全部结果，至少需要处理总输出长度 `L = Σ_result |result|`；双团则计两侧点数。硬件吞吐、结果缓冲和存储可能成为最后的瓶颈。

### 1.2 四种 batching 不应混用

| 批处理类型 | 批次中是什么 | 代表工作 | 与本课题的关系 |
|---|---|---|---|
| 图更新批次 | 一批新增边 H，共同形成新快照 G+H | ParIMCE | 动态维护问题；不是静态搜索状态批处理 |
| 根任务/队列批次 | 一组 seed、任务描述符、待拉取邻接表 | 并行 k-plex、Quick+、G-thinker | 已有共享图、批量搬运和调度技术 |
| 搜索状态/算子批次 | 多个独立状态的一批集合交、degree、共同邻居或极大性检查请求 | 本文优先考察的方案 | 目标是降低每个状态的实际处理成本 |
| 多查询批次 | 多组 q/k/γ、多个查询或图版本 | 另一类工作负载 | 不作为本文默认目标；跨参数/版本复用必须另证 |

后文默认输入为**一个静态图、一次精确枚举任务**。动态图批次作为主论文的重要组成单独分析，不将动态批次的收益直接套到静态任务上。

## 2. 核心论文：Shared-Memory Parallel Maximal Clique Enumeration from Static and Dynamic Graphs

Apurba Das、Seyed-Vahid Sanei-Mehri、Srikanta Tirthapura；**ACM Transactions on Parallel Computing，2020**；[DOI:10.1145/3380936](https://doi.org/10.1145/3380936)。所读 [arXiv:2001.11433v1](https://arxiv.org/abs/2001.11433v1)，28 页，2020-01-30；HiPC 2018 工作为前身，不应把会议和扩展稿当作两套独立方法累加。

这篇论文的核心价值有三层：**把递归兄弟分支改写为可独立构造的状态；用根所有权结合根间、根内并行；在动态图中用新增边所有权剪除重复搜索。** TBB 是实现这些思想的运行时工具，算法贡献不能概括成“用了多线程”。

### 2.1 TTT 的状态及其串行依赖

原文 §3–4，PDF pp.6–9；Algorithm 1 见 p.7。用 `P=cand`、`X=fini` 简写：

- `K`：当前已经选择的 clique。
- `P`：与 K 中全部顶点相邻、仍允许继续选择的顶点。
- `X`：与 K 中全部顶点相邻，但已由更早分支负责的顶点；也保留“当前 K 还能被这些点扩展”的证据。

只有 `P=∅ 且 X=∅` 时才能报告 K。若 `P=∅、X≠∅`，K 仍可被 X 中顶点扩展，不能报告为极大团。

TTT 从 `P∪X` 中选择使 `|P∩N(u)|` 最大的 pivot u，只对 `ext=P\N(u)` 中的点分支。每完成一个分支，就将该点从 P 移入 X。因而串行循环后一个分支的输入依赖前一个分支对 P/X 的更新。将这个循环直接改成 parallel-for，且让所有子任务使用同一份初始 P/X，会破坏原来的搜索划分。

### 2.2 ParPivot：并行化 pivot 的统计与归约

Algorithm 2、Lemma 1，PDF p.8。对每个 `w∈P∪X` 并行计算 `t_w=|P∩N(w)|`，再做并行 argmax；单个集合交内部也可以并行。

论文给出的工作量是：

```text
W_pivot = O( Σ_{w∈P∪X} min{|P|, |N(w)|} ) ≤ O(n²)
D_pivot = O(log n)
```

其哈希实现遍历较小集合，对较大集合查询成员。理论依赖论文的并行哈希模型；不能把所有查询视为真实 NUMA 机器上没有缓存未命中或同步成本的常数操作。

**有效之处**：pivot 计算是大量可独立的集合成员查询，并行归约清楚；继承 TTT 的强 pivot，避免为增加并行度而任意扩大分支。

**代价与局限**：很小的 P/X 不值得创建大量细任务；大状态的候选与邻接扫描可能受带宽限制；寻找最优 pivot 本身也有成本。并行化 pivot 与采用更便宜的 pivot 策略是两个变量，比较时应分别消融。

### 2.3 ParTTT：真正关键的是显式恢复兄弟前缀

Algorithm 3、Lemma 2，PDF pp.8–10。固定 `ext=(q₁,…,qᵣ)`，令 `E_<i={q₁,…,qᵢ₋₁}`，第 i 个子任务独立计算：

```text
K_i = K ∪ {q_i}
P_i = (P \ E_<i) ∩ N(q_i)
X_i = (X ∪ E_<i) ∩ N(q_i)
```

这不是等待前面的兄弟“真的执行完”，而是预先知道串行次序会把哪些点移到 X，从而直接构造相同的逻辑输入。子树执行的物理次序可以任意，逻辑所有权仍固定。

**正确性要点**：

1. P_i 与 X_i 中所有点仍与 K_i 完全相邻。
2. 更早的 ext 点不能再被第 i 个分支选入，但仍保留在 X_i 中用于排除重复和非极大输出。
3. 每个最终 clique 归属于其包含的最早可扩展分支；其余兄弟的 X 状态阻止重复报告。

这也是以后做 batch、异步拆分或 GPU donation 必须保持的不变量。将多个状态放在同一批中可以共享只读数据，却不能让它们互相覆盖 P/X。

**实际成本**：串行 TTT 每轮只移动一个点；ParTTT 要让各兄弟独立恢复前缀，可能产生更多集合构造、复制和分配。论文 §4.2 自己明确指出：最坏渐进工作量相同，实际输入上的工作仍可能更高。这里正是“总工作”和“并行时间”应同时衡量的原因。

### 2.4 理论保证应怎样理解

Lemma 2 报告 `W=O(3^(n/3))`、`D=O(M log n)`，M 是最大 clique 大小。它用每个调用与 TTT 同阶的操作成本，继承 TTT 的最坏工作量分析；递归链至多 M 层，每层并行集合操作/归约深度 O(log n)。

标准 work–span 推论应为：

```text
T_p = O(W/p + D)
    = O(3^(n/3)/p + M log n)
```

**版本核对发现**：所读作者版 PDF p.9 Corollary 1 把式子印成 `O(3^(n/3)/(M log n)+P)`，并把 Brent 公式印成 `O(w/d+P)`；已检查 PDF 图像，并非文字抽取错位。紧接着 p.10 的证明使用了正确的 `max{3^(n/3)/P, M log n}`。本文按 Lemma 2 和标准 Brent 定理重述，不照抄该排印错误，也不据此否定整个算法。

有三个重要边界：

- **模型边界**：CRCW PRAM 与期望/平均哈希成本不等于确定性的现实机器最坏延迟；更严格的并行内存模型可能引入额外代价。
- **比较边界**：与 TTT 同阶的最坏工作量，不代表每个输入都与当前最快串行实现做同样多的工作，也不代表 ParMCE 的所有工程步骤自动继承同一个界。
- **输出边界**：Moon–Moser 给出极大团个数可达 `3^(n/3)`。若要求逐结果写出全部顶点，还须计入 L；不能将每次 `Output K` 无条件当成 O(1) 的完整序列化。

这是一篇有理论支撑的并行算法论文，但其理论不是“任意核数下线性加速”或“2026 年所有 MCE 算法中的最优实现”。

### 2.5 ParMCE：根所有权与两层并行

Algorithm 4、§4.2，PDF pp.10–11。给顶点一个全序，对每个 v 建立根任务：

```text
G_v = G[N(v) ∪ {v}]
K_v = {v}
P_v = {w∈N(v) : rank(w)>rank(v)}
X_v = {w∈N(v) : rank(w)<rank(v)}
调用 ParTTT(G_v, K_v, P_v, X_v)
```

每个 clique 只属于其中 rank 最小的顶点。根任务之间并行，根内部继续用 ParTTT；共享内存避免像分布式方案一样把全部局部任务跨网络复制。

**为什么能快**：直接从空 K 开始时 pivot 要面对整个图；固定一个根后，工作域缩到它的邻域，候选统计更小，并且早期就有许多可执行任务。与单纯给同一串行程序增加线程相比，ParMCE 还改变了任务组织与具体工作量。

论文尝试 degree、triangle count、core number 三种排名，将估计更复杂的顶点排在后面，使它少拥有包含较早顶点的结果。这是负载启发式：相同度数或 core 值的局部图仍可能有极不相同的搜索树。

**一个容易误读的细节**：文中 `ParMCEDegen` 使用 `(core number, ID)` 排序，不是逐步最小度剥离得到的 degeneracy order。反例是星图：所有点 core number 都为 1；若中心 ID 最小，它的根候选集有 n−1 个点，而图 degeneracy 为 1。因此不能从该名称推出每根 `|P_v|≤d`。若新方法需要这一界，必须使用真正满足后邻居数限制的排序并重新分析成本。

ParMCE 的优势是根间与根内并行兼顾，并且排名、集合操作与 TBB 调度可以组合。局限是局部图/状态准备仍有代价，重根仍可能形成尾部，排名预处理可能不偿失；“共享原图”不意味着“所有任务状态都不复制”。

### 2.6 ParIMCE：动态图新增边批次的精确处理

§5、Algorithms 5–7，PDF pp.11–15、27–28。记 `C(G)` 为 G 的极大团集合，新增边批次为 H：

```text
Λ_new = C(G+H) \ C(G)
Λ_del = C(G) \ C(G+H)
```

Λ_del 中旧 clique 的边没有消失；它们因被更大的新 clique 包含而失去极大性，称为 subsumed cliques。

**新 clique 的搜索范围。** 新极大团必含 H 中至少一条边。对于新增边 `e=(u,v)`，只需在更新图中搜索 `{u,v}∪(N(u)∩N(v))`，固定 K={u,v}。但包含多条新增边的结果会出现在多个局部搜索中。

**去重依靠最早新增边所有权。** 给 H 固定全序，结果由它所包含的最早新增边拥有。处理 e_i 的 `ParTTTExcludeEdges` 一旦发现当前 K 已包含某条更早新增边，就剪掉整个分支。不能为了避免 earlier edge `(a,b)` 而直接删掉端点 a、b：只包含 a、不包含 b 的合法结果仍可能属于当前任务。

Algorithm 6 的 `K_q∩E` 是“当前 clique 包含禁止边”的简写，实际须检验两个端点；顶点集合与边集合不能按字面直接求交。并行循环内的 return 应解释为终止当前子分支，不能取消所有兄弟。

**旧极大团的处理。** Algorithm 7 对每个新 clique c，从候选集合 `{c}` 出发，逐个处理 c 内新增边 `(u,v)`：候选若包含这条边，就分成“删除 u”和“删除 v”两个候选；最后查询旧集合 C，取出仍是旧极大团的候选。不同新 clique 可能导出同一旧结果，集合插入/删除须有正确的并发语义。若实际接口直接累加计数或发送结果，contains 后再 append 的非原子组合可能重报，需要 atomic claim 或独立规范归属。

**为何此阶段可能昂贵。** 若 c 含 h 条新增边，拆分路径可达 `2^h` 量级；候选去重、存储和旧集合查询都是成本。更重要的是，有时指数代价来自真实输出：原图为 `K_(2h)` 删除 h 条互不相交边，则旧极大团有 `2^h` 个；将这些边作为一批补齐后，一个新完全图会 subsume 全部旧结果。要求列出全部变化时，不可能普遍消除这一输出下界。可研究的是多余候选与重复生成，不是承诺所有更新均多项式。

**理论与实现边界。** Lemma 3 报告新结果阶段相对顺序 FastIMCENewClq 的工作效率，深度 `O(Δ²+M log Δ)`；Appendix A 中 Δ² 来自每条新边的局部诱导子图串行构造。Lemma 4 对每个新 clique 的 subsumed 阶段给 `O(min{M²,ρ})` 深度，ρ=|H|；这依赖并行集合操作模型，不限制中间候选总量。删除边通过归约处理，论文没有全面验证任意混合插入/删除批次。

实验实现还有一个值得复现时注意的变化：§6.2 将每个 edge-local 子图再按 degree 排名切成 vertex-root 子问题，再调用排除边版本；不完全等于 Algorithm 5 的直接单次 ParTTT 调用。

### 2.7 实验到底支持什么

§6，PDF pp.15–24。实现为 C++11、ICC 18、TBB，使用并行循环、并发哈希表和动态 work stealing。机器为 32 个物理核、4 个 NUMA 节点、1 TB RAM；`numactl -i all` 做交错内存放置。triangle/core 排名使用串行预处理。该配置不是已经实现 NUMA 局部性自适应批处理的证据。

| 原文证据 | 能支持的结论 | 不应外推的结论 |
|---|---|---|
| Table 4：Orkut，TTT 28,923 s → ParMCEDegree 1,676 s；Wikipedia，2,646 s → 123 s | 指定输入、32 核配置下约 17.3×、21.5×；算法组织与并行共同有效 | 不能当全部输入的保证，也不是只改变线程数的纯 scaling |
| degree 排名通常有较好的总时间，复杂排名有额外开销 | 更精细的负载估计未必抵得上计算成本 | 不能只报告 enumeration time 而隐藏排名成本 |
| Table 7（均排除排名时间）：Orkut，ParMCEDegen 2,350 s，PECODegen 2,183.4 s | 存在该配置下基线更快的实例 | 不能照抄“所有配置一致优于基线” |
| 动态部分相对 IMCE 的累计加速约 3.6–19.1× | 新结果与 subsumed 阶段存在可利用并行度 | 不是任意批次、任意变化规模下的固定收益 |
| 通常 1,000 条边/批，Ca-Cit-HepTh 为 10 条/批 | 验证了固定更新批次下的维护 | 没有系统回答最佳 batch size、等待延迟和峰值内存 |

动态图从空图增长，按时间加入边；LiveJournal 用静态边的随机排列模拟更新流。它与真实相关 burst、任意混合更新不同。部分极大输出输入无法在很长时限内完成，说明并行不能绕过输出爆炸。

不同表格有取整或不同展示精度，例如 DBLP 的 degree 时间出现 2、3、2.6 s；本文不跨表拼出精确比率。原文也未明确证明其时间包含所有 clique 的完整顶点 ID 序列化与落盘。应将它作为待确认的输出口径，而不是武断归为“已经完整写出”或“明确只计数”。

### 2.8 对这篇论文的评价

**最有效的技术**是：以逻辑顺序解除 P/X 的执行依赖；用根/新增边的规范归属提前剪掉重复搜索；同时利用根间与根内并行；对 work 和 depth 分开论证。

**主要不足**是：相同最坏工作量不保证输入级工作量小；独立状态构造可能复制很多；负载排名只是粗代理；极大输出与 subsumed 候选可能主导；实验未覆盖现代强内核、系统 batch-size 设计与完整输出成本。

**可以深入的空间**是：在严格保持上述所有权的前提下减少实际复制/统计工作，以复制字节和可共享计算量指导拆分与成批执行，并明确何时应回退到普通 DFS。仅将 TBB 换成另一任务库，或仅将节点外层改为 OpenMP，不足以构成这个方向的核心贡献。

## 3. 与目标最接近的五篇论文

前四篇分别代表共享内存的松弛凝聚子图、分布式准团、GPU clique 和 GPU biclique；第五篇专门针对用户明确的位向量 AND 思路，核对已有 bit-parallel MCE 到底在哪个层次并行。

### 3.1 Efficient Enumeration of Large Maximal k-Plexes

Qihao Cheng 等；**EDBT 2025**；[作者版 arXiv:2402.13008v3](https://arxiv.org/abs/2402.13008v3)，2024-06-10，[本地 PDF](papers/Efficient-Enumeration-of-Large-Maximal-k-Plexes.pdf)。所读 PDF 首页正式页脚为 EDBT 2025，不能沿用早期笔记中误写的 ICDE 2024。重点：PDF pp.3–9 的定义、Algorithms 2–4、顶点对剪枝、§6 并行；pp.9–12、16–17 的实验。

#### 问题分解与算法内核

其约定为 `deg_P(v)≥|P|−k`，每点至多 k−1 个其它非邻居，k=1 即 clique。目标是大小至少 q 的全局极大 k-plex，利用 `q≥2k−1` 的直径至多 2 性质进行二跳局部化。不能把这个限制推广到所有小 k-plex；小解可能不连通。

先做 `(q−k)`-core 削减和 degeneracy 排序，为 seed v 构造一/二跳局部图。枚举结果中与 v 不相邻的 seed 集合 S，`|S|≤k−1`；初始化已选集合 `P={v}∪S`、候选 C 和排除集合 X，然后分支。最早顶点决定根所有权，S 决定根内子任务；X 还需保留较早顶点的全局极大性证据，不能因局部存储方便就丢掉。

这里 P 表示“已选点集”，与前面 clique 的 P=cand **含义不同**。实现共享执行框架时，应将状态字段明确命名为 selected/candidates/excluded，避免混淆。

分支选择诱导度较小、对已选集非邻居较多的 pivot；搜索分为 include 和 exclude。include 前用 upper bound 判断是否还有机会达到 q；exclude 将该点放入 X。若整个 P∪C 已是 k-plex，可在检查外部扩张后直接报告，不必逐点继续展开。

剪枝还包括缺边预算上界和顶点对共同出现的必要条件。Algorithm 4 使用 `slack_P(u)=k−missing_P(u)`，处理候选时会消耗临时 slack；**同一状态内部的候选循环存在顺序依赖**。把它直接拆成独立 GPU 线程会改变原上界，除非重新证明另一个安全界。

Boolean T 矩阵用于记录顶点对兼容性。论文有随任务候选域变化的检查，且 §6 拆分时需物化 T；不能未经进一步代码核对就认定所有 T 都是 seed 级不可变常量。

#### 并行机制：与用户目标已经很相近

§6 每阶段只处理接下来的 M 个 seed 图，M 对应工作线程数。同一 seed 的子任务共享邻接矩阵；各线程本地队列优先处理，空闲后窃取任务。阶段内任务全部结束再释放这些图并进入下一阶段。

长任务在递归边界检查 elapsed time，超过阈值就把未完成分支包装为新任务；回溯路径上尚未执行的分支也会形成任务。新任务复用 seed 图，但需保存 P/C/X 和 T 等状态。

因此，“shared seed graph＋local-first＋work stealing＋timeout splitting”是它已经完成的组合。timeout 是协作式拆分：一次剪枝、物化或输出可能超过阈值，它没有保证每个任务的 wall-clock 严格小于 timeout。

#### 有效技术、代价与实验

有效之处在于把强串行剪枝和可分解的搜索域一起使用，避免静态根分配的长尾；同 seed 图共享降低重复构图成本。本地优先调度也改善缓存复用。

代价是阶段屏障可能被重 seed 拖住；细拆分增加 P/C/X/T 物化；更多任务不必然减少总工作。q/k 变化会显著改变子问题数与剪枝强度。

Table 4 的 enwiki2021、k=3、q=50、16 线程设置：FP 为 19,056.73 s，ListPlex 为 3,860.17 s，本文方法为 1,008.26 s。**18.9× 是同为 16 线程时相对 FP 的比较，不是自身从 1 到 16 线程的扩展比。** 自身扩展的例子是 it-2004、k=3、q=2000，16 线程约 15.82×。时间包含 core、局部图构建与枚举，不含原图加载；完整结果落盘成本未明确。

原文省略一些无结果或基线极慢的参数设置；新实验应补上这些负例。默认 timeout 0.1 ms 在所测配置较好，最佳阈值跨实例变化很大，不能直接作为新系统的普适常数。

#### 剩余空间

可以研究**同 seed 内相关状态的统计复用与复制量约束**，尤其是度、共同邻居计数、缺边预算的输入统计。需要逐状态保留 C/X 和 slack，只共享可证明与状态无关的量，或通过精确差量恢复每个状态的量。

难点是强串行方法本来就可能增量维护计数；新的批 kernel 必须优于“每状态增量维护＋普通并行”，而不能只与每次重扫原图的弱实现比较。该论文是建议首先复现并剖析的直接基线。

### 3.2 Scalable Mining of Maximal Quasi-Cliques: An Algorithm-System Codesign Approach

Guimu Guo、Da Yan 等，Quick+；[arXiv:2005.00081v8](https://arxiv.org/abs/2005.00081v8)，2021-05-10，[本地 PDF](papers/Scalable-Mining-of-Maximal-Quasi-Cliques-QuickPlus.pdf)。本文引用所读作者版，不以其未填完的 PVLDB 模板推断正式卷期。重点：PDF pp.8–17，§5–7、Algorithms 2–10；pp.18–22，Tables 5、7、10、12–14。

#### 内核：剪枝本身就带有迭代与依赖

γ-quasi-clique 要求每个点满足 `deg_Q(v)≥ceil(γ(|Q|−1))`，本文定义还要求连通。其二跳局部化使用 γ≥0.5 等条件，不能对任意 γ 无条件套用。

状态为 selected S 和 `E=ext(S)`，维护 S 内度、跨 S/E 的度、E 内度，计算可扩张规模的上下界 U/L。Type-I 删除不可能进入解的候选；Type-II 剪掉整个分支或只剪严格扩展。满足紧度约束的 critical vertices 会强制其某些邻居进入解，随后重算度与界，迭代到固定点。原文已经延迟不必要的 E 内度计算，不能将“lazy degree”单独作为新贡献。

准团不具遗传性，不能把 k-plex 的单点可扩张性判断直接搬来。某些规则只说明不存在严格扩展，但当前 S 仍须检查、报告；强制加点之前也不能跳过这一边界。

#### 一个比负载均衡更深的并行问题：返回值依赖

串行递归的 `T_found` 告诉父调用“是否找到更大的合法准团”，决定当前 S 是否还需输出。子调用拆成独立任务后，父任务不能立即读到未来结果。

Quick+ 的任务版会先输出合法候选 S，再让子任务继续；最后全局过滤非极大候选，保证得到最终 maximal 结果。**候选生成、任务内局部极大和最终全局极大是不同阶段。** 删除预输出可能漏解；把尚未完成的子任务当作未找到解则可能多报；若保留原策略，后处理是算法成本的一部分。

这给未来研究留下更难的问题：能否以有界状态保存父子完成依赖，减少过早候选输出与后处理？仅加一个 future 标志并不解决跨任务包含关系、内存积累和完成检测，需要完整设计。

#### 系统已有怎样的 batching

G-thinker 引擎共享远端邻接缓存，异步拉取数据，将小任务放本地队列、大任务放全局队列并优先执行。**溢写/读回和跨机器任务偷取已经按批进行**。timeout 拆分在递归边界将未完成工作物化为更小子图；它仍利用规模阈值区分大/小任务，不是完全删除规模参数。

这里的 batch C 是队列搬运粒度；timeout 控制拆分；两者都不等于多个搜索状态共算同一次 degree/upper-bound kernel。远端原图缓存共享也不等于任务内诱导子图和状态共享。

#### 实验证据与真正的缺口

Table 7，Patent 默认设置：不拆分 911.06 s，按规模拆分 98.68 s，按时间拆分 36.66 s，说明长尾确实重要。但 USA Road 对应为 16.21、26.21、17.30 s，说明轻任务上拆分可以变慢。YouTube 的每机峰值内存从不拆分的 9.44 GB 变为 timeout 版的 16.02 GB，不能把拆分自动等同于省内存。

Tables 12–14 展示过小 timeout 引入额外工作：Hyves 的 0.01 s 设置中，materialization 为 245.76 s、mining 为 701.34 s，总累计物化成本已约为累计 mining 的 35%；这是 worker 工作量口径，不是直接相除 job wall-clock。不能只引用某一数据的低开销比率来概括全部实例。

Table 5 的 Patent γ=.89 设置产生约 4,408 万个候选，后处理 282.38 s。另一个表中的 timeout mining 时间不能与此直接拼接为完整结果服务时间，因为任务拆分可能改变候选生成量。实验使用 16 台机器，每台 16 核/32 线程；应区分单机扩展与跨机器扩展，并交代预削减后的实际 mining 图规模。

**优点**是把剪枝、输出依赖、任务粒度和物化成本放到一起处理；**局限**是候选过生成、复制开销、参数敏感和多阶段输出合同。它适合作为后续扩展，而不是第一版实现同时承担的全部复杂性。

### 3.3 Parallelizing Maximal Clique Enumeration on GPUs

Mohammad Almasri、Yen-Hsiang Chang 等；PACT 2023；[arXiv:2212.01473](https://arxiv.org/abs/2212.01473)，[本地 PDF](papers/Parallelizing-Maximal-Clique-Enumeration-on-GPUs.pdf)。重点：PDF pp.4–6，§III/Algorithm 4；p.7 起的 §IV。

每个 thread block 深搜一个独立 BK 子树，块内线程协作集合交与 pivot；整个搜索在一个 kernel 内进行，避免逐层 BFS frontier 爆炸与频繁 CPU/GPU 往返。根可以按顶点或边拆分；这比“GPU 每层批量生成所有孩子”更适合不规则深树。

负载均衡分两阶段：先通过原子计数领取根任务；根耗尽后，空闲 block 将 ID 加入 worker list。donor 发现确有接收者才复制可捐出的分支，并要求候选数达到阈值、自己仍有其它工作。这是**按需求 donation**，已经针对“先物化大量队列状态却未必会被偷走”的成本做优化。

数据表示也专门利用 MCE 结构：full/partial induced graph 可选；partial 只编码 P–P，X 邻接回原 CSR 查询。X 分成来自根 P 的部分和来自根 X 的部分，前者逐层位图，后者用单数组及层边界表示收缩前缀，将相关空间从 `O(Δd)` 降至 `O(Δ+d²)`。这不是简单把 CPU 哈希集合搬到 GPU。

**优势**：独立 DFS 与块内并行兼顾；对 X 的特殊语义设计表示；donation 同时控制空闲与复制。**限制**：partial 表示省存储却增加原图访问；最佳根粒度与 full/partial 组合依数据而变；深层小集合的线程利用率仍有限；公开性能并非全结果写出吞吐。

§IV-A 明确测量 **counting maximal cliques**，排除磁盘读取但包含 degeneracy 预处理。与某 GPU 基线比较时使用了不同代硬件的公开数字，不能把这部分比率当同机算法优势。它已使用单个搜索 kernel，所以新方案若声称收益仅来自“减少 kernel launch”，需要重新检查动机。

对本课题的约束是：异步 donation、只在需要时复制、层边界压缩均已有先例。微批方案必须证明在同等内存预算和剪枝内核下，还能降低读取/复制量，不能仅对比一个全 BFS、必然爆内存的弱基线。

### 3.4 Accelerating Maximal Biclique Enumeration on GPUs（cuMBE）

Chou-Ying Hsieh、Chia-Ming Chang、Po-Hsiu Cheng、Sy-Yen Kuo；[arXiv:2401.05039v2](https://arxiv.org/abs/2401.05039v2)，2025-05-22，[本地 PDF](papers/Accelerating-Maximal-Biclique-Enumeration-on-GPUs-cuMBE.pdf)。重点：PDF pp.5–7，§III；pp.8–9，§IV-D。另审查 [作者代码](https://github.com/NTUDDSNLab/cuMBE)，固定提交 `2fff8005b2f74e5683d915f9cd817409f6499bcf`。

cuMBE 用 compact arrays 与每层边界保存双团两侧集合及候选/排除状态，配合 vertex→position lookup，避免为每层分配递归对象。thread block 处理子树，块内协作候选筛选、闭包扩张与极大性检查；根任务结束后，通过有限层级 work stealing 缓解不均衡。其跨 block 协调使用 cooperative-grid 机制，不能任意换成普通 kernel 中的全局 barrier。

集合操作还利用 early-stop、从较小的扩张侧反向扫描来构建候选计数。层级 stealing 并非越细越好：当空闲已很少，再细分可能增加同步、复制而无足够收益。

**最有价值的实证发现**：§IV-D 中 DBLP-author、DBpedia locations 的 subtree-fetching 占总时间超过 80%，包括领取全局候选和复制为局部状态。某些浅子树在 maximal expansion 后很快结束，准备状态反而比搜索贵。这个结果直接支持“应剖析和减少状态准备/搬运”的动机，但不能推出所有图都有同样瓶颈。

**不能忽略已有 batch pivot。** cuMBE §II-C 将 ooMBE 的 batch pivot 视为正交方法且未在该版本实现。因此不能以 cuMBE 未用某批技术为由，声称 MBE 从未有 batching；新方法需要进一步比较 ooMBE 系列。

**代码核验的计时与输出边界**：

- [mbe_cuMBE.cuh](https://github.com/NTUDDSNLab/cuMBE/blob/2fff8005b2f74e5683d915f9cd817409f6499bcf/src/mbe_cuMBE.cuh#L295) 在发现极大双团时递增计数，末尾 atomicAdd 汇总；该接口未物化每个双团的左右顶点列表。
- [main.cu](https://github.com/NTUDDSNLab/cuMBE/blob/2fff8005b2f74e5683d915f9cd817409f6499bcf/src/main.cu#L143) 的 GLOBAL_EXTENSION、TRANSPOSE、排序及 prefetch 位于计时前；约第 190 行才记录 start，计的是 MBE kernel。

这支持“公开实现计数、主要报告 kernel 时间”的判断，不等于本次已经编译验证正确性或复现性能。后续对比应同时报预处理/传输/搜索/输出的端到端时间。

它的优点是对 MBE 的集合与状态表示有专门设计；限制是调度改善后仍可能被复制与极大性检查限制。拟研究的切入应是减少真实数据搬运，并保留闭包/规范所有权，而不是单独再加一种 stealing。

### 3.5 Efficiently Enumerating All Maximal Cliques with Bit-Parallelism（GreedyBB）

Pablo San Segundo、Jorge Artieda、Darren Strash；*Computers & Operations Research* **92:37–46，2018**；[DOI:10.1016/j.cor.2017.12.006](https://doi.org/10.1016/j.cor.2017.12.006)，[arXiv:1801.00202v1](https://arxiv.org/abs/1801.00202v1)，[本地 PDF](papers/Efficiently-Enumerating-All-Maximal-Cliques-with-Bit-Parallelism.pdf)。作者稿首页日期为 2017-12-30；不把 online/元数据中的 2017 当作正式卷期年。重点：PDF pp.5–8，§4.1–4.3、Algorithm 4；pp.9–10，§6。

**已有的 AND 与用户思路非常接近，但层次不同。** 该文把 P、X、pivot 分支集 L 及邻接矩阵各行编码成 bitstrings；已选路径 R 使用普通数组。§4.1 明确列出：

```text
P_child = P AND N(v)
X_child = X AND N(v)
L       = P AND complement-neighbors(pivot)
```

若补图向量不含自身，且 pivot∈P，还要把 pivot 自身补入 L，才能精确实现 `P\N(pivot)`。直接照抄补图 AND 而忘记这个细节会漏分支。

它还将 pivot 与数据表示共同设计：反复移除**当前剩余图中最大度顶点**形成 maximum-degree-first order，重编号后递归中保持该顺序；GreedyBB 从 X 选顺序最早点，X 为空才从 P 选。这样避免为所有 pivot 候选反复计算 `|P∩N(u)|`。这不是只按原图 degree 排序一次，也不是 degeneracy 的最小度剥离。

**Algorithm 4 仍是逐个子分支递归**：对一个 v 构造 P/X 交集并递归，之后 P 删除 v、X 加入 v，再处理下一分支。正文未给出用户所说的跨兄弟状态转置、联合 AND 或多路径共享搜索。因此它是强单状态 bitset 基线，不能据标题把它说成已经实现了全部用户设想；同样，不能凭这一篇未做就断言其它文献也未做。

实验在 dedicated single core 上比较，重点为中等密度及结构化难实例。报告相对 Tomita 在 74 个实例中的 60 个更快，多数为 1.2–2.2×、少数更高；这是排序、greedy pivot 和 bitset 的联合效果，既不是多核 speedup，也不是跨兄弟批处理效应。直接将 Tomita 换成 bitset 的 TomitaBB 在不少实例反而变慢，说明扫描 pivot 候选的成本可能抵消位集交收益。

**优点**：清楚说明按位并行需要与 pivot/排序共同考虑，便宜的每节点计算可以抵消更多搜索节点。**局限**：greedy pivot 没有保留 Tomita 的最坏最优工作量保证；位矩阵及补图的密集存储不适合所有巨型稀疏图；实验未验证跨兄弟共享。新算法应至少对照其类型的强 bitset 内核，并固定 pivot/ordering 做消融，否则难以判断收益是否来自联合 AND。

更早的 *pbitMCE: A bit-based approach for maximal clique enumeration on multicore processors*，ICPADS 2014，[DOI](https://doi.org/10.1109/PADSW.2014.7097844)，也高度相关。此次已核出版元数据，但公开全文入口未成功取得；不能替它推断“已经做/没有做跨兄弟联合计算”。这是当前位并行选题最直接的补读缺口之一。

## 4. 应一起读的相邻工作：哪些“新想法”其实已有基础

### 4.1 Shared Memory Parallel Subgraph Enumeration：窃取时才复制，短任务合批

Raphael Kimmig、Henning Meyerhenke、Darren Strash；IPDPSW 2017，[DOI](https://doi.org/10.1109/IPDPSW.2017.133)，[作者版](https://arxiv.org/abs/1705.09358)，[本地 PDF](papers/Shared-Memory-Parallel-Subgraph-Enumeration.pdf)。所读稿内文日期为 2018-10-08；重点 §3.1–3.5，PDF pp.5–8。

它枚举固定带标签模式的 injective embeddings，不是 maximal cohesive subgraphs。并行 RI/RI-DS 让每个 worker 保持自己的 partial mapping M；普通本地 DFS 任务只存下一匹配点等紧凑信息，不在每次 spawn 时复制全部 M。空闲 worker 从另一端偷取靠近根的任务时，才复制相应上下文。请求/传输机制减少私有任务的同步；**task coalescing 把多个短任务组成任务组**，摊薄窃取与复制开销。

这正是“批处理＋并行枚举”的直接先例，尽管输出对象不同。其优势是普通 DFS 保持轻量、跨 worker 转移才支付成本；限制是依赖特定匹配顺序和上下文恢复，不能不加证明迁移到动态 pivot、闭包与 X 证书。对新选题而言，“仅在 steal 时复制”“把短任务打包”应列为基线，而不是主要新颖性主张。

### 4.2 Fast Parallel Algorithms for Enumeration of Simple, Temporal, and Hop-Constrained Cycles：并行后总工作可能变大

Jovan Blanuša、Kubilay Atasu、Paolo Ienne；TOPC 2023，[DOI](https://doi.org/10.1145/3611642)，[作者版](https://arxiv.org/abs/2301.01068)，[本地 PDF](papers/Fast-Parallel-Algorithms-for-Cycle-Enumeration.pdf)。前身 *Scalable Fine-Grained Parallel Cycle Enumeration Algorithms* 为 **SPAA 2022**，[DOI](https://doi.org/10.1145/3490148.3538585)。重点读扩展稿 PDF pp.10–18 的 copy-on-steal、recursive unblocking、工作量与深度分析。

Johnson 的 blocked set/Blist 依赖已经走过的 DFS 历史。不同分支共用可变 blocked 状态会漏解，每个分支完全独立又可能丢掉兄弟已经积累的有效剪枝。该文在发生 stealing 时复制状态，并根据共同前缀执行 recursive unblocking，使迁移后状态重新适用于被偷子树。

**关键发现**：算法可以正确、实测可扩展，却不是 work-efficient。细粒度 Johnson 因各线程不能完全共享剪枝知识，会重复一些顺序算法不必做的工作。另一条 Read–Tarjan 路线利用本来更独立的 path extension，证明任务数与输出 cycles 相关，给出 `O(n+m+mc)` 工作、`O(nm)` span；强可扩展性还要求输出相对 n 足够丰富。

这篇给本课题的价值在于证明标准：不能只证明“任务分开后不漏解”，还要检查有用剪枝证书是否被复制、失效或丢失。如果批处理为方便 SIMD 而推迟强剪枝，必须量化多出来的搜索节点。cycle 状态的 unblock 规则不是 clique/k-plex 可直接照搬的通用规则，但这个工作量风险完全相关。

### 4.3 G-thinker：按相似请求分组与共享邻接缓存已存在

Da Yan 等；所读 [2017 v1](https://arxiv.org/abs/1709.03110v1)，[本地 PDF](papers/G-thinker-Early-Author-Version.pdf)。相关 ICDE 2020 正式文题为 *G-thinker: A Distributed Framework for Mining Subgraphs in a Big Graph*；本文只将早稿已核对的机制归于早稿。重点 §4–7、PDF pp.5–11。

任务携带子图与 context，异步请求邻接，数据齐备后本地 DFS。共享 remote vertex cache 避免反复传输同一邻接；用待请求顶点集合的 MinHash 特征对磁盘队列排序，让同批任务更可能复用邻接。MinHash 影响执行次序，不作为未经验证的精确剪枝依据。

因此“把相似任务放一起共享图数据”已有明确先例。新方案若转向 CPU cache/NUMA，应说明多出来的是哪类**状态统计复用**、如何保持极大性、如何受内存预算约束。早稿 §7 的 task stealing 仍在开发，不能把后来 Quick+ 引擎的全部能力回填为该版本已有。

另一个重要比较陷阱是：早稿实验中的 maximum clique 与其它系统的 maximal clique enumeration 不是同一个输出问题，不能拿它们的时间相除作为枚举加速比。

### 4.4 Pangolin 与 G2Miner：批执行和内存预算已有系统设计

**Pangolin**，PVLDB 13(8)，2020，[DOI](https://doi.org/10.14778/3389133.3389137)，[作者版](https://arxiv.org/abs/1911.06969)，[本地 PDF](papers/Pangolin.pdf)。§3–5，尤其 PDF p.8：按 extend→reduce→filter 执行分层搜索；用 parent index＋vertex ID 的前缀表示保存 embeddings；inspection–execution 先计扩展数、做 prefix sum，再分配并生成。edge blocking 将初始边分批，每批走完各层后再换批。

它的优势是减少候选物化和分配、支持 CPU/GPU；限制是 BFS frontier 仍可能很大，需要跨全层聚合的任务不能无条件启用 blocking。前缀存储与批量 BFS 本身不能作为本课题的新技术，尤其不能把固定模式实例等同于变长 maximal 结果。

**G2Miner**，*Efficient and Scalable Graph Pattern Mining on GPUs*，所读 [arXiv:2112.09761v3](https://arxiv.org/abs/2112.09761v3)，2022-07-27，[本地 PDF](papers/Efficient-and-Scalable-Graph-Pattern-Mining-on-GPUs-G2Miner.pdf)。§5–7，PDF pp.7–11：warp 级 DFS、集合交协作、局部重编号/位图；多 GPU 用 chunked round-robin；根据剩余显存和每 warp 缓冲需求限制活跃任务数。

这意味着“限制 live states 以免显存爆炸”“局部 bitset”“分块轮转”都已有系统先例。它多为小固定 pattern，某些 count 可用组合公式，maximal 变长结果的 X/闭包证书并未因此自动解决。新研究应继承其内存意识，但证明自己的语义与收益。

## 5. 横向比较与已经被覆盖的技术

| 工作 | 搜索分工/正确性核心 | 已有批量或共享机制 | 尚需关注的成本 |
|---|---|---|---|
| ParMCE / ParIMCE | ext 前缀、最小根/最早新增边所有权 | 根间＋根内并行；更新 H 批次 | P/X 构造、局部图准备、pivot、subsumed 候选 |
| EDBT 2025 large k-plex | seed＋非邻居 seed 集，P/C/X 与缺边预算 | 分阶段 seed 图共享、本地队列、timeout 拆分 | T 与状态物化、阶段尾部、强剪枝的串行依赖 |
| Quick+ | 规范搜索＋合法候选生成＋最终极大性过滤 | batch spill/reload/steal、remote cache、timeout | 子图复制、候选过生成、全局后处理 |
| GPU MCE | BK 的独立子树与 X 证书 | persistent 搜索、需求 donation、X 压缩 | block 资源、partial graph 访问、复制与输出 |
| cuMBE | 双团闭包与规范扩展 | compact arrays、块内协作、分层 stealing | subtree-fetching、极大性检查、同步 |
| GreedyBB | BK 的 P/X 与静态顺序 greedy pivot | 单状态 bitset AND，递归仍逐兄弟执行 | pivot/bit 扫描、密集位矩阵；不是跨兄弟批次基线 |
| Shared Memory Subgraph Enumeration | 固定匹配顺序与可恢复 mapping | copy-on-steal、task coalescing | 迁移上下文、任务过轻时调度成本 |
| 并行 cycle 工作 | 历史依赖 blocked 证书的正确迁移 | copy-on-steal、unblocking | 并行后的重复工作与 span 取舍 |
| G-thinker / Pangolin / G2Miner | 由任务/模式语义保证结果划分 | 相似请求分组、前缀表示、blocking、预算并行度 | 通用执行开销；maximal 输出语义需另接入 |

据此，以下说法不适合作为论文主张：首次并行枚举、首次两层并行、首次共享局部图、首次 timeout 拆分、首次合批短任务、首次只在 steal 时复制、首次用数组层边界、首次按显存控制并行度。即使把这些工程组合做得很好，也必须明确新增机制和适用边界。

更有意义的问题是：**在强剪枝已存在、任务已能动态平衡之后，仍有多少工作浪费在重复统计和状态准备上？能否以可证明的状态等价和受控开销消除其中一部分？**

## 6. 建议主线：有内存预算的搜索状态批处理

### 6.1 用户的具体设想：相近兄弟邻域的位向量联合 DFS

用户进一步明确：在 DFS 一个节点下，多个子节点的邻居相近，将邻居编码成 0/1 向量，希望通过按位 AND 一起推进多个子树。**这才是本课题目前的中心；此前较宽泛的任务批调度和 k-plex 统计复用，作为相邻技术保留。**

这个想法在 clique 上有直接的数学基础。若当前已选集合 R 已经是 clique，候选集合是它的可用共同邻居，则选择 q 后：

```text
P_child = P_parent AND N(q)     # 还须应用规范分支的 prefix mask
X_child = X_adjusted AND N(q)   # X_adjusted 包含更早兄弟转入的点
```

连续选择 `q₁,q₂,…` 就是持续求共同邻域交。位集编码天然能用 AND，关键研究问题在于**多条分支怎样共享执行、同时仍保留每条分支的独立状态**。

#### 6.1.1 一个可以联合计算的具体例子

假定规范分支条件已应用，位的位置从左到右为候选顶点 c、d、e：

```text
                 c d e
分支 A 的 P_A =  1 1 0       {c,d}
分支 B 的 P_B =  1 0 1       {c,e}
邻接向量 N(c) = 0 1 1       {d,e}

都选择 c 后：
P_A' = 110 AND 011 = 010     {d}
P_B' = 101 AND 011 = 001     {e}
```

可以复用 N(c) 的读取，把两个 AND 批量执行；如果之后沿相同扩展点走，可以继续复用。两行的已选路径 R_A/R_B 和排除集 X_A/X_B 始终独立。若下一步分别选择 d 和 e，邻接输入也随之不同，批执行仍可做，但不再自动共享同一邻接向量。

相近邻域的作用不是“才能做 bitwise AND”——不相近也能做——而是让多条分支更可能共享邻接块、公共候选及后续扩展路径，从而提供超过普通位集的复用收益。

#### 6.1.2 叶子全零的准确含义

用户所定义的 bit 是“有没有这个邻居”，所以 P 全零表示**没有可继续加入的候选**，不是“路径中没有 clique”。当前 R 按正确交集规则长出来，本来已经是 clique。

| 状态 | 含义 | MCE 的处理 |
|---|---|---|
| P 非空 | 可能还有当前分支可探索的扩展 | 继续 pivot/分支，或被有效规则剪掉 |
| P=0、X=0 | 没有任何可扩点 | **输出当前 R 为极大 clique** |
| P=0、X≠0 | 有已归给其它分支的点可以扩展 R | 不输出 |

另一种可能的编码是“每个 bit 代表一条固定路径是否仍可行”。此时可将各条路径上的必要邻接条件 AND，最终每 lane 的 0/1 表示可行/不可行。但这是**路径有效性 mask**，不同于邻居 membership mask；仅验证给定路径是 clique，还没有完成全部结果枚举和极大性检查。两种 mask 可同时存在，不能混作一个含义。

#### 6.1.3 布局一：每行一条分支，批量执行普通位集交

存 `P[i][word]`、`X[i][word]`，每行对应一条逻辑搜索状态，一个 word 的各 bit 对应不同候选顶点。64 位 AND 一次处理该分支的 64 个候选位置。多个分支可由 SIMD lanes 或 GPU threads/warps 同时处理；若共同选择 q，则向各 lane 广播 `N(q)[word]`。

这是最容易实现的版本，避免复杂的转置与 lane 映射，也适合不同状态长度。局限是普通 bitset MCE 已经有大量先例；若只把 set intersection 换成 AND，创新性很弱。需要展示跨兄弟的输入/结果复用，或不同于逐行独立处理的明显优势。

#### 6.1.4 布局二：按顶点转置，一个 word 的不同 bit 表示不同分支

设批内 B 条分支，B≤机器字宽 w。对局部顶点 x，存一个分支掩码：

```text
M_P[x] 的第 i bit = 1  ⇔  x∈P_i
M_X[x] 的第 i bit = 1  ⇔  x∈X_i
```

这就是位切片（bit-sliced）布局。一条 AND 在固定 x 上更新多条分支。令各 lane 下一步选择 q_i，构造：

```text
A[x] 的第 i bit = 1  ⇔  x 与 q_i 相邻
T[x] 的第 i bit = 1  ⇔  x 是该 lane 必须移入 X 的 earlier-ext 点

M_P'[x] = M_P[x] AND NOT T[x] AND A[x]
M_X'[x] = (M_X[x] OR T[x]) AND A[x]
```

这里 M_P/M_X 表示各个待生成孩子的父状态；同一个父状态产生多个孩子时，须先为不同孩子安排独立 lane。T 来自**各父状态自己的逻辑 ext 前缀**，不是所有 lane 通用的一套全局次序。未使用的 lane、word 高位必须用 active mask 屏蔽。

若所有 lane 选择相同 q，则 A[x] 对活跃 lane 为全 1 或全 0，可共享邻接查询。若 q_i 不同，A[x] 实质上是“选择顶点×候选顶点”邻接矩阵的一列：需要 gather、转置、预编码或局部映射才能得到。朴素构造仍需 B×|U| 次邻接检查。**一次 word AND 更新 B 个状态，并不等于整个算法工作量自动缩小 B 倍。**

跨 lane 的叶子判断也可以位并行：

```text
hasP = OR_{x∈U} M_P[x]
hasX = OR_{x∈U} M_X[x]
output_mask = active AND NOT (hasP OR hasX)
```

output_mask 第 i bit 为 1，才输出 lane i 的完整路径 R_i。这里输出标志 1 是从 P/X 空性归约得到的，与“P 内某个邻居 bit 为 1”不同。还需正确保存路径/parent ID，不能只保存 output_mask 就算已经输出全部 clique。

#### 6.1.5 相近邻域可以怎样真正少算：公共部分＋差量

把同父孩子所需邻接限制在共同局部 universe U。假设能表示为：

```text
N(q_i)∩U = C ∪ D_i，且 C∩D_i=∅
```

C 是这些邻接的公共部分，D_i 是各自剩余部分。与共同父 P 相交时，可先算一次 `S=P∩C`，各孩子仅补 `P∩D_i` 并应用自己的 ext 前缀；以后若多条分支共同选择 x，继续共享 `S∩N(x)`，分别维护差量。

该表示保持精确性，但**不能把 D_i 仍编码为完整长度密集 bitset，然后声称减少了所有扫描量**。若每个 D_i 依旧要扫完整 |U|/w 个字，可能只增加一份 C 的扫描。需要稀疏差量、非零块索引或有选择的物化，使扫描量与差量实际大小有关；分组与建立 C 的成本也必须摊销。

可把局部成本写为：

```text
独立位集：约 B·ceil(|U|/w) 个字操作/交集阶段
共享表示：一次公共扫描 + Σ_i 差量处理
          + 分组/编码/前缀过滤/输出物化成本
```

这是选择策略的起点，不是普遍加速定理。当邻域差异变大、分支选点分歧明显或公共部分快速消失时，应拆批、重新分组或退回逐行 DFS，而不是强迫所有 lane 永久同步。

#### 6.1.6 “一起处理子树”还需要解决的四件事

1. **一个状态会分裂为多个孩子。** 不能用一个 lane 覆写所有后继；需生成新 descriptor，记录父路径、选择点和 ext 次序。控制活跃层/窗口，避免把整个指数 frontier 一次物化。
2. **各状态的 pivot 与分支数不同。** 统一 pivot 只有在每个状态中均合法时才可用；即使合法，也可能削弱各自最优 pivot 的剪枝。可按共同下一步分组，但须计分类与等待成本。
3. **X 不能省。** 共享邻居相近不等于相同极大性证书；仅更新 P，会产生重复或非极大结果。压缩 X 可以研究，不能直接删除。
4. **完整输出仍需逐路径解码。** 多个 lane 同时完成时要逐个恢复 R；bit 并行可以加快验证，无法把指数多个不同结果压成一个“有结果”标志，同时声称完成全部枚举。

相似邻域也不意味着可以直接合并整棵子树。必须至少证明完整后继状态、合法 pivot/所有权及输出标签的等价，才可共享后继搜索；否则仅共享 primitive、只读邻接和公共统计更稳妥。

#### 6.1.7 对选题价值的具体判断

**技术上可以做，首个正确原型并不需要 GPU。** 可先在 CPU 上比较逐行位集、SIMD 多行、位切片多分支、公共部分＋差量四种方式。最有价值的潜在贡献不是 AND 指令本身，而是：**相似兄弟子树如何被精确地联合表示和执行，且编码、分歧、极大性与输出开销不会吃掉复用收益。**

先测同父候选的相似度和共同扩展长度，分别记录状态准备、编码/转置、实际 AND、pivot、分裂/重组、X 与输出成本。对照应是强 bitset BK/TTT，而非只用哈希集合的弱版本。

k-plex 暂不作为该原型第一对象：它允许一定数量非邻居，简单 `P AND N(q)` 会把仍可行的非邻居永久删除。扩展到 k-plex 需要缺边计数/预算的多位表示与比较；到 quasi-clique 还增加随规模变化的阈值。这些可以成为后续贡献，不能直接宣布 clique 的 AND 规则适用于所有 cohesive models。

#### 6.1.8 从“批量 AND”进一步到“共享后续子树”：精确 P/X 等价

以下是**本次分析的条件化推导**，尚不作为文献新颖性主张。它将用户的“一起处理子树”分为两个强度不同的层次：

- 不同 P/X 的分支可以共享邻接读取或批量 AND，通常仍访问相同数量的逻辑搜索状态。
- **P 和 X 都完全相同**的有效 BK 状态，可以共享后续扩展搜索，分别保留各自的已选路径标签。

形式化地，在固定图与固定顶点坐标中，考虑完整、有效的普通 BK 状态 `(K_i,P,X)`。P/X 互斥，均不含 K_i，且 P∪X 正好覆盖能单点扩展 K_i 的全部顶点。定义：

```text
Φ(P,X) = { F⊆P :
             F 是 clique，且
             (P∪X)\F 中不存在与 F 全部顶点相邻的顶点 }
```

空 F 按通常空集相邻约定处理，因此只有 P∪X 也为空时，空 F 才在 Φ 中。状态 i 的合法极大结果恰为：

```text
{ K_i ∪ F : F∈Φ(P,X) }
```

**证明要点**：P/X 中所有点与 K_i 完全相邻，所以 F 内部为 clique 就保证 K_i∪F 可行。若外部点能继续扩展 K_i∪F，它必先能扩展 K_i，故必在 P∪X 中；Φ 的第二个条件排除它。反向也成立。因此后缀族只依赖 P 内邻接与 P–X 邻接，不依赖 K_i 的具体顶点名字。

在相同 P/X 上使用相同 pivot 和分支规则，可只遍历一次后缀搜索；每找到 F，就对各前缀 K_i 输出 K_i∪F。若 K_i 不同且都与 P 不交，从输出中删去 P 就恢复各自 K_i，因此这些展开结果不会因本次合并而相互混淆。重复的同一 K_i 标签仍须避免引入。

F 本身通常不是全图极大团，不能先枚举全图极大团再将其当作后缀；应按上述 Φ 的相对边界搜索，并在接回 K_i 后解释全局极大性。

**能安全合并的前提不能省略**：固定图版本与坐标；完整有效的 BK 状态；比较 P/X 的精确内容；任何额外的禁边、query filter、路径相关约束、不同 owner 规则都要纳入等价键或另证。若使用了缩减后的 X 证书，需证明证书语义等价，不能仅比较两个缩减容器。为了保持同一搜索树的实验对照，pivot/tie-breaking 也应只依赖相同状态输入。

**同父 false twins 给出一个容易理解的充分条件。** 若多个候选的开放邻域相同，它们互不相邻；将这些点在该父 ext 中连续排列后，更早的同组点转入 X 时会被 `∩N(q_i)` 消去，因而组内孩子可得到相同 P/X。这里“开放邻域相同”不能偷换成邻居相似或近似哈希相同；不同组之间的 earlier-ext 前缀也必须照常处理。

这个条件揭示了比 AND 指令本身更强的方向：相近状态先共享公共计算，在某些位置成为精确等价状态时，再共享整个后缀。需要进一步查证 twin/module 压缩、memoization 和 exact clique representation 文献，不能把这一简单等价观察直接宣布为首创。

#### 6.1.9 已完成的小图语义验证

新增 [可运行原型](experiments/sibling_bitwise_mce.py)、[运行说明](experiments/README.md) 与 [结果记录](experiments/sibling-bitwise-results.json)。它比较普通 bitset BK、按顶点转置的多分支 AND、以及在批内进一步合并精确 P/X 的版本；三者使用相同 pivot、打平与 ext 规则。

2026-10-17 的默认运行覆盖 n=1…5 全部 **1,099** 个带标号简单图，另有固定 seed 的 **300** 个 n=6…10 随机图。批宽 1、2、4、8、64 各测试合并/不合并两种模式，**13,990 次批配置结果比较全部通过**。独立 oracle 穷举所有顶点子集，检查 clique 与全局极大性；同时检查无重复输出、逻辑状态数量与基线一致。

| 说明性图，批宽 64 | 极大团数 | 普通 BK 物理状态 | 只批量 AND | 精确 P/X 合并后 | 输出顶点 ID 数 |
|---|---:|---:|---:|---:|---:|
| 三角形加一条叶边 | 2 | 5 | 5 | 5 | 5 |
| 完全图 K₈ | 1 | 9 | 9 | 9 | 8 |
| 完全三部图 K₃,₃,₃ | 27 | 40 | 40 | 4 | 81 |

物理状态数**包含输出终止状态**。40→4 不是实测 10 倍提速：后者仍保留 40 个逻辑状态的路径含义、展开 27 个结果、处理 81 个输出顶点 ID。仅 AND 合批没有降低该例的搜索节点数，精确等价合并才降低了重复搜索。K₈ 则表明“图密”不自动提供兄弟共享收益。

原型采用 Python 整数和标量 packing/unpacking，**没有 SIMD、多线程或 GPU 性能实现**，也没有邻居相似度聚类。它显式保存 prefix labels，标签可能随输出规模增长；即使批宽受限，也没有证明总空间有界。上述结果验证实现的精确语义，不能代替一般证明、真实图复用率、硬件成本和新颖性核对。

### 6.2 选择哪个凝聚模型先做

| 首个对象 | 优点 | 难点/创新压力 | 建议 |
|---|---|---|---|
| Maximal clique | P/X 语义清楚、正确性易核对、强经典理论 | 高度优化的位集/并行/GPU 实现很多，简单执行优化空间可能小 | **作为当前位向量联合搜索的首个主问题** |
| Large maximal k-plex | 度/预算/共同邻居计算较丰富；有直接并行基线；遗传性便于证明 | q/k 敏感，T 与强上界有状态依赖；已有 seed 共享 | 后续扩展；单纯 AND 会错误删除允许的非邻居 |
| Maximal biclique | cuMBE 给出状态准备主导的明确实例；两侧结构可利用 | 闭包与所有权复杂；batch pivot、先进 CPU/GPU 基线密集 | 若 profile 显示复制瓶颈更强，可改为主问题 |
| Maximal quasi-clique | 剪枝固定点与候选过生成可能提供较大优化空间 | 非遗传性、完成依赖、后处理使首版正确性更难 | 后续扩展或单独研究方向 |

技术难度应分开看：在现成 C++ 内核上做线程池与队列，中等；做可安全共享的状态表示与批统计，中高；同时给跨模型的工作量保证、GPU 实现和完整输出协议，高。建议第一阶段只做单机 CPU、一个模型、固定图快照，降低调试维度。

### 6.3 相邻可选方向：跨状态精确统计复用

**拟研究目标**：多个状态独立保留 selected/candidates/excluded 和所有权，但共享一次可复用的输入扫描或统计，减少每个状态的物理读取与复制。

第一种是**完全相同输入的请求复用**。例如同图快照、相同候选 P 的 pivot 分数：

```text
t_P(u) = |P ∩ N(u)|
```

不同状态的 X 可以不同，只需对被请求的 u 计算一次分数；每个状态仍在自己的 `P∪X` 中选 pivot。分组键至少包含图版本、局部顶点映射、精确 P；哈希可用于分桶，但精确算法必须验证内容或使用可靠的规范对象标识。

设 `U_s=P∪X_s`，独立方式与共享方式的成本可写为：

```text
W_sep    ≈ Σ_s Σ_{u∈U_s} cost(P∩N(u))
W_shared ≈ Σ_{u∈∪_s U_s} cost(P∩N(u))
           + Σ_s |U_s| + grouping/equality/index cost
```

这是一个可检验的局部收益条件，不是总枚举复杂度定理。完全相同 P 的状态可能很少；为找相同 P 而反复构建大哈希键也可能抵消收益。不能把“候选集合相似”统计成“精确请求命中”。

第二种是**同一 base 的精确差量统计**。固定只读图及局部映射，若 `C_i⊆C_0`、`D_i=C_0\C_i`，则：

```text
deg_Ci(v)  = deg_C0(v) − |N(v) ∩ D_i|
cn_Ci(u,v) = cn_C0(u,v) − |N(u) ∩ N(v) ∩ D_i|
```

可共享 base 统计，再按状态 delta 恢复候选度或共同邻居数，逐状态调用原剪枝规则。selected 集不同，缺边计数与 slack 仍不同；一个状态消耗过的 slack、收缩后判 false 的 T 不能直接广播给其它状态。

**这些恒等式本身不是新的算法贡献。** 强串行内核可能已经沿父子增量维护计数，copy-on-write 也是已有技术。潜在贡献必须进一步落到：如何发现值得合批的状态家族、如何共享多个增量请求的实际读取、如何避免重复建表、何时 materialize、何时回退，以及相对强增量基线仍能减少多少成本。

第三种是**相同邻接输入的协同扫描**。多请求 `I_i=C_i∩N(u)` 可在同一邻接块上执行不同 state masks，或使用顶点到 state IDs 的倒排。共享的是 N(u) 的读取/解码，结果 I_i 必须分别保留。不要为了复用而计算所有状态×所有顶点的完整笛卡尔积；只处理实际请求。

若采用倒排，建立它需扫描 `Σ|C_i|`，扫描 N(u) 需 deg(u)，生成结果还需 `Σ|I_i|`。而优良的独立交集可扫描每对较小集合。当 deg(u) 很大、各 C_i 很小时，统一扫完整邻接可能明显更慢。应保留稀疏交、位集交、差量恢复三种可选择的路径。

**可证明的第一层结果**应是逐状态统计与原算法完全相同，因此相同规则下剪枝、分支和结果集合不变；**性能结果**则需独立证明或测量，尤其分清减少算术操作与只减少内存流量。

### 6.4 方向 B：隐式兄弟前缀与有界物化——实现支撑，单独创新偏弱

ParTTT 的前缀转移可以表示为父状态引用＋ext 顺序＋分支序号，而不先物化 `P\E_<i` 与 `X∪E_<i` 两个中间容器。令 `pos_ext(w)=∞` 表示 w 不在 ext：

```text
w∈P_i ⇔ w∈P_0 且 w∈N(q_i) 且 pos_ext(w)≥i
w∈X_i ⇔ w∈N(q_i) 且 [w∈X_0 或 pos_ext(w)<i]
```

逐点与 Algorithm 3 等价，提供一个可审查的正确性起点。它省的是前缀中间容器，**不会自动省掉真正的 child intersection、pivot 和输出**。层层 lazy view 会增加祖先链访问成本；需要限制 view 深度、缓存或周期性 materialize。

必须保持父快照不可变且活到所有引用者结束。compact array 原地交换不能与异步兄弟共享写入；引用计数、position map、悬挂父状态、临时缓冲都应计入峰值内存。逻辑 ext 次序不能用任务实际完成次序代替，也不能用全局顶点 rank 代替局部 ext 前缀。

GPU MCE/cuMBE 已有层边界和紧凑数组，普通并行子图枚举已有 copy-on-steal。因此此方向更适合支撑 A，而不是单独以“只存指针减少复制”作为顶会级贡献。

### 6.5 方向 C：根据复制成本、可复用量与空闲资源联合决定拆分和合批

已有 timeout splitting 主要解决“任务多久还没结束”；新的控制目标可进一步包含：还剩多少空闲执行槽、一次 split 要复制多少字节、当前待执行状态能共享多少输入、内存余量和等待时间。

一个可实现的执行框架是：

```text
取一个已准备状态；为其邻近状态建立有上限的微批候选窗口
估计独立执行、差量恢复、协同扫描三种成本
若复用不足或分组成本过高：按原 DFS 执行
若可复用且预计总驻留字节不超预算：按算子小批执行
重子树仅在存在接收能力或满足调度目标时继续拆分
队列/预算达到阈值：回到本地 DFS 或安全延迟物化
```

这只是研究原型规格，不是完成的最优调度算法。预算应写成图/共享 base＋活跃状态＋悬挂父快照＋临时 kernel 缓冲＋输出缓冲的总字节约束。仅限制“最多 B 个任务”不足以保证空间；单个任务也可能很大，需要保守预留与分块处理。

不应为凑一个同 seed batch 无限等待。设最大等待/队列年龄，及时执行孤立重任务；选择 fallback 时保证工作不丢失。若需要严格峰值内存证明，必须覆盖临时分配而不仅是任务入队后的稳定状态。

这与现有预算执行器的差别应具体体现在**可共享统计与状态复制成本参与同一个选择规则**。只换 timeout、自适应队列长度或 NUMA 绑核，创新性仍偏弱。

### 6.6 可另做的更难方向

**Quasi-clique 的依赖与极大性后处理。** 研究有界 completion records/continuations，按分支完成传播信息，减少预输出候选；或批量处理包含关系并控制候选存储。必须同时解决非遗传性和跨任务关系，证明不能只停留在某个父子返回标志。难度较高，但比泛化调度更贴近模型特有瓶颈。

**动态图 subsumed 阶段。** 研究跨新 clique 的重复候选、共享边删除分裂和旧结果查询，或者利用结构表示减少无效中间量。真实变化集仍可能指数大，成果应相对输出规模或重复工作定义。它是另一条独立路线，不建议在首篇静态 batching 工作中同时展开。

### 6.7 具体反例：方案正确性必须能通过这些检查

**反例一：同 P 不能合并整个状态。** 图边为 `{ab,ac,bc,cd}`，全序 `a<b<d<c`。两个根状态为：

```text
s_b: K={b}, P={c}, X={a}
s_d: K={d}, P={c}, X=∅
```

第一个不能输出 {b,c}，因为 a 可扩展；第二个应该输出 {d,c}。共享 X 的并会漏后者，共享 X 的交会错报前者。即便 t_P(a) 可复用，a 也不是 s_d 的合法 pivot；统一使用组内最大 pivot=a 会让 s_d 漏解。

**反例二：局部 ext 前缀不能换成全局 rank。** 三角形 a–b–c，父 P={a,b,c}、X=∅，pivot=b，则 ext 只有 b。其孩子必须保留 a、c；若因为 a<b 而将 a 当作已经由前面兄弟负责的点，就会漏掉三点团。此处并不存在 a 对应的 ext 兄弟。

**反例三：相同 seed 图不意味着同样的可行候选。** 同一根 r 的 a、b、x 都邻接 r，但 a–x 存在、b–x 不存在。即使 k=1，分支 {r,a} 可以继续选 x，分支 {r,b} 不可以。状态相关的 false 兼容性不能跨兄弟传播。

**反例四：高复用的假设会失败。** 两个兄弟经邻接过滤后候选几乎互不相交，或各 D_i 接近 C_0，差量恢复可能比独立小集合交更贵。状态很多也不等于重复计算很多；应测重复率和真实成本，而不是只报告 batch 大小。

## 7. 怎样判断能否成为一篇有分量的论文

### 7.1 可以争取的贡献组合

一个较有说服力的主张可以是：**为精确 maximal clique 枚举设计保留分支身份的位向量联合搜索，对相近兄弟邻域复用公共 AND 计算，并在有界活跃内存下处理分歧、极大性证书和回退。** 需要以下证据相互支撑：

1. 形式化每个逻辑状态、唯一 owner 与可共享数据，证明 soundness、completeness、无重复输出。
2. 给出至少一个具体的算子成本模型/受控开销性质，包含分组、物化和临时状态，而非只给 TBB 调度的直觉。
3. 在强剪枝、增量维护、copy-on-steal 等直接基线上，证明加速来自少做读取/复制或更好利用有限资源。
4. 说明何时无效，并提供成本低、结果相同的回退路径；有真实多类图的收益分布，而非只挑几个高共享实例。

VLDB/SIGMOD 会看问题价值、方法的新机制、完整执行成本与强基线；SPAA/PPoPP/TOPC 等也可能更贴近工作效率、并行依赖和体系结构的贡献。投稿方向应由最终贡献决定，不能由“并行＋batch”这个标签判断录用可能性，也不能预先保证顶会。

### 7.2 必须做的对照与消融

先固定一个强内核、同样 pruning 与 tie-breaking，进行 2×2 对照：

| 配置 | 批统计/共享 | 多线程 | 回答的问题 |
|---|---|---|---|
| S | 无 | 1 | 强顺序内核基线 |
| B | 有 | 1 | 批处理是否真减少准备/计算成本 |
| P | 无 | p | 普通并行已能做到多少 |
| BP | 有 | p | 二者结合的增益与争用 |

再加入只改表示、只改调度、只改算子、全部结合的消融。若改变了剪枝/分支规则，另做同规则对照，并报告搜索节点变化，避免把强剪枝收益全部归给批处理。

clique 的直接基线应包括强 bitset BK/TTT、ParMCE 和能取得的现代强实现；扩展到 k-plex 时包括 EDBT 2025 方法的原并行方式及强串行版本；biclique 包括 ooMBEA 系列、先进 CPU 并行及 GPU 方法；quasi-clique 包括 Quick+ 和 FastQC。先按 [现有文献表](reference-enumeration.md) 筛选可取得代码/复现的版本，再补近期工作，不能只与 2020 年 TTT 比较。跨硬件算法数字只能作背景，主要比较须同机、同资源、同输出合同。

### 7.3 指标应覆盖工作、空间和结果服务

| 维度 | 至少记录的指标 | 解释作用 |
|---|---|---|
| 时间 | 图准备、排名/局部图、分组、复制、剪枝/搜索、调度、结果处理与总时间 | 找到加速来源，不隐藏预处理和后处理 |
| 总工作 | 搜索节点、失败分支、集合扫描元素/字节、popcount/成员查询、重复统计次数 | 区分少做工作与仅增加并行度 |
| 状态 | 分配次数、复制字节、base/delta 大小、挂起父状态、live bytes 峰值 | 验证批次预算与 view 生命周期 |
| 并行 | 1/2/4/8/16/32…线程，单 NUMA/跨 NUMA，steal 次数、队列等待、尾部耗时 | 解释带宽、局部性、长尾与过度拆分 |
| 批次 | 实际 batch 分布、精确重复率、等待时间、fallback 比例、分组成本 | 检验批处理收益条件 |
| 输出 | 结果数、总 ID/字节、首结果时间、最长/分位输出间隔、写出吞吐 | 区分 count-only 与真正结果服务 |

输出至少区分：exact search 后只计数、逐结果 ID 回调/内存物化、完整流式写出。计数可以作为搜索内核实验，但要同时提供一致的完整枚举接口；不要将能够组合计数、根本不访问每个输出的算法放到同一 listing 图表而不说明。

对 Quick+ 类方法，应报告候选数、最终极大结果数、后处理时间与内存。对 GPU，应同时报告 H2D/D2H、预处理、kernel、输出，而非只比较 kernel 时间。结果缓冲背压也应纳入预算。

### 7.4 正确性与数据选择

小图用独立穷举 oracle 比较**规范化结果集合**，不能只比总数；总数相等仍可能一边漏解、一边重复。覆盖前述反例、随机小图、complete/multipartite/star 图、任务窃取、batch 边界、内存压力回退，以及同一 P 不同 X 的状态。并发状态的物理编码可以不同，结果集合必须相同。

大图应覆盖社交、合作、Web、二部关系、近团密集区、重尾 hub，以及 q/k/γ 参数变化。保留空输出、很小工作量、单重根、输出主导、低共享和内存紧张的实例。不要只报告原始图规模而隐藏 core/二跳削减后很小的实际搜索图。

### 7.5 建议的起步顺序和停止条件

**第 1–2 周：先 profile，不先写通用系统。** 跑通一个强 bitset clique 内核及其并行版本；确认输出语义和小图正确性；量测状态复制、统计计算、调度与输出各占多少，并记录同 parent/seed/精确候选集的可复用率。时间是工作规划估计，取决于代码可用性和熟悉程度。

**第 3–4 周：只实现一个批算子。** 优先比较逐行位集、跨状态位切片和公共邻域＋差量三种 AND 执行方式，加入逐状态 P/X masks 与低成本 fallback；对比现有增量维护，记录实际字节而不仅 wall-clock。

**随后再决定是否加入联合调度。** 若算子没有实质收益，不应通过扩大 batch 或削弱剪枝让 GPU/CPU 看起来更忙。若收益存在且被复制/等待抵消，再加入有界状态表示和拆分选择；最后才考虑第二凝聚模型或 GPU。

建议预先设定可证伪门槛，例如目标成本在有代表性的输入上是否达到值得优化的比例、批处理能否在多个类别中超过已有并行而不显著放大内存。具体百分比应由基线与测量噪声决定，不冒充理论阈值。若目标成本占 5%，即使完全消除也只有约 `1/(1−0.05)=1.053×` 的时间上限；此时单靠该优化通常撑不起主要贡献。

**当前最合理的下一步是：以强 bitset BK/TTT 为基线，对同父兄弟的联合 AND 搜索建立小图正确性原型，再测公共邻域复用率和分支分歧成本。** ParMCE 提供正确性骨架，Quick+/GPU 工作提供复制与调度的反例和基线；它们应共同约束方法设计。

## 8. 来源索引与仍需补齐的文献

2026-10-17 继续核查了以下三篇的出版记录、公开入口与摘要。三篇均未取得全文，仍不计入正文精读；新增信息只用于收紧新颖性判断：

| 论文 | 元数据/摘要明确提到的机制 | 与用户方案的待核问题 |
|---|---|---|
| *Root-Down Exposure for Maximal Clique Enumeration on GPUs*，PPoPP 2026，[DOI](https://doi.org/10.1145/3774934.3786449)，RDMCE | root-down 工作暴露、bitmap-centric MCE、节点生成 | 一个位对应顶点还是分支？兄弟是否联合生成/搜索？暴露状态的生命周期和输出合同是什么？ |
| *Enumeration of Billions of Maximal Bicliques in Bipartite Graphs without Using GPUs*，SC 2024，[DOI](https://doi.org/10.1109/SC41406.2024.00106)，AdaMBE / ParAdaMBE | 动态 computational subgraph、局部邻域、bitmap 集合交、减少冗余访存 | 位图按父/子/兄弟哪一级复用？是否共享公共交集结果或整个后缀？构图成本如何摊销？ |
| *Advanced Maximal Biclique Enumeration on GPUs Using Bitmaps*，IEEE TC 2025，[DOI](https://doi.org/10.1109/TC.2025.3566898)，GMBE+ | node reuse、bitmap intersection、warp 内负载调度及 set union | node reuse 指内存复用还是计算复用？是否跨状态打包？各分支闭包与排除证书如何保留？ |

“node reuse”不能仅凭名称解读为共享后缀搜索；“bitmap intersection”也不能仅凭名称解读为只做单状态操作。本轮 OpenAlex/Semantic Scholar 未给出可取得的作者 PDF，arXiv 检索未找到对应稿，出版社/会议入口返回访问拒绝。**这是本次获取范围的限制，不是不存在作者版的证明。** 未引用这些论文摘要中的加速倍数来验证本课题性能。

### 8.1 本文主要正文证据

| 文献 | 本文使用的具体内容 | 本地材料 |
|---|---|---|
| Shared-Memory Parallel MCE，TOPC 2020 | Algorithms 1–7，Lemmas 1–4，§4–6，Appendix A | [28 页 PDF](papers/Shared-memory-Parallel-Maximal-Clique-Enumeration-from-Static-and-Dynamic-Graphs.pdf) |
| Efficient Enumeration of Large Maximal k-Plexes，EDBT 2025 | Algorithms 2–4，pair pruning，§6，Table 4/Appendix B | [18 页 PDF](papers/Efficient-Enumeration-of-Large-Maximal-k-Plexes.pdf) |
| Quick+，所读 2021 v8 | §5–7，Algorithms 2–10，Tables 5/7/10/12–14 | [23 页 PDF](papers/Scalable-Mining-of-Maximal-Quasi-Cliques-QuickPlus.pdf) |
| GPU MCE，PACT 2023 | §III 的分工/donation/编码，§IV-A 计数口径 | [14 页 PDF](papers/Parallelizing-Maximal-Clique-Enumeration-on-GPUs.pdf) |
| cuMBE，所读 2025 v2 | §III，§IV-D，指定提交源码 | [12 页 PDF](papers/Accelerating-Maximal-Biclique-Enumeration-on-GPUs-cuMBE.pdf) |
| GreedyBB，COR 2018 | §4.1–4.3，Algorithm 4，§6；单状态位并行与单核实验 | [15 页 PDF](papers/Efficiently-Enumerating-All-Maximal-Cliques-with-Bit-Parallelism.pdf) |
| Shared Memory Parallel Subgraph Enumeration | §3 的任务表示、copy-on-steal、coalescing | [18 页 PDF](papers/Shared-Memory-Parallel-Subgraph-Enumeration.pdf) |
| Fast Parallel Cycle Enumeration，TOPC 2023 | copy-on-steal/unblocking，Johnson 与 Read–Tarjan 的工作量差别 | [34 页 PDF](papers/Fast-Parallel-Algorithms-for-Cycle-Enumeration.pdf) |
| G-thinker，2017 早稿 | pull/cache/MinHash 队列，版本能力边界 | [13 页 PDF](papers/G-thinker-Early-Author-Version.pdf) |
| Pangolin，PVLDB 2020 | 前缀 embeddings、inspection–execution、edge blocking | [16 页 PDF](papers/Pangolin.pdf) |
| G2Miner，2022 v3 | warp DFS、局部映射、分块与显存预算 | [21 页 PDF](papers/Efficient-and-Scalable-Graph-Pattern-Mining-on-GPUs-G2Miner.pdf) |

ooMBEA 的 batch-pivots 另依据已收集的 *Efficient Maximal Biclique Enumeration for Large Sparse Bipartite Graphs*，PVLDB 2022，§5；见 [reference-enumeration.md 的 biclique 分类](reference-enumeration.md#b01) 及该文原文链接。它与本文拟研究的“多个逻辑状态的分数请求融合”不是同一个层次，不能笼统宣布首次 batching。

### 8.2 新颖性判断的限制

本文是在已收集文献中针对并行/批处理作重点精读，不是截至今日所有论文均已取到全文的证明。尤其以下直接相关工作，若尚未取得全文，就不能因为缺失而假定其没有解决拟议问题：

- *Parallelizing maximal clique and k-plex enumeration over graph data*，JPDC 106，2017，79–91，[DOI:10.1016/j.jpdc.2017.03.003](https://doi.org/10.1016/j.jpdc.2017.03.003)。已有书目核对，是独立选题的新颖性必补项。
- *pbitMCE: A bit-based approach for maximal clique enumeration on multicore processors*，ICPADS 2014，478–485，[DOI:10.1109/PADSW.2014.7097844](https://doi.org/10.1109/PADSW.2014.7097844)。OpenAlex/Semantic Scholar 未给公开 PDF，IEEE 全文入口返回访问拒绝；已取得的 GreedyBB 对其二手描述不足以代替全文精读。
- *Shared-Memory Parallel Maximal Biclique Enumeration*，HiPC 2019，[DOI:10.1109/HiPC.2019.00016](https://doi.org/10.1109/HiPC.2019.00016)。不能由与 ParMCE 相似的标题推定相同证明。
- *Maximal clique enumeration with data-parallel primitives*，LDAV 2017，[DOI:10.1109/LDAV.2017.8231847](https://doi.org/10.1109/LDAV.2017.8231847)。与数据并行原语直接相关。
- *Differentiating Set Intersections in Maximal Clique Enumeration by Function and Subproblem Size*，2024，[DOI:10.1145/3650200.3656607](https://doi.org/10.1145/3650200.3656607)。集合交自适应路线须重点比较。
- *Enumeration of Billions of Maximal Bicliques in Bipartite Graphs without Using GPUs*，SC 2024，[DOI:10.1109/SC41406.2024.00106](https://doi.org/10.1109/SC41406.2024.00106)。与 CPU 高吞吐枚举直接相关。
- *Advanced Maximal Biclique Enumeration on GPUs Using Bitmaps*，2025，[DOI:10.1109/TC.2025.3566898](https://doi.org/10.1109/TC.2025.3566898)。GPU 位图方向不能只比较早期 cuMBE。
- *Root-Down Exposure for Maximal Clique Enumeration on GPUs*，2026，[DOI:10.1145/3774934.3786449](https://doi.org/10.1145/3774934.3786449)。需要核对新根/任务暴露方式，防止与近期调度工作重合。

上述缺口不妨碍开始 profiling 与正确性原型，但在声称新颖性、确定论文标题和投稿前必须补核。本文不为未读到的方法编造算法细节。

2026-10-17 对 pbitMCE 与 LDAV 2017 的公开作者/仓储入口再次补查，仍未取得新全文；LDAV 的公开仓储位置存在，但本环境访问返回拒绝。因此保留“待正文核对”状态，不将访问失败解释为没有相关算法，也不据此宣布跨兄弟位并行或精确后缀共享的首创性。
