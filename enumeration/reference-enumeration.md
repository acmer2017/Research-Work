# Clique、凝聚子图与图枚举：分类文献与算法调研

调研截止：**2026-10-16**。本报告延续 [GraphRAG 文献调研](../graph4RAG/reference-graph4RAG.md) 的粒度：列出标题、来源与阅读章节，解释实际算法、剪枝与复杂度前提，分别评价优点和不足。重点覆盖 clique/biclique、松弛凝聚子图、动态时序枚举以及通用图枚举；附带分解索引、排名和压缩表示作为研究边界对照。为说明算法来源，纳入部分 2010 年以前的奠基文献。

本报告含 **69 个正文编号条目**；另有未取得全文的明确补读项与有限数据库检索发现的候选表。正文方法记录以实际取得的正式全文/作者版为依据；早期历史条目的全文缺口会单列，不能把候选数当作精读数。这里的广泛覆盖不等于对所有数据库、语言、模型及最新未索引论文无遗漏的系统综述。

## 1. 阅读与检索方法

阅读优先级：正式全文/作者全文 > 出版与版本元数据 > 作者实现 > 引用链/检索元数据。条目注明实际阅读章节、伪代码或定理；报告“论文证明/报告”不等于本调研重新证明所有定理或复现全部性能。机制推断会与实测结论区分。arXiv 最新版、在线发表年份和会议/期刊卷期可能不同，不从模板页脚猜 venue；预印本和正式版不重复计为独立方法。

检索沿核心论文与 BCviz 的参考文献前后扩展，同时以 OpenAlex 做 10 组补充查询：`maximal clique enumeration`、`maximal biclique enumeration`、`maximal k plex enumeration`、`quasi clique enumeration`、`cohesive subgraph enumeration`、`connected induced subgraph enumeration`、`graph enumeration dynamic temporal`、`graph nucleus decomposition`、`Efficient alpha beta core Computation an Index based Approach`、`CSV visualizing mining cohesive subgraphs`；日期过滤到 2026-10-16，各组最多取前 100 条，共返回 980 条、按 OpenAlex ID 合并后 909 条。存在弱相关结果，且未翻完数据库分页；这些数字不是该领域独立论文总量。

本地全文、抽取文本与各专题 manifest 保存在 `/workspace/research-notes/enumeration/`，条目中的 `clique-sources/…` 等路径均以此为根；缓存与克隆仓库不纳入当前代码仓库，长期复核以 DOI/arXiv/正式链接为准。BCviz 使用用户上传正式 PDF，文本缓存位于上一轮 GraphRAG 证据目录。除少量反例复核外，未统一重跑所有论文实现，不把作者最高加速倍数当作公平跨论文结论。

## 2. 问题定义与复杂度口径

| 任务 | 输出对象 | 不能混同的概念 |
|---|---|---|
| maximal clique | 无法加入任何其它顶点的完全子图 | maximum clique 是大小/权重最优；固定 k-clique 未要求极大 |
| maximal biclique | 二部图中两侧完全相连且不能扩展的 `(L,R)` | 不要求同侧边；在一般图做诱导 biclique 时语义不同 |
| k-plex | 常用约定 `deg_S(v)≥|S|−k`；每点最多缺 k−1 条对内邻边 | k=1 为 clique；不同论文可能采用差一的参数约定 |
| k-defective clique | 全子图缺失的边总数不超过 k | 不是每点允许缺 k 条边，不能套相同剪枝 |
| k-biplex | 每点对另一侧最多缺有限条边 | 须统一 k 定义和两侧规模，不能用 biclique 的公共邻居条件硬裁剪 |
| γ-quasi-clique | 文献可能按最低相对度，或按总边密度定义 | 两种模型不同；通常不具 clique 式遗传性 |
| core/truss/nucleus 分解 | 按支持阈值构造全局/连通的极大结构及层次 | 通常不是枚举所有 clique/k-plex；输出规模和任务不同 |
| connected induced k-subgraph | 每个大小恰好 k 且诱导连通的顶点集 | 不是固定 pattern 的 embeddings，也不要求 maximal |
| pattern matching/listing | 给定 pattern 的所有映射或按对称性去重的实例 | induced/non-induced、mapping/instance 必须明确 |
| frequent/closed graph mining | 按同构归并的模式与支持度 | 不是大图中全部实例；closed、maximal 和 maximum 不同 |
| temporal enumeration | 顶点集与满足时序约束的极大时间区间 | 和动态图每个快照的结果差集不同 |
| counting / compressed family | 数量，或可解释的压缩表示 | 不能直接拿性能当作逐个顶点 ID 写出的速度 |

**复杂度必须逐项看前提。** 设输入规模 n+m，结果数 N，显式输出长度 `L=Σ|result|`：总输出敏感时间、output-polynomial、增量多项式、worst-case delay、摊还 delay 和平均秒/结果是不同保证。首解、空结果判定和最后结果后的终止时间也需计入。显式全输出有 Ω(L) 的写出成本；“额外线性索引/工作空间”不包括任意大的输出缓冲。

检索时还会出现 potential maximal cliques（用于图三角化/treewidth 的特定候选对象），它们不等于原图中的实际 maximal cliques；候选目录遇到此类标题时应另行筛选。

**极大性相对于哪个域**也必须定义：原图全局极大、某允许顶点诱导图内极大、时间与顶点双重极大可能给不同结果。对非遗传 quasi-clique，“不存在单点扩展”不自动推出不存在更大的可行超集。

## 3. 分类与阅读路线

| 类别 | 编号 | 核心问题 |
|---|---|---|
| **并行枚举专题（本次重点）** | P 系列，另见 D02/D10、B07、R03/R05、G 系列 | 任务分区、共享状态、负载、访存、通信与输出 |
| 静态 clique 枚举 | C 系列 | pivot、退化度、归约、混合分支、覆盖聚合 |
| 二部图枚举 | B 系列 | closure、pivot、双侧约束、稀疏边界与 biplex |
| 松弛凝聚子图 | R 系列 | 缺边预算、规模剪枝、非遗传模型的正确分支 |
| 动态、时序与 GPU | D 系列 | 变化敏感、时间极大性、持久化、并行状态 |
| 通用图枚举与系统 | G 系列 | 连通 k-集、路径环、模式对称、外存与闭模式 |
| 分解与候选索引 | I 系列 | core/nucleus/bitruss、GPU core 与 BCviz 边界 |
| 排名与紧凑表示近邻 | F 系列 | join 排名、投影去重、共享查询、精确表示与近似索引 |

**按你对并行算法的偏好，优先读 D02（ParMCE）→ B07（cuMBE）→ R03/R05（并行 k-plex/准团）→ P01/P02（分布式）→ P04/P05（工作效率与细粒度并行）。** P06/P07 是 CPU/GPU 模式系统，须分清 counting 与 full listing。

一般路线先沿 clique 的 `R/P/X + pivot → 稀疏归约`，再读 biclique 的 `closure/pivot → large-size/biplex`，然后比较动态 maximality、通用枚举 certificate 和 BCviz。若计划做重复查询索引，必须补读 F05；若做压缩表示，必须区分聚合容器、exact family、edge cover 和 counting-only 中间表示。

## 4. 机制横向比较

| 机制 | 可削减什么 | 正确性要点 | 常见代价/失效边界 |
|---|---|---|---|
| BK pivot + P/X | 无需逐候选扩展 | X 参与极大性与所有权，不能只保留 R/P | 最坏输出指数；集合交与 X 存储可很大 |
| degeneracy/低出度顺序 | 稀疏图每根候选范围 | 顺序与当前图的低出度条件 | 原始度/平均度不能代替 d；更新后旧顺序界可能失效 |
| biclique closure/pivot | 相同公共邻居与重复分支 | 完整 closure、双侧极大性与规范次序 | 不能把 two-hop projection 的 clique 直接当 biclique |
| 缺边/度/规模界 | 无法满足规模或预算的分支 | 所有完成解都满足的必要条件 | k-plex、defective、biplex 的预算分摊不同 |
| reverse search/certificate | 无结果分支与全解 visited 表 | 唯一 parent、连通解图、可回滚可行性证书 | 生成邻居与重算 parent 成本需计入 delay |
| canonical owner/对称消除 | 同一对象多次生成 | 保留一个且至少一个合法表示 | automorphism、非诱导/诱导及用户约束会改变规则 |
| change-sensitive | 重算未变化部分 | 新增、消失与失去极大性全部处理 | 单边可改变指数多结果，batch 中间变化可能膨胀 |
| temporal state/persistence | 重复时间邻域与历史访问 | 时间扩展、顶点扩展都极大，窗口定义一致 | 事件去重或端点修改可能改变目标结果集合 |
| factorization/aggregation | 共享前缀、子模式和邻接 | 精确解码/去重，或承认是覆盖容器 | counting-only 优势不等于能快速展开全部实例 |
| 并行 task splitting | 搜索树负载不均衡 | 状态分派不漏不重，处理共享修改 | 状态复制、内存、同步和输出带宽形成尾部瓶颈 |


<a id="parallel"></a>

## 5. 并行枚举专题：优先阅读

下列是最贴近“并行算法优化枚举”的阅读顺序；编号链接跳到具体方法、状态和局限。**这些都是已有近邻，不能把其中的共享根图、timeout splitting、work stealing 本身再当新贡献。**

| 论文/系统 | 年份/所读版本 | 并行层次 | 应重点看什么 |
|---|---|---|---|
| [Shared-memory Parallel MCE](#d02) | TOPC 2020；含 HiPC 2018 前身 | 多核 CPU | 解除 cand/fini 依赖；根间/根内并行；work/span |
| [Accelerating MBE on GPUs / cuMBE](#b07) | 2024 初稿；v2 2025 | GPU | compact array、闭包/极大性、两级 stealing、复制开销 |
| [Parallelizing MCE on GPUs](#d10) | PACT 2023 | GPU/多 GPU | worker-list donation、partial graph、X 压缩；实验计数口径 |
| [Efficient Enumeration of Large Maximal k-Plexes](#r03) | 2024 作者版 | 多核 CPU | 共享 seed graph、顶点对剪枝、超时拆任务 |
| [Scalable Mining of Maximal Quasi-Cliques / Quick+](#r05) | 2020 初稿；v8 2021 | 多线程/分布式 | big-first、timeout 分解、串行返回依赖如何处理 |
| [MapReduce Maximal Bicliques](#p01) | TSC 2017 | 分布式 | 两跳任务复制、最小排名所有权、通信量/负载 |
| [G-thinker](#p02) | 2017 稿；相关正式版 2020 | 分布式 | 邻接缓存/请求复用；版本中 stealing 能力不同 |
| [Fine-Grained Parallel Cycle Enumeration](#p04) | SPAA 2022；TOPC 2023 扩展 | 多核 CPU | copy-on-steal、unblocking、work-efficient 与仅可扩展的区别 |
| [Parallel Clique Counting and Peeling](#p05) | ACDA 2021 | 多核 CPU | 固定 k 的低出度 listing 内核；实际计数而非全部 maximal |
| [Pangolin / G2Miner](#p06) | 2020 / 所读 2022 稿 | CPU/GPU | 中间状态、设备内存与任务并行度；pattern/counting 语义 |


<a id="p01"></a>

### [P01] Enumerating Maximal Bicliques from a Large Graph Using MapReduce（IEEE TSC 10(5):771–784，2017；会议前身 2014）

- **来源与阅读证据**：Arko Provo Mukherjee、Srikanta Tirthapura；正式 DOI https://doi.org/10.1109/TSC.2016.2523997 。读 https://arxiv.org/abs/1404.4910 的 34 页作者稿，§2 定义/Sequential DFS、§3.1–3.5 的 Algorithms 1–12 与 Lemmas 1–5、§4；本地 `parallel-sources/mapreduce-biclique.pdf/.txt`。该 PDF 首栏写 arXiv v1/2014，但内文日期为 2018-09-19，不能由内文日期另算一篇新论文；Crossref 正式卷期是 2017，不把 online 标识中的 2016 写成卷期年。
- **输出语义**：普通图中的 non-induced maximal bicliques；同侧是否有边不影响，不能和 induced biclique 枚举混用。论文支持最小大小阈值，仍要求 maximal。
- **算法细节**：对每个顶点 v 构造 2-hop 诱导子图 C(v)，任何包含 v 的 biclique 均位于其中。一个结果只由其中**全局排名最小的顶点**拥有。基础 CDFS 先完整枚举后检查 owner，会做大量重复计算；CD0 在根候选中排除排名小于 v 的点，并在 DFS 闭包 `N=Γ(X∪{u}), Y=Γ(N)` 中一旦 Y 含更小点就剪掉整支。闭包检验还需保证 `Y\(X∪{u})⊆T`，否则闭包越过已经处理的分支造成重复。CD1 用 degree、CD2 用 2-neighborhood size 排全局次序：更复杂的根安排在更后位置，降低它获得结果所有权的比例；排序不是把运行最久 reducer 事后直接切走。CD1/CD2 需要多一轮 MapReduce 传播排名属性。
- **保证与通信**：Lemmas 1–3 证明局部/全局 maximality 与唯一输出；Lemmas 4–5 得总通信 `O(mΔ+β)`，其中 β 为输出总大小，Δ 为最大度。两跳邻域可非常大；“每个 reducer 一小图”不是规模保证。排序是负载启发式，没有保证每个 reducer 等量搜索。只以结果个数代替 β 会漏掉每个 biclique 顶点 ID 的输出成本。
- **优点**：已经把“唯一 owner—剪掉重复搜索—以结构量调 owner 负载”串成完整算法，并分析 shuffle；是 BCviz 衔接并行 MBE 必须比较的经典工作。28 节点 Hadoop 实验计入构图等所有轮次，而非只计最后 DFS。
- **局限**：2-hop 复制和 Hadoop 轮次成本显著，轻任务上额外负载均衡轮次反而变慢；同 degree/2-hop-size 的根仍可有完全不同搜索树。静态 reducer 内 DFS 无法消除单个超大根造成的尾部负载，作者也讨论 MapReduce 动态再分配不易；直接并行 consensus 需要大中间集和反复去重，实测明显更差。不能据此说“MapReduce 天生比共享内存快”。

<a id="p02"></a>

### [P02] G-thinker: Big Graph Mining Made Easier and Faster（2017 作者预印本；相关正式论文 ICDE 2020）

- **来源与版本边界**：Da Yan 等；https://arxiv.org/abs/1709.03110 。所读 13 页 v1 是 2017 年早期系统稿，正式记录题为 *G-thinker: A Distributed Framework for Mining Subgraphs in a Big Graph*，https://doi.org/10.1109/ICDE48307.2020.00122 。本条只将早稿正文核对到的机制归于该版本，未将 2020 终稿的所有能力回填。读 §2、§4–§7 的接口、缓存/LSH 队列、例程及 §8。
- **技术细节**：任务持有局部 subgraph 和可序列化 context，用 `pull` 请求远程顶点邻接表；数据按顶点分片，不需每台机器持整图。批内请求同一个远程顶点只发一次；`Tcache` 的 LRU 表让多个任务复用只读邻接。任务队列落本地磁盘，按任务待请求集合 P(t) 的多组 MinHash 签名字典序分组，让同批任务倾向共享邻接表，降低网络请求。每批 task fetching → vertex pulling → task computing；局部数据齐全后在本机 DFS/backtracking，不为每个递归节点发远程消息；未满足新 pull 的任务再入队。
- **负载与空间**：可递归分解过大的根任务，API 支持创建后继任务；但所读 v1 §7 明说 task stealing 仍在开发、未报告，不可称本版已完成强动态窃取实验。固定活动任务数和缓存容量降低驻内存任务量，仍有高阶单任务例外：v1 对单个 P(t) 超缓存的任务临时扩大缓存。按顶点数量分片且度高度偏斜时，`O(davg n/workers)` 是设计量级，不能当不依赖度偏斜/任务大小的严格峰值字节保证。
- **优点**：系统性解决计算与通信重叠、只读邻接共享和中间子图不必逐个物化；方法与未来 parallel MBE 紧密相关，尤其是 task migration 的状态大小与 cache affinity。
- **局限与重要读文发现**：§8 的主要任务是 triangle counting、**maximum clique** 和固定 pattern matching。早稿把另两系统 maximal clique enumeration 无法完成，与本系统 maximum clique 约 20 秒并列，二者输出任务不同，不能作为“枚举快几百倍”的证据。§2 的较大 ID 邻居分解可唯一拥有 clique，但若要输出**全局 maximal** clique，还必须保留较小邻居的 excluded/maximality 证书；例如三角形中后两个点的局部 clique 并非全图 maximal。未来不能直接把局部结果合法性当全局 maximality。MinHash 仅影响排序/性能，不能参与精确剪枝而无验证。

<a id="p03"></a>

### [P03] Shared Memory Parallel Subgraph Enumeration（IPDPSW 2017；所读作者版内文日期 2018-10-08）

- **来源与阅读范围**：Raphael Kimmig、Henning Meyerhenke、Darren Strash；https://doi.org/10.1109/IPDPSW.2017.133 ；https://arxiv.org/abs/1705.09358 。读 18 页全文 §2.1、§3.1–3.5、§4、§5；本地 `parallel-sources/subgraph-shared.pdf/.txt`。
- **输出对象**：带点/边标签、可有向数据图中固定 pattern 的**非诱导** injective embeddings，不是 maximal cohesive subgraphs。同一顶点集上不同合法映射可能是不同输出；需按应用明确是否再做 automorphism quotient。
- **算法细节**：并行 RI/RI-DS 的静态 pattern 匹配顺序。任务只存“下一 pattern 顶点、待匹配数据顶点”，不在每次 spawn 复制完整 partial mapping M。每个 worker 私有 deque，自己从前端弹出保持 DFS，故可原地复用 M；空闲 worker 请求从别人的后端取得靠近根的任务，此时才复制相应的 M。采用 request/transfer 数组与原子请求协调，减少每个私有任务的同步；task coalescing 合并短任务以摊薄复制/窃取开销。全局完成用白/黑 token ring 检测。RI-DS 增强包括 domain size 打破匹配顺序平局，以及 singleton domain 的 injectivity forward checking，反复传播被唯一占用的数据顶点。
- **优点**：是“复制发生在窃取时，普通 DFS 任务不复制”的明确先例，任务紧凑化不只换队列；将负载、状态开销、剪枝分开消融。16 workers 的长任务可明显提速，也降低超时比例。
- **局限**：不提供适用于任意 pattern/图的多项式 delay 或近线性加速证明；实验为生物图与几十点/上百边 pattern，不能把其结果外推至无标签超大图或 maximal biclique。弱标签、很多 embeddings、昂贵候选验证时瓶颈改变；依赖静态匹配顺序，换成动态顺序需要重新设计状态恢复。文中主要报告 matching time，最终写出所有 ID 的 I/O 不是自动包含的公平比较条件。

<a id="p04"></a>

### [P04] Scalable Fine-Grained Parallel Cycle Enumeration Algorithms；Fast Parallel Algorithms for Enumeration of Simple, Temporal, and Hop-constrained Cycles（SPAA 2022；TOPC 10(3)，2023 扩展）

- **来源与版本**：Jovan Blanuša、Kubilay Atasu、Paolo Ienne；会议 https://doi.org/10.1145/3490148.3538585 ，https://arxiv.org/abs/2202.09685 ；期刊 https://doi.org/10.1145/3611642 ，https://arxiv.org/abs/2301.01068 。读会议 12 页及期刊扩展 34 页，重点 §3.3–§7、Algorithms 1–6/Theorems 1–5 和 §8。作为同一研究线计一组，不能把扩展稿当独立发现。
- **核心问题**：只按 starting vertex/edge 并行，某一根可包含指数多 cycles，root-level 分区仍出现尾部任务。另一方面，Johnson 的 blocked set 和 Blist 依赖 DFS 历史；不同分支直接共享会漏解，每个 child 都全复制又会丢失兄弟分支积累的剪枝信息。
- **细粒度 Johnson**：每个递归调用是任务，同一线程复用 path/Blk/Blist，只有发生 stealing 才复制。被偷任务启动时，victim 的状态可能已前进到另一个分支，不能原样使用；**copy-on-steal + recursive unblocking** 弹掉共同前缀之外的 path 并按依赖递归解除 blocked，保留对共同前缀仍有效的禁止证书。每线程 mutex 保证复制时不会读到执行一半的 unblocking 状态。算法避免粗粒度瓶颈，但理论上 **不是 work-efficient**：不同线程的 blocked 状态不完全共享，工作可为 `O(n+m+min{p c m,s m})`，c 为 cycles 数、s 为 maximal simple paths 数；不能因实测强扩展就宣称和顺序 Johnson 总工作同阶。
- **细粒度 Read–Tarjan**：不同 path extension 本来可独立，阻塞证书只从 parent 向 child 转发；再用 path-extension forwarding、成功 DFS 时提前 blocking 减少重复。每个任务输出一个 cycle 或至少产生两个子任务，据此界任务数 O(c)，每任务 O(m) 工作，得到 `O(n+m+mc)` work，span `O(nm)`；文中强可扩展性需要 `c/n→∞` 的条件，不是少量结果实例也保证线性 speedup。Johnson 较小 span 与更大/不稳定工作，Read–Tarjan 较好工作效率与更长 span，是两种不同取舍。
- **优点**：直接给“如何精确迁移可变剪枝状态”的算法与反例，适合作为 BCviz 并行枚举论文的理论标尺；扩展覆盖 temporal/hop-constrained cycles，证明与实测均比只改 OpenMP 外层循环扎实。
- **局限/实验口径**：TBB 管节点内任务，MPI 按起始边轮转分配跨节点工作；每 MPI 进程保存整图副本，并非 out-of-core 分片系统。同步成本在低 cycle/vertex 比率图可让少做工作反而更慢。上千线程结果包含多处理器/硬件线程条件，不能宣传成单个普通 CPU 千核。计数/回调输出与写盘全部 ID 需分别量测。对 biclique 候选/排除状态不能直接照搬 Johnson unblock 规则，安全复用条件需重证。

<a id="p05"></a>

### [P05] Parallel Clique Counting and Peeling Algorithms（ACDA 2021；arXiv 2020 初稿，所读 v4 2021-07-16）

- **来源与阅读范围**：Jessica Shi、Laxman Dhulipala、Julian Shun；https://doi.org/10.1137/1.9781611976830.13 ；https://arxiv.org/abs/2002.10047 。读 20 页 §2、§3.1–3.5、Algorithm 1/Theorems 3.1–3.3、§4/§5 计时及附录 ranking。不要误写成 ALENEX：Crossref 容器明确为 *SIAM Conference on Applied and Computational Discrete Algorithms (ACDA21)*。
- **输出语义**：固定大小 k 的 clique counting/listing；不要求 maximal，不是“输出所有不同大小的 maximal cliques”。附带 k-clique density 近似和 peeling 是相关任务，不能都算枚举。
- **算法细节**：先构造出度 `O(α)` 的有向无环 orientation，α 为 arboricity。并行 ranking 每轮剥掉常比例低度点，可采用 Barenboim–Elkin 阈值 `(2+ε)α` 或 Goodrich–Pszona 低度分位数，实现 O(log n) 轮。递归候选 I 与 `N⁺(v)` 求交，对每个 v 并行递归，固定排序保证一个 k-clique 只有一条上升序列；只差最后一个点时，counting 直接返回 |I|，listing 则需逐项输出。理论使用并行哈希交集。实际先构造根出邻居的诱导子图、局部重编号和 mark arrays，通常只并行最初两层，后续原地串行递归节约调度与数组开销。
- **理论与实现分开看**：对固定 k，Theorem 3.2 为 `O(m α^(k−2))` work、`O(k log n+log² n)` span（高概率），理论总空间 `O(m+pα)`。构造诱导子图的实际优化用 `O(α²)` 每 processor；全局标记/实现数组也另计，不能用理论最省空间版给最快实现背书。低出度 orientation 的 O(m) work/polylog span 是实质贡献，不是仅按 degree 排序。
- **优点**：是可证明工作效率、低 span、稀疏参数和真实并行工程结合的好样板；使用图压缩扩到巨型图。相关代码 https://github.com/ParAlg/gbbs/tree/master/benchmarks/CliqueCounting 可作为 fixed-k 基线。
- **局限**：实验重点 **counting**；作者还将 KCLIST 的最后一层从逐项遍历改成直接返回数量再比较，因此其时间不能当“所有 clique IDs 已写出”的 listing 成本。含近似采样和 density 近似的额外结果不能作为精确枚举加速。maximal clique/biclique 的证书与分支结构不同，不能直接继承此 polylog span 界。所有复杂度中固定 k 的假设应保留。

<a id="p06"></a>

### [P06] Pangolin: An Efficient and Flexible Graph Pattern Mining System on CPU and GPU（PVLDB 13(8):1190–1205，2020）

- **来源与阅读证据**：Xuhao Chen、Roshan Dathathri、Gurbinder Gill、Keshav Pingali；正式 DOI https://doi.org/10.14778/3389133.3389137 的 Crossref title 简写 *Pangolin*；作者全文题名如上，https://arxiv.org/abs/1911.06969 。读 16 页 §2.2、§3/Algorithms 1–2、§4、§5.1–5.4 和 §6。原作者版首页有未填 PVLDB 模板，正式卷期从 DOI 核实。
- **输出与接口**：以 embedding 为对象，extend → reduce → filter 的分层 BFS，支持 triangle counting、固定 k-clique finding、motif counting、frequent subgraph mining。具体用户的 support 和 output 决定是 counting、listing 还是 pattern aggregation；k-clique finding 不等于 maximal clique enumeration。
- **技术细节**：`toExtend/toAdd` 让应用提前禁掉重复/不可能扩展；clique 只沿最后一个点扩展且检验新点与当前全部点相邻，degree/ID orientation 去除多序列重复；小 motif 用规则分类，昂贵同构仅用于确有必要的任务。embedding 以 **SoA 前缀层数组**保存 `(parent index, vertex ID)`，沿 parent 链恢复完整实例；edge-induced 情形再带 history。loop fusion 在物化候选前调用 toAdd；**edge blocking** 将初始边分小批，每批跑完所有 BFS 层再换批。inspection–execution 先算每个 embedding 的扩展数、做 prefix sum 精确分配下一层，再第二次生成内容，减少原子 append 和反复扩容。
- **优点**：结合共享 CPU/GPU、接口可编程性、搜索空间削减和内存访问优化；前缀表示和成批处理都是未来压缩枚举/并行索引必须面对的现有技术，不能只以“保存共同前缀”作为创新。
- **局限**：BFS frontier 仍可能指数大；edge blocking 依赖各块可独立完成，**需要全层聚合/filter 的 FSM 在本版禁用 blocking**，并非所有任务都有预算内存保证。前缀压缩的是生成的 embeddings，不是任意图上 O(n) 大小完整解索引。GPU 某些任务仍 OOM；§6 与硬件专用计数器的比较有部分依据作者报告的加速比估算，不能当全部同机实测。论文中“不可能一般多项式图同构”的措辞不应被当作已知复杂性定理。

<a id="p07"></a>

### [P07] Efficient and Scalable Graph Pattern Mining on GPUs（G2Miner；2021 初稿，所读 arXiv v3 2022-07-27）

- **来源与阅读范围**：Xuhao Chen、Arvind；https://arxiv.org/abs/2112.09761 。读 21 页 §2.1–2.4、§4/Listing 1–4、§5.1–5.4、§6、§7.1–7.2 和 §8；本条未核实最终 venue，保留预印本标记，不把标题相似的 SBAC-PAD 论文拼接为其正式出版。代码 https://github.com/chenxuhao/GraphMiner 。
- **输出语义**：固定 pattern 的 GPM；API 明确区分 `list()`、`count()`、`PATTERN_ONLY` 与 per-subgraph output callback。counting 可用组合公式，例如 diamond 从一条边的共同邻居数 n 直接加 `n(n−1)/2`；listing 必须展开各对，不允许用 count 的速度冒充 full enumeration。
- **搜索与 GPU 映射**：根据 pattern/input/hardware 生成专用 CUDA，DFS 每 task 交给一个 warp，各线程合作计算集合交/差，减少线程内部不同递归路径造成的 divergence；多 pattern 在共享子模式收益与寄存器压力之间做 kernel fusion/fission。集合交采用并行 binary search 等原语。对有 hub 的 pattern，搜索限定到 hub 邻居；对多 hub 的候选共同邻域局部重编号，用 bitmaps 减少标记存储。FSM 之类需要 domain support 的任务采用分块的 bounded BFS，不能把所有任务都当同一种 DFS。
- **多 GPU 调度与内存**：等量连续根区间容易极端偏斜，细粒度逐根 round-robin 又增队列构造成本；采用 **chunked round-robin**，块大小按 warp 数设置，CPU 持续喂任务，可与 kernel 执行重叠。§7.2 的 **adaptive buffering 已明确按可用显存限制并行度**：图 G 和根 edgelist Ω 占用后剩余 Y，每 warp 最多 X 个 Δ 长度缓冲，令活动 warp 数不超过 `Y/(XΔ)`，同时受根任务数约束。真实字节需乘元素大小，文中公式采用元素数单位。对 hub-pattern 用拥有根的 neighborhood 数据来分配 GPU，必须保留其全部候选邻居/必要 halo；不能仅把原图做互不相交的诱导分区然后宣称无跨边遗漏。
- **优点**：已有“局部 universe+重编号、显存预算控制活动任务数、分块轮转调度、多 GPU”组合，为拟做并行 MBE 提供强相邻系统基线；可复用底层集合原语而把创新放在 maximality/closure 状态。
- **局限**：多数实验偏小 pattern 的计数/挖掘，不能说明变长 maximal biclique 的排除证书或长尾树已解决；chunked round-robin 仍是启发式，没有保证任一重根可进一步平衡的 work/span theorem。对非 hub、多跳 pattern 的分布式图访问仍有通信问题，不能泛称每 GPU 都无需图复制/通信。预算限制 warp 数会牺牲并行度，Δ 的 worst-case 缓冲在重尾图可能浪费很大；未来若只重复同一预算公式，无独立算法新意。

<a id="p08"></a>

### [P08] Theoretically Efficient Parallel Graph Algorithms Can Be Fast and Scalable（2018 初稿；所读 v4，2019；相邻并行基础）

- **来源与正文**：[全文](https://arxiv.org/abs/1805.05208)；`direction-sources/parallel-gbbs.pdf`；重点读 §4.2 的输入输出、Algorithm 10、MSF 实现及实验。本文是并行图算法框架，不是 maximal 子图枚举论文。
- **技术总结**：Borůvka 每轮用 priority-write 为组件选择最低权 incident edge，标根后 pointer-jumping，重编号并滤去自环；CSR/CSC 上先筛取低权边进行常数轮 filtering，避免巨大完整 edge-list 复制。所读实现给 PW-TRAM 模型下 O(m log n) 工作与 O(log²n) 深度，最大生成森林可改变权比较方向获得。
- **优点**：提供可复现并行 MSF 基础；适合核查“用阈值连通层次替代顺序排序”的实际成本，而非从零发明通用 MSF。
- **不足**：该界只含已给权图的森林计算，不包含 BCviz 边凝聚度上界求值、层次树构造或枚举输出；低权边筛选的常数和带宽也影响性能。现成 MSF 本身不是新的枚举贡献，不能直接将其 work/span 宣称为新流水线整体复杂度。

## 6. 静态 clique 枚举

<a id="c01"></a>

### [C01] Listing All Maximal Cliques in Sparse Graphs in Near-optimal Time（2010，作者版）

- **来源与正文**：[全文](https://arxiv.org/abs/1006.5440)；`clique-sources/Eppstein2010.pdf`；核对 §2–3、BronKerboschDegeneracy、Theorem 1、Lemma 3–6 和复杂度分析。
- **技术总结**：外层按 degeneracy 顺序，每个顶点作为该团最早顶点；P 放后邻居、X 放前邻居，内部采用最大化 |P∩N(u)| 的 BK pivot，仅对 P\N(u) 分支。额外维护只含与 P 有关边的 H_(P,X)，递归时增量更新以降低 pivot/交集成本。每个根的 P 大小至多 d，X 仍可能很大；通过对各根累加分析得到 O(dn·3^(d/3)) 形式的稀疏参数界，需留意论文中输出处理与模型约定。
- **优点**：将一般图 n 的指数依赖变成退化度 d；canonical root 保证无重复，适合根任务并行化。
- **不足**：d 小不等于每根工作相同，不能按根数量均分就期待线性加速；X 存储及递归交集仍有成本。静态低出度顺序的界不能无条件用于更新后的旧顺序；输入总体稀疏也不必意味着 d 很小。

<a id="c02"></a>

### [C02] Listing All Maximal Cliques in Large Sparse Real-World Graphs（2011，作者版）

- **来源与正文**：[全文](https://arxiv.org/abs/1103.0318)；`clique-sources/Eppstein2011.pdf`；读 §2–3，重点 §3.1 实现与实图对照。
- **技术总结**：实现上一条的稀疏算法，将 X、P 放在共享数组连续片段，用反向位置表实现常数时间 membership，子问题把交集成员交换到相关后缀，以区间边界表示状态；动态邻接仅存 pivot/交集所需边。比较无专门结构、动态稀疏结构、bit-vector 以及 Tomita 邻接矩阵/邻接表版本；数据结构版可保持 O(n+m) 额外空间。
- **优点**：展示“同一搜索理论，不同状态表示”会改变实际可用规模；是并行迁移/复制开销研究必须比较的轻量串行底座。
- **不足**：原文 bit-vector 版本并没有更快，不能由此推广位图必优；共享可变数组的串行回滚不能直接被多个线程同时修改。论文基于当时硬件和数据，不能把旧性能排序直接搬到现代 NUMA/GPU。

<a id="c03"></a>

### [C03] Accelerating Maximal Clique Enumeration via Graph Reduction（PVLDB 2024；所读作者版）

- **来源与正文**：[全文](https://arxiv.org/abs/2311.00279)、[DOI](https://doi.org/10.14778/3675034.3675036)；`clique-sources/Reduction2024.pdf`；读 RMCE 的 global/dynamic/maximality-check reduction、BK 状态和实验；作者版有未替换页脚，不据模板认定卷期。
- **技术总结**：先识别低度顶点涉及的极大团并输出/维护，再删去已处理结构；不参与任何 triangle 的边直接对应极大 2-clique。递归构造子图后继续做动态削减。利用 X 内已访问顶点的邻域支配缩减极大性检查集合，避免反复把不提供额外排除能力的 X 元素做交集。
- **优点**：把减少搜索量与减少 maximality 维护区分开；对并行算法，先减少每个任务工作可能比盲目增线程更有效。
- **不足**：削减时已输出/已保留的解必须进入完整性证明，不能只删低度点；每层重建/归约也有成本。支配关系检查需要精确，静态串行共享状态不自动线程安全；最高加速仅代表该实验设置。

<a id="c04"></a>

### [C04] Maximal Clique Enumeration with Hybrid Branching and Early Termination（ICDE 2025）

- **来源与正文**：[全文](https://arxiv.org/abs/2412.08218)、[DOI](https://doi.org/10.1109/ICDE65448.2025.00051)；`clique-sources/Hybrid2025.pdf`；读 §III–V、Algorithm 2–8，尤其 HBBMC 与终止规则。
- **技术总结**：边向分支一次将一条边的两个端点加入当前团，采用 truss-based edge ordering 控制候选；混合框架在边根下调用 vertex-oriented pivot 搜索，兼用两者优势。候选图成为 2-plex 且 X 为空时，其补图为匹配，可在每个缺边对选一个端点直接组合；3-plex 的补图是路径/环/孤点，分解枚举对应 maximal independent sets 后组合，提前终止一般递归。
- **优点**：利用“稠密残余子问题有特殊结构”减少搜索；终止器和根分解是并行 kernel 的强比较对象。
- **不足**：2/3-plex 快速输出受 X 为空等条件约束，不能只看 P 稠密就跳过原图极大性；组合输出仍可能指数。边根可能增加任务/重复状态准备，truss 预处理需计入全成本；不是对任意图都更快。

<a id="c05"></a>

### [C05] Aggregating Maximal Cliques in Real-World Graphs（2025 预印本；2026 正式记录需按版本区分）

- **来源与正文**：[全文](https://arxiv.org/abs/2512.03960)；`clique-sources/Aggregate2026.pdf`；读 §2–4 的 ρ-dense aggregator、递归构造与覆盖保证、实图实验。
- **技术总结**：输出一批允许重叠的密集 vertex sets，使每个 maximal clique 被某个集合包含。递归保持 clique 前缀 C 和与其完全相连的候选 H；若 C∪H 密度达 ρ，直接把整个容器加入输出；否则选择低度点，在包含该点与排除该点的子问题中继续覆盖。对固定 ρ<1 给出次指数大小的容器界，并分析稀疏参数情形。
- **优点**：避免显式重复列出大量高度重叠团，提供全覆盖而非仅抽样；紧凑候选区域可用于后续探索。
- **不足**：容器内可有非边，聚合结果不是精确团家族；不能直接支持 exact clique counting、ranking 和无重复展开。它与 full MCE 的输出合同不同，速度比较必须明确。并行容器之间可能重叠，作为枚举任务时需 canonical ownership，不能每容器独立输出后声称无重复。

<a id="c06"></a>

### [C06] Near-Optimal Algorithms for Maximal Clique Enumeration in Structurally Sparse Graphs（2026，预印本）

- **来源与正文**：[全文](https://arxiv.org/abs/2608.02614)；`clique-sources/Structural2026.pdf`；核对 Algorithm 1、minor/immersion 两种分析、停止时的 X 检查与输出规模下界。
- **技术总结**：按 degeneracy 最早点分配根。minor-free 路线选候选子图最小度点做 include/exclude；候选足够小时交给标准 BK，局部足够稠密时交给输出敏感算法，并用 X 过滤不能全局极大的结果。结构定理控制中间递归的下降和终止子图的输出量；immersion-free 的度结构采用不同分析。原文给 n·4^(2t/5+o(t))、n·3^(t/3+o(t)) 型参数界。
- **优点**：说明改进枚举界不只靠更快集合交，还可利用特定图类的结构障碍；为结构参数实验提供理论近邻。
- **不足**：限排除特定 minor/immersion 的图类及 t 参数，不能把有界平均度实图视为已经满足该条件；不是一般图的普遍线性枚举。预印本定理与工程效果需进一步验证，不能推断有现成并行可用实现。

<a id="c07"></a>

### [C07] Engineering Algorithms for ℓ-Isolated Maximal Clique Enumeration（2025，所读预印本 v2）

- **来源与正文**：[全文](https://arxiv.org/abs/2511.03525)；`clique-sources/Isolated2025.pdf`；读 §2–3、Theorem 3 的隔离剪枝与四种 ω(G[P]) 上界及实验。
- **技术总结**：目标团平均外部度小于 ℓ，不是每个点都小于 ℓ。在 BK 中由当前 C、剩余 P 和外部边数推导任何完成团的隔离必要条件，再以 ω(G[P]) 的安全上界代入。依次采用 |P|、Δ+1、度序 h 型界、degeneracy+1，比较计算成本与剪枝能力；越紧的界不一定总体越快。
- **优点**：query-specific 约束可形成安全分支界，适合将任务优先级与正确性过滤分离；精确分析界计算成本。
- **不足**：输出是全图极大且满足隔离的团，不是任意 isolated subgraph；不同 ℓ 只改变过滤，不能由快慢推断 MCE 内核通用优越性。每任务都重做 core 上界可能增加并行总工作，需摊销/缓存实验。

## 7. Biclique 与二部松弛结构枚举

<a id="b01"></a>

### [B01] Efficient Maximal Biclique Enumeration for Large Sparse Bipartite Graphs（PVLDB 15(8), 2022）

- **来源与正文**：[正式全文](https://www.vldb.org/pvldb/vol15/p1559-chen.pdf)；`biclique-sources/ooMBEA.pdf`；读 iMBEA 状态、§4 的 unilateral order、Algorithm 2/3、包含剪枝与实验。
- **技术总结**：ooMBEA 在选定一侧的规范顺序上，将每个 biclique 归属于最早根；根 v 以 N(v) 为另一侧候选，用两跳同侧邻居初始化 P，并以已处理 Q 检查极大性。枚举中做公共邻居闭包和包含关系剪枝，调用 iMBEA 内核。单侧按当前 two-hop 度反复剥离得到 unilateral coreness/order，限制每根后继两跳候选；比较两侧的估计代价后选择搜索方向。
- **优点**：面向大稀疏二部图的强串行基线；规范根适合并行任务，闭包/集合交可复用。
- **不足**：构造两跳关系的时间与空间不能忽略，原图稀疏仍可能两跳稠密。选择侧和顺序改变工作量，但不保证各根均衡；多线程复制 A/P/Q 可能放大内存。iMBEA 机制在本文正文核对，不冒充另外读过 2014 原文。

<a id="b02"></a>

### [B02] BBK: a simpler, faster algorithm for enumerating maximal bicliques in large sparse bipartite graphs（2024 起，所读作者版）

- **来源与正文**：[全文](https://arxiv.org/abs/2405.04428)；`biclique-sources/BBK.pdf`；核对 §3.1–3.2、Definition 3.1/3.2、Algorithm 1/2 与 bidegeneracy 分析。
- **技术总结**：从 clique-extended graph 出发：概念上将每侧补成完全图，原图 biclique 对应扩展图 clique；实现并不显式加所有同侧边，而利用二部邻接性质缩小根候选、提前极大性检查，仅从一侧根出发，采用 bidegeneracy 顺序减少候选。递归仍保留 BK 式候选/排除及 pivot，但避免直接处理巨大的扩展图。
- **优点**：提供与 MCE 理论/实现联通的简洁框架，并证明二部特化为何必要；是并行状态压缩的合适底座。
- **不足**：不能把显式补齐扩展图当实际可扩展实现，也不能用单侧 two-hop 图中的 clique 直接替代 biclique。空侧/非空侧输出约定需与应用统一；排序及状态维护仍有代价，未自动提供并行负载和显式输出扩展性。

<a id="b03"></a>

### [B03] Maximal Biclique Enumeration with Improved Worst-Case Time Complexity Guarantee: A Partition-Oriented Strategy（2026，所读预印本）

- **来源与正文**：[全文](https://arxiv.org/abs/2602.21700)；`biclique-sources/Partition2026.pdf`；读 ParBB/IPS、Algorithm 2、IE 技术、Theorem 4.1 及实验；不从残留 Conference’17 模板猜 venue。
- **技术总结**：把候选 C 划分为 C′ 与补集，pivot 同时结合划分产生互斥分支，针对旧单顶点 pivot 在只有一个非邻居时的最坏递归瓶颈改进分支结构；加入适用停止条件、规模剪枝，并用 inclusion–exclusion 式根分解及稀疏参数控制局部搜索。论文改善的是明确递推和参数下的最坏界，而不是普遍多项式枚举。
- **优点**：直接挑战已有强串行内核；“分区”可借鉴为并行任务所有权设计，但先有更少的搜索树也可能胜过旧内核多线程。
- **不足**：**ParBB 的 Par 指 partition，不等于论文已经实现 parallel 算法**；不可据名字当作并行基线。稀疏参数、界常数和预处理须统一，IE 也要确认目标是逐解枚举而非仅计数；新稿的理论/代码应在实际数据上独立复核。

<a id="b04"></a>

### [B04] Efficient Algorithms for Maximal k-Biplex Enumeration（SIGMOD 2022）

- **来源与正文**：[作者正文](https://arxiv.org/abs/2112.14414)；[DOI](https://doi.org/10.1145/3514221.3517847)；本地 `biclique-sources/Biplex2022.pdf` 的标题/算法已核对；读 §3 的 bTraversal/iTraversal、left-anchored/right-shrinking/exclusion 和 §4 EnumAlmostSat。所读 arXiv v1，2021-12-29。
- **技术总结**：利用 k-biplex 遗传性，在 maximal solutions 构成的解图上遍历；给现有解加入外部顶点形成 almost-satisfying 子图，在其中枚举包含新点的局部极大解，再按固定顺序扩张成全局极大解。iTraversal 放宽基础框架不必要的局部要求，并用左侧锚定、右侧缩减、排除策略减少冗余邻接解与重复遍历。
- **优点**：不是把普通 BK 硬套缺边模型，局部枚举与全局扩张职责明确；可作为探索解空间并行化的理论底座。
- **不足**：解图遍历的去重/访问状态、局部解数量和扩张成本不可忽略；局部极大不等于全局极大。并行多个出发解会重复到达同一全局解，需要精确所有权或 visited 协议；不能只开启多个 traversal 就保证工作高效。

<a id="b05"></a>

### [B05] Maximum k-Biplex Search on Bipartite Graphs: A Symmetric-BK Branching Approach（2022 起，所读作者版；最大问题对照）

- **来源与正文**：[全文](https://arxiv.org/abs/2208.13207)；`biclique-sources/BiplexMax.pdf`；读 §3 Sym-BK、FastBB、Algorithm 2 与四类剪枝。
- **技术总结**：Sym-BK 的第 i 个分支包含前 i−1 个候选、排除第 i 个，和普通 BK 的“包含第 i 个、排除此前候选”对称。依据已选点对另一侧的缺邻数推导两侧规模上界，结合当前最好解的边数做 branch-and-bound，并用排除集合判定无法产生极大解的分支。
- **优点**：说明缺边预算能用于更强分支和二维规模界，为大 biplex 候选索引提供构件。
- **不足**：求 maximum，不是全部 maximal enumeration；基于 incumbent 的“无法超过当前最优”剪枝会删除许多合法极大解，枚举版不能照搬。并行优化中共享 incumbent 的效果也不能直接类比全解输出任务。

<a id="b06"></a>

### [B06] Fairness-aware Maximal Biclique Enumeration on Bipartite Graphs（2023，所读预印本）

- **来源与正文**：[全文](https://arxiv.org/abs/2303.03705)；`biclique-sources/FairMBE.pdf`；读单侧/双侧公平定义、§III–IV、Algorithm 1 FCore、FairBCEM 家族。
- **技术总结**：用属性取值的最低数量与数量差约束定义 fair bicliques；为顶点维护每个属性值的邻居数，FCore 迭代剥离不满足属性度或规模下界的点，继而用 colorful 属性界增强削减；搜索过程中按属性可达规模/平衡条件剪枝，并区分不同公平目标的最大性语义。
- **优点**：将属性约束纳入搜索，而非先生成全部解再过滤；对种子/属性过滤的并行任务有参考意义。
- **不足**：不能把其“公平极大”与无属性全图 maximal biclique 直接当同一结果族；colorful/属性计数有开销，group 分布不均也会导致并行长尾。论文省略部分证明的情况需要在新算法迁移时重新补齐，不能凭约束名称推断遗传性。

<a id="b07"></a>

### [B07] Accelerating Maximal Biclique Enumeration on GPUs（cuMBE；2024 初稿，所读 v2 为 2025-05-22）

- **来源与正文**：[全文](https://arxiv.org/abs/2401.05039)；`biclique-sources/GPU.pdf`；读 compact array、Algorithm 1/2、块内优化、两级 work stealing 和 §IV 的性能分解。
- **技术总结**：GPU thread blocks 负责粗粒度子树，块内线程协作候选筛选、最大扩张与极大性检查。compact array 用每层边界指针表示逐渐缩小的局部集合，配辅助缓冲/atomic 计数无冲突分区，避免完整递归对象分配；在有限深度做两级 stealing 缓解任务偏斜。
- **优点**：直接针对 MBE 的 GPU 状态与闭包操作，兼顾内存与计算；比单纯外层线程分根更完整，是并行 biclique 首要阅读对象。
- **不足**：原文性能分解显示某些数据中 stealing 后空闲已小，继续细分调度可能不抵同步；状态 Pg 获取/复制与 maximality 检查仍可能主导。持久数组小不等于所有活动 block 的总状态小；需另核对 CPU/GPU 传输、实际输出 ID 与计数口径。新方案应展示减少总工作/访存，而不是重复已有 stealing。

## 8. 松弛凝聚子图枚举

<a id="r01"></a>

### [R01] Listing Maximal k-Plexes in Large Real-World Graphs（WWW 2022；ListPlex）

- **来源与正文**：[全文](https://arxiv.org/abs/2202.08737)；`relaxed-sources/ListPlex.pdf`；读 Algorithm 1、附录 BKPivot、二跳直径性质与小解处理。
- **技术总结**：先处理规模≤2k−2 的小解，再按 degeneracy 最早顶点建立一/二跳 seed graph；为最早点的不超过 k−1 个非邻居枚举 seed，内部用缺边预算约束的 BKPivot。pivot 若已选，则按其候选非邻居序列分支；否则做 include/exclude。局部输出仍检查更早一/二跳顶点能否扩展，以保证全图极大性。
- **优点**：明确区分小解和 large 解，避免将二跳局部性错用于可能不连通的所有 k-plex；根图可成为并行任务分组基础。
- **不足**：非邻居 seed 组合数随 k 增大，不能只报告每个局部图小；局部极大还需外部检查。不同 seed 的候选图可高度重叠，直接复制后并行可能放大内存和交集总工作。

<a id="r02"></a>

### [R02] Scaling Up Maximal k-plex Enumeration（2022，所读作者版）

- **来源与正文**：[全文](https://arxiv.org/abs/2203.10760)；`relaxed-sources/kplex2022.pdf`，v3；核对 Algorithm 1 的上界、Algorithm 2 的 branch、core/二跳削减。
- **技术总结**：对规模阈值 q≥2k−1，先取 (q−k)-core 并按退化顺序在二跳邻域内分根。为已选 S 的每个点维护尚可接受的非邻居预算；给候选按对 S 的缺邻数分桶，以最紧预算点约束可再加入的候选数，得到 S∪{v} 的规模上界。达不到 q 的加入分支可提前剪；S∪C 已为 k-plex 时做全局极大性检查后终止。
- **优点**：预算上界强于只看候选数，为大解任务减少无用搜索；上界计算和分支是清楚的独立组件。
- **不足**：规模范围是方法的重要前提，不能用 q≥2k−1 的二跳证明宣称无约束所有解；高 k 或低 q 时可能变弱。上界每层重算的总成本、X 的维护和全图检查仍需计入；并行版不应给每个任务重复昂贵剥离。

<a id="r03"></a>

### [R03] Efficient Enumeration of Large Maximal k-Plexes（EDBT 2025；所读 2024 作者 v3）

- **来源与正文**：[全文](https://arxiv.org/abs/2402.13008)；`relaxed-sources/kplex2024.pdf`；读 §4–6、Algorithm 2/3、顶点/顶点对剪枝与 timeout-based parallel execution。
- **技术总结**：二跳 seed graph 中按规范次序创建任务，维护 P/C/X；选择低度且对 P 缺邻较多的 pivot，通过规模上界决定是否探索加入分支，排除分支仍保留。进一步以顶点对兼容性表削减候选。并行中同 task group 共享 seed graph；每线程队列处理任务，超过时间阈值后把未完成递归拆为新任务，新任务复用图但需要物化 P/C/X 和顶点对状态等。
- **优点**：**直接对应用户偏好的并行凝聚子图枚举**，将算法剪枝、共享根图与长尾拆分结合，而不只是外层多线程。
- **不足**：共享 seed graph、超时拆分已经存在，新工作不能泛称首次；新任务状态/布尔矩阵物化仍有成本，阈值太小会放大调度和空间。性能受 q/k 与图结构影响；只列“stragglers eliminated”不等于最坏工作/深度保证。

<a id="r04"></a>

### [R04] Fast Maximal Quasi-clique Enumeration: A Pruning and Branching Co-Design Approach（2023 初稿；所读更新作者版，FastQC）

- **来源与正文**：[全文](https://arxiv.org/abs/2305.14047)；`relaxed-sources/FastQC.pdf`；核对 §3–5、Algorithm 2/3、Sym-SE/Hybrid-SE 与目标输出定义。
- **技术总结**：逐点相对度 γ-quasi-clique 的缺边上限随最终规模变化，不能使用普通 k-plex 固定遗传预算。FastQC 以分支规模界 σ(B) 和允许缺邻 τ(σ(B)) 推导必要条件，迭代削减并重检直到不再变化；Sym-SE 使后继分支已选集扩张，某条件失败可连同后续分支剪掉，再按情况混合两种分支。DCFastQC 用 core、退化根和 one/two-hop 削减缩小局部任务。
- **优点**：剪枝和分支共同设计，有超越朴素 2^n 搜索的递推分析；是并行版必须使用的强串行比较内核。
- **不足**：算法输出合同写为“包含全部 MQCs 的 QC 集合”，应检查是否还需后处理过滤非极大项，不能仅按输出行数与纯 MQC 列表比。γ 与阈值等前提必须保留；分支仍可能指数。把准团当遗传模型直接套 BK 可能漏解，简单局部不可扩展也不等于全局极大。

<a id="r05"></a>

### [R05] Scalable Mining of Maximal Quasi-Cliques: An Algorithm-System Codesign Approach（Quick+；2020 初稿，所读 v8 为 2021-05-10）

- **来源与正文**：[全文](https://arxiv.org/abs/2005.00081)；`relaxed-sources/QuickPlus.pdf`；读 iterative bounding、Algorithm 2/3、G-thinker 执行引擎改造、timeout-based divide-and-conquer。
- **技术总结**：维护当前 S 与 ext(S)，结合规模上下界、critical vertices 和覆盖顶点反复做 Type-I 候选/Type-II 分支剪枝。分布式/多线程层将 big/small tasks 分开，优先调度大任务，避免大任务藏在本地队列尾部；时间超限后拆分剩余搜索并缩小子图。串行递归返回“能否找到更大 QC”的依赖在任务拆开后不再立即可知，需按该执行语义处理当前可行 QC，不能擅自沿用串行返回判断。最终极大结果过滤/输出合同需一并核对。
- **优点**：**与并行枚举优化非常相近**，明确研究搜索剪枝、任务粒度、数据准备与长尾共同影响；而且解释了并行化为何会改变返回值依赖。
- **不足**：big-first、timeout splitting 已是已有能力；新研究需进一步减少复制/重复搜索或给出新边界。剪枝与分布式系统同时改变时，不能把全部收益归于并行；任务缩小/迁移和候选 QC 后处理应纳入端到端成本。

<a id="r06"></a>

### [R06] Efficient Defective Clique Enumeration and Search with Worst-Case Optimal Search Space（2025，所读完整作者版）

- **来源与正文**：[全文](https://arxiv.org/abs/2512.10354)、[DOI](https://doi.org/10.1145/3769787)；`relaxed-sources/Defective2025.pdf`；读 §3 Algorithm 1、clique-first/pivot/refine、UB1 和最大问题扩展。
- **技术总结**：k-defective 约束全子图总缺边数。递归维护 S/C/X，先在与 S 完全相连的候选内用 clique pivot 选分支，优先加入不产生新缺边的点；只有无法继续 clique 扩张时才消耗缺边预算。refine 检查加入两个点后是否仍满足预算，结合规模上界剪掉达不到 q 的分支。论文分别处理全部 maximal 与 maximum search，不能混用后者 incumbent 剪枝。
- **优点**：clique-first 让缺边预算分析更紧，给强搜索空间界；并行研究应先比较新的串行分支内核，避免旧内核多核胜过更旧基线的假优势。
- **不足**：worst-case optimal search space 不等于输出最优 delay/端到端时间；候选 refine、集合操作和写出仍有多项式因素。缺边全局预算不同于 k-plex 的逐点预算，并行拆分必须保存剩余预算与排除语义。

<a id="r07"></a>

### [R07] Efficient Antagonistic k-plex Enumeration in Signed Graphs（2024 作者版；2025 正式元数据）

- **来源与正文**：[全文](https://arxiv.org/abs/2406.16268)、[DOI](https://doi.org/10.1109/TBDATA.2025.3552335)；`relaxed-sources/SignedPlex.pdf`；读 BAPE、Algorithm 1、Lemma 2、signed one/two-hop 候选与剪枝。
- **技术总结**：将结果划成两个阵营，同阵营正边、跨阵营负边，允许模型约定的缺邻但禁止相反符号边。状态含左右已选、候选和排除六个集合；按正/负二跳邻域初始化根，扩张时既检查 k-plex 缺邻预算，也检查阵营一致性。交替左右扩张配合规模 t 和极大性检查。
- **优点**：说明额外标签/边符号会改变候选兼容性和分支状态，不能只把无符号算法换输入；六集合状态是并行迁移的真实成本实例。
- **不足**：signed 二跳/规模假设与无符号模型不同；结果两阵营交换对称需规范化。缺边与符号错误不是同一容错，不能把一般边噪声都当可接受。论文模板页脚不是正式年，性能也不能与无标签 k-plex 输出量直接比较。

## 9. 动态、时序与并行枚举

<a id="d01"></a>

### [D01] Incremental Maintenance of Maximal Cliques in a Dynamic Graph

- **作者/年份/版本**：Apurba Das, Michael Svendsen, Srikanta Tirthapura；The VLDB Journal 2019，DOI [10.1007/s00778-019-00540-5](https://doi.org/10.1007/s00778-019-00540-5)。2016 年预印本最初题为 *Change-Sensitive Algorithms for Maintaining Maximal Cliques in a Dynamic Graph*；[arXiv:1601.06311](https://arxiv.org/abs/1601.06311) 最新 PDF 使用期刊题名，二者不能当两项独立算法计数。
- **阅读证据**：18 页作者版 `dynamic-sources/change-sensitive.pdf`；§2 的 change-sensitive 定义，§3/Theorem 3 的变化界，§4.1–4.4/Algorithms 1–5，§5 的数据处理、签名优化及批次实验。
- **问题定义**：对一批新增边 H，同时找新增 maximal cliques Λnew 与仍存在但被更大 clique 包含的旧 maximal cliques Λdel。`subsumed` 不是旧 clique 的边被删掉，而是其 maximality 消失。
- **技术细节**：每个新增 clique 必须包含至少一条 H 中的边。对 `e=(u,v)`，只在 `{u,v}∪(N_G'(u)∩N_G'(v))` 的诱导图内枚举 maximal cliques；该局部 maximal clique 与全图中包含 e 的 maximal clique 一一对应。给 H 一个顺序，只让 clique 归属于它包含的最早新增边。理论 Algorithm 1 用输出敏感静态 MCE，并在输出处抑制重复；实际 `FastIMCENewClq` 用 `TTTExcludeEdges`，一旦当前递归 clique 已包含此前处理边就剪掉整个分支，避免先完整生成重复结果。找 subsumed 时，对每个新 clique c 从 `c−H` 构造候选：每遇一条被移除边 `(u,v)`，将含该边的候选分成去 u 与去 v 两个，再检查候选原来是否 maximal。
- **保证/复杂度**：新增部分 Theorem 4 为 `O(Δ³ρ|Λnew|)` 时间、`O(n+m)` 空间，其中 ρ=|H|、Δ 为更新后最大度。旧结果处理的 Lemma 5 为 `O(2^ρ|Λnew|)` 的签名/成员表方案；不保存所有旧 clique 也可逐候选检查原图 maximality，时间增加为 `O(2^ρ|E(G)||Λnew|)`，工作空间仍可线性。因此不能把整篇概括为对任意大批次均关于 ρ 的多项式 change-sensitive 算法。删除批次通过反向增边问题归约。混合插入/删除先删后加可正确计算最终状态，却可能产生大量不属于最终差集的中间 clique，§4.4 明说不再保证最终变化敏感。
- **优点**：局部化有完整正确性依据；批量所有权规则避免逐边维护的中间结果膨胀；同时讨论新增和 maximality 消失，而非只找新增 clique；输出与状态存储分开，可不存全部旧结果。
- **局限/复现边界**：实际优化用 canonical clique 的 64-bit MurmurHash 签名判断旧成员，论文承认碰撞可能造成假阳性；需要严格 exact 时应存可验证内容或重新验 maximality。实验主要是时间戳增边数据，先转无向简单图、重边只保留最早时间，不能解释成处理重复交互的时序枚举。理论新增算法的 change-sensitive 性质不能直接转移给使用 Tomita 最坏情形搜索的最快实现。单边就可能带来指数级结果变化；更快更新不消除输出成本。
- **与 BCviz 的关联**：避免物化所有 clique、按更新边做候选局部化都已有先例；新方向应明确维护的是物理排序/安全上界/局部证书，而不是再把完整结果表换成签名。

<a id="d02"></a>

### [D02] Shared-memory Parallel Maximal Clique Enumeration from Static and Dynamic Graphs

- **作者/年份/来源**：Apurba Das, Seyed-Vahid Sanei-Mehri, Srikanta Tirthapura；ACM Transactions on Parallel Computing 2020；[DOI:10.1145/3380936](https://doi.org/10.1145/3380936)，[arXiv:2001.11433](https://arxiv.org/abs/2001.11433)。静态算法的 HiPC 2018 会议前身 *Shared-Memory Parallel Maximal Clique Enumeration*（[1807.09417](https://arxiv.org/abs/1807.09417)，DOI 10.1109/HiPC.2018.00016）并入本条，不重复计工作数。
- **阅读证据**：28 页 `dynamic-sources/shared-memory.pdf`；§3 模型，§4/Algorithms 2–4，§5/Algorithms 5–7 及附录 A，§6 实验与计时范围。
- **技术细节**：`ParPivot` 并行计算每个 `cand∪fini` 顶点与 cand 的邻域交集大小，再选最大 pivot。TTT 各递归分支原本依赖之前分支把顶点从 cand 移到 fini；算法先固定 `ext=(v1,…,vκ)`，第 i 个分支显式用 `cand\ext[1:i−1]` 和 `fini∪ext[1:i−1]` 构造输入，再与 N(vi) 相交，因而分支可并行且保持唯一输出。实用 `ParMCE` 先按顶点 v 分解邻域子图，令 v 为该 clique 的最小排名顶点，并用 cand/fini 拦住其它根中的重复；degree、triangle count、core-number 三种排名用于负载估计。动态 `ParIMCE` 在 H 中各边上并行应用 D01 的局部共同邻域与 earlier-edge 排除；新 clique 内拆分 subsumed 候选和成员表访问再并行。
- **保证/开销**：CRCW PRAM/并发哈希表模型下，`ParTTT` 工作 `O(3^(n/3))`，深度 `O(M log n)`，M 是 maximum clique 的大小。通常采用的 work–span 调度界是 `O(W/P+D)`，不是 P 倍无条件加速。动态新增算法与其顺序基线同阶工作、深度 `O(Δ²+M log Δ)`；subsumed 候选仍可能随批次边数指数增长。物理共享图减小分布式复制，不等于总中间空间不受并行分支数影响。
- **优点**：不是简单把外层 for 改 OpenMP，明确解除 cand/fini 依赖；兼有根间与根内并行；理论工作效率和实际负载策略有区分；动态已有可直接比较的强基线。
- **局限**：只研究共享内存，不能据此推断分布式 shuffle 成本；动态主要是增边批次；排名近似负载，度相同子图的 clique 搜索量仍可悬殊。§6 分开比较“仅枚举”与含预处理总时间，不能只摘前者速度用于索引总成本。D01 的签名状态、候选膨胀和最坏输出界并未消失。
- **未来约束**：采用 vertex-root ownership、静态排序、parallel pivot、增边并行不是空白；可研究的是相同内存预算下如何避免结果写出/证书验证成为新的瓶颈，以及更新、查询、重建三类负载的共同调度。

<a id="d03"></a>

### [D03] Computing maximal cliques in link streams

- **作者/年份/来源**：Tiphaine Viard, Matthieu Latapy, Clémence Magnien；Theoretical Computer Science 2016；[DOI:10.1016/j.tcs.2015.09.030](https://doi.org/10.1016/j.tcs.2015.09.030)，[arXiv:1502.00993](https://arxiv.org/abs/1502.00993)，所读 v7 日期 2016-07-04。
- **阅读证据**：13 页 `dynamic-sources/temporal-viard.pdf`；§2 定义，§3 Algorithm 1、Lemmas 1–5 和 Theorems 1–2，后续实验和优化。
- **输出定义**：瞬时事件 `(t,u,v)` 下，Δ-clique 是 `(X,[b,e])`，每对 X 中顶点在区间内每个长度 Δ 的子窗口至少交互一次；maximal 同时不允许加顶点与扩大时间。将全部边聚合后找 static clique 会产生不存在于任一共同时间区间的伪结果。
- **算法细节**：从每个事件的 `({u,v},[t,t])` 种子出发，工作集合 S 中取一项，尝试三类扩展：加一个仍满足 Δ 条件的顶点；将左端扩到 `max_pair(first occurrence)−Δ`；将右端扩到 `min_pair(last occurrence)+Δ`。S 为待处理，M 为已经见过的全部状态，R 为 maximal 结果；只有三类扩展均失败才输出。扩展依赖每对边的 first/last occurrence 的极值，不是把全部边时间并集作为一个区间。
- **保证**：Theorem 1 完整枚举；Theorem 2 给 `O(2^n n m²)` 空间与 `O(2^n n²m³+2^n n³m²)` 时间，m 是时序事件数。因为起止点来自事件时间或其 ±Δ，状态区间种类 `O(m²)`；节点子集仍可 `2^n`。
- **优点**：定义清楚、构造简单，给出加点/扩时的完整性证明；提出可复用的 Δ-交互语义，接触网络可解释性强。
- **局限**：M 保存所有中间状态，内存可比最终输出大很多；最坏情况下即使只有少量 maximal 结果，也会遍历大量非 maximal 子集，不是最终结果数的多项式延迟算法。窗口语义不要求事件完全同时发生，也不等于边在每个时间点均持续存在。

<a id="d04"></a>

### [D04] Adapting the Bron–Kerbosch Algorithm for Enumerating Maximal Cliques in Temporal Graphs

- **作者/年份/来源**：Anne-Sophie Himmel, Hendrik Molter, Rolf Niedermeier, Manuel Sorge；Social Network Analysis and Mining 2017；[DOI:10.1007/s13278-017-0455-0](https://doi.org/10.1007/s13278-017-0455-0)，[arXiv:1605.03871](https://arxiv.org/abs/1605.03871)，所读作者版标注 2018-08-09。ASONAM 2016 前身标题 *Enumerating Maximal Cliques in Temporal Graphs* 并入该条。
- **阅读证据**：32 页 `dynamic-sources/temporal-bk.pdf`；§2.1 定义/Δ-cut，§3 Algorithms 4–5 与 pivot 证明，§4 Δ-slice degeneracy 分析，§5 实验。
- **算法细节**：把 BK 的 P、X 从顶点集合改为 `(v,I)` 集合，R=`(C,I)` 始终 time-maximal。加入 `(v,I')` 后，新 P/X 用 Δ-neighborhood 做 **Δ-cut**：逐顶点交集时间区间，仅保留长度至少 Δ 的最大重叠区间。相同顶点可在不同时段出现，不能简单做一次位图 AND。若 P∪X 中没有候选能覆盖 R 的整个时间区间，R 才同时 vertex-maximal。Pivot 也改为 `(vp,Ip)`，只在满足区间包含条件的子问题中跳过 pivot 的 Δ-neighbors；可选多组互不重叠时间 pivot，最优选择化为 weighted interval scheduling。
- **保证/参数**：若 x 是所有 time-maximal cliques 数，Theorem 2 时间 `O(x|E|+|E||T|)`；这里 x **不是最终 vertex-and-time-maximal 结果数**。以每个 Δ 时间片聚合图的最大 degeneracy d 为参数，Theorem 3 界为 `O(3^(d/3) 2^d |V||T||E|)`，为 d 参数的 FPT，但还有指数 `2^d` 因子。Pivot 的实际显著加速不等于其最终输出延迟获得静态 Tomita 同样的最坏界。
- **优点**：避免 D03 需要全局保存所有已见配置的做法；区间对的 P/X 同时处理完整性和去重；时间局部稀疏性比全生命周期聚合图更能解释代价。
- **局限**：time-maximal 中间结果可比真正输出指数多；当 Δ 变大使时间片稠密，d 增大，运行仍困难；区间列表交、排序和同一顶点多区间状态使数据结构比 static BK 复杂，不能只替换邻接查询就完成 temporal 扩展。

<a id="d05"></a>

### [D05] Faster maximal clique enumeration in large real-world link streams

- **作者/年份/来源**：Alexis Baudin, Clémence Magnien, Lionel Tabourier；Journal of Graph Algorithms and Applications 2024；[DOI:10.7155/jgaa.v28i1.2932](https://doi.org/10.7155/jgaa.v28i1.2932)，[arXiv:2302.00360](https://arxiv.org/abs/2302.00360)。
- **阅读证据**：28 页 `dynamic-sources/faster-link-stream.pdf`；§2 的持续时间 link 定义，§4 Algorithm 2、ForbidEdges 与 end-time-aware pivot，§5 理论/空间/r 比率，§6 结果及并行化局限。
- **对象**：link 为 `(b,e,u,v)`，表示两点在整个 `[b,e]` 均相连；结果要求顶点和时间双 maximal。瞬时事件的 Δ-clique 需要先正确转成这种持续区间，不能直接当普通持续边。
- **技术细节**：按 link 开始时间 t 扫描瞬时图 Gt。每个新开始的边 `(u,v)` 是锚，在共同邻域上递归列 time-maximal candidates；候选 C 的结束时间 `Et(C)=min_{pair∈C} pair_end_time`。对共同邻居 x，只有 `Et(C∪{x})<Et(C)` 才说明 x 不能在完整区间加入；对所有 x 成立才输出。`ForbidEdges` 把同一时刻已处理的起始边列为禁止，搜索一旦包含该边就剪掉重复分支。时间感知 pivot 仅删除满足 `Et(R∪{u})=Et(R∪{u,p})` 的 pivot 邻居，不能直接照搬 static BK 的全部邻居排除。
- **复杂度/空间**：设 d 为瞬时图最大度、q 为最大 clique 大小、m 为 links 数；论文给 `O(m 3^(d/3) 2^q d²)` 时间、`O(m+qd)` 工作空间（把 maximality 检验放递归中以流式输出，不存 Cliques 全集合）。最终输出 α 的式子为 `O((1/r)d²qα)`，r 是搜索叶中真正输出结果的比例；`1/r≤2^q`，所以“output-sensitive”在此仍可能含指数质量因子，不能误写为每个最终结果多项式开销。
- **优点**：只访问当前瞬时邻域，避免整个 lifetime 大图；ForbidEdges 与时间 pivot 结合；可流式验证和输出，低内存，实验包含上亿 links 规模。
- **局限**：部分候选仍只 time-maximal；低质量叶比例决定无效工作。并行实验按相近起始边数切时间段，许多数据四线程后收益很小，作者归因于短时间稠密区承担绝大部分 clique 搜索，说明平均事件数并非可靠负载估计。声称简单按时间分区可线性加速不符合实测。

<a id="d06"></a>

### [D06] An Efficient Updation Approach for Enumerating Maximal (Δ, γ)-Cliques of a Temporal Network

- **作者/年份/来源**：Suman Banerjee, Bithika Pal；Journal of Complex Networks 2022，10(5), cnac027；[DOI:10.1093/comnet/cnac027](https://doi.org/10.1093/comnet/cnac027)，[arXiv:2007.04411](https://arxiv.org/abs/2007.04411) 为所读完整作者稿。
- **阅读证据**：37 页 `dynamic-sources/delta-gamma.pdf`；§3 问题定义，§4 Algorithm 1 与 Procedures 2–5、Lemmas 2–10、Theorems 1–3 及复杂度；§5 对 batch、Δ/γ 的实验。
- **输出与更新语义**：每对顶点在每个 Δ 窗口至少出现 γ 次事件；按时间顺序到达新事件批次，由截至 T1 的 clique 集更新为截至 T2 的 clique 集。它不是任意旧边插入删除的 fully dynamic 问题。
- **算法细节**：`Edge on Clique` 保存所有旧 maximal 结果和可能延长到未来的边界集合 `C_ex`，后者包括当前右端至少到达 T1 的相关 clique。先只扩展旧边界 clique 的右端；再以重叠事件 `E[T1−Δ,T2]` 初始化二顶点 clique，逐个执行加点、左扩、右扩并 memoize。扩右使用各点对“倒数第 γ 次事件”时间的最小值加 Δ；扩左对称用“第 γ 次事件”最大值减 Δ。有限历史窗口可能把本可向更早延长的候选误判为 maximal，因此 Procedure 5 用 `(顶点集包含, 区间包含)` 清理 boundary 假 maximal，再与不再受影响的旧结果合并。
- **优点**：明确区分旧稳定结果与边界结果；保留 Δ 长度 overlap，避免只用新批次造成跨边界 clique 漏检；解释为什么仅“向右扩旧结果”不够，新顶点集还必须重新发现。
- **局限**：它保留旧结果、边界状态及 memoization，状态仍可能指数；不是每条新事件只花 Δ 窗口大小的时间，边界 clique 数与包含比较也是成本。原稿复杂度仍显式含 `2^n`、边界配置与批次事件量，不能概括为总运行线性或多项式延迟。只处理按事件时间追加，旧时间补录、撤回与乱序 watermark 没有同时解决。
- **实现注意**：需要独立精确 oracle 对跨批次结果集合做校验；Procedure 5 这类“先局部候选后去包含”的完整性依赖保存的边界集合，不能随意只留 top-k 旧结果。

<a id="d07"></a>

### [D07] Span-core Decomposition for Temporal Networks

- **作者/年份/来源**：Edoardo Galimberti, Martino Ciaperoni, Alain Barrat, Francesco Bonchi, Ciro Cattuto, Francesco Gullo；ACM TKDD 2020；[DOI:10.1145/3418226](https://doi.org/10.1145/3418226)。所读 [arXiv:1910.03645](https://arxiv.org/abs/1910.03645) 作者版标题带副标题 *Algorithms and Applications*；CIKM 2018 前身 *Mining (maximal) Span-cores from Temporal Networks*（arXiv:1808.09376）并入此条。
- **阅读证据**：44 页 `dynamic-sources/span-core.pdf`；§3 定义/Proposition 1，§4 Algorithm 1/Corollary 1，§5 Algorithm 2/Lemmas 1–3，§6 temporal community search 的联系，§7–8 实验与应用。
- **模型边界**：对区间 I 取**每个时间点都存在**的边交 `E_I=∩_{t∈I}E_t`，在 G_I 上求 k-core。`(k,I)` span-core 是唯一最大点集；maximal span-core 是在 k 与区间包含两个维度不被支配的项，不是列出所有任意 k-core 子集，也不是 Δ 窗口内至少出现一次的 OR 语义。
- **算法细节**：满足 `k'≤k` 且 `I'⊆I` 时，`C_(k,I)⊆C_(k',I')`。全分解按区间长度递增，只用左右去一端的两个父区间之 1-core 交集作为起始候选，再做静态 core decomposition；这已等于所有更短父区间能提供的 1-core 候选限制。只找 maximal 时反向考虑大区间，每个区间只可能贡献其 innermost core。其 coreness k* 必须严格超过向左/向右各扩一个时间点的大区间 innermost coreness 最大值 lb；先删 `degree_I(v)≤lb` 的点，再仅在剩余小图求 innermost core，若 k*>lb 才输出。
- **保证/复杂度**：每个区间至多一个 maximal span-core，故结果项数 `O(|T|²)`；方法最坏时间 `O(|T|²|E|)`，优势来自剪掉许多区间/候选点。不能从“输出可达 Ω(|T|²)”推出额外 `|E|` 因子也是不可改进下界；逐顶点结果材料化时仍需另外计点集大小。
- **优点**：区间包含与 coreness 两维偏序有强可证明剪枝；直接求 maximal 而不全分解后过滤；可作为 clique/plex 枚举的上界/候选过滤，亦适合交互视图的紧凑多尺度概览。
- **局限**：稳定边 AND 语义对缺测敏感，长时间任意一次缺边即可删去整条关系；不能代替容忍间断的 Δ-clique。degree/core 条件比 clique 弱很多，可能留下大量无法形成目标 clique 的点。它求唯一最大 core/偏序前沿，本身并非指数多对象的 clique 枚举，基准需区分任务。

<a id="d08"></a>

### [D08] Fast maximal clique enumeration in weighted temporal networks

- **作者/年份/来源**：Hanjo D. Boekhout, Frank W. Takes；Social Network Analysis and Mining 2026；[DOI:10.1007/s13278-025-01539-3](https://doi.org/10.1007/s13278-025-01539-3)，所读 [arXiv:2412.02434](https://arxiv.org/abs/2412.02434) 为 43 页完整作者稿。
- **阅读证据**：§3 的 Definitions 1–4 和边界反例，§4.2 双指针 stretching，§4.3 bulking/temporal dominance 剪枝，Appendix A Algorithms 1–7，§6 实验与结果口径。
- **定义上的实质变化**：γ 从窗口内事件**次数**推广为事件权重之和；离散窗口用 `[τ,τ+δ−1]`，且 clique 区间两端必须落在 clique 内实际事件上。它与旧定义输出不同：旧定义允许“事件前后各延展空白时间”形成多个 maximal 区间；本文把边界收至真实事件后，一些旧 maximal 小顶点集不再 maximal。因此结果数量下降并不全是算法剪枝成果，比较前必须统一边界语义。
- **算法细节**：先对每条点对事件序列执行 stretching，两个单调向右指针维护不超过 δ 长的事件窗口与累计权重，找到所有二顶点 duration-wise maximal 区间；每次循环至少推进一个指针，阶段时间从旧方案 `O(γm)` 降为 `O(m)`。再执行按点标签单调增长的 bulking，二点扩三点时合并三条边的区间，后续从上层已经得到的两个扩展 clique 与连接两个新点的基础边区间合并。除当前真实首末事件边界，还维护可增长的 outer borders，以判断加点后区间缩小、保持或因新事件增长。剪枝不能仅看当前状态被包含，还必须证明该分支未来所有可扩点的空间和时间增长都受另一已处理分支支配；相邻分支的既有扩展信息被复用。
- **优点**：加权模型与双指针基础阶段适用于强度数据；去重依赖点序而非保存所有已见子集；复杂 dominance 判定重用已有计算，减少额外邻域工作；完整伪代码可复现。
- **局限**：`O(m)` 只属于 stretching，不是完整枚举复杂度；bulking 仍可指数输出。作者把新边界定义称为解决解释问题，应理解为替代语义，不能说旧定义数学错误。形式描述写权重为实数，但双指针累计阈值与剪枝依赖的单调性不能不经证明就推广到任意负权；复现宜先采用其频率/强度型非负数据并显式写出假设。完整实现的参数、标签排序和区间元信息多，直接扩到 BCviz 的二维二部阈值仍需新证明。

<a id="d09"></a>

### [D09] Tight bounds and output sensitive algorithms for maximal clique enumeration in link streams

- **作者/年份/来源**：George Manoussakis；[arXiv:2610.11385v1](https://arxiv.org/abs/2610.11385)，首版 **2026-10-08**，截至本调研日期为预印本，不能标为已同行评议定论。
- **阅读证据**：26 页 `dynamic-sources/tight-bounds.pdf`；§2 输出延迟/缓冲引理，§3 threshold characterization，§4 Algorithm 1/Theorems 1–3，§5 Algorithm 2/suffix 字典/动态 orientation/Theorems 4–8，§6 到 Δ-clique 的归约。不是只依据摘要。
- **关键改变**：D05 先枚举大量 time-maximal 子集再验 vertex maximality，可能多 `2^q` 因子；本稿固定结果的**结束时间 e**，对开始阈值 τ 扫描图 `G_[τ,e]`，该图只含持续覆盖 `[τ,e]` 的点对。随着 τ 增大，图仅增边。最大起点 `s_e(C)=max pair_start`、最小终点 `f_e(C)=min pair_end`；结果 maximal 的充要条件是 C 在 `G_[τ,e]` 中 maximal、`s_e(C)=τ`、`f_e(C)=e`。因此可以调用静态 **maximal** clique 枚举而不把每个静态子 clique 都作为 time-maximal 候选。
- **两种算法**：第一种以某条在 e 结束的 canonical 最小点对为锚，在其共同邻域中对 τ 调用静态 MCE，利用 canonical 规则去重。第二种在 e 的低出度顺序下令 clique 归属于最早点 w，只在 `N⁺(w)∪{w}` 的 O(k) 大小窗口枚举，k 为瞬时 degeneracy；若局部 maximal 候选不是全局 maximal，它是先前输出某 clique 按该顺序的 **proper suffix**，用 `(τ, reversed suffix)` 的 trie/dictionary 验证，避免扫描高最大度的早序邻居。
- **动态与持久化细节**：§5.4 复用已有动态图 level 结构，按 level 与 ID 形成出度 O(k) 的无环定向；维护每对点的 anchor 集 `Π(xy)={w:x,y∈N⁺(w)}`。同一时间先插入新开始 links，再处理结束 links，最后删除结束 links，以符合闭区间语义。在线算法在 end-time 输出；离线小延迟版本先进行时间扫描，将 balanced trees、N⁺、Π、level 历史通过 path copying 持久化，以便枚举阶段按 e 回访快照。
- **声称的保证**：总 maximal 结果上界 `O(n|T|k²3^(k/3))`，指数部分较旧 `2^k` 改进，并给多项式因子内匹配构造。Theorem 8 预处理 `O(m log m+mk² log³n)`，延迟 `O(k⁵(k² log m+λ(k)))`，λ 为小静态图 MCE 延迟；在线版总时间为预处理/维护项加 α 倍多项式 k 因子。§6 将事件窗口转换成“所有滑窗起点均满足该点对交互”的持续 links，建立 maximal Δ-clique 的双向对应，而非直接聚合事件。
- **优点**：明确关注最终双 maximal 输出，避开 time-maximal 候选的指数冗余；理论给实际可能高 hub 但低 degeneracy 场景另一条路；把所有权、事件顺序、持久化和查询成本分开。
- **局限**：这是新理论稿，所读版本未给大规模工程实验，不能承诺比 D05 代码更快；多项式 k 次数很高。最重要的是 §5 末明确承认 suffix 字典 D 与把 amortized delay 转 worst-case delay 的输出缓冲可要求**指数空间**；要保证多项式空间，可改用直接 maximality 检验和 geometric amortization，但会重新引入最大度 Δ（及 log α）因子。持久化结构的 `O(mk²log³n)` 不是线性空间，不能泛称“低延迟、低内存同时解决”。也不能把在线 end-time 输出误称为任意后补事件修订支持。
- **未来约束**：动态图 orientation、suffix 去重、时序持久化、最终结果 polynomial delay 均已有新先例。可检验缺口是有界内存、实际低延迟和可证明安全过滤的共同折中，需先复核新稿证明并实现对照。

<a id="d10"></a>

### [D10] Parallelizing Maximal Clique Enumeration on GPUs

- **作者/年份/来源**：Mohammad Almasri, Yen-Hsiang Chang, Izzat El Hajj, Rakesh Nagi, Jinjun Xiong, Wen-mei Hwu；PACT 2023；[DOI:10.1109/PACT58117.2023.00022](https://doi.org/10.1109/PACT58117.2023.00022)，[arXiv:2212.01473](https://arxiv.org/abs/2212.01473)。
- **阅读证据**：14 页 `dynamic-sources/gpu.pdf`；§II-D 根分解/degeneracy 背景，§III-B–E/Algorithm 4、worker list、partial induced graph、X 压缩，§IV-A 计时口径与 §IV-B–F 消融/多 GPU。
- **技术细节**：每个 thread block 深搜独立 BK subtree，block 内线程协作集合交与 pivot，整段搜索一个 kernel，避免 GPU BFS 多层 frontier 爆炸和 CPU 逐次 offload。根可按顶点或边拆分：边根 `(vi,vj)` 的 P 为双方共同邻居中晚于两者的点，X 为此前已分配的共同邻居。GPU 资源持续驻留；最初通过原子计数拿根任务，根任务耗尽后，空闲 block 把自身 ID 放 **worker list**，正在搜索的 donor block 仅在有 receiver 时才复制一个较大分支，减少工作队列存海量 R/P/X 状态。donation 还要求分支 `|P|≥10` 且 donor 尚有其它分支，避免捐完又立刻索取。
- **内存设计**：degeneracy 排序使根 P 的大小 O(d)，但 X 仍可 O(Δ)。full induced graph 编码 P 与 P∪X 的所有相关边；partial 仅位图编码 P–P，X 边回原 CSR 查，节省 O(Δd) 大邻域构造；partial 时 pivot 仅从 P 与根 P 内已处理点选，正确性仍成立但剪枝强弱改变。X 拆为会增长/缩小、来自根 P 的 `X_P`（逐层 O(d) 位图）与只会缩小、来自根 X 的 `X_X`（共享一份数组，逐层仅记录有效前缀边界）；将各层 X 存储从 `O(Δd)` 减到 `O(Δ+d²)`。
- **优点**：针对 MCE 特有的 maximality X 集而非只套 k-clique counting kernel；动态负载与内存压缩相互配合；有 full/partial、first/second-level、worker-list 消融，并考虑多 GPU。
- **局限与结果解释**：§IV-A 明确计时的是 **counting maximal cliques**，排除磁盘读入、包含 degeneracy 预处理；结果表的高吞吐不意味着已逐顶点输出全部 clique、传回 CPU 并落盘。GPU baseline 缺代码，用更旧 Titan X 公开数字对比 V100/A100，作者承认硬件不公平；另给 CPU 同机对照，但 CPU 与 GPU 资源/功耗不同。默认表格选 first/second-level×full/partial 最佳组合，部署仍需要选型策略。静态图为主，完全动态图和 online 输出协议不在该算法中。
- **未来约束**：不能把 worker-list donation、部分邻域编码、逐层 X 压缩包装成新贡献。若做 BCviz 枚举加速，应报告 CPU/GPU 端到端、峰值显存、传输、每个结果的解码与输出字节，并与“仅计数”分开。

<a id="d11"></a>

### [D11] Incremental Maximal Clique Enumeration for Hybrid Edge Changes in Large Dynamic Graphs

Ting Yu 等；TKDE，online 2023、正式卷期 2024；[DOI:10.1109/TKDE.2023.3311398](https://doi.org/10.1109/TKDE.2023.3311398)。Crossref 核对到题名/作者/卷期，IEEE 与 USQ 资源访问 403，尚未得到方法全文。其“混合边更新”与 D01 先删后加缺口直接重叠，是任何 fully dynamic 新颖性判断的**必须补读项**；本笔记不据题名虚构其状态或复杂度。

<a id="d12"></a>

### [D12] Mining maximal cliques from a large graph using MapReduce: Tackling highly uneven subproblem sizes

Michael Svendsen, Arko Provo Mukherjee, Srikanta Tirthapura；JPDC 79 (2015), 104–114，online 2014；[DOI:10.1016/j.jpdc.2014.08.011](https://doi.org/10.1016/j.jpdc.2014.08.011)。D02 把它作为 PECO 的前身/对照，说明其分布式邻域复制与根排名做法；但本轮未拿到独立全文，因此不把 D02 的相关工作叙述替代该文正文阅读。做分布式负载工作必须补读。

<a id="d13"></a>

### [D13] Parallelizing maximal clique and k-plex enumeration over graph data

Zhuo Wang, Qun Chen, Boyi Hou, Bo Suo, Zhanhuai Li, Wei Pan, Zachary G. Ives；JPDC 106 (2017), 79–91；[DOI:10.1016/j.jpdc.2017.03.003](https://doi.org/10.1016/j.jpdc.2017.03.003)。DASFAA 2016 的 *Parallelizing Maximal Clique Enumeration Over Graph Data* 为前身。已核对书目，未独立核对算法全文；不能声称 workload-aware 分割、并行 plex 是无人做的方向。

## 10. 通用图枚举与模式挖掘系统

<a id="g01"></a>

### [G01] A Polynomial Delay Algorithm for Generating Connected Induced Subgraphs of a Given Cardinality（2015，JGAA；读取 arXiv v3，2016-08-22）

- **来源与阅读范围**：正式 DOI https://doi.org/10.7155/jgaa.00357 ；作者全文 https://arxiv.org/abs/1411.2262 ，PDF https://arxiv.org/pdf/1411.2262 ；本地 `general-sources/reverse-enum.pdf/.txt`。已读 §1–§4、Proposition 1、Theorem 1、Lemma 1–2 和修订脚注。
- **输出对象**：无向图中所有恰好 k 个顶点的 connected induced vertex sets；k 是输入的一部分。枚举所有大小 ≤k 再只输出 k，不自动是此问题的 output-polynomial 算法，因为中间层可能比目标层巨大。
- **算法细节**：把每个合法 k-set 当作解空间 supergraph 的节点；两个解若交换一个顶点且保持连通则相邻。借助生成树叶子删除和朝目标集合的最短路加入，证明该 supergraph 强连通。字典版本 BFS 保存访问过的解，避免重复。为消除指数解存储，先按输入图 DFS 定义顶点顺序和解的字典序；证明非最小解都有更小的合法交换邻居，选唯一 predecessor，反向遍历这棵隐式解树。重算 parent 而不保留所有访问历史，且**奇深度进入时输出、偶深度退出时输出**，把长串无输出回溯分散到相邻输出，不能把普通 DFS 直接当作相同 delay。
- **复杂度与条件**：令 b=min(n−k,kΔ)，非平凡 k 情形，线性空间版本 Theorem 1 给出 delay `O((kb)^2(Δ+log k))`、空间 `O(n+m)`（不含输出）；字典版 delay `O(kb[k(Δ+log k)+log n])`，空间 `O(n+m+kN)`。v3 脚注明确修复早版漏掉计数上界中 n 引起的 log n 因子，不能沿用旧界。
- **优点**：把 exact-cardinality 问题与“所有较小子图”的复杂度严谨区分；展示邻域、唯一 parent、低空间、输出调度四个可分别复用的组件。
- **局限**：parent 检查和大邻域导致多项式因子较大；本篇主要理论，没有现代大图系统的吞吐评测。线性空间不意味着 index 能存下所有解，也不意味着 O(n+m) 总时间。BCviz 的 vertex ordering 若替换此 DFS 顺序，必须重新证明每个非根解有合法下降 parent，不能仅以实验无重复作为证明。

<a id="g02"></a>

### [G02] Algorithms with improved delay for enumerating connected induced subgraphs of a large cardinality（2024，Information Processing Letters 183:106425；作者版 v2 2023-03-15）

- **来源与阅读范围**：https://doi.org/10.1016/j.ipl.2023.106425 ；https://arxiv.org/abs/2112.07204 ；本地 `general-sources/connected2023.pdf/.txt`。读 §1–§3、Algorithm 1–2、Lemma 1–3、空间讨论；正式卷期年由 Crossref published-print 确认为 2024，OpenAlex 的 2023 年记录不作最终卷期依据。
- **输出对象**：同 G01 的所有恰好 k 个顶点的 connected induced subgraphs，重点是 k 接近 n 的场景。
- **算法细节**：加强解空间邻域条件，要求 |X∩Y|=k−1 且 **G[X∩Y] 也连通**。每个当前解先用 articulation-point 检测找可删顶点，只删非割点；再给连通的 k−1 集合加一个邻居，避免 G01 删除割点后还要找多个分量的共同邻居。仍证明解空间强连通。IRwD 使用 balanced dictionary；变体用高度 n 的 binary incidence trie。IRwP 按 DFS 顶点顺序定义唯一 predecessor，只接受当前节点为 predecessor 的候选。
- **复杂度与条件**：b=min(n−k,kΔ)。三种 delay 分别 `O(kb(k logΔ+log n))`、`O(kbn)`、`O(k² b min(k,Δ))`。前两种须保存已访问结果，空间依赖 N；论文 Algorithm 2 展示的是 BFS 版 IRwP，**BFS 仍可能占指数空间**，线性空间+所述 delay 需采用 DFS 和奇偶层输出安排。相对当时 Simple 的 `O(k²Δ)` 改善只在论文推导的 k 很大区间成立，不是全参数占优。
- **优点**：用“保留交集连通”简化邻域生成，适合系统性研究大 k 与 small complement 参数；准确讨论 BFS 队列破坏 linear-space。
- **局限**：主要是理论 short communication，无大规模实证；字典版以内存换 delay，不能说所有算法都是线性空间。最新 G03 已给出更好的通用 O(kΔ) 界，因此不能把本文当作 2026 年全局最佳 delay。

<a id="g03"></a>

### [G03] An algorithm with a delay of O(kΔ) for enumerating connected induced subgraphs of size k（2024 预印本；读 v3，2025-07-08）

- **来源与阅读范围**：https://arxiv.org/abs/2404.12559 ；本地 `general-sources/connected2024.pdf/.txt`。读 §2.1–2.3 的 Algorithm 1、执行案例及完备/无重复/delay/space 证明，§3 实验、§4；正式期刊录用未在本次核实，保持预印本标记。
- **输出对象**：无向图的全部 size-k 连通诱导顶点集，不按拓扑归并，不是最大/极大凝聚子图。
- **算法细节**：先 O(n+m) 做 DFS，按**逆发现顺序**处理根并逐个排除；未处理的 DFS 树保持连通，免去任意根删除后过滤不足 k 分量的额外成本。递归维护 S（当前连通集）、F（前部 forbidden，后部待访问 permitted）、N（已访问 permitted 邻居）、T（两次输出间已探索顶点）。不同于通常逐个禁止已访问邻居的回溯，本文逐步激活已访问邻居供后续兄弟分支使用；因此一旦一支有解，后续支可继续有解，减少连锁失败回溯。T 复用已探索失败部分，|S∪T|=k 时可以直接输出该合法集合并清 T。全局列表尾部修改及 Boolean membership 数组降低每步开销，输出后 N 回移 F 的批量成本单独分析。
- **复杂度与验证**：在线预处理后 delay `O(kΔ)`；含图、全局列表和 Boolean 数组工作空间 `O(n+m)`。§3 明确**计入写磁盘的时间**；Java、8 GB、600 秒阈值，表中“large”图最大约 56,739 点/212,945 边，主要比较 k=2…6 及 large-k；不能据此称已证明 billion-edge 部署能力。
- **优点**：对一般 k 明确改善旧 `O(k²Δ)` delay，提供可复现实现入口 https://github.com/miningsubgraphs/algorithms ；技术创新在候选允许顺序与输出复用，而非泛泛“用 DFS”。
- **局限**：Δ 在 hub-heavy 图中可能很大，worst-case delay 并非固定常数；输出仍可指数多，查询早停或筛选约束会改变证明。将 BCviz peak interval 作额外剪枝时，只能删去已证明无 size-k 解的分支，否则破坏完备性与 delay 分析。

<a id="g04"></a>

### [G04] Optimal Listing of Cycles and st-Paths in Undirected Graphs（2013，SODA；读 2012 arXiv v2 作者版）

- **来源与阅读范围**：正式 DOI https://doi.org/10.1137/1.9781611973105.134 ；https://arxiv.org/abs/1205.2766 ；本地 `general-sources/optimal-paths.pdf/.txt`。读 §2.1–2.5 的 reduction、bead string、Algorithm 1、certificate operations，§3 的 spine 摊还分析与 §4 的数据结构。所读是早期作者版，未宣称与会议终稿逐字相同。
- **输出对象**：无向简单图中的所有 simple s–t paths 或所有 simple cycles，允许有 chord；输出路径的顶点/边序列。
- **算法细节**：先按 biconnected components 建 block tree；任何 s–t path 必在唯一的 component chain（bead string）中并经过其中割点。每步选当前端点的一条边，二分“使用它”和“不使用它”；certificate 是带 DFS tree/back edges 的动态 bead-string 首块，不只是一个布尔 reachability 值，支持 choose、left-update（取边后删前缀端点）、right-update（弃边）、restore。certificate 保证进入的递归分支至少有解。将连续 right branches 按同一端点组织成 spine，再把维护代价分摊至该 spine 下输出，避免每个结果重新 DFS 全图。cycles 则在每个 biconnected component 选 back edge (s,t)，枚举去掉该边的 s–t paths 后重新分解剩余图。
- **复杂度**：paths 为 `O(m+Σπ |π|)`，cycles 为 `O(m+Σc |c|)`，按显式输出总长度达到总时间最优；这是**总输出敏感界**，不能直接改写为每次输出 O(|当前结果|) 的 worst-case delay。图不连通时须先处理分量，完整输入项可写 O(n+m)。
- **优点**：certificate + 可回滚更新 + recursion-spine 摊还非常适合作为枚举论文理论样板；明确支付输出写出的线性成本。
- **局限**：限无向 simple graphs；不能直接套 directed/temporal/有标签关系约束。动态 biconnectivity 维护比普通 DFS 难实现；早期作者版的示意图/文字不作为额外实验事实引用。若只要长度≤k 或 ranked top-k，需重新处理可行性证书与搜索顺序。

<a id="g05"></a>

### [G05] Amortized Õ(|V|)-Delay Algorithm for Listing Chordless Cycles in Undirected Graphs（2014，ESA）

- **来源与阅读范围**：https://doi.org/10.1007/978-3-662-44777-2_35 ；https://arxiv.org/abs/1408.1265 ；本地 `general-sources/chordless.pdf/.txt`。读 §3.1–3.5、§4 Algorithm 1 与 Remark 1、§5 摊还证明、Theorem 1–2/Corollary 1。
- **输出对象**：chordless（诱导）s–t paths 与相应 chordless cycles，非所有 simple cycles。
- **算法细节**：“存在任意 u–t path”可作为存在 chordless u–t path 的证书，但不能把任意 path 直接输出。对当前端点 u 做 cleanup：从一条证书 path 上挑**离 t 最近的 u 邻居 v**，记 v 和其后缀证书，暂删 v，再找另一条 u–t path，直到断开，得到全部 good neighbors。然后对每个 good v 递归，**其余 good neighbors 仍保持删除**，只恢复当前 v；否则先前端点与后续 path 可能形成 chord，Remark 1 给出反例。残留的 bad neighbors 无需全部扫描删除，结合 reduced degree 分析避免高阶无用邻居反复付费。
- **复杂度**：Theorem 2 为 `O(m+N(tp+n tq+n tu))`，tp/tq/tu 分别是任取路径、连通查询、边更新代价；搭配动态 connectivity 数据结构，得到 `Õ(m+nN)`。标题中的 delay 是**摊还**，不是最坏相邻输出延迟。polylog 隐藏因子与采用的数据结构必须保留。
- **优点**：只识别真正可扩展邻居，体现“少遍历无结果分支”可比单纯优化集合交集更重要；正确性中讨论邻居恢复顺序，具实现指导意义。
- **局限**：动态 spanning forest 有实际实现复杂度；论文主要理论，并未给出一个普通 BFS 实现就能达到相同 Õ(n) 摊还代价。chordless 有效性不具有任意添加顶点的单调性，通用 induced pattern 过滤不可随意继承。

<a id="g06"></a>

### [G06] Finding All Bounded-Length Simple Cycles in a Directed Graph（2021，预印本；读 v2）

- **来源与阅读范围**：https://arxiv.org/abs/2105.10094 ；本地 `general-sources/bounded-cycles2021.pdf/.txt`。读 §3.1–3.4 的三段伪代码、§4 Lemma 1–3、§5 复杂度、§6 数据设置；同时对照 G07 的具体反例，**不采信其完备性和 delay 为已成立结论**。
- **输出对象**：有向图中长度≤k 的所有 simple cycles，按最小顶点 owner 消重。
- **算法细节**：对每个 s，仅保留顶点 id≥s 的图及从 s 出发 k−1 层 BFS 可达区间；Johnson 风格 DFS 中把二值 blocked 改成 numeric Lock(v)。达到 v 时记前向深度 flen，仅在新深度小于 Lock(v) 且未超预算时递归；成功返回时传播反向长度 blen，把 Lock(u) 放宽为 k−blen+1；失败依赖通过 Blist 反向记忆和传播。不同根 s 可以并行，度排序是实际启发式。
- **复杂度状态**：作者 §5 声称单根 `O((cs+1)(k−1)(|Vs|+|Es|))`，并在**度均匀**假设下写出全局 `O((c+n)(k−1)d^k)`。平均度 d 不能给一般图的每根 neighborhood 大小上界；更关键地，G07 v4 已给出原伪代码漏解反例及每结果时间证明缺口，因此本报告把这些记录为“原文主张，已受反例挑战”。
- **优点**：研究动机和 bounded-length local filtering 很实用；numeric lock 的缓存思路解释了现有库中常见的优化来源。
- **局限**：在五点图 AD,AE,BD,BE,CA,CB,DA,DB,EC、k=5、所列邻接顺序下，缓存的 stack-relative backward distance 阻止有效环 A–E–C–B–D–A。**不能在精确枚举论文中未经修复和核验便作为 correctness gold standard**。这不表示每个以其名命名的库版本都有相同 bug；实现可能已修改，须逐版本检查。

<a id="g07"></a>

### [G07] Finding All Bounded-Length Simple Cycles in a Directed Graph — Revisited（2025 初稿；读取 v4，2026-07-17，预印本）

- **来源与阅读范围**：https://arxiv.org/abs/2512.08392 ；本地 `general-sources/bounded-cycles2025.pdf/.txt`。读 §3–§5 的逐步 counterexample、§6 Figure 7/SimpleSearch、Theorem 1–4、§7 与 Appendix B。正文署日期 2026-07-20，arXiv v4 上传 2026-07-17；不误称 2025 正式会议。
- **输出对象**：核心 `simple_search(G,s,k)` 输出所有**经过指定根 s**且长度≤k 的有向 simple cycles；全图去重还需最小根等外层机制，不能把单根 theorem 直接当成全图同一 delay。
- **算法细节**：指出 G06 在一次 DFS stack 下合法的回程距离不能在另一 stack 下复用。新算法放弃锁缓存：每个当前简单前缀 P，对其末端 v 的后继，在**排除当前 path 内点**的图中，从 s 做 reverse BFS，限制剩余长度；只保留可在剩余 budget 回到 s 的 fruitful successors，随后递归。到 s 即输出，不再延伸。每个被进入的非初始分支都有至少一个结果，树高≤k，于是相邻输出之间最多沿树回溯再下降 O(k) 层。可达 BFS 临时集合在递归前释放，只保存各层的 fruitful neighbor 列表。
- **复杂度与条件**：固定根的 worst-case delay（含首解与终止）`O(k(n+m))`；总时间 `O((cs+1)k(n+m))`；工作空间 `O(n+m)`，因为简单 path 上顶点各异，其保留后继列表总长度≤m，BFS scratch 不跨递归保留。原伪代码为清晰使用 list/set；严格界需 Boolean membership 数组，作者 Implementation Notes 明说。
- **优点**：给可独立检查的小反例、准确定位证明错误；以重新计算**上下文相容**的可行性证书换取直接完备性和 delay 证明，对动态索引缓存复用特别有启发。本次另按 G06 原伪代码转写，在所列五点图与穷举 DFS 对照，确认只得到 3 个过 A 环、漏掉第四个；可复核脚本及结果 `general-sources/check-cycle-counterexample.py/.json`。这只是单一反例复核。
- **局限**：是预印本，未做系统性大图性能比较；§7 仅说初测每环时间同量级，优化和严谨实验留待后续。每层 BFS 成本可能高，不能把正确性修补本身说成数据库系统性能突破。BCviz 后续若缓存 peak bound/候选 intersection，也须把排除集合、版本和参数上下文纳入有效性条件。

<a id="g08"></a>

### [G08] Arabesque: A System for Distributed Graph Mining（2015，SOSP；读 extended version）

- **来源与阅读范围**：https://arxiv.org/abs/1510.04233 ；本地 `general-sources/arabesque.pdf/.txt`，作者 extended report 2015-09-29。读 §2–§5、Algorithm 1–2、§6 中 ODAG 可扩展性讨论和 Appendix 关键正确性条件。
- **输出对象**：通用 embedding exploration，可写 k-clique listing、motif counting、单大图 frequent patterns 等应用。vertex expansion 是 vertex-induced；edge expansion 是 edge-induced；用户函数决定输出，不统一等同 maximal clique 枚举。
- **算法细节**：Think Like an Embedding / filter-process 抽象按 BSP 超步扩展一顶点或一条边，再执行 filter、process 和下一轮可见的 aggregation。每个实例采用最小 id 起点及可扩展的 canonical traversal order，本地 incremental canonicality check 消除同一实例的不同遍历序，不依赖全局 seen 集。**ODAG** 将所有序列同一深度、相同 vertex 合并，层间保留相邻关系，是原 embedding 集的 overapproximation；恢复路径会生成伪 embedding，必须重跑 canonical/filter 等验证。按 pattern 分 ODAG 降低虚假组合，两级 quick pattern→canonical pattern 聚合减少昂贵 graph isomorphism 次数。
- **保证与成本**：无重复/完备性需要用户函数 **automorphism invariance**，且失败 filter 必须对所有扩展 anti-monotone。单个固定 pattern 的 ODAG upper bound 可写 `O(k n²)` 而非保存 n^k tuples；全局 pattern 数、复制、merge 和重验成本额外，不能称线性空间。每 worker 保留输入图副本，ODAG 按 pattern 合并后广播复制。
- **优点**：统一表达枚举和 mining，代码量低；明确把实例 canonicality 与 pattern 同构区分；压缩可重建中间解集是 BCviz 研究的重要前史。
- **局限**：压缩引入伪路径，通信和按 pattern 复制会限制扩展；不保证 polynomial delay。反单调 filter 不可直接用于一般 quasi-clique 密度判断：当前不够密不代表以后不能形成合法稠密图。若新工作仅“把所有枚举结果压缩成 DAG”，必须与 ODAG 的压缩率、重验负担、语义差异比较。

<a id="g09"></a>

### [G09] GraphZero: Breaking Symmetry for Efficient Graph Mining（2019 作者预印本；相关正式系统文 OSR 2021）

- **来源与阅读范围**：完整所读题名如上，https://arxiv.org/abs/1911.12877 ，本地 `general-sources/graphzero.pdf/.txt`。读 §2、§4.1–4.3 的 Algorithm 1/Theorem 1–2、§5 schedule exploration/cost model、§6 orientation、§7；2021 期刊记录 DOI https://doi.org/10.1145/3469379.3469383 ，正式记录简称 GraphZero，**本条不把预印本年份当作会议录用**。
- **输出对象**：给定结构 pattern 的所有实例/计数，去除 pattern automorphism 导致的重复搜索；代码中的邻居交、差支持相应 adjacency/non-adjacency constraints，具体任务的 induced 语义要按配置固定。
- **算法细节**：编译器把某个 pattern vertex schedule 变成 nested loops 和邻居集合运算。枚举 pattern 的 automorphism group，对 schedule 顶点依次取 stabilizer：把当前顶点与其仍可互换的像之间加入 ID 大小关系，然后只保留固定当前顶点的 automorphisms。Theorem 1 给每实例恰有一个满足约束的映射；Theorem 2 可为每个位置只保留最近前驱给的单一上界检查。进一步只生成 connected、去对称的 schedule，以概率模型估计集合运算和已累计 restrictions 的通过率；按 degree/id 重编号，使对称约束与邻居 orientation 的访问顺序相容。
- **复杂度口径**：主张去除对称重复和减少编译搜索，不给一般图上 polynomial delay。pattern 的 automorphism 计算/排列搜索属于编译开销，小 pattern 时可承受，不能忽略为零。
- **优点**：同一 pattern 内实例等价和 schedule 等价分别处理；可自动生成 safe symmetry breaking，为从 BCviz ordering 构造唯一 owner 提供强基线。
- **局限**：Erdős–Rényi 式独立边概率模型难捕获 hubs、局部团和相关性；单组 restriction 未与 schedule 联合优化，这是 G10 的直接改进点。去重不是 top-k ranking，也不解决指数输出和索引空间。本文含 clique 实例，不是 maximal clique 专门算法。

<a id="g10"></a>

### [G10] GraphPi: High Performance Graph Pattern Matching through Effective Redundancy Elimination（2020，SC）

- **来源与阅读范围**：https://doi.org/10.1109/SC41405.2020.00104 ；https://arxiv.org/abs/2009.10955 ；本地 `general-sources/graphpi.pdf/.txt`。读 §II 定义、§IV-A–D 的 group restriction、two-phase schedule、performance model、IEP，§V distributed implementation、§VI 实验口径。
- **输出对象**：无向无标签给定 pattern 的 edge-preserving injective matches，去除同一 pattern edge instance 的自同构重复；还提供只计数模式。正文定义并不要求所有非边也保持，故不能无条件把全部任务称 induced。
- **算法细节**：不是只找一套 symmetry restrictions，而基于 automorphism 的 permutation 2-cycle 表达，生成多组可消除对称的 ordering restriction sets；对置换与当前限制共同构成的有向图作 acyclicity 检查，筛去不相容 automorphisms；再在与 pattern 等大 complete graph 上检验受限映射数是否等于未受限数除以 |Aut(q)|，验证 restriction set。两个阶段 pruning 降低 schedule 候选数。性能模型把 **schedule 与 restriction set 的组合**作为 configuration，考虑 nested-loop 各层候选规模和不等式通过概率，选成本最低组合后生成编译 C++。OpenMP/MPI 配合细粒度任务与 work stealing；当用户只需 count，使用 inclusion–exclusion 合并候选末端组合，避免逐一输出大量完整 embeddings。
- **保证与验证口径**：去自同构不改变实例集合；cost model 的 optimal 是候选空间和估计代价下选最小，非对任意图实际运行时间最优。论文的 IEP 大幅加速是 **counting 优化**，必须与 embedding listing 分开。SC 系统实验扩展到 Tianhe-2A 1,024 nodes，但不能把该硬件规模当作普通单机实现成本。
- **优点**：把“同样都无重复”的多种合法约束对运行时间的影响作为优化变量；BCviz 的几种 vertex orders 若都正确，应比较选择成本与收益，而非只和随机序比。
- **局限**：需要编译、小 pattern 规划、统计估计与分布式运行时；不存在通用低 delay 或低存储证明。计数和 listing 混用会夸大性能。新研究仅“更好匹配序+去对称”重叠很大，需明确额外查询语义/物理表示贡献。

<a id="g11"></a>

### [G11] HUGE: An Efficient and Scalable Subgraph Enumeration System（2021，SIGMOD；complete version）

- **来源与阅读范围**：https://doi.org/10.1145/3448016.3457237 ；https://arxiv.org/abs/2103.14294 ；本地 `general-sources/huge.pdf/.txt`。读 §2、§3.1–3.3 Algorithm 1、§4.2–4.4 Algorithm 2–4/LRBU、§5 scheduler/space 与 §7。
- **输出对象**：给定小查询图 q 在大数据图中的全部匹配，不是无 pattern 的所有 connected subgraphs；默认无标签、无向、连通。
- **算法细节**：逻辑计划分解为 join units（默认 stars）和 bushy join order；物理计划同时选择 hash join / worst-case-optimal-style complete-star intersection 与 push / pull。complete star 可 pull 邻居在本地求交，已有根的 star 可 pull 后枚举组合，否则 push 中间关系；DP 遍历 connected subqueries 和 disjoint-edge splits，以估计中间基数与通信代价选择混合计划。PULL-EXTEND 使用 **LRBU batch cache**：fetch 阶段单写者取邻居并 seal 当前 batch 需要项，intersect 阶段只读、零拷贝，结束 release，使 lock-free 有明确阶段同步前提。DFS/BFS 自适应调度在队列临界时切换算子，另有 work stealing。
- **空间与最优性边界**：论文给任务缓冲项与 `O(|Vq|² DG)` 关联的 bound（DG 为数据图最大度），并单独处理图分区、缓存、join 的额外项；不是声称整个 distributed system 只用此空间或索引 O(n)。DP optimal 指**设定的计划空间和成本模型**，准确结果基数本身通常要估计，实际 runtime 不保证全局最优；使用 wco 算子也不等于任意带不等式/非边条件的整条管线都有同样 theorem。
- **优点**：逻辑与物理优化分开，push tuples 与 pull neighborhoods 不必二选一；有可解释的缓存生命周期、内存控制和消融，符合数据库系统研究路径。
- **局限**：规划、运行时、通信、cache 共同增加工程难度；缺少 ranked/interactive output delay 保证；偏斜图和错误基数估计仍能影响计划。BCviz 后续若以 compressed blocks 替代部分 join units，应证明物理算子的语义与展开成本，再与 HUGE 既有混合计划比较。

<a id="g12"></a>

### [G12] DwarvesGraph: A High-Performance Graph Mining System with Pattern Decomposition（2020 初稿；读取 arXiv v5，2022-11-11，正式 venue 未核实）

- **来源与阅读范围**：https://arxiv.org/abs/2008.09682 ；本地 `general-sources/dwarvesgraph.pdf/.txt`。读 §3.1–3.2、§4.1–4.3 的 partial-embedding API 与适用条件、§5 Algorithm 1、§6 cost models、§7 compiler、§8 实验。
- **输出对象**：主要是给定 pattern **counting** 和可由 partial embeddings 计算的 domain/MNI 类统计；并非每个完整 embedding 都输出。
- **算法细节**：选 pattern vertex separator VC，将其与去掉 VC 后各 connected component 合并成 smaller subpatterns。枚举每个 VC match ec，分别算其扩展数 Mi；乘积 ΠMi 给组合数，再枚举 **shrinkage patterns** 扣掉不同子图把两个 pattern 顶点映到同一数据顶点的非法组合，最后调整 multiplicity。partial API 给 UDF 片段 pe 及其可扩展完整结果数 count；系统保证同一 subpattern 的片段全集 complete、所有 subpatterns cover 原 pattern 各点，因此可计算 domain/MNI 而无须 materialize 全部 tuples。编译器搜索 separator 和 matching orders，借 locality-aware 或 approximate-mining cost model 选 AST，做 CSE/LICM 与 pattern-aware loop rewrite。
- **核心边界**：§4.3 明确若应用必须把**全部 embeddings 写盘**，则退回不分解的方式，性能接近现有系统。计数/统计避免了完整 Ω(L) 输出，不应拿其时间作为 full enumeration 实验。clique 没有可用 separator，本身也不能享受这一路径的分解收益。
- **优点**：提供“表示/接口改变才能释放算法收益”的清楚实例；对 compact enumeration 可借鉴对外暴露因子化结果和按需 materialize 的 API，明确什么操作可在压缩态完成。
- **局限**：不是任意 per-full-embedding UDF 都能转为 partial 操作；误选 separator 可能比不分解更慢，作者消融直接显示 cost model 重要。必须处理 shrinkage、重叠和对称关系，不能简单乘两个子图计数。大性能倍数基于部分自实现 AutoMine baseline，复现需核实版本；本条不将 arXiv v5 日期推作录用。

<a id="g13"></a>

### [G13] Kaleido: An Efficient Out-of-core Graph Mining System on A Single Machine（2020，ICDE；读取 2019 作者预印本）

- **来源与阅读范围**：正式 DOI https://doi.org/10.1109/ICDE48307.2020.00064 ；https://arxiv.org/abs/1905.09572 ；本地 `general-sources/kaleido.pdf/.txt`。读 §3.1–3.2 的 CSE、Algorithm 1/谱签名，§4 hybrid storage、§5 API、§6 实验。作者版首页残留 PVLDB2018/TBD 模板，**不能用模板当正式 venue**。
- **输出对象**：embedding-centric mining：vertex/edge induced exploration，之后按 pattern 聚合，可用于 motif counting、FSM、clique discovery；输出配置不同，不能统一认为 maximal enumeration。
- **算法细节**：以 sparse tensor 视角保存所有 k-embeddings，**Compressed Sparse Embedding (CSE)** 按层保存 vertex IDs 与父前缀 offset，可追父恢复完整实例，减少显式 k-tuples 重复。canonical expansion 复用最小 ID 和可扩展遍历顺序。内存不足时把大层 offload disk，保留可索引的上层，在 sliding window 内批处理并按预测候选量分任务。pattern aggregation 的快捷判等使用排序 labels、degrees、由带 label 权重邻接矩阵计算的 characteristic polynomial（Faddeev–LeVerrier）组合成 hash，避免每次调用 bliss。
- **保证/适用范围**：谱法在本篇限定的 tiny-pattern 范围使用：无标签纯谱在 k<6；联合 degree 在 k<9 的论述，labelled 签名另有加权构造。**不能推广“同谱即同构”到一般图**；有限 hash 的一致也不自动等于无碰撞 canonical form，精确系统须补 collision check/证实限定域。预印本称 GI 为 NP-hard 的说法不能当作已知复杂性定理引用。
- **优点**：单机 out-of-core、压缩中间解与串行 I/O 可组合；让大中间结果超内存的评测成为研究对象，不只看总CPU时间。
- **局限**：压缩可弱化随机访问，外存吞吐与 SSD 带宽要单独计量；tiny-pattern 签名限制不适合大 cohesive subgraphs；压缩前缀存储与 BCviz linear order 不是同一种“线性空间”，CSE 总量仍由生成层的 embeddings 规模决定。

<a id="g14"></a>

### [G14] cgSpan: Closed Graph-Based Substructure Pattern Mining（2021，IEEE Big Data）

- **来源与阅读范围**：https://doi.org/10.1109/BigData52589.2021.9671995 ；https://arxiv.org/abs/2112.09573 ；本地 `general-sources/cgspan.pdf/.txt`。读 §II Definitions II.3–II.8、II.11–II.15、§III-A–E 的 Theorem III.1、early termination/hash/trie exception，及 §IV 实验。
- **输出对象与容易混淆点**：多 labeled-graph 事务数据库中的 closed frequent **patterns**，不是数据图每个实例。本文 II.8 明确把 closed 改为：不存在 proper supergraph 与它具有 **equivalent occurrence**（每个 embedding 都可对应扩展）。这不同于 CloseGraph 的 `support(g)=support(g′)` 事务闭合；相同 graph-ID 支持集但部分 embeddings 不能扩展的 g，在本文仍可能保留，因此不能把输出数直接与标准 closed transaction-support miners 互比。
- **算法细节**：继承 gSpan 的 minimum DFS code canonical labeling、DFS code tree 与 right-most extension（forward 加新点、backward 接回 right-most path）。若新 code 与已完整探索的 closed superpattern 在 embeddings 上可递归等价，则可停止扩展，因为相关闭超图已被发现。为少做 subgraph tests，以数据库中的 `(graph id,edge id)` **投影 edge sets**作为 hash key 找可能等价的已知 closed graphs，再实际验证 injection/extension。early termination 并非对所有形态安全：§III-D 标识已知 failure cases，把不可作为终止证据的 DFS codes 存 trie，匹配相关 prefix 时拒绝剪枝。
- **复杂度与保证口径**：主要是 search-space reduction 与实现，不给一般 labeled-graph FSM 的 polynomial delay；canonical-code/subgraph isomorphism 与 projection storage 仍有成本。只要“同 support”即终止的简化实现会混淆定义并可能漏其目标闭模式；异常处理不能省略。
- **优点**：给出 projected-occurrence 索引如何支持 dominance pruning 的具体设计；对 BCviz 延伸到“只枚举代表结构”尤其重要，能明确代表性到底保留 transaction support 还是所有 embeddings 的可扩展位置。
- **局限**：主要对小/中型 labeled graph transactions、ETL复用场景，不直接覆盖 huge single unlabeled graph；闭模式并不意味着 inclusion-maximal pattern，也不是 largest pattern。不同 support/closure 定义必须先对齐才能谈压缩保真或优于旧算法。

## 11. 分解与候选索引：相邻基础而非同一任务

<a id="i01"></a>

### [I01] An O(m) Algorithm for Cores Decomposition of Networks（2003，预印本）

- **类别与阅读证据**：core 分解基础，**不是全部凝聚子图枚举**。[全文](https://arxiv.org/abs/cs/0310049)；本地 `root-sources/cores.pdf`，核对 §2–5、Algorithm 1 和 §4.1 复杂度。
- **技术总结**：邻接表计算度数，用 `vert/pos/bin` 做按度桶排序；顺序移除当前最小度顶点，只对度大于当前顶点的邻居递减，通过与同桶首元素交换常数时间维护排列。输出每个顶点的 core number，隐式表示全部嵌套 k-core。原文严格总时间 O(max(m,n))，连通或忽略孤立点情形才可简写 O(m)。
- **优点**：线性时间、数组空间低、实现透明；为 clique 大小阈值和部分松弛模型提供廉价必要条件。
- **不足与边界**：给定 k 的全图最大 k-core 唯一但不一定连通，不是枚举全部 maximal clique；core 值不能当作 clique membership 充分条件。阈值/模型改变时要证明必要条件，不能用 clique 的剪枝条件直接剪 biplex。论文有小型词图示例，未覆盖现代 GPU 或动态负载。

<a id="i02"></a>

### [I02] Finding the Hierarchy of Dense Subgraphs using Nucleus Decompositions（WWW 2015）

- **来源与阅读**：[作者全文](https://arxiv.org/abs/1411.3312)、[DOI](https://doi.org/10.1145/2736277.2741640)；本地 `root-sources/nucleus.pdf`，读 §3–5、Definition 1–3、Algorithm 1、Lemma 1/2 和 §4.1。所读 arXiv v2，2015-03-09。
- **技术总结**：对固定 r<s，以 r-clique 为低阶对象、s-clique 为高阶关联；每个 r-clique 至少参与 k 个 s-clique，并通过共享 s-clique 连通的极大并集称 nucleus。先枚举基础 cliques、统计支持，逐次剥离支持最低的 r-clique；只有同一 s-clique 尚未被处理时才递减其中其它支持高于当前值的对象。由 κ 值反向建立连通层次森林，避免对每个 k 从零遍历。层次的层叠性质定义在 clique 对象集合上，投影到顶点/边仍可重叠。
- **优点**：把 core/truss 推广到高阶结构，可形成全局可视层次；不必显式输出所有任意 dense vertex subsets。不同参数能区分低阶模型无法拆开的重叠密集区域。
- **不足与边界**：nucleus 不等于 maximal clique/k-plex；基础 r/s-clique 生成及储存会变贵，复杂度需含这些中间对象，不能因最终森林紧凑就称输入线性。提高阶数通常增强局部密度，但不构成对任意问题语义质量的保证；静态层次不自动支持高效边更新。

<a id="i03"></a>

### [I03] Theoretically and Practically Efficient Parallel Nucleus Decomposition（PVLDB，2021；期次对应后续会议年度）

- **来源与阅读**：[全文](https://arxiv.org/abs/2111.10980)、[DOI](https://doi.org/10.14778/3494124.3494140)；本地 `root-sources/parallel-nucleus.pdf`；核对 §3–6、Algorithm 2、Theorem 4.2 和实验。不要与 2023 SPAA 同名摘要重复计数。
- **技术总结**：先将图定向为 O(α) 出度，α 为 arboricity，递归交集列出定长 s-clique，并在哈希表累计各 r-clique 支持。并行 bucket 每轮取最小支持集合 A，批量剥离并枚举受影响 s-clique；若一个高阶对象含 a 个同时剥离的低阶对象，使用 1/a 分摊避免重复递减。批量更新支持和桶，得到 nucleus core numbers。固定 r,s 下给出含 α、剥离轮数 ρ、log n 的 work/span 界，分别包含摊销期望及高概率前提。
- **优点**：同时分析总工作和并行深度，处理了同时剥离导致的重复计数；较只报多核加速更能说明何时可扩展。
- **不足与边界**：理论允许哈希期望成本和固定阶数，不能改写成任意 r,s 的线性工作；大 clique 中间量、桶轮数和不均衡仍影响资源。输出是 core numbers 而不是完整层次森林或全部极大凝聚子图，后者需单独算法。

<a id="i04"></a>

### [I04] Parallel Algorithms for Hierarchical Nucleus Decomposition（2024，ACM 正式记录）

- **来源与阅读**：[全文](https://arxiv.org/abs/2306.08623)、[DOI](https://doi.org/10.1145/3639287)；本地 `root-sources/hierarchical-nucleus.pdf`，所读 v2 2024-01-20；核对 §3、§5、Algorithm 1、Theorem 5.1 和实验。
- **技术总结**：先计算 r-clique 的 nucleus core number；以最高 core number 为层数，为每层建立将 r-clique 映射到 s-clique 邻居链表的哈希表。自高层向下，将链表通过 list ranking 转数组构造关联图，在每层做并行连通分量；形成父结点，并将对应代表和链表合并到低层。链表连接免于逐次复制全部成员，减少重复遍历；固定 r,s 下分析 O(mα^(s−2)) 期望工作及依赖最大 core number/剥离轮数的 span。
- **优点**：明确补足“core 数值计算”和“完整层次构建”的区别；并行连通和延迟合并为可复用层次索引提供思路。
- **不足与边界**：为层次关系存储高阶关联所需空间不能只按原图顶点计；复杂度依赖固定阶数和概率假设，span 仍受层数影响。层次不直接提供任意阈值下全体 maximal clique 的精确枚举索引，也未证明动态局部维护。

<a id="i05"></a>

### [I05] Efficient Bitruss Decomposition for Large-scale Bipartite Graphs（ICDE 2020）

- **来源与阅读**：[全文](https://arxiv.org/abs/2001.06111)、[DOI](https://doi.org/10.1109/ICDE48307.2020.00063)；本地 `root-sources/bitruss.pdf`；读定义、§IV 的 BE-Index、Algorithm 2/3、Lemma 3/6、后续 bottom-up/top-down 改进和实验。
- **技术总结**：bitruss 约束边参与的 butterfly 数。将 butterfly 按顶点优先级唯一归属到 maximal priority-obeyed bloom（2×k biclique）中；BE-Index 连接 bloom 与原始边，并保存 twin edge。删除边时，不再从全图重复发现所有 butterfly，而通过相关 bloom 更新 twin 的 k−1 个支持与其它边的一次支持。优先级 wedge 扫描构造索引，bottom-up 剥离及进一步渐进构建/压缩减少重复访问。
- **优点**：用结构压缩复用 motif 关联，展示了“无需显式存每个 butterfly”仍能精确更新支持；是压缩枚举/计数及 BCviz 未来索引方向的直接参照。
- **不足与边界**：索引空间 O(Σ_(u,v) min(d(u),d(v)))，不是普遍 O(n)；密集 motif 负载仍可能很大。它计算 bitruss 层次，不输出全部 maximal biclique；内部 bloom 是特定压缩单元，不能混同待枚举的最大 biclique。静态 peeling 中的删除更新不等于一般在线插入/删除维护协议。

<a id="i06"></a>

### [I06] Efficient (α, β)-core Computation and On-the-fly Query at Billion Scale with GPUs（2026，预印本）

- **来源与阅读**：[全文](https://arxiv.org/abs/2606.07148)；本地 `root-sources/gpu-bicore.pdf`；核对 §III–VI、Algorithm 1 GCC、Algorithm 2 GCC+、GFQ 和实验。未依据 IEEE 模板认定会议录用。
- **技术总结**：GCC 在 GPU 上先并行扫描两侧不满足 α/β 阈值的顶点，再由 warp 协作处理邻接，atomic 度递减与局部队列缓冲待剥离项。GCC+ 以普通对称 core number 提供提前排除/保留界，仅在 min(α,β) 与 max(α,β) 之间的不确定区域更新。GFQ 用并行 connectivity 标识连通分量；插入合并分量，删除时对受影响分量重新计算连通，再局部 peeling 回答指定对象是否留在 core。
- **优点**：给出 GPU CSR、warp 队列和低成本先验剪枝的实现路径；相对完整二维 core 索引，适合空间受限和临时阈值查询。
- **不足与边界**：不是 clique/biclique 枚举；GFQ 的“局部”可能是整个巨型连通分量，最坏 O(m)，不能宣传为单边更新常数成本。删除后 connectivity 重算及主机/设备数据准备应计入端到端时间；GPU 优势需相同硬件/内存条件核对。不能仅凭 core membership 推断存在指定大小 biclique。

<a id="i07"></a>

### [I07] In-depth Analysis of Densest Subgraph Discovery in a Unified Framework（2024 预印本；后有 PVLDB 正式记录）

- **来源与阅读**：[全文](https://arxiv.org/abs/2406.04738)、[DOI](https://doi.org/10.14778/3717755.3717771)；本地 `root-sources/dense-unified.pdf`；读 §2–7、Algorithm 1–5、附录的验证条件；属于边界对照与统一实验，不是 maximal enumeration 算法。
- **技术总结**：按 graph reduction → vertex weight update → candidate extract/verify 拆解无向/有向 densest subgraph 算法，比较流、凸规划和 peeling 等路线。用密度下界将无向最优解限定在相应 core 中；迭代更新辅助变量/顶点权重后提取候选，使用各算法适用的误差/最优性验证，不满足则继续。统一比较 12 个无向和 7 个有向代表算法以及组件替换。
- **优点**：提醒应分解分析削减成本、求解成本和验证成本；原型可借鉴其组件控制与失败案例，而非仅比较最终运行时间。
- **不足与边界**：无向 |E(S)|/|S| 最大化与边密度阈值 quasi-clique、最大 clique、全部 maximal dense subgraphs 是不同问题。一个目标可多项式求解，不代表相关枚举输出多项式；报告的算法数量也不是本调研逐篇另读数量。顺序优化结果不能直接代表 GPU/动态版本。

<a id="i08"></a>

### [I08] BCviz: A Linear-Space Index for Mining and Visualizing Cohesive Bipartite Subgraphs（PACMMOD 3(1), Article 16；SIGMOD 2025）

- **来源与阅读**：[DOI](https://doi.org/10.1145/3709666)；用户提供 27 页正式全文，抽取文本 `/workspace/research-notes/graph4rag/bcviz-sources/user-fulltext.txt`；核对 §3–8，特别是 Definition 3.1、Theorem 3.2/4.1/4.2/5.4、Algorithm 1–4 和 §7(5)。
- **技术总结**：以包含边的最大 biclique 大小为凝聚度，按与已排序邻居的最大边凝聚度生成顶点序列；两个数组保存排列和局部凝聚度。θ-peak intervals 定位包含足够大 biclique 的候选诱导子图，结合 core 剥离和求解器寻找 MEB/MVB/MBB。BCviz+ 用渐进 core/度界保守估计边凝聚度，保持精确最大查询；BCviz− 的 one-spot 排序省略更新，近似性不同。§7(5) 已明确说明对 MEB 索引用 θ=st 的区间和现有枚举器枚举 |S|≥s、|T|≥t 的 maximal bicliques。
- **优点**：额外索引 Θ(|U|+|V|)，将结构削减与求解器解耦；静态重复阈值查询能够摊销构建；BCviz+ 的安全上界尤其适合发展正确性可证的枚举候选索引。
- **不足与边界**：额外线性空间不包括原图、结果流或缓存；局部上界计算线性不等于全局构建线性。现有论文最大查询的实验不能直接证明枚举吞吐/延迟。BCviz− 不能继承全解召回保证；原文说明单边更新可能使整个连通分量重新排序。仅“BCviz 加一个 MBE 枚举器”已在论文提出，不宜声称新研究贡献。

## 12. 排名、共享查询与紧凑表示的近邻文献

<a id="f01"></a>

### [F01] Ranked Enumeration of Conjunctive Query Results

- **Shaleen Deep, Paraschos Koutris；LMCS21(2):14，2025；早期ICDT2021版，arxiv1902.02698**。正式PDF共33页；[arxiv](https://arxiv.org/abs/1902.02698)，[DOI](<https://doi.org/10.46298/LMCS-21(2:14)2025>)。本地 `direction-sources/RankedCQ.pdf/.txt`。
- **已读**：§2 定义2.3/2.7、§3 Theorem3.1与Alg2之后的priority-queue/cell实现、§4扩展，§5下界。不是clique专用枚举器，是数据库排名枚举近邻。
- **技术**：对full CQ固定树分解；每个bag materialize、full reducer去悬空tuple；按separator/key建优先队列。cell存局部tuple、child cell pointers与next链接，按需生成下一组合并复用子序列。ranking须与分解compatible（条件decomposable），使子树排序不因外部赋值逆转。Theorem3.1在固定query/分解和相容ranking下，预处理时间空间O(|D|^fhw)，延迟O(log|D|)，枚举额外空间O(min{k,|Q(D)|})；预处理不依赖k。哈希索引/查找采用摊销模型，不能笼统称worst-case所有操作。
- **优点**：严格区分预处理/延迟/额外空间，能在用户未知k时按需排序，不全物化结果；支持比简单sum更一般但有结构条件的ranking。
- **局限**：不是任意ranking；空间可随输出数增长到全输出量；full CQ无projection。固定k-clique可编码join，但变量数增长的“全部maximal clique”、maximality反连接与未知size不能直接套定理；树宽高也会使预处理昂贵。
- **未来方向启示**：next/可停/PQ复用已有成熟基线，想做ranked cohesive enumeration必须说明越过其适用条件的难点。

<a id="f02"></a>

### [F02] Ranked Enumeration of Join Queries with Projections

- **Shaleen Deep, Xiao Hu, Paraschos Koutris；PVLDB15(5)，2022；DOI10.14778/3510397.3510401**；[arxiv2201.05566v2](https://arxiv.org/abs/2201.05566)，本地 `direction-sources/RankedProjection.pdf/.txt`，21页；另核对[正式14页版本](https://www.vldb.org/pvldb/vol15/p1024-deep.pdf)，本地 `direction-sources/RankedProjection-formal.pdf/.txt`。
- **已读**：§2问题/排名/复杂度，§3 Alg1–3及Lemma1–4，§4 heavy/light star query算法与权衡，§5循环query分解，§6实验。
- **技术**：对有projection的join，多个完整witness可能投影到同一答案，直接枚举full join再dedup导致巨大间隔。用join tree/separator队列、cell和next指针复用子结果；Topdown循环跳过重复投影答案，rank equality后再按投影属性确定性比较，排序使相等结果邻接。一般acyclic join-project支持SUM/LEXICOGRAPHIC，正文Theorem1简介写O(|D|)预处理及O(|D|log|D|)worst-case delay；但已取得v2的§3 Lemma2与附录证明均给PreprocessAcyclic为O(|D|log|D|)，§3 lexicographic也含排序。因此稳妥引述方法细节时采用近线性预处理O(|D|log|D|)，并标明该v2正文口径不一致，不能凭猜测消掉log。Star query按join key heavy/light，将heavy投影结果物化、light部分按需枚举，并用阈值控制预处理/延迟/空间权衡。该arxivv2（正式版也保留相关正文公式）的Theorem2、Lemma5与附录对delta/epsilon的延迟和空间公式存在口径不一致，故不将其摘要式空间公式直接复制成无条件结论；可核对的机制是heavy物化大小受每属性heavy值数限制，light枚举延迟受该值频率阈值限制，完整精确阶应以校正或独立重证后的版本再审计。§5对循环query用GHD/PANDA先物化bag。
- **优点**：把重复witness直接纳入delay分析；给空间/预处理权衡并开源实现，强于“全join→distinct→sort”基线。
- **局限**：ranking族与query结构受限；projection可把延迟从full-CQ的log提升到近线性；不能当作任意graph-maximality问题通用常数延迟法。图查询若需canonical去同构，其成本另计。
- **启示**：任何“共享结果句柄+去重+排名”提案须比较/引用这条文献链，输出去重不只是工程细节。

<a id="f03"></a>

### [F03] MCI: A Maximal Clique Index for Efficient Arbitrary-Filtered Approximate Nearest Neighbor Search

- **Xiaowei Ye, Rong-Hua Li, Guoren Wang, Xubin Li；arxiv2604.22171v1，2026-04-24预印本**；[全文](https://arxiv.org/abs/2604.22171)，16页，`direction-sources/FilteredMCI2026.pdf/.txt`。PDF尚留Conference17模板，不能把模板当正式会议。
- **已读**：§2AFANNS定义、§3.1–3.3 Def3.1–3.2、Theorem3.4和3.8、Alg1，§4Alg2与seed/filter开销，§5实验。
- **技术**：先NN-Descent建稀疏k'NNG。对每点局部邻域，按最近邻距离乘alpha阈值形成稠密邻接，逐轮加倍alpha，贪心抽取足够大maximal cliques直到每个局部顶点被某clique覆盖，处理孤点/超级中心特例。全局存clique成员和vertex→clique倒排，丢原k'NNG；邻居为所属clique成员之并。query随机多seed初始化，在clique隐式邻居上做predicate过滤和beam search。Theorem3.4依赖高维pair-distance Gaussian concentration模型；不是任意数据的精确NN连通性定理。
- **优点**：面向arbitrary metadata filter，clique成员代替显式稠密邻边，结构复用可省空间、减少重复邻域扩展；无需列出全部极大团。
- **局限**：MCC是node cover，不是覆盖所有maximal-clique家族，更不是原NNG所有边的exact表示；近似beam召回须实测。§4预先计算过滤谓词可需遍历全部n点，随机seed自身也有成本，不能只看邻居扩展部分就声称端到端sublinear。构图与语义/分布依赖明显。
- **启示**：与BCviz+GraphRAG结合时的紧凑clique索引已有直接近邻，但exact enumeration与AFANNS任务不同，不应用其QPS直接比较。

<a id="f04"></a>

### [F04] Compact Representations of Geometric Bipartite Graphs via Weighted Biclique Covers

- **Aryan Esmailpour, Khoi Le, Stavros Sintos；arxiv2608.20767v1，2026-08-21预印本**；[全文](https://arxiv.org/abs/2608.20767)，19页，`direction-sources/GeometricBicliqueCover2026.pdf/.txt`。
- **已读**：§1定义、§2NP-hard reduction、§3.1/3.2 Alg1与range-tree/densest-subgraph reduction、§4模型扩展和§5实验。
- **技术**：目标是边cover，允许biclique重叠，最小 Σ(|L_i|+|R_i|)+c·#bicliques；与只算最少个数的cover或不重叠edge partition不同。把边作为set-cover universe、每个biclique作为带成本集合，理想greedy每次最大化新覆盖边/成本，但候选族指数。针对固定低维几何disk/rectangle-intersection结构用range tree生成canonical rectangles，每轮只在这些容器中解c-densest subgraph，容器保证所选两侧构成原图biclique；近似ratio再接weighted-set-cover保证。ℓ∞固定d的理论比为O(log^{d+1}n)，一般metric扩展依赖range cover参数lambda，并非任意图通用强保证。
- **优点**：明确包含每biclique固定开销，edge-cover压缩质量有理论保证；避免要求所有潜在biclique完整枚举；承认cover比partition更灵活。
- **局限**：几何embedding错误会改变目标图，不能把原图近似嵌入后宣称原图所有边无损；覆盖边也不直接枚举所有maximal biclique，overlap会给下游去重带来成本；固定小维假设不能直接搬到数百维embedding。
- **启示**：若未来用biclique cover做共享证据图/边压缩，需要把结构假设、cover成本、恢复语义与下游enum独立讲清。

<a id="f05"></a>

### [F05] Batch Hop-Constrained s-t Simple Path Query Processing in Large Graphs

- **Long Yuan, Kongzhang Hao, Xuemin Lin, Wenjie Zhang；ICDE2024；DOI10.1109/ICDE60146.2024.00201**；[arxiv2312.01424v2](https://arxiv.org/abs/2312.01424)，2024-01-09版本。本地 `direction-sources/BatchPaths2024.pdf/.txt`。
- **已读**：§II–IV Def4.1–4.7、Lemma4.1–4.2、Theorem4.1、Alg1–4，§V基线/负载/缓存与运行口径。任务是同一有向图上批量 q(s,t,k) 的所有长度≤k简单路径。
- **技术**：底层PathEnum用s正向/t反向距离下界排除不满足hop预算的扩展，并双向枚举后连接。将查询拆成单源、剩余hop预算的HC-s子问题；以BFS探索的可达顶点集合交叠构造查询相似度，层次聚类避免低共享组。同步传播子查询，在同一vertex和相同/兼容剩余hop预算处发现可共享后缀，建Query Sharing DAG；按拓扑序物化公共子路径到缓存，再连接原prefix，并检查最终路径不含重复顶点。最后一个消费者完成后释放该子查询缓存。Theorem4.1只分析共享检测 O(|Q|(n+m)) 时间、O(n²) sharing-graph空间，不是整体枚举多项式时间保证；公共路径缓存仍可能很大。
- **优点**：直接研究跨查询公共计算，不只复用一次BFS索引；将共享检测、物化、组合与生命周期释放连接成完整算法。12个真实图、最高十亿边级；对照PathEnum、相同双向BasicEnum及优化顺序变体，使收益来源较清楚。
- **局限**：主要是已知批次与路径模型，非online硬容量cache保证、不是global-maximal cohesive family。缓存释放能减少峰值但没有声明任意输入都固定B bytes；公共路径爆炸、查询不相关时检测开销可能抵消收益。默认合成100查询、k均匀4–7且预选可达(s,t)，不能直接代表无解查询或所有生产负载。输出对外是否写盘需另列，不能将内存计算wall-clock当全量落盘吞吐。
- **正文论证边界**：§IV Lemma4.1按字面声称只要 `k'≤k−dist(v,v')`，q(v,k)的每条路径都包含某条q(v',k')路径；这个条件并不强制任意v起始路径经过v'。例如v的另一分支可完全避开v'。其证明仅给一类拼接路径的包含关系，未支持这个“任意path”量词。实际Alg4是prefix确实到达共享起点时才接cache并做simple检查，应按该更具体的局部复用语义理解，不把Lemma字面升级为可剪掉其它分支的规则；这也不等于已证明实现有漏解。
- **对未来方向的限制**：不能再泛称首次图枚举多查询共享/查询支配/缓存公共子结构。拟研究BCviz方向的实质区别应是全局极大性、二维规模下界证书、规范排除集、容量受限的跨会话复用与失效协议，并据此设计新界与成本分析。

## 历史基础与未取得全文的补读项

以下是本轮已读论文的明确算法来源，尚未取得独立原文，不按全文精读计数：Bron–Kerbosch《Algorithm 457: Finding All Cliques of an Undirected Graph》（1973，DOI 10.1145/362342.362367）；Tomita–Tanaka–Takahashi《The Worst-Case Time Complexity for Generating All Maximal Cliques and Computational Experiments》（2006）；Tsukiyama 等《A New Algorithm for Generating All the Maximal Independent Sets》（1977）；Makino–Uno《New Algorithms for Enumerating All Maximal Cliques》（2004）。BK/pivot 的机制由 C01/C02/C04 和 D02 实际正文交叉核对，不冒充重新精读这些经典原文。


## 尚未取得全文的基础文献

本轮独立全文尚缺：2014《On Finding Bicliques in Bipartite Graphs: A Novel Algorithm and Its Application to the Integration of Diverse Biological Data Types》（MBEA/iMBEA，DOI 10.1186/1471-2105-15-110）；2020《Pivot-based Maximal Biclique Enumeration》；2023《Hereditary Cohesive Subgraphs Enumeration on Bipartite Graphs: The Power of Pivot-based Approaches》（DOI 10.1145/3589283）；《Efficient Personalized Maximum Biclique Search》（ICDE 2022，DOI 10.1109/ICDE53745.2022.00042）。这些是必须补读的近邻，不按本轮已全文核对计数。


## 尚未取得全文的基础文献

本轮未取得独立全文的 SIGMOD 2015/KDD 2017/AAAI 2020 早期 maximal k-plex 工作、PACMMOD 2023 defective-clique 工作，应沿 R01/R02/R06 的引用继续补齐。2025 IPEC《Efficient Enumeration of k-Plexes and k-Defective Cliques》元数据入口 DOI 10.4230/LIPIcs.IPEC.2025.22；一次替代下载实际为《Efficient Maximum k-Defective Clique Computation with Improved Time Complexity》，两者不同，未把该替代文件充作 IPEC 原文。s-club、更多有向/多层/不确定模型本轮仅列候选，不声称已全文覆盖。


## 13. 扩展发现目录：仅元数据候选

以下来自前述有限 OpenAlex 检索批次，按标题筛选并尽量去掉已在正文出现的规范标题；仅用于暴露覆盖缺口，**未逐篇读全文，不提供从题名猜测的技术优缺点**。同一工作重命名、预印本/正式版的重复仍可能存在；年份是索引记录年份，并非逐项验证过的正式会议年份。不是全部图枚举文献的穷举清单。

| 索引年份 | 候选标题 | 入口 |
|---|---|---|

| 2026 | Split-and-Reduce: A New Exact Algorithm with Tight Multi-Order Intersection Bounds for the Quasi-Clique Enumeration Problem | [入口](<https://doi.org/10.3390/math14081298>) |

| 2026 | Root-Down Exposure for Maximal Clique Enumeration on GPUs | [入口](<https://doi.org/10.1145/3774934.3786449>) |

| 2026 | Output-linear time enumeration of potential maximal cliques | [入口](<https://doi.org/10.48550/arxiv.2610.19850>) |

| 2026 | On the enumeration of potential maximal cliques | [入口](<https://hal.science/hal-05687163v1>) |

| 2026 | More Than Pivot for Maximal Clique Enumeration | [入口](<https://doi.org/10.1109/icde65706.2026.00097>) |

| 2026 | Maximal Balanced Quasi-Clique Enumeration in Signed Graphs | [入口](<https://doi.org/10.1145/3806834>) |

| 2026 | High-Modularity Graph Partitioning Through NLP Techniques and Maximal Clique Enumeration | [入口](<https://doi.org/10.48550/arxiv.2602.23948>) |

| 2026 | From Enumeration to Covering: Near-Optimal Densest P-Partite Subgraph Search over Large Heterogeneous Information Networks | [入口](<https://doi.org/10.48550/arxiv.2608.06906>) |

| 2026 | Engineering Algorithms for $$\ell $$-Isolated Maximal Clique Enumeration | [入口](<https://doi.org/10.1007/978-981-95-7127-7_36>) |

| 2026 | Efficient Simple Temporal Cycle Enumeration on Large Graphs with Lightweight Preprocessing | [入口](<https://doi.org/10.1145/3770855.3817777>) |

| 2026 | Efficient Maximal Frequent Clique Enumeration in Multilayer Networks | [入口](<https://doi.org/10.1007/978-981-95-3906-2_11>) |

| 2026 | Efficient Maximal Directed Plex Enumeration With Worst-Case Time Guarantee | [入口](<https://doi.org/10.1109/tkde.2026.3701661>) |

| 2026 | A linear-delay algorithm for enumerating strongly-connected induced subgraphs based on SSD set system | [入口](<https://doi.org/10.1016/j.jcss.2026.103833>) |

| 2025 | Yet another algorithm for maximal clique enumeration problem | [入口](<https://doi.org/10.1142/s1793830925500703>) |

| 2025 | Temporal Cycle Enumeration for Detecting Financial Fraud | [入口](<https://doi.org/10.3724/2096-7004.di.2024.0058>) |

| 2025 | Reproducibility Report for ACM SIGMOD 2024 Paper: 'Fast Maximal Quasi-clique Enumeration: A Pruning and Branching Co-Design Approach' | [入口](<https://doi.org/10.1145/3687998.3717040>) |

| 2025 | Parallel Recursive Decomposition for Maximal Clique Enumeration on Multicore Systems | [入口](<https://doi.org/10.1109/icitr69413.2025.11353511>) |

| 2025 | Minimizing the Number of Roles in Bottom-Up Role-Mining using Maximal Biclique Enumeration | [入口](<https://doi.org/10.1145/3734436.3734442>) |

| 2025 | Maximal Similar-Weight Biclique Enumeration for Large Bipartite Graphs | [入口](<https://doi.org/10.1109/icde65448.2025.00086>) |

| 2025 | Maximal $$\Delta $$-biclique enumeration in temporal bipartite graphs | [入口](<https://doi.org/10.1007/s10115-025-02545-9>) |

| 2025 | Efficient Enumeration of k-Plexes and k-Defective Cliques | [入口](<https://doi.org/10.4230/lipics.ipec.2025.22>) |

| 2025 | Efficient Antagonistic $k$k-Plex Enumeration in Signed Graphs | [入口](<https://doi.org/10.1109/tbdata.2025.3552335>) |

| 2025 | Designing Output Sensitive Algorithms for Subgraph Enumeration | [入口](<https://doi.org/10.4230/oasics.grossi.19>) |

| 2025 | DIST: Efficient k-Clique Listing via Induced Subgraph Trie | [入口](<https://doi.org/10.48550/arxiv.2502.00317>) |

| 2025 | An Efficient Seed-Initialized Algorithm for Maximal Clique Enumeration and Its Applications | [入口](<https://doi.org/10.1007/s42979-025-04271-z>) |

| 2025 | Advanced Maximal Biclique Enumeration on GPUs Using Bitmaps | [入口](<https://doi.org/10.1109/tc.2025.3566898>) |

| 2025 | Accelerating Skyline Path Enumeration with a Core Attribute Index on Multi-attribute Graphs | [入口](<https://doi.org/10.1145/3725261>) |

| 2025 | A linear delay algorithm in SD set system and its application to subgraph enumeration | [入口](<https://doi.org/10.1016/j.jcss.2025.103637>) |

| 2025 | A Linear Delay Algorithm of Enumerating Strongly-Connected Induced Subgraphs Based on SSD Set System | [入口](<https://doi.org/10.1007/978-3-031-98740-3_7>) |

| 2024 | The Complexity of Finding and Enumerating Optimal Subgraphs to Represent Spatial Correlation | [入口](<https://doi.org/10.1007/s00453-024-01256-x>) |

| 2024 | Single-exponential FPT algorithms for enumerating secluded F -free subgraphs and deleting to scattered graph classes | [入口](<https://doi.org/10.1016/j.jcss.2024.103597>) |

| 2024 | Maximal Biclique Enumeration: A Prefix Tree Based Approach | [入口](<https://doi.org/10.1109/icde60146.2024.00200>) |

| 2024 | Enumeration of Billions of Maximal Bicliques in Bipartite Graphs without Using GPUs | [入口](<https://doi.org/10.1109/sc41406.2024.00106>) |

| 2024 | Efficient k-Clique Listing: An Edge-Oriented Branching Strategy | [入口](<https://doi.org/10.1145/3639262>) |

| 2024 | Efficient Maximal Temporal Plex Enumeration | [入口](<https://doi.org/10.1109/icde60146.2024.00240>) |

| 2024 | Efficient Maximal Biplex Enumerations with Improved Worst-Case Time Guarantee | [入口](<https://doi.org/10.1145/3654938>) |

| 2024 | Efficient Maximal Biclique Enumeration on Large Signed Bipartite Graphs | [入口](<https://doi.org/10.1109/tkde.2024.3373654>) |

| 2024 | Efficient Enumeration of Maximal Cliques in Weakly Closed Graphs | [入口](<https://doi.org/10.2139/ssrn.5066441>) |

| 2024 | Efficient Distributed Hop-Constrained Path Enumeration on Large-Scale Graphs | [入口](<https://doi.org/10.1145/3639277>) |

| 2024 | Differentiating Set Intersections in Maximal Clique Enumeration by Function and Subproblem Size | [入口](<https://doi.org/10.1145/3650200.3656607>) |

| 2024 | Compression with wildcards: Enumerating specific induced subgraphs, and packing them as well | [入口](<https://doi.org/10.48550/arxiv.2412.01540>) |

| 2024 | Comparison of Algorithms and Implementations for Enumerating Support-closed Connected Induced Subgraphs | [入口](<https://doi.org/10.2197/ipsjjip.32.894>) |

| 2024 | An algorithm with a delay of $\mathcal{O}(kΔ)$ for enumerating connected induced subgraphs of size $k$ | [入口](<https://doi.org/10.48550/arxiv.2404.12559>) |

| 2024 | An Algorithm with a Delay of $\Mathcal{O}(K\Delta)$ for Enumerating Connected Induced Subgraphs of Size $K$ | [入口](<https://doi.org/10.2139/ssrn.4814047>) |

| 2024 | Accelerating Maximal Bicliques Enumeration with GPU on large scale network | [入口](<https://doi.org/10.1016/j.future.2024.07.021>) |

| 2024 | AMBEA: Aggressive Maximal Biclique Enumeration in Large Bipartite Graph Computing | [入口](<https://doi.org/10.1109/tc.2024.3441864>) |

| 2023 | Single-Exponential FPT Algorithms for Enumerating Secluded $\mathcal{F}$-Free Subgraphs and Deleting to Scattered Graph Classes | [入口](<https://doi.org/10.4230/lipics.isaac.2023.42>) |

| 2023 | Maximal Defective Clique Enumeration | [入口](<https://doi.org/10.1145/3588931>) |

| 2023 | Hereditary Cohesive Subgraphs Enumeration on Bipartite Graphs: The Power of Pivot-based Approaches | [入口](<https://doi.org/10.1145/3589283>) |

| 2023 | Fast Parallel Algorithms for Enumeration of Simple, Temporal, and Hop-constrained Cycles | [入口](<https://doi.org/10.1145/3611642>) |

| 2023 | Enumeration Complexity: Incremental Time, Delay and Space | [入口](<https://doi.org/10.48550/arxiv.2309.17042>) |

| 2023 | Enumerating All Maximal Clique-Partitions of an Undirected Graph | [入口](<https://doi.org/10.4204/eptcs.389.6>) |

| 2023 | Efficient maximal cliques enumeration in weakly closed graphs | [入口](<https://doi.org/10.48550/arxiv.2303.02390>) |

| 2023 | Efficient enumeration of maximal split subgraphs and induced sub-cographs and related classes | [入口](<https://doi.org/10.1016/j.dam.2023.10.025>) |

| 2023 | Efficient Maximal Biclique Enumeration on Large Uncertain Bipartite Graphs | [入口](<https://doi.org/10.1109/tkde.2023.3272110>) |

| 2023 | Efficient Maximal Biclique Enumeration on GPUs | [入口](<https://doi.org/10.1145/3581784.3607059>) |

| 2023 | A Linear Delay Algorithm for Enumeration of 2-Edge/Vertex-Connected Induced Subgraphs | [入口](<https://doi.org/10.1007/978-3-031-34347-6_31>) |

| 2023 | (p,q)-biclique counting and enumeration for large sparse bipartite graphs | [入口](<https://doi.org/10.1007/s00778-023-00786-0>) |

| 2022 | Rough maximal cliques enumeration in incomplete graphs based on partially-known concept learning | [入口](<https://doi.org/10.1016/j.neucom.2021.08.160>) |

| 2022 | Proximity Search for Maximal Subgraph Enumeration | [入口](<https://doi.org/10.1137/20m1375048>) |

| 2022 | Maximal Balanced Signed Biclique Enumeration in Signed Bipartite Graphs | [入口](<https://doi.org/10.1109/icde53745.2022.00187>) |

| 2022 | Index-based top k α-maximal-clique enumeration over uncertain graphs | [入口](<https://doi.org/10.1007/s11227-022-04613-1>) |

| 2022 | Fast Maximal Clique Enumeration on Uncertain Graphs: A Pivot-based Approach | [入口](<https://doi.org/10.1145/3514221.3526143>) |

| 2022 | Fairness-aware Maximal Clique Enumeration | [入口](<https://doi.org/10.1109/icde53745.2022.00024>) |

| 2022 | Edge-colored directed subgraph enumeration on the connectome | [入口](<https://doi.org/10.1038/s41598-022-15027-7>) |

| 2022 | BFS-based distributed algorithm for parallel local-directed subgraph enumeration | [入口](<https://doi.org/10.1093/comnet/cnac051>) |

| 2022 | A parallel algorithm for maximal cliques enumeration to improve hypergraph construction | [入口](<https://doi.org/10.1016/j.jocs.2022.101905>) |

| 2022 | A Polynomial Delay Algorithm for Enumerating 2-Edge-Connected Induced Subgraphs | [入口](<https://doi.org/10.1587/transinf.2021fcp0005>) |

| 2022 | A Declarative Framework for Maximal k-plex Enumeration Problems | [入口](<https://doi.org/10.65109/dwbr8683>) |

| 2021 | Spatial and Graphical Data Processing: Spatial Crowdsourcing and Quasi-Clique Enumeration | [入口](<https://doi.org/10.31274/cc-20240624-1316>) |

| 2021 | On fast enumeration of maximal cliques in large graphs | [入口](<https://doi.org/10.1016/j.eswa.2021.115915>) |

| 2021 | Maximal clique enumeration problem on graphs: status and challenges | [入口](<https://doi.org/10.1360/ssi-2021-0155>) |

| 2021 | Efficient (k, α)-Maximal-Cliques Enumeration Over Uncertain Graphs | [入口](<https://doi.org/10.1109/access.2021.3125198>) |

| 2021 | Accelerating the Bron-Kerbosch Algorithm for Maximal Clique Enumeration Using GPUs | [入口](<https://doi.org/10.1109/tpds.2021.3067053>) |

| 2021 | A Two-Phase Approach for Enumeration of Maximal $$(\varDelta , \gamma )$$-Cliques of a Temporal Network | [入口](<https://doi.org/10.1007/978-3-030-86475-0_33>) |

| 2020 | Pivot-based Maximal Biclique Enumeration | [入口](<https://doi.org/10.24963/ijcai.2020/492>) |

| 2020 | Parallelizing Maximal Clique Enumeration on Modern Manycore Processors | [入口](<https://doi.org/10.1109/ipdpsw50202.2020.00047>) |

| 2020 | Improved Overlapping Community Detection in Networks based on Maximal Cliques Enumeration | [入口](<https://doi.org/10.1016/j.procs.2020.09.081>) |

| 2020 | Enumerating connected induced subgraphs: Improved delay and experimental comparison | [入口](<https://doi.org/10.1016/j.dam.2020.04.036>) |

| 2020 | Enumerating Maximal k-Plexes with Worst-Case Time Guarantee | [入口](<https://doi.org/10.1609/aaai.v34i03.5625>) |

| 2020 | Enumerating 2-Edge-Connected Induced Subgraphs | [入口](<https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202002250494408932>) |

| 2020 | Efficient enumeration of maximal induced bicliques | [入口](<https://doi.org/10.1016/j.dam.2020.04.034>) |

| 2020 | Efficient Maximal Balanced Clique Enumeration in Signed Networks | [入口](<https://doi.org/10.1145/3366423.3380119>) |

| 2020 | Diverse Enumeration of Maximal Cliques | [入口](<https://doi.org/10.1145/3340531.3417458>) |

| 2020 | Detecting and Enumerating Small Induced Subgraphs in $c$-Closed Graphs | [入口](<https://doi.org/10.48550/arxiv.2007.12077>) |

| 2020 | Codeword Set Selection for the Error-Correcting 4b/10b Line Code with Maximum Clique Enumeration | [入口](<https://doi.org/10.1587/transfun.2019dmp0019>) |

| 2020 | Biclique: an R package for maximal biclique enumeration in bipartite graphs | [入口](<https://doi.org/10.1186/s13104-020-04955-0>) |

| 2020 | Another time-complexity analysis for the maximal clique enumeration algorithm CLIQUES | [入口](<https://ci.nii.ac.jp/naid/120006880181>) |

| 2020 | Another Time-Complexity Analysis for Maximal Clique Enumeration Algorithm CLIQUES | [入口](<https://uec.repo.nii.ac.jp/records/9653>) |

| 2020 | An Efficient Updation Approach for Enumerating Maximal $(Δ, γ)$\mbox{-}Cliques of a Temporal Network | [入口](<https://doi.org/10.48550/arxiv.2007.04411>) |

| 2019 | Sublinear-Space and Bounded-Delay Algorithms for Maximal Clique Enumeration in Graphs | [入口](<https://doi.org/10.1007/s00453-019-00656-8>) |

| 2019 | Shared-Memory Parallel Maximal Biclique Enumeration | [入口](<https://doi.org/10.1109/hipc.2019.00016>) |

| 2019 | On the Enumeration of Maximal (Δ, γ)-Cliques of a Temporal Network | [入口](<https://doi.org/10.1145/3297001.3297015>) |

| 2019 | New polynomial delay bounds for maximal subgraph enumeration by proximity search | [入口](<https://doi.org/10.1145/3313276.3316402>) |

| 2019 | Listing Maximal Subgraphs Satisfying Strongly Accessible Properties | [入口](<https://doi.org/10.1137/17m1152206>) |

| 2019 | Listing All Maximal k -Plexes in Temporal Graphs | [入口](<https://doi.org/10.1145/3325859>) |

| 2019 | Fast Maximal Clique Enumeration for Real-World Graphs | [入口](<https://doi.org/10.1007/978-3-030-18576-3_38>) |

| 2019 | Enumerating Potential Maximal Cliques via SAT and ASP | [入口](<https://doi.org/10.24963/ijcai.2019/156>) |

| 2019 | Enumerating Connected Subgraphs and Computing the Myerson and Shapley Values in Graph-Restricted Games | [入口](<https://doi.org/10.1145/3235026>) |

| 2019 | Efficient Maximal Spatial Clique Enumeration | [入口](<https://doi.org/10.1109/icde.2019.00083>) |

| 2019 | Efficient Algorithm for Maximal Biclique Enumeration on Bipartite Graphs | [入口](<https://doi.org/10.1007/978-3-030-32591-6_1>) |

| 2019 | COOMA: A Components Overlaid Mining Algorithm for Enumerating Connected Subgraphs with Common Itemsets | [入口](<https://doi.org/10.7155/jgaa.00497>) |

| 2019 | An Efficient Algorithm for Enumerating Maximal Bicliques from a Dynamically Growing Graph | [入口](<https://doi.org/10.1007/978-3-030-32591-6_35>) |

| 2019 | A memory efficient maximal clique enumeration method for sparse graphs with a parallel implementation | [入口](<https://doi.org/10.1016/j.parco.2019.05.005>) |

| 2019 | A linear delay algorithm for enumerating all connected induced subgraphs | [入口](<https://doi.org/10.1186/s12859-019-2837-y>) |

| 2018 | On the Enumeration of Maximal $(\Delta, \gamma)$-Cliques of a Temporal Network | [入口](<http://arxiv.org/abs/1804.10981>) |

| 2018 | On the Enumeration and Counting of Bicriteria Temporal Paths | [入口](<https://doi.org/10.48550/arxiv.1812.02507>) |

| 2018 | Listing k-cliques in Sparse Real-World Graphs* | [入口](<https://doi.org/10.1145/3178876.3186125>) |

| 2018 | Enumerations, Forbidden Subgraph Characterizations, and the Split-Decomposition | [入口](<https://doi.org/10.37236/6431>) |

| 2018 | Enumerating maximal cliques in link streams with durations | [入口](<https://doi.org/10.1016/j.ipl.2018.01.006>) |

| 2018 | Enumerating Top-k Quasi-Cliques | [入口](<https://doi.org/10.1109/bigdata.2018.8622352>) |

| 2018 | Enumerating Simple Paths from Connected Induced Subgraphs | [入口](<https://doi.org/10.1007/s00373-018-1966-9>) |

| 2018 | Enumerating All Subgraphs without Forbidden Induced Subgraphs via Multivalued Decision Diagrams | [入口](<https://doi.org/10.48550/arxiv.1804.03822>) |

| 2018 | Efficient Enumeration of Subgraphs and Induced Subgraphs with Bounded Girth | [入口](<https://doi.org/10.1007/978-3-319-94667-2_17>) |

| 2018 | An Output Sensitive Algorithm for Maximal Clique Enumeration in Sparse Graphs | [入口](<https://doi.org/10.4230/lipics.ipec.2017.27>) |

| 2018 | A top down approach to enumerate α -maximal cliques in uncertain graphs | [入口](<https://doi.org/10.3233/jifs-18263>) |

| 2018 | A parallel framework for maximal clique enumeration | [入口](<https://doi.org/10.1201/9781351124140-141>) |

| 2018 | A new decomposition technique for maximal clique enumeration for sparse graphs | [入口](<https://doi.org/10.1016/j.tcs.2018.10.014>) |

| 2018 | A Linear Delay Linear Space Algorithm for Enumeration of All Connected Induced Subgraphs | [入口](<https://doi.org/10.1145/3233547.3233695>) |

| 2017 | On Enumerating Maximal Bicliques of Click-Through Graph | [入口](<https://doi.org/10.26483/ijarcs.v5i1.1992>) |

| 2017 | Maximal clique enumeration with data-parallel primitives | [入口](<https://doi.org/10.1109/ldav.2017.8231847>) |

| 2017 | Fast Enumeration of Large k-Plexes | [入口](<https://doi.org/10.1145/3097983.3098031>) |

| 2017 | Efficiently enumerating all maximal cliques with bit-parallelism | [入口](<https://doi.org/10.1016/j.cor.2017.12.006>) |

| 2017 | A new algorithm for enumerating all maximal cliques | [入口](<https://doi.org/10.1109/compcomm.2017.8322922>) |

| 2017 | A linear time algorithm for maximal clique enumeration in large sparse graphs | [入口](<https://doi.org/10.1016/j.ipl.2017.05.005>) |

| 2016 | Sublinear-Space Bounded-Delay Enumeration for Massive Network Analytics: Maximal Cliques | [入口](<https://doi.org/10.4230/lipics.icalp.2016.148>) |

| 2016 | Parallelizing Maximal Clique Enumeration Over Graph Data | [入口](<https://doi.org/10.1007/978-3-319-32049-6_16>) |

| 2016 | Knowledge-Guided Maximal Clique Enumeration | [入口](<https://doi.org/10.1007/978-3-319-49586-6_43>) |

| 2016 | Enumeration of Maximal Cliques from an Uncertain Graph | [入口](<https://doi.org/10.1109/tkde.2016.2527643>) |

| 2016 | Enumerating maximal cliques in temporal graphs | [入口](<https://doi.org/10.1109/asonam.2016.7752255>) |

| 2016 | Efficient Maximal Clique Enumeration Over Graph Data | [入口](<https://doi.org/10.1007/s41019-017-0033-5>) |

| 2016 | A fast and complete algorithm for enumerating pseudo-cliques in large graphs | [入口](<https://doi.org/10.1007/s41060-016-0022-1>) |

| 2016 | A Complexity Theory for Hard Enumeration Problems | [入口](<https://doi.org/10.48550/arxiv.1610.05493>) |

| 2015 | Refined pivot selection for maximal clique enumeration in graphs | [入口](<https://doi.org/10.1016/j.tcs.2015.11.016>) |

| 2015 | Fast Parallel All-Subgraph Enumeration Using Multicore Machines | [入口](<https://doi.org/10.1155/2015/901321>) |

| 2015 | Enumerating Maximal Clique Sets with Pseudo-Clique Constraint | [入口](<https://doi.org/10.1007/978-3-319-24282-8_28>) |

| 2015 | Enumerating Maximal Clique Sets with K-plex Constraint by using Meta-cliques | [入口](<https://ci.nii.ac.jp/naid/40020491228>) |

| 2015 | Efficient Enumeration of Maximal k-Plexes | [入口](<https://doi.org/10.1145/2723372.2746478>) |

| 2014 | pbitMCE: A bit-based approach for maximal clique enumeration on multicore processors | [入口](<https://doi.org/10.1109/padsw.2014.7097844>) |

| 2014 | Viral Quasispecies Assembly via Maximal Clique Enumeration | [入口](<https://doi.org/10.1371/journal.pcbi.1003515>) |

| 2014 | The Index-Based Subgraph Matching Algorithm with General Symmetries (ISMAGS): Exploiting Symmetry for Faster Subgraph Enumeration | [入口](<https://doi.org/10.1371/journal.pone.0097896>) |

| 2014 | Subgraph Enumeration in Massive Graphs | [入口](<https://doi.org/10.48550/arxiv.1402.3444>) |

| 2014 | Overlapping Community Detection with a Maximal Clique Enumeration Method in MapReduce | [入口](<https://doi.org/10.1007/978-3-319-07776-5_38>) |

| 2014 | Maximal clique enumeration for large graphs on hadoop framework | [入口](<https://doi.org/10.1145/2567634.2567640>) |

| 2014 | Enumerating maximal bicliques in bipartite graphs with favorable degree sequences | [入口](<https://doi.org/10.1016/j.ipl.2014.02.001>) |

| 2014 | Efficiently Enumerating All Connected Induced Subgraphs of a Large Molecular Network | [入口](<https://doi.org/10.1007/978-3-319-07953-0_14>) |

| 2014 | Efficient Enumeration of all Connected Induced Subgraphs of a Large Undirected Graph | [入口](<http://rave.ohiolink.edu/etdc/view?acc_num=case1386363081>) |

| 2014 | Asymptotic lattice path enumeration using diagonals | [入口](<https://doi.org/10.48550/arxiv.1402.1230>) |

| 2014 | An Important Corollary for the Fast Solution of Dynamic Maximal Clique Enumeration Problems | [入口](<https://doi.org/10.48550/arxiv.1412.4620>) |

| 2014 | A Novel Enumeration Strategy of Maximal Bicliques from 3-Dimensional Symmetric Adjacency Matrix | [入口](<http://ceser.in/ceserp/index.php/ijai/article/view/3317>) |

| 2013 | Maximal Clique Enumeration in Finding Near Neighbourhoods | [入口](<https://doi.org/10.1007/978-3-642-36505-8_7>) |

| 2013 | Large-scale metagenomic clustering via quasi clique enumeration and read assignment ambiguity resolution | [入口](<https://doi.org/10.1109/iccabs.2013.6629239>) |

| 2013 | Hereditary biclique-Helly graphs: recognition and maximal biclique enumeration | [入口](<https://doi.org/10.46298/dmtcs.626>) |

| 2013 | A Maximal Clique Enumeration Based on Ordered Star Neighborhood for Co-location Patterns | [入口](<https://doi.org/10.1109/ihmsc.2013.46>) |

| 2012 | Fast algorithms for maximal clique enumeration with limited memory | [入口](<https://doi.org/10.1145/2339530.2339724>) |

| 2012 | Fast Maximal Cliques Enumeration in Sparse Graphs | [入口](<https://doi.org/10.1007/s00453-012-9632-8>) |

| 2012 | A novel algorithm for enumerating maximal bicliques from a symmetric matrix | [入口](<https://doi.org/10.1109/eait.2012.6407897>) |

| 2011 | The enumeration of vertex induced subgraphs with respect to the number of components | [入口](<https://doi.org/10.1016/j.ejc.2011.03.017>) |

| 2011 | Parallel Metagenomic Sequence Clustering Via Sketching and Maximal Quasi-clique Enumeration on Map-Reduce Clouds | [入口](<https://doi.org/10.1109/ipdps.2011.116>) |

| 2010 | dMaximalCliques: A Distributed Algorithm for Enumerating All Maximal Cliques and Maximal Clique Distribution | [入口](<https://doi.org/10.1109/icdmw.2010.13>) |

| 2010 | Theoretical underpinnings for maximal clique enumeration on perturbed graphs | [入口](<https://doi.org/10.1016/j.tcs.2010.03.011>) |

| 2010 | On Enumerating All Maximal Bicliques of Bipartite Graphs. | [入口](<https://dblp.uni-trier.de/db/conf/colognetwente/colognetwente2010.html#Kayaaslan10>) |

| 2010 | Fast, Nearly Optimal ISE Identification With I/O Serialization Through Maximal Clique Enumeration | [入口](<https://doi.org/10.1109/tcad.2010.2041849>) |

| 2010 | An Improved Maximal Clique Enumeration Algorithm in Co-Location Mining | [入口](<https://en.cnki.com.cn/Article_en/CJFDTOTAL-YNMZ201004022.htm>) |

| 2009 | On perturbation theory and an algorithm for maximal clique enumeration in uncertain and noisy graphs | [入口](<https://doi.org/10.1145/1610555.1610562>) |

| 2009 | Large Maximal Cliques Enumeration in Large Sparse Graphs | [入口](<http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.175.9880>) |

| 2009 | Isolation concepts for efficiently enumerating dense subgraphs | [入口](<https://doi.org/10.1016/j.tcs.2009.04.021>) |

| 2009 | Enumeration of isolated cliques and pseudo-cliques | [入口](<https://doi.org/10.1145/1597036.1597044>) |

| 2009 | A scalable, parallel algorithm for maximal clique enumeration | [入口](<https://doi.org/10.1016/j.jpdc.2009.01.003>) |

| 2009 | A Maximal Cliques Enumeration Algorithm for MBA Transaction Data* | [入口](<https://doi.org/10.1201/9781420070224.axb>) |

| 2009 | A Distributed Algorithm to Enumerate All Maximal Cliques in MapReduce | [入口](<https://doi.org/10.1109/fcst.2009.30>) |

| 2008 | Uncovering Genomic Reassortments among Influenza Strains by Enumerating Maximal Bicliques | [入口](<https://doi.org/10.1109/bibm.2008.78>) |

| 2008 | Parallel Algorithm for Enumerating Maximal Cliques in Complex Network | [入口](<https://doi.org/10.1007/978-3-540-88067-7_12>) |

| 2008 | Large maximal cliques enumeration in sparse graphs | [入口](<https://doi.org/10.1145/1458082.1458288>) |

| 2008 | Enumeration of maximal clique for mining spatial co-location patterns | [入口](<https://doi.org/10.1109/aiccsa.2008.4493526>) |

| 2008 | Enumeration aspects of maximal cliques and bicliques | [入口](<https://doi.org/10.1016/j.dam.2008.10.010>) |

| 2008 | An anytime-anywhere approach for maximal clique enumeration in social network analysis | [入口](<https://doi.org/10.1109/icsmc.2008.4811845>) |

| 2008 | A game–theoretic approach to partial clique enumeration | [入口](<https://doi.org/10.1016/j.imavis.2008.10.003>) |

| 2007 | On Enumerating Minimal Dicuts and Strongly Connected Subgraphs | [入口](<https://doi.org/10.1007/s00453-007-9074-x>) |

| 2007 | A Parallel Algorithm for Enumerating All the Maximal k-Plexes | [入口](<https://doi.org/10.1007/978-3-540-77018-3_47>) |

| 2006 | A Parallel Algorithm for Enumerating All Maximal Cliques in Complex Network | [入口](<https://doi.org/10.1109/icdmw.2006.17>) |

| 2006 | A New Algorithm for Enumerating All Maximal Cliques in Complex Network | [入口](<https://doi.org/10.1007/11811305_67>) |

| 2004 | New Algorithms for Enumerating All Maximal Cliques | [入口](<https://doi.org/10.1007/978-3-540-27810-8_23>) |

| 2004 | Maximal Clique Enumeration and Related Tools for Microarray Data Analysis | [入口](<https://trace.tennessee.edu/cgi/viewcontent.cgi?article=6251&context=utk_gradthes>) |

| 2001 | Enumerating all connected maximal common subgraphs in two graphs | [入口](<https://doi.org/10.1016/s0304-3975(00)00286-3>) |

| 1996 | Local multiple alignment via subgraph enumeration | [入口](<https://doi.org/10.1016/s0166-218x(96)00072-8>) |

| 1973 | The Enumeration of Maximal Cliques of Large Graphs | [入口](<https://doi.org/10.1137/0202001>) |


本表 187 条发现记录不计为已完成正文精读；正文编号也包含明确标注未取得全文的补读项，应按各条证据等级理解。

## 14. 核对结论与后续补读

1. “新的枚举算法”必须说明输出对象、所有权/去重、极大性判定、复杂度与工作空间；计数与全解输出需分开。
2. 研究不能仅停在摘要：正文记录了具体 pivot/closure、剪枝必要条件、状态与排除集合、证书恢复和实验输出口径；每条优点/局限限定在实际方法与版本。
3. BCviz 原文已经提出候选区间加枚举器；未来工作需要超出该直接组合。动态/共享/压缩方向也已有近邻工作，见 [future-enumeration.md](future-enumeration.md)。
4. 仍需补全受访问限制的经典原文和所有候选的人工筛选；不能据此保证没有更近竞争论文。投稿前要更新 2026 年新增与后续正式版本，并核对实现和数据许可证。
