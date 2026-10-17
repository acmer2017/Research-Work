# Graph for RAG 论文分类与算法调研（2010—2026-10-16）

本报告整理 **74 篇分类条目**：包含 GraphRAG 主干方法、历史图问答与路径推理、非图 RAG 对照、综述，以及 BCviz。具体方法按全文方法、算法和相应实验核对；综述按分类章节核对，不声称逐篇读完其全部参考文献。另附元数据候选目录，明确区别于正文精读。

“齐全”按可复核的覆盖过程推进，不能保证截至今日所有语言、所有领域、尚未索引的预印本均无遗漏。2010—2019 年工作属于技术前史，不能倒称当时已有现代 LLM GraphRAG。2026 年条目包括预印本，预印本年份不代表会议录用。本文比较的是语义图、证据图和层次图；仅使用 HNSW 等 ANN 图，不算语义图增强。

## 阅读与检索口径

检索入口包括三篇综述的引用与维护列表、作者仓库及正式论文站点，并对 OpenAlex 以 `GraphRAG`、`graph retrieval augmented generation`、`knowledge graph retrieval augmented generation`、`temporal GraphRAG` 四组检索做补充；时间过滤 2010-01-01—2026-10-16，每组只取前 100 条，因此**不是数据库全量穷举**。该批次规范化标题去重得到 308 条元数据，含相关性较弱记录；下方候选表再做标题筛选。API 的总命中数不能当作本领域论文数量。

证据优先级：正式全文/作者全文 > 正式出版元数据 > 作者代码与 README > 综述和索引元数据。已读正文中，“实证”仅指该论文设置，“机制风险/推断”不冒充已测结果；不能横比不同生成器、token 预算和数据划分的分数。论文版本、实际阅读章节和原文链接随条目给出。

本地下载全文及抽取文本统一位于 `/workspace/research-notes/graph4rag/`。条目中反引号标出的相对文件路径均以该目录为根，便于当前环境复核；长期使用请以原文 URL 为准，本地缓存未纳入仓库。BCviz 使用本次用户上传正式 PDF。未重跑各论文训练和实验。

## 分类框架与阅读路线

| 类别 | 图的作用 | 关键算法 | 条目 |
|---|---|---|---|
| 历史路径推理 | 在给定 KG 中寻找关系链 | PRA、RL 路径搜索 | H00–H03 |
| 早期图问答 | 融合文本与实体、传播证据 | GNN、迭代拉取、层次注意力 | H04–H13 |
| 无图对照 | 独立段落检索和生成 | 双塔、隐变量边缘化 | B01–B03 |
| 现代主干 | 摘要层次、实体索引、扩散、证据组织 | Leiden、PPR、一跳扩展 | C01–C05 |
| KG 路径/子图检索 | 有约束地查找答案证据 | beam、PCST、MLP/GNN、关系计划 | K01–K14 |
| 文本图与物理索引 | 减少构图和候选访问成本 | 二部图、层次索引、图重排 | S01–S08 |
| 新结构与适应性检索 | 树、超图、按需推理、记忆 | 聚类、流剪枝、查询规划 | N01–N07 |
| 专业领域与 agent | 约束知识使用和多轮检索 | schema、工具调用、RL、路由 | X01–X09 |
| 近期交叉方向 | 模块化、core、最小子图、时间、溯源 | 算子组合、core 层次、IB、双时态 | F01–F06 |
| 评测与综述 | 控制变量、覆盖问题类型 | 基准、统一实现、分类 | N08–N11、V01–V03 |
| BCviz 基础 | 凝聚结构的候选削减 | 排序、peak interval、安全上界 | BC01 |

建议先读 C01/C03/C04 → S04/N03/N02 → K04/K06/K13 → F02/F03/F05/F06 → N11/X08，最后阅读研究展望。不要只按系统名判断创新：实体—片段二部图、覆盖打包、core 层次、双时态存储都已有非常接近的工作。

## 关键方法横向比较

| 方法 | 检索单元/机制 | 训练或主要离线代价 | 对 BCviz 后续研究的约束 |
|---|---|---|---|
| Microsoft GraphRAG | 社区报告、map-reduce | LLM 抽取与多层报告 | 全局概括收益不等于多跳事实检索收益 |
| LightRAG | 实体/关系向量命中与邻居 | LLM 抽取、描述 | 追加合并不等于版本一致性 |
| HippoRAG 1/2 | PPR → 原始段落 | OpenIE/实体与片段索引 | 二部关联和度校正已存在 |
| KG²RAG | 向量种子后关系扩展/组织 | KG 抽取 | 已有检索后结构化组织 |
| G-Retriever | PCST 子图、图与文本输入 | 图编码器与适配训练 | prize-cost 选择已有，非严格 token 最优 |
| SubgraphRAG | 三元组独立评分和距离特征 | 轻量 MLP | 简单检索器必须作为强基线 |
| GFM-RAG | query-conditioned GNN → 文档 | 图基础模型训练 | 必须区分索引收益与学习收益 |
| KET-RAG | KG skeleton + keyword–subchunk 二部图 | 选择性抽取 | BCviz 二部图方案最直接对照 |
| E²GraphRAG | 实体交集 postings、覆盖排序 | 轻量图索引 | 交集与覆盖本身不足以构成创新 |
| LinearRAG/MiniRAG | 实体–片段关联和轻量检索 | 较少关系抽取 | 不抽关系和低成本构图已有 |
| HyperGraphRAG | 多元事实超边、关联二部图 | n 元事实抽取 | 使用二部表示不构成首创 |
| Core-based Hierarchies | core 层次、报告 token 分配 | 剥离、摘要 | “凝聚子图 + GraphRAG”已有 |
| LineageRAG | demand–passage 覆盖、原文 span | LLM 选证与抽取 | 证据覆盖与溯源已有 |
| MemGraphRAG/T-GRAG | 记忆冲突、时态图检索 | 更新分析与代理 | 不能声称首个动态/时序方法 |
| post-graph-rag | PostgreSQL 双时态、as-of 检索 | 数据维护、派生摘要 | 新机会在全通道版本一致和物理维护 |
| LEGO/DIGIMON | 模块化算子与对比框架 | 统一管线 | 单纯拆模块不是新贡献 |
| PolyG/GraphRAG-Router | 查询结构/后端路由 | LLM 规划或 RL | 单纯自适应路由不是新贡献 |
| RAGSearch | 固定 agent、更换检索后端 | 多轮检索成本 | 需强 agentic text RAG 对照 |


## 历史：事实排序与路径推理

<a id="h00"></a>

### [H00] FactRank: Random Walks on a Web of Facts（2010，COLING）

- **来源与阅读范围**：https://aclanthology.org/C10-1057/；全文 https://aclanthology.org/C10-1057.pdf；本地 `research-notes/graph4rag/history-evidence/factrank2010.pdf`。已读 §2–§4，特别是 §3.1–3.4 的图表示、随机游走及排序融合，§4.2 的稀疏性误差分析；venue 由正式论文首页确认。
- **类别**：历史前身；基于图的事实质量评估和排序，不是问答生成系统。
- **技术总结**：把“事实”而非实体作为节点：如果两个事实在相容的关系参数类型上共享同一参数值，就连接两个事实，若干共享参数类型的关系组成一个 fact farm。算法先运行普通 PageRank 对照，再分别引入邻居事实的抽取置信度（Dst）、边两端置信度平均值（Avg），或者置信度与连接到的不同关系种类比例的组合（Nde），使“有多种关系支持的事实”得到不同传播权重。随机游走排名与原始抽取器排名再作平均或加权融合（R-Avg/R-Wgt），孤立事实保留原排名，避免仅因抽取覆盖不足便被压低。实验由五亿网页语料的关系抽取结果产生十万以上事实，再对电影领域关系作人工抽样评估，比较平均精度、不同图规模、不同关系数量和 top-rank 质量。
- **优点**：在关系抽取之外明确建模跨事实的相互支持，图传播和已有抽取器可组合；对孤立节点的处理意识到“不被支持”并不等于“错误”。§4.2 报告原始 PageRank 不如结合置信度/原始排序的变体，说明图结构本身并不足够。
- **局限**：**论文实证/自述**：作者明确说小规模人工金标准使部分平均精度提升未达到统计显著，director-of 的收益较弱；稀疏图削弱 Nde 和整体排序收益。**本综述推断**：共享高频参数、重复转载或共谋错误也能制造高连接度，因而这种支持强度不是事实真实性证明；人工设定的关系参数类型也限制开放域迁移。
- **对 BCviz 的启发**：可以把实体—证据二部图中的内聚结构作为“待检查的相互支持群”，但应保留独立来源、多样性和冲突信号，不能把高内聚直接当成正确。

<a id="h01"></a>

### [H01] Random Walk Inference and Learning in A Large Scale Knowledge Base（2011，EMNLP；PRA 的 KB 推理扩展）

- **来源与阅读范围**：https://aclanthology.org/D11-1049/；全文 https://aclanthology.org/D11-1049.pdf；本地 `research-notes/graph4rag/history-evidence/pra2011.pdf`。已读 §1.3、§2.1–2.4、§3–§4，含公式 4–6、表 1–4 与人工评估偏差讨论；venue 由正式首页确认。
- **类别**：历史前身；路径约束随机游走、关系检索/链接预测。
- **技术总结**：对查询实体 s 和候选实体 e，以关系类型序列 P 约束游走，只沿下一指定关系的出边分配概率，得到到达 e 的概率 h(s,P,e)，每个路径类型因此成为一个可解释的排名特征；多个路径概率通过带正则的逻辑回归组合，针对每个待预测关系学习排名。为避免关系种类和路径长度造成指数枚举，路径生成仅保留被至少 α 比例训练查询支持、且曾到达某个训练目标的路径，实验 α=0.01、最大长度通常为 3，并用 L1 正则进一步稀疏化。另用低方差抽样替代独立采样的随机游走近似，使有限粒子在概率区间更均匀地覆盖分支。NELL 实验在约五十万事实、48 种关系的正反两个方向共 96 个任务上比较 RWR、PRA 和 N-FOIL，并额外人工检查未见查询的预测事实。
- **优点**：保留边类型序列的语义，既能利用精确的关系链，也能学习类型先验、别名和局部邻域特征；路径组合比只保留少数高精度 Horn 规则具有更高覆盖，并能处理非函数型关系。表 1 显示长度 3 的平均候选路径从 15,376 经支持度、目标可达性和 L1 筛选缩到约 63 条，提供具体的结构剪枝思路。
- **局限**：**论文实证/自述**：长度 4 训练耗时约为长度 3 的 4–5 倍；交叉验证把未记录事实当负例，与不完备 KB 不一致；众包与作者人工金标准仅 74% 一致且有流行对象偏差。**推断**：固定短路径和逐关系模型难直接支持自然语言开放生成、跨文档证据冲突及全局聚合，路径得分也不等于可验证逻辑蕴含。
- **对 BCviz 的启发**：将“支持度剪枝＋结构索引”视作可复用思想，研究是否能对二部图证据集合给出更紧的候选上界，而不是只替换游走实现。

<a id="h02"></a>

### [H02] DeepPath: A Reinforcement Learning Method for Knowledge Graph Reasoning（2017，EMNLP）

- **来源与阅读范围**：https://aclanthology.org/D17-1060/；全文 https://aclanthology.org/D17-1060.pdf；本地 `research-notes/graph4rag/history-evidence/deeppath.pdf`。已读 §3.1–3.3、算法 1–2、§4.1–4.3，含初始化、奖励、双向验证和路径数量分析；venue 由正式首页确认。
- **类别**：历史前身；强化学习路径发现与知识图谱链接/事实预测。
- **技术总结**：训练时给定源、目标实体对，状态拼接当前实体嵌入和“目标减当前”的向量差，动作空间是全图关系类型，用两层 MLP 的随机策略逐步扩展关系链。先以随机中间节点连接的两段 BFS 路径作模仿学习热启动，再用 REINFORCE 优化由终点成功、路径长度倒数、与已有路径嵌入的负余弦相似度组成的奖励，分别鼓励正确、短而多样的路径；无效动作受到负奖励且保持原位。找到的路径并不直接生成答案，而作为关系规则候选：在待判断实体对之间用双向路径约束搜索核实是否存在，从较小的前沿扩展，产生二值路径特征，再训练类似 PRA 的线性预测器。实验删除目标关系及其逆关系避免直接泄漏，在 FB15K-237 的 20 个关系和 NELL-995 的 12 个任务评估 MAP。
- **优点**：把路径的相关性、代价和多样性显式写入目标；相比 PRA，论文表 4 报告平均只使用约 20.3 条而非 137.2 条路径，并保留可检查的关系链。双向验证减轻了逆向关系连接大量实体时的前沿爆炸。
- **局限**：**论文实证/自述**：直接从巨大动作空间随机探索难以收敛，需要 BFS 热启动；filmWrittenBy 仅找到四种路径，效果较差，说明稀疏证据是硬瓶颈。**从算法直接可见**：训练状态知道目标实体，且模型按关系分别训练，不能原样当作“未知答案”的开放问答检索器；候选路径存在并不证明因果或逻辑有效。**推断**：路径多样性采用关系嵌入求和，会丢失顺序信息，与生成答案所需的证据覆盖度也不完全等价。

<a id="h03"></a>

### [H03] Go for a Walk and Arrive at the Answer: Reasoning Over Paths in Knowledge Bases Using Reinforcement Learning（MINERVA；2018，ICLR）

- **来源与阅读范围**：https://arxiv.org/abs/1711.05851；全文 https://arxiv.org/pdf/1711.05851；本地 `research-notes/graph4rag/history-evidence/minerva.pdf`。已读 §2.1–2.3、§3.1–3.2，含表 2–4 和 FB15K-237 关系类型/路径重复率分析；下载版本首页明确“Published as a conference paper at ICLR 2018”（首次 arXiv 为 2017）。
- **类别**：历史前身；查询条件化的图导航和实体答案检索。
- **技术总结**：输入为 (起点实体, 查询关系, ?)，把图导航表述成有限时域部分可观测决策过程；与 DeepPath 不同，答案仅用于环境计算奖励，并不进入 agent 的观测。动作是当前节点实际存在的出边，表示同时包含关系和目标实体嵌入；LSTM 编码已访问实体和动作历史，再结合当前实体及查询关系向量，对可选出边打分，加入逆边与 NO-OP 以允许撤销决策和提前到达后停留。训练用终点命中奖励、REINFORCE、多次 rollout、滑动平均 baseline 及熵正则，不需要先挖路径或监督路径热启动；推理用 beam search，对到达实体按轨迹概率排名。论文在 COUNTRIES、UMLS、KINSHIP、WN18RR、FB15K-237、NELL-995 等不同图特性上比较嵌入法、逻辑法及随机路径聚合对照。
- **优点**：把“沿什么路径走”与查询关联，避免对全部实体逐对评分；单一策略跨关系共享训练信息，路径可作预测来源的检查入口。全文明确区分已知两端事实验证和未知终点问答，适合解释现代 agentic 图搜索的历史来源。
- **局限**：**论文实证/自述**：FB15K-237 上落后于较强嵌入模型，作者分析与一对多关系比例较高、可重复路径类型稀少及标准单目标评估有关；若答案不可达则无法输出，NELL 中未见实体样本也被排除。**推断**：稀疏终点奖励及 beam 宽度使长路径探索有覆盖损失；路径可读并不保证它是忠实的证明，且任务尚未处理长文本生成、引用或文档图构建。

## 历史：文本与图的联合问答

<a id="h04"></a>

### [H04] GRAFT-Net — Open Domain Question Answering Using Early Fusion of Knowledge Bases and Text

- **年份与发表状态**：2018，EMNLP 2018。题名已核对全文首页，venue 已核对 ACL Anthology 会议目录；论文中的模型名为 GRAFT-Net / GRAFT-Nets。
- **原文与全文证据**：[正式论文页](https://aclanthology.org/D18-1455/)；[已阅读 PDF](https://arxiv.org/pdf/1809.00782)；本地 `/workspace/research-notes/graph4rag/history-evidence/graftnet.pdf`、同名 `.txt`。**阅读范围**：§2 任务及子图检索，§3.1–3.5 异构更新、问题条件化、答案分类及 fact dropout，§5.1–5.5 数据集、主要结果、消融与失败原因。
- **类别与 GraphRAG 关系**：图检索及 KB–文本早期融合的历史前身；是实体答案抽取/分类模型，而不是今天的 LLM 自由文本生成 RAG。
- **技术总结**：先分别检索 KB 与文本，再把它们组成问题相关的异构子图：对问题链接得到的种子实体运行关系名称与问题词向量相似度加权的 Personalized PageRank，保留 top-E 实体；文本端先取相关 Wikipedia 文章，再以 Lucene 取句子，把实体与其在句中的具体 mention 位置连接。实体节点用定长向量，文本节点保留逐 token 的 LSTM 表征，因此实体更新可聚合关系邻居与所有 mention 的状态，文本更新则将实体状态注入对应 token 后再运行 LSTM，这比把整篇文本压成单一节点向量更精细。各层除向量外还维护从问题种子扩散的标量 PageRank 状态，用它和问题条件化的关系注意力调节消息传播，逐层沿与问题有关的路径扩展影响；关系变换采用关系向量加 FFN，降低逐关系矩阵的显存代价。最终对每个候选实体做 sigmoid 二分类，以答案实体集合的交叉熵监督，训练中随机丢弃 KB 边，防止模型过度依赖容易读取的结构化事实。
- **优点与实证**：在 KB 完整度 10%/30%/50%/100% 的控制实验中，显式保留实体、关系与文本之间连接有助于把两种来源的证据组合起来；论文 §5.3 显示 early fusion 的收益比独立 KB/text 模型的 late fusion 更稳定。异构更新、位置级实体链接、种子引导传播均有消融支持。WebQuestionsSP 的 KB+文本子图答案召回达到 94.0%，WikiMovies-10K 达到 99.6%；这些是检索候选覆盖率，不应当写成最终问答正确率。
- **局限**：**论文实证**：KB-only WebQuestionsSP 的子图召回仅 90.2%，把漏掉的正确答案补入后 F1 增加 4.8 个百分点；对所有问题采用统一答案阈值，以及处理“first”等排序约束不足，也是作者识别的失败来源。**方法推断**：一次性启发式检索会把未进入子图的证据永久排除，实体链接错误也会切断跨文档传播；固定层数限制可表达的路径长度，神经注意力不能替代具有形式语义的聚合、比较或否定操作。适合借鉴其实体–句子关联建模，但不能据此声称任意图结构或高密度子图都能带来生成质量提升。

<a id="h05"></a>

### [H05] PullNet — Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text

- **年份与发表状态**：2019，EMNLP-IJCNLP 2019。题名核对全文，venue 与正式记录核对 [ACL Anthology](https://aclanthology.org/D19-1242/)。
- **原文与全文证据**：[PDF](https://arxiv.org/pdf/1904.09537)；本地 `/workspace/research-notes/graph4rag/history-evidence/pullnet.pdf`、同名 `.txt`。**阅读范围**：§3.1–3.3、Algorithm 1、§4.1–4.6，尤其弱监督来源、各数据源结果与 wall-clock 训练实验。
- **类别与 GraphRAG 关系**：问题驱动的迭代子图检索历史前身；可看作“检索—图推理—继续检索”而非固定 top-k 检索，但输出仍是实体选择。
- **技术总结**：问题子图包含实体节点、单句文本节点和 KB fact 节点；fact 节点分别连接头尾实体，文本节点连接其实体 mention，初始图只有问题实体。每一轮用 GRAFT-Net 式图 CNN 判断哪些实体值得扩展，对被选实体执行两类 pull：从已实体链接的语料中检索与该实体关联且与问题 IDF 相似度高的句子，以及检索其主语/宾语邻接事实；事实按关系向量与问题 LSTM 向量内积的 sigmoid 得分排序。加入新事实、文本、实体及与旧节点的连边后重复该过程，最终再用独立输出头选择答案实体，从而将检索预算集中在模型认为有用的前沿。训练不直接给出人工推理链，而从训练问题实体与答案实体之间的 KB 最短路径构造中间实体和关系标签；使用 teacher forcing，在某轮没有检索到应出现的中间实体时仍将其加入图，因此“只用 QA 对弱监督”不等于完全不借助完整 KB 路径信息。
- **优点与实证**：§4.6 的检索曲线显示，相比 PageRank-Nibble 的一次性检索，PullNet 能以更少实体取得更高答案召回；多轮文本检索也优于单轮 IDF 检索。MetaQA 3-hop 的 50% KB+文本设置中 Hits@1 为 85.2%，对应重跑的 GraftNet 为 66.4%；Complex WebQuestions dev 的 KB-only 为 47.2%，GraftNet 为 32.8%。这些证据支持“在复杂问题中学习扩展位置”这一机制，而不是单纯增大最终子图。
- **局限**：**论文明确说明**：不完整 KB 实验的训练最短路径仍来自完整 KB，所以训练监督强于真实只有不完整 KB 的场景；把该实验直接解释成不依赖完整图监督是不准确的。**论文实证**：Complex WebQuestions 上一个训练 epoch 约 114 分钟，GraftNet 约 31.9 分钟；交错运行检索和学习带来实际训练成本。WebQuestionsSP text-only 与既有 GraftNet 大体相当甚至略低，收益并非所有设置一致。**方法推断**：答案限制为 KB 实体，文本检索依赖实体链接和词法匹配，最短路径伪标签可能压低非最短但更可靠的证据路径；固定轮数与扩展预算会遗漏需要更深或并行分支的查询。

<a id="h06"></a>

### [H06] DrKIT — Differentiable Reasoning over a Virtual Knowledge Base

- **年份与发表状态**：2020，ICLR 2020；PDF 首页明确写有 “Published as a conference paper at ICLR 2020”。
- **原文与全文证据**：[PDF](https://arxiv.org/pdf/2002.10640)；本地 `/workspace/research-notes/graph4rag/history-evidence/drkit.pdf`、同名 `.txt`。**阅读范围**：§2.1–2.3 的方程 1–6、稀疏算子复杂度、索引预训练；§3.1–3.3 的 MetaQA、WikiData slot-filling、HotpotQA 检索结果与消融。
- **类别与 GraphRAG 关系**：把文本索引当作虚拟知识图谱的检索与软图遍历前身，尤其适合研究索引与查询执行；本身不是语言生成模型。
- **技术总结**：系统先做 corpus-wide 实体链接，为每个 mention 保存由 BERT 编码起止 token 后投影得到的查询无关向量，同时建立实体到共现 mention 的稀疏矩阵 A，以及 mention 到规范实体的归并矩阵 B。每一跳把当前实体概率分布经 A 扩展到候选 mention，使用由问题及当前实体加权词向量组成的稠密查询执行最大内积检索 MIPS，再将稀疏扩展分数和 top-K mention 分数逐元素相乘，按 B 聚合回实体分布；这个 textual follow 操作可递归模拟关系路径。top-K 截断使每跳活跃实体至多 K，避免分支数随跳数爆炸，论文给出约 Õ(K·max(K,μ)+Kp+p²) 的查询复杂度与 O(μ|E|+p|M|) 的索引空间，其中 μ 是每实体最多关联 mention 数、p 是向量维度。索引编码器先用 KB–文本远程监督 slot-filling 和共享实体/共享关系/随机负例预训练并冻结，之后在固定索引上用最终答案交叉熵训练多跳问题编码；因此端到端可微指的是该受限检索计算链及候选得分，并不意味着离散 ANN 候选选择或全库 mention 表征每步共同更新。
- **优点与实证**：文本不必先抽取成固定关系 schema，且昂贵的文档编码移到离线；稀疏邻接约束和向量相似度互补。MetaQA text-only 3-hop Hits@1 为 87.6%，PullNet 为 78.2%；同一论文的六核 CPU 查询实验中对 PullNet 的速度收益约 5–15 倍，应引用这个具体设置而非把摘要中宽泛的倍率当普适结论。移除 TF-IDF 约束后 3-hop 下降到 48.8%，直接使用未做任务预训练的 BERT 索引为 55.5%，显示结构候选约束和索引训练均是关键。WikiData 的训练/测试使用不同文章与实体集合，也比仅在固定小图上测试更接近索引迁移问题。
- **局限**：**论文明确说明**：若更新 mention 编码器就需重新编码全库，因此采用阶段训练并冻结索引；HotpotQA 的答案可能不是实体，所以 DrKIT 在该任务作为段落检索器，需另接阅读理解模块。**论文实证**：人工分析 100 个答对的 2-hop 问题，有 17 个在第一跳直接得到最终类别答案再复制到第二跳，说明多跳计算轨迹不自动构成忠实解释。**方法推断**：实体链接与 co-occurrence 过滤会限制召回，固定 K/μ 形成效率与覆盖率折中；空间对 mention 总数线性但向量常数大，不等价于 BCviz 意义上的纯拓扑轻量索引，更没有给出动态更新或磁盘 I/O 的维护保证。

<a id="h07"></a>

### [H07] CogQA — Cognitive Graph for Multi-Hop Reading Comprehension at Scale

- **年份与发表状态**：2019，ACL 2019，pp. 2694–2703；正确 PDF 首页及页脚已核对。
- **原文与全文证据**：[正式论文页](https://aclanthology.org/P19-1259/)；[正确 PDF](https://aclanthology.org/P19-1259.pdf)；本地 `/workspace/research-notes/graph4rag/history-evidence/cogqa-correct.pdf`、`cogqa-correct-clean.txt`。**证据纠错**：原 `sources.json` 的 `cogqa=https://arxiv.org/pdf/1905.05448` 实际指向热弹性材料与注塑逆向设计论文，不能作为 CogQA 引用；本文已重新下载 ACL 原文。**阅读范围**：§2 与 Algorithm 1、§3.1–3.4、§4.1–4.4 的训练图、预测器、消融、类型分析和案例。
- **类别与 GraphRAG 关系**：检索与推理相互反馈、在线构造认知图的历史前身；是 BERT+GNN 的抽取式多跳 QA。
- **技术总结**：认知图的有向节点分为可继续查找 Wikipedia 导言段落的实体/hop 节点，以及候选答案节点；边表示读取父节点段落后发现下一实体或答案，而非预先给定的 KG 事实关系。System 1 用 BERT 读取 `[CLS] Question [SEP] clues [SEP] Paragraph`，分开预测 next-hop 与 answer 两组起止位置，并把 [CLS] 的答案起点概率用作负阈值，过滤不相关段落中的候选；其倒数第三层 [CLS] 状态作为节点语义表示。System 2 汇集前驱中提到当前实体的原句作为 clues，并通过归一化有向邻接上的 GNN 消息传递更新节点，新的前驱边可使节点重新进入 frontier；实现中最终图建好后统一多轮更新比逐节点异步更新更高效而效果接近。训练从 HotpotQA 支持事实通过模糊实体匹配构建 gold reasoning graph，再加入负 hop 和负答案节点，以 span 交叉熵和答案节点分类共同训练；普通实体/跨度答案与比较、yes/no 问题使用不同预测头。
- **优点与实证**：显式保留实体发现顺序及支持句，能展示树、DAG 和带环证据图，避免单轮初检无法发现仅在后续线索中出现的页面。HotpotQA fullwiki 测试集 Joint F1 为 34.9、Answer F1 为 48.9，均是当年该系统版本与当时基线比较的结果；移除 System 2 后性能下降，初始实体来源消融也表明收益不只来自更好的第一轮检索。对图的前驱句进行追溯，对今天设计可检验的检索执行记录有直接启发。
- **局限**：**论文实证**：比较/一般疑问句没有观察到同样的改进，作者将其归因于这些判断所需证据难从支持事实构造，监督不足。**方法推断**：训练依赖支持事实与其派生图，不能当作无需推理监督的系统；节点扩展调用 BERT 读取段落，对复杂前沿的成本仍会增长。“图上有一条可展示路径”也不保证答案真由该路径因果决定，论文的联合 EM/F1 和案例展示只能支持证据覆盖与一致性，不能直接证明解释忠实性；Wikipedia 标题索引及导言段落假设限制向普通企业文档迁移。

<a id="h08"></a>

### [H08] DFGN — Dynamically Fused Graph Network for Multi-hop Reasoning

- **年份与发表状态**：2019，ACL 2019；题名核对全文，[正式会议记录](https://aclanthology.org/P19-1617/) 已核对。预印本与正式会议记录的作者顺序存在差异，引用时应采用所选版本的书目记录。
- **原文与全文证据**：[PDF](https://arxiv.org/pdf/1905.06933)；本地 `/workspace/research-notes/graph4rag/history-evidence/dfgn.pdf`、`dfgn-clean.txt`。**阅读范围**：§3.1–3.5、方程 1–15，§4.1–4.3，实体图不完整性与 ESP 解释路径评估。
- **类别与 GraphRAG 关系**：检索后阅读阶段的实体图–文本双向融合历史前身；主要研究给定候选段落后的图推理，不能与面向全库检索的 GraphRAG 直接等同。
- **技术总结**：首先用 BERT 段落分类器筛选输入候选；命名实体 mention 成为图节点，同句实体、同表面字符串实体、段落标题中心实体与段内实体之间分别连边，不要求已有全球知识图谱。BERT 加 bi-attention 编码问题和上下文，每个 fusion block 先用 token–entity 二值映射矩阵做 mean-max pooling 得到实体表征，再依据当前问题与实体的注意力生成 sigmoid soft mask，抑制与当前推理步骤无关的实体传播。随后进行图注意力消息传递，使用更新后的实体状态通过 bi-attention 更新问题表示，再把实体状态映射回 token 并经 LSTM 更新文本，形成 Doc2Graph→graph→Graph2Doc 的闭环，故最终答案不必是 NER 识别出的实体。模型联合预测支持句、答案起止位置和答案类型，另用问题种子实体及其 BFS 邻域构造弱监督 mask，通过二元交叉熵约束分步传播。
- **优点与实证**：把图节点级推理重新注入 token 可以保留非实体答案以及词序、限定词等文本细节；图的 soft mask 随推理步骤变化，避免所有实体无差别参与每一跳。HotpotQA distractor 的正式表 1 中，原版 Joint F1 为 58.23，改用 BERT NER 后为 59.82；消融去掉 entity-to-token 流、query update、BFS supervision 等均会降低 QA 指标。论文还将各步 mask 与边注意力乘积定义为路径得分，以支持句覆盖率而非仅图示来评估推理路径。
- **局限**：**论文明确范围**：只评估 HotpotQA distractor（给定 10 篇候选），未评估 fullwiki；“可在开放语料库检索有用证据”并非该实验验证的能力。**论文实证**：开发集 31.3% 的样本至少一个支持句中没有识别出的实体，因此无法通过实体图完成完整推理，后续 ESP 路径分析只在剩余 68.7% 样本上进行，报告时必须保留这一条件。**方法推断**：同名连接和共现关系并非语义蕴涵边，BFS 伪监督也不等于真实推理步骤；soft mask/注意力路径可以辅助检查，但不能当作严格可验证的逻辑证明。

<a id="h09"></a>

### [H09] HGN — Hierarchical Graph Network for Multi-hop Question Answering

- **年份与发表状态**：2019 首次预印本；正式发表为 EMNLP 2020。题名核对所读 2020-10-06 arXiv v4，[正式会议记录](https://aclanthology.org/2020.emnlp-main.710/) 已核对。
- **原文与全文证据**：[PDF](https://arxiv.org/pdf/1911.03631)；本地 `/workspace/research-notes/graph4rag/history-evidence/hgn.pdf`、`hgn-clean.txt`。**阅读范围**：§3.1–3.4，§4.1–4.4，Tables 3–6，附录段落选择及错误分析说明。
- **类别与 GraphRAG 关系**：多粒度异构图证据聚合与联合多任务阅读的历史前身，和今天的分层 GraphRAG 有概念关联但不是社区摘要式图索引。
- **技术总结**：图包含问题、段落、句子、实体四种节点和七种边；先以标题/问题实体匹配和 RoBERTa ranker 选择首跳段落，再沿 Wikipedia 超链接获取第二跳段落，将源句子和目标段落显式连接。其余边覆盖问题–段落、问题–实体、段落–句子、句子–实体、段落之间及段内相邻句子，因而能同时表达文档层级和跨文档跳转；不是仅把同现实体构成单层图。RoBERTa、bi-attention 与共享 BiLSTM 从文本跨度起止位置初始化节点，按边类型使用不同的 attention 参数在 GAT 中传播，再以 gated attention 把图表示融合回 token 上下文。段落节点预测相关段落，句子节点预测支持事实，实体预测作为辅助正则，最终答案仍由 span 起止与 yes/no/type 预测得到；训练总目标是这六类交叉熵的加权和，答案不在候选实体时实体损失置零。
- **优点与实证**：不同粒度的节点为不同监督提供自然对应，比只用实体图更能处理没有明确实体 mention 的证据句，并可显式给出段落–句子–实体的出处关联。Table 4 的 RoBERTa-large 开发集消融中，无图 Joint F1 为 71.02，paragraph/sentence 图为 73.83，加实体为 74.13，完整层级图为 74.37；主要收益来自段落/句子结构，而不是大量实体边本身，这对选用 BCviz 式二部关联模型尤其值得重视。论文还用相同预训练语言模型对照，避免将全部提升简单归于更大的编码器。
- **局限**：**论文明确范围与实证**：实验主要按 HotpotQA 的两跳设置裁剪图，默认最多 4 段落、40 句子、60 实体；依赖 Wikipedia 超链接，迁移普通文档需要实体链接替代。对 100 个 answer F1=0 的开发集错误进行分类，15% 归于离散比较推理、16% 归于常识/外部知识、16% 归于多跳错误、20% 归于正确证据下的 span 抽取错误，其余为标注或多正确答案问题；这些比例是所抽错误样本内部的构成，不是整个测试集错误率。**方法推断**：fullwiki 的外部检索器与阅读器仍有脱节，论文结论也把联合训练作为未来工作；没有验证大规模图索引维护、数据更新或查询规划，因此借鉴多粒度建模时还需补齐数据库系统层贡献。

<a id="h10"></a>

### [H10] Scalable Multi-Hop Relational Reasoning for Knowledge-Aware Question Answering（MHGRN，2020，EMNLP）

- **原文与全文证据**：[arXiv:2005.00646](https://arxiv.org/abs/2005.00646)；[PDF](https://arxiv.org/pdf/2005.00646)；本地全文 `/workspace/research-notes/graph4rag/history-evidence/mhgrn.pdf`，解析文本同目录 `mhgrn.txt`。会议信息由作者仓库 `INK-USC__MHGRN/README.md` 和 DRAGON 全文参考文献 [33] 交叉核实；本地 PDF 为 2020-09-18 的 v2。
- **阅读范围**：§2–§6，尤其 §4.1–§4.5 的多跳消息传递、结构化关系注意力、复杂度与路径解码；§5.1 子图抽取；Table 2–6、Figure 6–8 的实验和局限。
- **类别／历史位置**：KG 子图检索后的神经多跳推理，属于 GraphRAG 的历史前身。任务是有候选选项的判别式问答，不是自由文本生成。
- **技术总结**：对每个“问题—答案选项”，先链接 ConceptNet 实体，加入任意两个已链接实体之间两跳路径上的桥接实体，并保留这些节点间的所有边；文本编码器与子图编码器分别形成表示。MHGRN 按问题实体、答案实体及其他实体作类型变换，在单层内聚合最长 K 跳的关系路径消息，以逐跳关系矩阵的乘积表示关系组合，而不显式枚举所有路径。路径注意力被分解为上下文相关的端点类型势、单关系势和相邻关系转移势，借助动态规划计算指数多条路径的加权和；再对不同路径长度注意力聚合，并通过残差更新节点。答案实体池化结果与文本表示拼接，由交叉熵训练候选答案得分；预测后先确定答案节点和路径长度，再用动态规划解码高分关系路径作为解释。
- **优点**：比逐路径 LSTM 编码更适合大候选路径集，同时保留关系类型、路径长度与可读路径；Table 2 给出稀疏图上时间 `O(m²nKΔ)`、空间 `O(mnK)`，其中 m 为关系类型数、n 为节点数、Δ 为最大度，不能笼统说对所有输入因素都是线性。论文在相同 RoBERTa-Large 下，CommonsenseQA in-house test 从无 KG 的 68.69 提升到 71.11；Figure 7 显示每批训练成本随 K 近似线性，实验代价约为 RGCN 的两倍，而非理论最坏情况下的 m 倍。可给后续 GraphRAG 提供“保留多路径而压缩计算”的算法启发。
- **局限**：**论文实证**：Figure 6 中 K=3 的开发集效果高于 K=4/5，长路径可能引入更多噪声；实验主要是 CommonsenseQA 和 OpenBookQA 的固定选项任务，不能据此声称开放域生成有效。**方法分析／推断**：图抽取仍依赖实体链接与预设两跳连接，无法补救未进入子图的证据；注意力主要依赖关系序列与端点类型，不能充分区分具有相同关系模式但具体语义不同的路径。高注意力路径是模型行为解释线索，不等价于经过因果干预验证的充分证据，也没有文本来源级引用或更新维护机制。

<a id="h11"></a>

### [H11] QA-GNN: Reasoning with Language Models and Knowledge Graphs for Question Answering（2021，NAACL-HLT）

- **原文与全文证据**：[arXiv:2104.06378](https://arxiv.org/abs/2104.06378)；[PDF](https://arxiv.org/pdf/2104.06378)；本地全文 `/workspace/research-notes/graph4rag/history-evidence/qagnn.pdf`，解析文本 `qagnn.txt`。出版年份与会议由作者仓库 `michiyasunaga__qagnn/README.md` 和 DRAGON 全文参考文献 [8] 核实；本地全文是 2022-12-13 的 v5，版本日期不能当成首次发表年份。
- **阅读范围**：§2–§4，重点 §3.1–§3.6 的 working graph、相关性评分、消息与注意力公式、复杂度；§4.2 子图构建，Table 3–8 及 §4.6 的消融、结构推理与解释分析。
- **类别／历史位置**：语言模型与检索 KG 子图的联合推理；现代 GraphRAG 的相关性剪枝、上下文节点与图传播的历史前身。
- **技术总结**：对问题和每个答案候选做实体链接，抽取连接这些实体的两跳子图，并用预训练 LM 对“问题／选项上下文 + 实体名”的条件相关性评分，保留得分最高的 200 个节点。在子图中加入表示整个 QA 上下文的 z 节点，以不同关系连接问题实体和答案实体，使文本上下文与 KG 成为共同的 working graph。五层 GNN 的消息同时编码源节点状态、节点类型和边关系，而注意力额外读取节点相关性分数，迭代更新 KG 节点与 z 的表示；这不同于只在最终层拼接一个固定图向量。最终将原始 LM 表示、GNN 更新后的 z 和池化后的 KG 表示拼接，使用交叉熵端到端训练候选答案分类。
- **优点**：把“候选子图是否相关”和“怎样联合推理”明确分开，减少桥接扩展带来的无关实体；关系通过嵌入进入共享消息网络，不必为每种关系维护独立传播网络。相同 RoBERTa-Large 下，CommonsenseQA in-house test 为 73.41，相比 MHGRN 的 71.11 和无 KG 的 68.69 有提升；OpenBookQA 在同一 AristoRoBERTa 设置下为 82.77。Table 8 分别去除类型、关系、相关性以及联合连接会降低性能，提供了部件级证据；论文还把高注意力子图用于解释，表达形式不限于单一路径。
- **局限**：**论文实证范围**：主要结论来自固定候选的 CommonsenseQA、OpenBookQA、MedQA-USMLE，后者准确率仍为 38.0；层数超过五层未继续提升，说明增加传播深度不自动增加有效推理。**方法分析／推断**：top-200 剪枝按节点相关性而非完整证据链覆盖优化，可能丢失单独看不相关却必要的桥接实体；每个候选需单独构图和评分。z 是 LM 已编码文本的单一向量，GNN 更新 z 不等于反复更新全部文本 token；这一融合瓶颈正是后续 GreaseLM 改进的动机。注意力可视化与否定词切片实验并未证明严格逻辑正确性，也未解决自由文本生成的引用忠实性。

<a id="h12"></a>

### [H12] GreaseLM: Graph REASoning Enhanced Language Models for Question Answering（2022，ICLR）

- **原文与全文证据**：[arXiv:2201.08860](https://arxiv.org/abs/2201.08860)；[PDF](https://arxiv.org/pdf/2201.08860)；本地全文 `/workspace/research-notes/graph4rag/history-evidence/greaselm.pdf`，解析文本 `greaselm.txt`。PDF 首页明确标注 “Published as a conference paper at ICLR 2022”。
- **阅读范围**：§3 的输入、单模态预编码、跨模态融合公式 (1)–(11)；§4–§5 的实验和分析；附录 B.1–B.2 的实体链接和图初始化、C.1 的消融，Table 2–8。
- **类别／历史位置**：深层 LM–GNN 融合的 KG 增强问答，属于表示层增强的历史前身；不是通过文本提示把图交给生成式 LLM。
- **技术总结**：沿用问题／上下文／候选实体链接、两跳桥接扩展和 LM 相关性 top-200 剪枝，构建包含实体类型和关系类型的局部 KG，并在文本前加入 interaction token、在 KG 中加入连接已链接实体的 interaction node。先由 N 层普通 LM 编码文本，再运行 M 层融合块：每块分别执行一个 Transformer 层和一个关系／类型感知 GNN 层。两侧交互节点的向量经拼接、共享的两层 MLP 混合后再拆回各自模态，其他 token 和实体通过下一层的自注意力或消息传递间接得到跨模态信息，而不是让所有 token 与节点做全连接交叉注意力。最后使用 interaction token、interaction node 和图注意力池化向量预测答案，端到端优化交叉熵；论文主要配置 M=5，学习的重点是多层反复交换而非仅做最终融合。
- **优点**：能让否定、限定与不确定表达在后续层持续修正 KG 推理，同时让 KG 信息重新影响具体 token 表示。Table 2 的 CommonsenseQA in-house test 为 74.2，QA-GNN 为 73.4；使用额外科学事实的 AristoRoBERTa 设置下，OpenBookQA 为 84.8，QA-GNN 为 82.8。附录 C.1 去掉跨模态交互使开发集从 78.5 降至 76.5，隔层交互为 76.3；连接 interaction node 到所有子图节点也比仅连接已链接实体更差，支持“受控的信息入口”有价值。
- **局限**：**论文实证**：效果高度依赖节点初始化：随机初始化使 CommonsenseQA 开发集从 78.5 降到 60.8；M=7 降到 76.2，更多融合层并非必然更好。MedQA 约 5% 样本没有检出实体，只能用零初始化的 dummy 节点退化为 LM；其 MedQA 准确率 38.5 仍有限。**方法分析／推断**：单对 interaction token/node 是信息瓶颈，top-200 裁剪和外部 KG 的覆盖仍决定上限；逐候选计算和模型微调不适合直接当作无需训练的 GraphRAG 检索插件。论文以介词短语数、否定词和 hedge 词作复杂度代理，并没有金标准推理结构，不能将这些切片上的提升视作一般组合逻辑能力的证明。

<a id="h13"></a>

### [H13] Deep Bidirectional Language-Knowledge Graph Pretraining（DRAGON，2022，NeurIPS）

- **原文与全文证据**：[arXiv:2210.09338](https://arxiv.org/abs/2210.09338)；[PDF](https://arxiv.org/pdf/2210.09338)；本地全文 `/workspace/research-notes/graph4rag/history-evidence/dragon.pdf`，解析文本 `dragon.txt`。PDF 首页明确标注第 36 届 NeurIPS 2022；这里的 DRAGON 是 LM–KG 预训练方法，应与同名稠密检索器区分。
- **阅读范围**：§2.1–§2.4 全部方法与目标函数，§3.1–§3.4 的预训练设置、九个下游任务、消融；§4 生物医学实验，§5 结论中的生成限制；附录 A 和 B.1 的风险、图检索细节。
- **类别／历史位置**：语言—知识图联合自监督预训练，属于 GraphRAG 的表示学习前身；其正文明确说明当前是 encoder，不能执行语言生成。
- **技术总结**：从文本段落链接实体，加入两跳桥接节点及其诱导边，形成粗对齐的文本—局部 KG 对；附录 B.1 明确说超过 200 个节点时随机采样裁剪，因此不能把此处误写成 QA-GNN 的相关性 top-200。编码器复用 GreaseLM 的 19 层文本编码与 5 层双向融合，通过 interaction token/node 反复交换表示，但把训练扩展到大规模自监督预训练。目标为 `L_MLM + L_LinkPred`：随机遮住 15% 文本 token、移除 15% KG 边，分别预测词和被移除三元组，链接预测默认采用 DistMult 并为每个正例采样 128 个负例，也检验 TransE／RotatE。下游仍检索局部 KG，通过文本交互向量、图交互向量和图池化表示微调问答／分类；收益来自先预训练融合能力，再进行任务微调，而不是新提出一种图检索索引。
- **优点**：自监督目标让“KG 帮助理解文本”和“文本帮助理解 KG”同时进入优化。Table 5 中完整方法在 CSQA/OBQA 为 76.0/72.0，只有 MLM 为 74.3/67.2、只有 LinkPred 为 73.8/66.4；把图变成三元组句子后为 74.7/70.1，说明该设置中保留结构有额外价值。九个常识任务和医学任务覆盖面比前作广，10% 标注训练数据下 CosmosQA/PIQA 的收益尤其明显。注意该文 OBQA 不提供额外科学事实，不能直接拿 72.0 与 GreaseLM 论文使用 AristoRoBERTa 和额外事实的 84.8 比较。
- **局限**：**论文明确限制与成本**：§5 明言没有语言生成能力；一般领域预训练使用八张 A100、FP16、七天，普通团队完整重训成本较高，论文采用的批量 8,192、20,000 步不能当成轻量微调。附录 A 指出 LM 与 ConceptNet 的偏见会传入模型。**方法分析／推断**：200 节点随机裁剪没有证据链覆盖保证，训练与推理都依赖实体链接和已有 KG；预训练后的静态表示并未提供知识更新、删除传播或来源引用机制。图结构转句子的消融仅说明此编码器／预算设置中的结构优势，不能推出所有现代长上下文生成器都需要 GNN，也不能直接证明其对开放式 GraphRAG 的收益。

## 必要的非图 RAG 对照

<a id="b01"></a>

### [B01] REALM: Retrieval-Augmented Language Model Pre-Training（2020，ICML）

- **原文与阅读**：[论文](https://arxiv.org/abs/2002.08909)；`history-evidence/realm.pdf`；读 §3 模型／训练、异步 MIPS 刷新与实验。所读为 arXiv v1。
- **技术总结**：将检索文档 z 当隐变量，优化 `log Σz p(z|x)p(y|x,z)`；双 BERT 编码查询和文档，用 MIPS 取 top-k，知识增强 encoder 联合读输入与文档预测 mask。以显著实体／日期 masking 促使模型利用外部知识，问答微调采用答案 span 分布。训练文档 encoder 更新会使索引过期，因此另一个 job 异步重新编码并建索引，检索后对 top-k 用新参数重算概率。
- **优点**：用无监督预测信号学检索，并明确展示学习模型与索引刷新耦合的工程问题；外部语料可更换。
- **不足**：top-k 截断可能漏掉有价值文档，周期刷新成本高且暂时不一致；不是显式多跳证据组检索，也不是现代对话生成器。BCviz 的维护方向可借鉴索引陈旧问题，但不能照搬预训练收益解释为图索引收益。

<a id="b02"></a>

### [B02] Dense Passage Retrieval for Open-Domain Question Answering（DPR；2020，EMNLP）

- **原文与阅读**：[正式论文](https://aclanthology.org/2020.emnlp-main.550/)、[预印本](https://arxiv.org/abs/2004.04906)；`history-evidence/dpr.pdf`；读 §3–5、负例与检索／reader 评测。
- **技术总结**：两独立 BERT 把问题和段落映射到 768 维，内积打分；用正片段、batch 内其它问题正片段、BM25 hard negative 构造对比 softmax 损失。离线编码约 2,100 万个 100-word Wikipedia 段，FAISS 检索后由 reader 抽答案。关键是正负样本和可预计算的可分解打分，而非复杂交叉注意。
- **优点**：可复用向量索引，检索与 reader 分开诊断；构成图方法不可缺少的朴素检索对照。
- **不足**：逐片段独立相似度没有显式覆盖多条证据、关系约束和去冗余目标，正例／答案匹配也可能有偏。2026 年研究不能只与原始 DPR 比，需加统一 embedding、reranker 与强多轮检索，排除“旧弱模型”因素。

<a id="b03"></a>

### [B03] Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks（2020，NeurIPS）

- **原文与阅读**：[论文](https://arxiv.org/abs/2005.11401)；`history-evidence/rag.pdf`；读 §2–4、解码与知识更换实验。
- **技术总结**：DPR 取 top-k 文档，BART 生成；RAG-Sequence 对完整输出的单一隐文档边缘化，`Σz pη(z|x)Πi pθ(yi|x,z,y<i)`；RAG-Token 则每个 token 各自对文档求和，`Πi Σz pη(z|x)pθ(yi|x,z,y<i)`。联合微调 query encoder 与 generator，文档 encoder／索引固定。Sequence 使用各文档 beam 的联合重评分，Token 可直接按混合下一词分布 beam search。
- **优点**：统一外部非参数记忆与预训练生成器，并测开放问答、生成、事实验证及知识替换。
- **不足**：隐文档分布与真实可追溯引用不同；边缘化不显式保证证据完整、逻辑合取或跨源独立性。不能把更改索引即可更新知识扩大为生成绝不产生旧事实；现代 GraphRAG 需用原文和有效时间约束验证这一点。

## 现代 GraphRAG 主干

<a id="c01"></a>

### [C01] From Local to Global: A Graph RAG Approach to Query-Focused Summarization（2024；所读 arXiv v2，2025-02-19，预印本）

- **分类与来源**：社区检测及层次摘要。原文：https://arxiv.org/abs/2404.16130 ；[本地全文](/workspace/research-notes/graph4rag/sources/core/graphrag.pdf)，[全文文本](/workspace/research-notes/graph4rag/sources/core/graphrag.txt)。实际阅读 §3.1.1–3.1.6、§3.2–3.3、§4–6；所读 PDF 首页仍标注 “Preprint. Under review.”，不据此认定任何正式会议录用。
- **技术总结**：先切块，用 LLM 抽取实体、关系、claims 及文本描述；同名实体按字符串匹配归并，关系重复次数成为边权，并聚合描述。递归 Leiden 构建互斥、覆盖图节点的社区层次。叶社区按边两端节点总度排序装入上下文；上层超预算时，以子社区摘要替换详细元素，形成自底向上的报告。查询时选择层次，把社区报告打乱并分块，LLM 并行生成局部答案及 0–100 helpfulness 分数；过滤零分，按分数拼接，最后 reduce 生成全局答案。这主要解决全局主题综合，不能等同于一般多跳证据检索。
- **优点（实证）**：在约百万 token 的 Podcast、News 两语料、每组 125 个生成问题上，覆盖度和多样性相对向量 RAG 有明显优势；预生成报告可复用。v2 还以 Claimify 抽取主张并聚类，补充 LLM 成对裁判。
- **不足与边界**：论文承认只有两套语料，尚需评估事实捏造；LLM 偏好与更多主张均不等于事实正确。尤其 v2 §5.2 的 claim-based 结果中，图社区方法与全文 map-reduce 的差异并不显著，故不能把全部提升归于图结构。索引成本高，Podcast 实验约 281 分钟；重摘要会损失细节、度排序可能偏向热门实体，是机制推断而非已测结论。基于当前社区层次做删除与事实纠错未获验证。

<a id="c02"></a>

### [C02] LightRAG: Simple and Fast Retrieval-Augmented Generation（2024 预印本；Findings of EMNLP 2025）

- **分类与来源**：实体／关系双层向量检索和一跳扩展。正式出处：https://aclanthology.org/2025.findings-emnlp.568/ ；arXiv：https://arxiv.org/abs/2410.05779 。[正式全文](/workspace/research-notes/graph4rag/sources/core/lightrag_acl.pdf)，[正式全文文本](/workspace/research-notes/graph4rag/sources/core/lightrag_acl.txt)；另有 [arXiv v3](/workspace/research-notes/graph4rag/sources/core/lightrag.pdf)。实际阅读正式版 §3、§4、§7、附录 §9.1–9.2，并核对表 1、5–7。**是 Findings，不是 EMNLP main。**
- **技术总结**：切块后抽取实体和关系，为其生成 key–value 文本档案并去重；实体名作为低层键，关系具有表达全局主题的关键词。查询由 LLM 提取局部／全局关键词，分别在向量库匹配实体与关系，再收集命中图元素的一跳邻接信息；把实体、关系描述及原始片段一起交给 LLM。这里的 high-level 指主题关系检索，不是社区层次摘要。新增文档单独抽取后合并节点、边，避免每次重做全图社区报告。
- **优点（实证）**：四个 UltraDomain 子集各 125 个问题，用 GPT-4o-mini 成对裁判；相对纯 chunk RAG 有较强的覆盖、多样性表现。附录报告平均查询 11.2 秒对 GraphRAG 23.6 秒，并提供五份文档的插入耗时与存储比较，说明在该设置下工程开销较小。
- **不足与边界**：对 GraphRAG 的 Overall 胜率仅 49.6–54.8%，不能改写成全面显著领先；评估依赖 LLM 裁判，未建立可靠的事实正确率优势。一跳邻居不提供有保证的多跳路径检索；抽取错漏、同名归并可能传播到生成，是机制风险。论文“增量”主要指追加及集合合并，没有证明删除、版本冲突或时态一致性；后续仓库的删除功能不能当原文贡献。声称“100 token”仅是关键词检索相关开销，不是完整端到端回答总成本。

<a id="c03"></a>

### [C03] HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models（NeurIPS 2024；所读 arXiv v3，2025-01-14）

- **分类与来源**：知识图上的 Personalized PageRank（PPR）关联检索。原文：https://arxiv.org/abs/2405.14831 ；会议记录：https://openreview.net/forum?id=hkujvAPVsg 。[本地全文](/workspace/research-notes/graph4rag/sources/core/hipporag1.pdf)，[全文文本](/workspace/research-notes/graph4rag/sources/core/hipporag1.txt)。实际阅读 §2.3、§3–5，重点表 2–5 及概念／上下文讨论。
- **技术总结**：离线先 NER，再把实体提示加入 OpenIE，得到不限固定 schema 的名词短语节点及关系；编码器余弦相似度超过阈值的短语之间加同义边。维护短语—段落计数矩阵 P。在线从问题抽实体，各自链接到最相似图节点；用节点出现段落数的倒数进行 specificity 加权，形成 PPR 的重启分布，扩散到联合相关邻域。最后以节点概率乘 P 得到段落排名，交给 reader；PPR 检索也能嵌入 IRCoT 的多轮流程。它返回原始段落，图主要充当关联索引。
- **优点（实证）**：MuSiQue、2Wiki、HotpotQA 各抽 1,000 个问题；单步 ColBERTv2 版本平均 Recall@5 为 72.9，对直接 ColBERTv2 的 65.6；2Wiki 增益尤其大。消融显示直接邻居扩展不如 PPR，支持全图扩散并非可由简单一跳替代。对固定 IRCoT 设置，在线调用更省且更快，但该优势不涵盖离线构图成本。
- **不足与边界**：优势偏实体中心，HotpotQA 的 QA F1 55.0 低于 ColBERTv2 的 57.7；问题压缩为实体会丢失语境。相似性阈值加边可能把相关而非同义概念混合，PPR 排名也不是显式逻辑证明，均属机制风险。多语料追加、删除、冲突处理与长期正确性没有由本文验证；“仿海马”是设计启发，不是人类记忆能力等价性的证明。

<a id="c04"></a>

### [C04] From RAG to Memory: Non-Parametric Continual Learning for Large Language Models（HippoRAG 2；ICML 2025，PMLR 267）

- **分类与来源**：实体—段落异构图、语境化种子及 PPR。原文：https://arxiv.org/abs/2502.14802 。[本地 PMLR 正式全文](/workspace/research-notes/graph4rag/sources/core/hipporag2_pmlr.pdf)，[全文文本](/workspace/research-notes/graph4rag/sources/core/hipporag2_pmlr.txt)。实际阅读 §3–6、附录 E 错误分析、G.1 初始化；会议名称及卷号由 PDF 首页核实。
- **技术总结**：保留 OpenIE 关系边和短语同义边，再把段落作为节点，用 contains 边连接其短语，直接在图中保存上下文。查询同时向量检索段落与三元组；用 LLM “recognition memory”过滤 top-5 三元组，按三元组平均得分选至多五个短语种子。所有段落也是种子，但其相似度重启权重乘默认 0.05；PPR 后直接按段落节点分数返回原文。若过滤后无三元组则退回稠密检索。过滤提示通过 DSPy MIPROv2 优化，主要配置使用 Llama-3.3-70B 和 NV-Embed-v2。
- **优点（实证）**：覆盖事实问答、关联多跳、NarrativeQA；相同主要模型下，五个可测检索数据集平均 Recall@5 为 78.2，对 NV-Embed-v2 的 73.4。去掉段落节点使三套多跳平均召回从 87.1 降至 81.0；query-to-triple 比 NER-to-node 更有效，明确说明上下文和种子选择的重要性。
- **不足与边界**：过滤器并非总有益，2Wiki 去过滤召回略增；附录对 100 个失败样本分析发现过滤后不含支持短语的比例增加，不能把该失败集比例外推到全体。在线 LLM 过滤新增延迟，图扩散不保证关系方向或推理有效性。持续学习实验仅把 NQ/MuSiQue 分为四段逐批加入，复杂任务仍随库增大退化；不等于验证时态更新、撤回、冲突消解或无遗忘。

<a id="c05"></a>

### [C05] Knowledge Graph-Guided Retrieval Augmented Generation（KG²RAG；NAACL 2025）

- **分类与来源**：种子 chunk 检索、KG 扩展和上下文组织。正式记录：https://aclanthology.org/2025.naacl-long.449/ ；原文：https://arxiv.org/abs/2502.06864 。[本地全文：arXiv v1](/workspace/research-notes/graph4rag/sources/core/kg2rag.pdf)，[全文文本](/workspace/research-notes/graph4rag/sources/core/kg2rag.txt)。实际阅读 §2.1–2.3、§3.1–3.3、Limitations；所述数字来自已读 v1，正式卷页只用于核实 venue。
- **技术总结**：LLM 抽取并保留四元组 (h,r,t,source-chunk)。先语义检索 top-k 种子片段，再从其对应三元组的实体出发做 m-hop BFS，找共享或邻近事实关联的其他片段。组织阶段将扩展子图转为无向加权图，以原文 chunk 与问题相似度作边权；每个连通分量取**最大生成树**去冗余。以最高权边作为起点 DFS，将关联原文拼成段落；另把树三元组串联给 cross-encoder 重排各树，按预算加入树对应的原文，最后由 LLM 回答。不能误记成最小生成树或社区检测。
- **优点（实证）**：统一 LLaMA3-8B、mxbai-embed-large 和 bge-reranker-large；在 HotpotQA distractor/fullwiki 与实体替换 Shuffle 版本验证。fullwiki 设置含 66,581 文档，答案 F1 0.631 对语义检索加 rerank 的 0.587；删除 5%/10% 随机三元组实验提供有限噪声鲁棒性证据。返回原文使证据可溯源，检索后处理可插入现有管线。
- **不足与边界**：组织消融答案 F1 0.660 对完整 0.663，主要收益是平均片段数 16.76→8.11、精度改善，而非已证明大幅推理提升。无向树化可能移除方向、环和多个独立证明；随机删边不代表错误事实、实体混淆或对抗污染。实验主要围绕 HotpotQA，不能外推为全领域统一优势；BFS 的枢纽爆炸和预算截断仍需系统研究。

## 知识图谱的路径、子图与学习型检索

<a id="k01"></a>

### [K01] Think-on-Graph: Deep and Responsible Reasoning of Large Language Model on Knowledge Graph（2023 预印本；ICLR 2024）

- **来源与阅读证据**：[原文](https://arxiv.org/abs/2307.07697)；本地全文 `research-notes/graph4rag/kg-sources/ToG/paper.pdf`。读 §2.1–2.2、§3 实验/消融/可追溯性及附录 E 提示词；PDF 页首确认 ICLR 2024。
- **具体技术**：以实体为点、关系为有向边的既有 KG 为检索对象。抽取问题实体后维护宽度为 N 的路径束；每跳先枚举当前尾实体的出入关系，由 LLM 排序剪枝，再沿保留关系查实体并再次剪枝。LLM 判断当前路径是否足够回答，否则扩展至最大深度 D；ToG-R 改为保留关系链。基本版最多约 `2ND+D+1` 次 LLM 调用，无需训练。检索到的真实三元组序列作为生成上下文；达到深度上限仍不足时允许依赖模型参数知识回答，故不能将所有输出都视为有图证据。
- **优点**：推理路径可检查；查询既有 KG 使事实更新无需重训 LLM。作者在多项知识问答任务中验证收益，并比较三元组/序列/自然语言提示，以及 LLM/BM25/SentenceBERT 剪枝，展示效率与准确性的权衡。
- **局限**：作者消融中轻量剪枝降低调用量，但同时明显损失准确性。分析：高出度实体使候选和串行调用膨胀；早期剪枝可能不可逆地丢失正确路径；路径存在只证明 KG 内一致性，不能保证图本身正确、时间有效或生成完全忠实。与 BCviz 的接口在“候选证据压缩及可解释浏览”，而非将路径直接替换为任意稠密子图。

<a id="k02"></a>

### [K02] Think-on-Graph 2.0: Deep and Faithful Large Language Model Reasoning with Knowledge-Guided Retrieval Augmented Generation（2024 预印本；ICLR 2025）

- **来源与阅读证据**：[原文](https://arxiv.org/abs/2407.10805)；本地 `kg-sources/ToG-2/paper.pdf`（位于上述研究笔记目录）。读 §3、§4.5–4.7、附录 B/E；PDF 页首确认 ICLR 2025。
- **具体技术**：把 KG 与实体对应文档耦合，先实体链接和主题剪枝，并尝试用初始实体文档直接作答。迭代中仍以 LLM 选择关系，但对候选实体的文档块，用稠密检索器/重排器打分；打分输入将当前三元组的自然语言描述拼到文档块前，保留结构上下文。实体分数是该实体命中 top-K 块分数的指数衰减加权和，从而以文本证据反向选择下一跳实体。LLM 联合路径、文档与前轮线索判断能否回答；不足时总结线索并重写查询。无需额外训练。
- **优点**：既保留图的导航作用，又补充三元组难表达的细节。作者测试 WebQSP、QALD、AdvHotpotQA、FEVER 及金融任务；消融显示 reranker 适合实体剪枝，原文报告该阶段耗时约为 ToG 的 68.7%，不能误写成端到端同幅加速。人工分析区分纯图、纯文本和联合证据贡献。
- **局限**：实验中宽度超过约 3、深度超过约 3 后收益趋缓，扩大探索不必然更好。分析：依赖可靠实体—文档映射；多轮 API、图查询与重排延迟仍存在；对文档删除、图文本版本不一致、引用覆盖没有系统保证。适合作为图—文档二部结构检索的强基线。

<a id="k03"></a>

### [K03] Reasoning on Graphs: Faithful and Interpretable Large Language Model Reasoning（RoG；2023 预印本；ICLR 2024）

- **来源与阅读证据**：[原文](https://arxiv.org/abs/2310.01061)；本地 `kg-sources/reasoning-on-graphs/paper.pdf`。读 §4、§5、附录 A.3 检索算法、A.6/A.7 训练与分析；PDF 页首确认会议信息。
- **具体技术**：“规划—检索—推理”三段。LLM 先生成关系序列而非答案实体；检索器从问题实体出发做受该序列约束的 BFS，获得在 KG 中真实存在的实例路径，再让 LLM 从路径作答。训练用问题实体到答案实体的最短路径关系序列作规划监督，以 ELBO 形式解释规划和答案生成联合目标；同一 LLaMA2-7B 接受规划、检索推理两类指令微调。推理时 beam search 生成 top-3 关系计划，计划模块也可为其他 LLM 提供证据。
- **优点**：把学习关系模式与查询动态实体解耦；无需 LLM 在每条边上决策，真实路径易展示。作者在 WebQSP/CWQ 验证，并评估把规划器接到其他模型、计划数量与答案覆盖的关系。
- **局限**：作者指出更多计划增加噪声及检索时间，召回增长不等于最终 F1 增长。分析：需要问题答案监督与图中可达的训练路径；受规划关系覆盖和实体链接约束。SubgraphRAG 后续专门讨论 WebQSP/CWQ 重叠及联合训练泄漏，因此复现应拆分数据、明确 Hit 与 Hit@1，不能直接把各论文榜单拼成统一排名。关系计划可执行也不等于自然语言解释在因果上忠实。

<a id="k04"></a>

### [K04] G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering（NeurIPS 2024）

- **来源与阅读证据**：[原文](https://arxiv.org/abs/2402.07630)、[会议页面](https://openreview.net/forum?id=MPJ3oXtTZl)；本地 `kg-sources/G-Retriever/paper.pdf`。读 §3–6、§7 局限及附录 B/D/E；作者仓库给出正式会议引用。
- **具体技术**：对带文本属性的节点和边编码，按问题余弦相似度取 top-k，赋予递减 prize；在全图求近似 prize-collecting Steiner tree，最大化节点/边 prize 减边成本。边 prize 大于成本时转成有奖励的虚拟节点，使其能用现成 PCST 求解。所得连通子图同时经过 GNN、池化和 MLP，变成 LLM 的软图提示，并线性化为文本；以答案损失训练图编码器和投影，基础设置冻结 LLM，另比较 LoRA。
- **优点**：明确处理相关性、连通性及上下文规模的矛盾；同时利用文本和图结构。GraphQA 包含 ExplaGraphs、SceneGraphs、WebQSP，作者进行模块消融、训练耗时和图引用有效性评估，验证图 token 与文本图各有贡献。
- **局限**：作者明确承认检索模块是静态的，未端到端学习。分析：PCST 的连通树偏好可能牺牲多个独立证据团；按边数罚项并非真实 token 预算；近似优化目标不等于最优回答证据。原文 WebQSP 约 99% 节点/token 缩减是特定输入子图设置，不能外推为任意全图的端到端加速。BCviz 方向应与此类结构约束检索直接比较。

<a id="k05"></a>

### [K05] GNN-RAG: Graph Neural Retrieval for Large Language Model Reasoning（2024 预印本；所读预印本版本）

- **来源与阅读证据**：[原文](https://arxiv.org/abs/2405.20139)；本地 `kg-sources/GNN-RAG/paper.pdf`。读 §3–6、附录 B 理论分析、D 消融、E 局限；本地全文为 2024-05-30 v1，以上年份不冒充会议信息。
- **具体技术**：先在主题实体附近的稠密 KG 子图运行监督训练的 KGQA GNN，以答案/非答案节点分类得到候选答案；抽取主题实体到候选答案的最短路径，线性化后送入 LLM。GNN 通过问题—关系语义匹配控制消息传播；作者用 SBERT 与专门关系匹配语言模型构造两个检索器。RA 版本合并 GNN 与 RoG 的路径，以互补多跳结构推理和单跳关系匹配；Ensemble 版本合并两个 GNN。开放权重 LLM 再用真实答案最短路径进行回答微调。
- **优点**：把昂贵逐跳 LLM 探索转交 GNN；作者在 WebQSP/CWQ 比较答案覆盖和输入 token，深 GNN 在多跳召回上更好，且能接入不同回答模型。
- **局限**：作者显示单跳问题中精确语义匹配可能更适合 LLM 检索；附录 E 明确指出初始子图遗漏答案、实体链接失败或断连会导致无法提供证据，其中原文 CWQ 初始子图仅约 79.3% 问题含答案。分析：训练/推理证据分布不同，候选答案最短路径不保证包含解释所需全部条件；RA 扩大上下文和训练依赖，不能只看精度。

<a id="k06"></a>

### [K06] Simple is Effective: The Roles of Graphs and Large Language Models in Knowledge-Graph-Based Retrieval-Augmented Generation（SubgraphRAG；2024 预印本；ICLR 2025）

- **来源与阅读证据**：[原文](https://arxiv.org/abs/2410.20724)；本地 `kg-sources/SubgraphRAG/paper.pdf`。读 §3–4、附录 A/D/F；PDF 页首确认 ICLR 2025。
- **具体技术**：将子图采样分布分解为三元组独立的 Bernoulli 因子，用问答最短路径构造替代监督。对实体及关系预计算文本向量；查询时把问题、头实体、关系、尾实体向量与 DDE 结构特征拼接，交给轻量 MLP 二分类，取 top-K 三元组。DDE 从主题实体指示向量出发，沿正向/反向边做多轮均值传播，并拼接各轮结果，编码与问题实体的方向距离关系。下游无需微调 LLM，以少样本示例指导解释和答案生成。
- **优点**：并行逐三元组打分允许任意形状及可调大小的子图，避免强制单路径或连通树；作者报告检索召回、耗时、跨数据集迁移和证据支持度，并指出旧评测把 Hit 混称 Hit@1、数据集重叠等问题。
- **局限**：作者发现小 LLM 输入更多三元组会退化，跨域也有性能下降；部分基线因复现失败采用原报告结果。分析：因子化检索未显式优化证据之间的协同、覆盖和冗余，也不强制连通；最短路径弱监督并非完整解释金标准。这正是二部证据组、预算化覆盖和可验证压缩可以研究的切口，但需证明优于强 MLP+DDE 基线。

<a id="k07"></a>

### [K07] StructGPT: A General Framework for Large Language Model to Reason over Structured Data（2023，EMNLP）

- **原文与阅读**：[论文](https://arxiv.org/abs/2305.09645)、[正式记录](https://aclanthology.org/2023.emnlp-main.574/)；`kg-sources/StructGPT/paper.pdf`；读 §4.1–4.4、§5 及错误分析。
- **技术总结**：将读取和推理解耦。结构库暴露邻居关系、指定关系三元组、表列／子表、表名／外键等接口；每轮调用接口取真实数据、线性化、让 LLM 选择下一关系或生成答案／SQL。KGQA 从已链接主题实体出发，先选关系再取三元组，多跳时判断是否继续；表和库则逐层缩小列／表范围。无需为每项任务训练图编码器，主要采用 zero/few-shot 提示。
- **优点**：把图检索实现为可执行算子，便于检查 LLM 选取内容与实际返回是否一致；同时测 KGQA、TableQA、Text-to-SQL，并将 100 个错误样本分成选择、推理、格式、幻觉等类别。
- **不足**：实体链接、选关系错误会传播；接口执行正确不保证 LLM 最终判断正确。原文不少设置仍低于全监督系统，部分 zero-shot 表格任务会退化。分析：它已给出“LLM+结构数据算子”的一般模式，后续数据库创新需有新算子、代价优化或正确性语义，不能只封装 API。

<a id="k08"></a>

### [K08] KG-GPT: A General Framework for Reasoning on Knowledge Graphs Using Large Language Models（2023，Findings of EMNLP）

- **原文与阅读**：[论文](https://arxiv.org/abs/2310.11220)；`kg-sources/KG-GPT/paper.pdf`；读 §2–4、附录关系候选构建与错误分析。
- **技术总结**：给定已识别实体，将问题／断言拆成单关系子句；由 KG schema 及实体类型生成合法关系候选，让 LLM 为每子句选择 top-K 关系，再查询相应真实三元组组成证据图，线性化后做验证或问答。所有阶段用 ICL，不把 LLM 自行生成的三元组当数据库事实。
- **优点**：对多跳、合取、存在及否定类问题统一拆解；在 FACTKG 与 MetaQA 用 4/8/12-shot 对比，有逐阶段 100 个失败样本分析，能够区分分解与检索失败。
- **不足**：依赖输入实体集合和候选 schema；MetaQA 3-hop 对示例数敏感，12-shot 到 4-shot 显著下降，FACTKG 也未胜过全监督 GEAR。分析：句子拆解可能漏掉跨子句约束，关系筛选无法补回缺失事实；不能把其模板化电影 QA 结果等同于开放文档 GraphRAG 的可靠性。

<a id="k09"></a>

### [K09] MindMap: Knowledge Graph Prompting Sparks Graph of Thoughts in Large Language Models（2023 预印本，ACL 2024）

- **原文与阅读**：[论文](https://arxiv.org/abs/2308.09729)；`kg-sources/MindMap/paper.pdf`；读 §3.1–3.3、§4、证据探索与提示附录。
- **技术总结**：LLM 抽问题实体，以 BERT 相似度链接 KG；检索连接问题实体的 k-hop 路径，再扩一跳邻居，按头实体分组采样以控制规模。为路径和邻居证据编号并转自然语言，让 LLM 合并为 reasoning graph；最后输出回答、推理过程和带证据编号的 mind map，并允许调用参数知识扩展图。
- **优点**：路径证据与邻居背景分开，输出便于人工检查；三个中英文医学任务测开放回答、对话、选择题，并有检索知识不匹配的实验，提醒“更多知识”可能伤害答案。
- **不足**：生成的 mind map 可混入参数知识，不是原 KG 的等价可验证证明；所谓 hallucination 量化包含 NER 后 TF-IDF 相似度，不能直接当事实错误率或临床安全指标。分析：多轮改写会改变关系含义；可视化增强本身已有，BCviz 新系统需证明可定位、纠正的检索错误及人机成本收益。

<a id="k10"></a>

### [K10] Retrieve-Rewrite-Answer: A KG-to-Text Enhanced LLMs Framework for Knowledge Graph Question Answering（2023，IJCKG）

- **原文与阅读**：[论文](https://arxiv.org/abs/2309.11206)；`kg-sources/Retrieve-Rewrite-Answer/paper.pdf`；读 §4–5，尤其 §4.2 语料生成、§5.4 指标及 §5.5 训练设置。
- **技术总结**：BERT 分类预测跳数，再按问题和已有关系前缀逐跳分类，保留关系路径并取关系概率乘积排序，按图实例化至多 M 条路径。以 LoRA 微调 KG-to-Text 模型把线性三元组改写成自然语言，再给冻结问答模型。训练图文对来自训练问题的标注路径／SPARQL，中间由 ChatGPT 写描述，并以是否答出真值筛选样本。
- **优点**：直接研究相同知识的表达形式对 reader 的影响；多种问答模型、中英文数据和 triple／通用 data-to-text 对照支持领域改写的作用。
- **不足**：需跳数／路径／SPARQL 标注，MetaQA 实验直接用真值跳数；其 hit@1 定义为生成文本包含任一答案实体，不能等同严格单个 top-1 预测。自然语言改写有丢事实及添事实风险，问答成功筛选也不等于改写完全忠实；多模块训练、rewrite 推理必须计入总成本。

<a id="k11"></a>

### [K11] REANO: Optimising Retrieval-Augmented Reader Models through Knowledge Graph Generation（ACL 2024）

- **原文与阅读**：[正式论文](https://aclanthology.org/2024.acl-long.115/)；`kg-sources/REANO/paper.pdf`；读 §3.1–3.3、§4、附录生成图消融。
- **技术总结**：对已召回段落先用 spaCy／TAGME 识别实体；段内关系由在 REBEL 上训练的 DocuNet 提取，段间实体关系从 Wikidata 补入。T5 上下文实体表示加关系感知 GNN，按 query 与头／关系／尾向量匹配选 top-10 三元组，拼成额外 FiD 段落。KG generator 和 reader 分阶段训练；reader 联合回答交叉熵与相关实体分布 KL，后者以问题实体到答案实体路径构造弱监督。
- **优点**：把文档显式事实与外部跨段关系结合；五个 QA 数据集、FiD 与多个图增强 reader 的对照及统计检验支持 reader 增强，训练细节清楚。
- **不足**：2Wiki／MuSiQue 直接采用数据集附带的候选段落，因此不证明开放全库召回；外部补边可能并不在原文中，有出处语义差异。离散 top-K 与抽图使整体非完全可微，作者也明确分开训练；原文 API 访问、关系抽取和 FiD 成本不宜隐去。

<a id="k12"></a>

### [K12] Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs（Graph-CoT；ACL 2024）

- **原文与阅读**：[论文](https://arxiv.org/abs/2404.07103)；`kg-sources/Graph-CoT/paper.pdf`；读 §3–5 及演示消融。
- **技术总结**：提出 GRBench，五大领域十张图，174 个手写模板生成 1,740 题；用程序图函数计算可回答题真值。Graph-CoT 每轮执行“LLM 判断还需什么→生成图函数调用→实际执行返回”：算子包括 RetrieveNode、NodeFeature、NeighborCheck、NodeDegree，直到 Finish。由少量 in-context 轨迹示范如何组合算子，不需将整图塞入提示。
- **优点**：明确测计数、邻居、属性等结构能力，适合作为图检索交互／查询规划的基准；对文本 RAG、一跳 Graph RAG 有控制比较，图本身含百万级节点。
- **不足**：测试题数和模板多样性远小于图规模，不能由大图规模直接宣称开放问题已覆盖。原文无演示时几乎无法工作，展示轨迹是关键依赖；LLM 函数选择和累计错误仍在。Hard 类有些答案不能直接从图读出，评价使用 ROUGE-L／GPT-4，需与精确图查询正确率分开。

<a id="k13"></a>

### [K13] GFM-RAG: Graph Foundation Model for Retrieval Augmented Generation（2025，NeurIPS）

- **原文与阅读**：[论文](https://arxiv.org/abs/2502.01113)、[作者正式引用](https://github.com/RManLuo/gfm-rag)；`kg-sources/gfm-rag/paper.pdf`；读 §3.1–3.3、§4.1–4.8 与训练设置。
- **技术总结**：OpenIE+相似实体归并形成 KG，保存实体—文档倒排矩阵。以文本编码器对齐问题、关系，问题实体初始化为 query 向量，其他实体为零；NBFNet 式 query-dependent GNN 用 DistMult 消息与聚合预测相关实体。先做遮实体 KG completion 预训练，再用支持文档内实体监督微调，目标结合 BCE 和排序项。取 top-T 实体后按文档频次倒数赋权、累加给文档，返回 top-K 原文，不用逐跳 LLM。
- **优点**：8M 参数检索器在 60 张图训练，原文提供未见领域迁移、两阶段训练、图规模和推理效率研究；可与 IRCoT 组合。
- **不足**：需大规模多图训练与离线抽图；6 层全图相关计算的空间／时间需在真实库量级测。倒排映射、频率惩罚本身已有，不是新 BCviz 贡献。**版本注意**：后续 G-reasoner 正文脚注说明修复 GFM-RAG 的 R@k 计算 bug 并重评；不能直接将两篇旧／新召回表拼接作排行榜，应重跑相同评价代码。

<a id="k14"></a>

### [K14] G-reasoner: Foundation Models for Unified Reasoning over Graph-structured Knowledge（2025 预印本，ICLR 2026）

- **原文与阅读**：[论文](https://arxiv.org/abs/2509.24276)；`kg-sources/G-reasoner/paper.pdf`（页首确认 ICLR 2026）；读 §4.1–4.3、§5、分布式消息传递与指标更正脚注。
- **技术总结**：QuadGraph 统一 attribute/entity/document/community 四类节点与跨层关系。query-dependent GNN 同时使用原始节点文本、关系向量和查询种子，type-specific predictor 对各类型打相关分数；训练结合稀疏相关节点监督与冻结文本 teacher 的全节点 Bernoulli 分布蒸馏。34M 参数模型用混精、METIS 划分与跨 GPU 消息交换扩展；取各类型 top-k 内容给 LLM。
- **优点**：统一不同现有构图方式，六数据集评测问答／证据召回与跨图结构迁移，并测蒸馏、文本、图模型消融；证明纯结构启发式之外，已存在强可迁移学习检索器。
- **不足**：模型训练、teacher 编码、多层图建设和分布式边界通信均有成本；每类型 top-k 不等于全局 token 预算最优，密集冗余仍可能挤掉桥接证据。作者表中的部分旧系统缺失／重评结果不能理解为统一官方榜单。分析：BCviz 可作为候选预筛／紧凑底层，但必须测是否牺牲此类强学习器的证据召回。

## 文本图、层次检索与低成本索引

<a id="s01"></a>

### [S01] Knowledge Graph Prompting for Multi-Document Question Answering（KGP；2023 预印本，AAAI 2024）

- **原文与阅读**：[论文](https://arxiv.org/abs/2308.11730)；本地全文 `system-sources/KGP.pdf`；读 §3–5、§8.3、构图和 traversal 消融。这里 KG 的主要节点是段落、页、表，并不全是实体三元组。
- **技术总结**：以 TF-IDF 共同关键词、TAGME 共享实体或 KNN 语义相似度连接段落；KNN-MDR 编码器用“已有支持段落→下一支持段落”监督训练。页、表节点保留 PDF 结构。问题先分内容型和结构型，结构型直接定位页表；内容型以 TF-IDF 选种子，维护路径队列及候选邻居，T5/LLaMA traversal agent 根据问题与已访问原文生成下一证据的描述，再匹配真实候选段落，更新前沿直至片段预算用尽。训练生成的证据只是导航提示，实际上下文来自文档。
- **优点**：把多文档关联检索和版面结构纳入统一图；实验覆盖 HotpotQA、IIRC、2Wiki、MuSiQue、PDFTriage，固定片段数预算比较不同 traversal agent，检查图密度、分支数、规模的影响，证据比单看答案摘要充分。
- **不足**：图更密时召回提高但精度、邻居匹配延迟变差；固定预算下分支过大会挤占种子覆盖，性能先增后降。分析：共享词不等于逻辑支持，训练分布和实体链接限制跨域；这里的段落数预算也不等同于真实 token/总延迟约束，适合为 BCviz 候选剪枝提供对照。

<a id="s02"></a>

### [S02] GRAG: Graph Retrieval-Augmented Generation（2024 预印本；所读 arXiv 版本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2405.16506)；`system-sources/GRAG.pdf`；读 §3–5、§5.3–5.4 与附录的描述转换。注意名称 **GRAG** 与 Microsoft **GraphRAG** 是不同工作。
- **技术总结**：为每个节点预计算 K-hop ego-graph，把节点和边的文本经 SentenceBERT 编码后均值池化为子图向量。查询检索 top-N ego-graph 并合并；两个 MLP 按查询与节点／边向量差异产生 soft-pruning 系数，控制 GNN 消息传播。生成侧同时给冻结 LLM 一枚经 GNN+MLP 对齐的软图提示，以及 BFS 树先序遍历并补回非树边的层次文本描述；用回答损失训练剪枝、图编码与投影模块，另测 LoRA。将子图联合效用近似为各 ego-graph 效用和是启发式分解，不是有界近似最优性证明。
- **优点**：显式检索子图并保留非树边，比只检索孤立三元组更重视拓扑。WebQSP、ExplaGraphs 的模块消融显示软剪枝、图编码和原文描述均重要；额外评估跨数据迁移和 100 样本的引用节点有效性。
- **不足**：ego-graph 增大可能向量过平滑且训练推理变慢，top-N 从 15 到 20 的设置出现退化；代码／论文所谓线性候选检索不意味着所有 K-hop 邻域物化为线性空间。100 样本中引用图实体存在，不证明完整答案事实正确。分析：soft pruning 主要抑制图表示而非删除全部硬提示 token；新索引应比较实际端到端 token、图物化空间和延迟。

<a id="s03"></a>

### [S03] ArchRAG: Attributed Community-based Hierarchical Retrieval-Augmented Generation（2025 预印本；所读 arXiv 版本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2502.09891)；`system-sources/ArchRAG.pdf`；读算法 1–2、Offline Indexing、Online Retrieval、实验与消融（PDF pp.3–7）。
- **技术总结**：LLM 构建实体关系图，以属性相似性补充边并做加权社区检测，为社区生成摘要，再把社区当作新节点重复聚类，形成多级 attributed communities。C-HNSW 每层存对应粒度实体或社区；层内近邻边与层间近邻链接支持自顶向下搜索，复用上层候选作为下层入口，各层都返回相关内容。LLM 对各层结果生成带相关分数的分析报告，排序、截断、汇总回答。原文算法 1 权重写作 `1−cos`，复现时需与所选聚类的相似度／距离约定核对，不能自行假定完全一致。
- **优点**：同时检索具体实体和抽象社区，明确把查询相关的多粒度索引作为系统问题；在 Multihop-RAG、HotpotQA、NarrativeQA 和附加数据集比较质量、索引及查询成本，并有社区、单层和直接提示消融。
- **不足**：社区摘要及全图关系抽取仍有离线成本；ANN 与摘要过滤均不保证最优证据覆盖。实验对部分基线设置三天超时，缺失项不能当零分；与 GraphRAG-Global 的高倍成本差异同时反映查询范式区别。分析：已有社区 ANN 索引，因此 BCviz 不能只以“为图加索引”主张创新，应展示不同检索算子、可证剪枝和空间收益。

<a id="s04"></a>

### [S04] KET-RAG: A Cost-Efficient Multi-Granular Indexing Framework for Graph-RAG（KDD 2025）

- **原文与阅读**：[论文](https://arxiv.org/abs/2502.09304)、[正式 DOI](https://doi.org/10.1145/3711896.3737012)；`system-sources/KET-RAG.pdf`（v2）；读 §4–6、算法 3–4、§5.3 成本分析及表 2–3。
- **技术总结**：先建混合词汇／语义 KNN chunk 图，以 PageRank 选比例 β 的 core chunks，仅对这些调用 LLM 抽关系得到 KG skeleton。全部语料则用普通分词构建 keyword–subchunk 二部图，关键词向量为包含它的句向量均值。在线将 token 预算 λ 按 θ 分给 skeleton 的实体／关系局部检索及关键词通道；后者按 query–keyword 相似度扩展候选邻接文本至约两倍子预算，再按 query–chunk 相似度截取实际预算。两路原文拼接后回答。
- **优点**：直接研究构图成本而不只问答精度；三个数据集、每个采样 500 题，比较 13 种配置以及 skeleton、keyword、随机／PageRank 选点消融。给出输入 token 成本模型 `β·ITC_KG+3ℓ|T|c_e`，说明省下的是关系抽取，embedding 计算并未消失。
- **不足**：Coverage 指“上下文出现答案”，不是完整推理链或全部金标准支持段落召回；β、θ 多为固定配置，缺查询自适应预算与严格最优性。实验主要使用抽样形成的数千／数万段落语料，不证明 TB 规模。**对 BCviz 最直接的先行工作之一**：低成本关键词—文本二部图、预算划分和双通道已经存在；应与纯 Keyword-RAG 也比较，而非只打昂贵 GraphRAG。

<a id="s05"></a>

### [S05] E²GraphRAG: Streamlining Graph-based RAG for High Efficiency and Effectiveness（2025，所读 arXiv v4）

- **原文与阅读**：[论文](https://arxiv.org/abs/2505.24226)；`system-sources/E2GraphRAG.pdf`；读 §3–4、算法附录与成本讨论，重点 PDF pp.3–8。
- **技术总结**：按原文顺序每 g 个 chunk 递归摘要，建立树；同时以 spaCy 抽实体及普通名词，在同句共现实体间加权边，并维护 entity→chunk、chunk→entity 两向索引。在线问题无有效实体时检索 collapsed summary tree；有实体但无近距离实体对时，先稠密召回，再按实体出现数重排。存在 h-hop 实体对时，求两实体倒排列表交集，合并不同实体对的候选；候选过多则逐步减 h，仍超预算时按实体覆盖数、出现频次筛选，最后去重并合并相邻重叠块。
- **优点**：图检索阶段不需要 LLM 调用，CPU 实体抽取可与 GPU 摘要并行；在长篇 NovelQA、InfiniteBench 的选择题／问答任务测构建与检索时间，支持 7B–8B 本地模型。原文明确出现“两个实体共同支持的 chunk”交集算子，是 BCviz 稠密二部证据检索的重要近邻。
- **不足**：表 1 有些任务质量低于 GraphRAG-Local，不是全面精度领先；速度表的 QT 是检索而非含回答生成。单实体问题被导向全局路由未必符合语义；共现交集可能漏掉分别位于不同原文的桥接事实，属于机制风险。实验中小模型结构化输出重试显著拖累部分基线，不能外推为所有模型、硬件上的普遍倍数优势。

<a id="s06"></a>

### [S06] KG-Retriever: Efficient Knowledge Indexing for Retrieval-Augmented Large Language Models（2024 预印本；所读版本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2412.05547)；`system-sources/KG-Retriever.pdf`；读 §3、§4.1–4.3、参数和双层图消融。
- **技术总结**：构建双层 HIG：下层用 Qwen-72B 抽文档实体／关系，上层对文档语义向量建立 top-K 相似图。查询先稠密匹配 N 个文档，再加入一跳邻文档；attentive 版本用文档间余弦作权，多跳版本乘沿途权值。下层仅对候选文档所连实体计算 query 相似度，乘上层权值超过 λ 则返回相关三元组，最多 T 条。回答模型一次读这些三元组，避免逐跳调用回答 LLM；“single retrieval”内部仍有两层匹配和图扩展。
- **优点**：明确区分文档级关联与实体级细节；中英文、单／多跳、长短答案五数据集及实体层／文档层消融支持其作用。三种协同策略便于进行效率和噪声权衡。
- **不足**：原文参数实验显示邻文档或三元组过多会引入噪声，阈值过严又漏证据；昂贵离线抽图成本不可因在线一次作答而忽略。表中 Time 主要描述生成响应耗时，不是完整索引维护成本。分析：仅给三元组可能丢失否定、条件和原文出处；相似文档连接不保证逻辑支持，尚缺明确 token 预算选择和更新一致性保证。

<a id="s07"></a>

### [S07] HYBGRAG: Hybrid Retrieval-Augmented Generation on Textual and Relational Knowledge Bases（2024 预印本，所读 v2 为 2025）

- **原文与阅读**：[论文](https://arxiv.org/abs/2412.16311)；`system-sources/HybGRAG.pdf`；读 §2–4、算法 1、STaRK／CRAG 实验、§4.3 调用成本。
- **技术总结**：将问题拆成文本要求和关系要求。router 识别实体、关系类型并选择纯文本或 hybrid retrieval；hybrid 根据关系从主题实体扩展 ego-graph，多约束取交集，再用关联原文向量排序。validator 结合实际关系路径检验候选；拒绝后 commenter 按预定义错误类别给修正建议，router 再识别并重查，最多 T 轮。用约 30 个有训练集真值确认的成功反馈示例做 ICL，正式推理不用真值；原文 oracle 是诊断上界，不是方法运行条件。
- **优点**：直接暴露图条件与文本条件不可互相替代的问题；在 STaRK-MAG／PRIME 测候选实体检索，在 CRAG 另测端到端答案和幻觉，因而没有混淆两类目标。对路由、验证上下文和反馈分别消融。
- **不足**：多轮 router／validator／commenter 带来串行 API 成本；验证器仍可能自信误判。部分昂贵基线只在 10% 测试题上评测，不能将原表当严格统一全量排行榜。分析：关系交集与倒排查询是现有贡献；后续应研究这些算子的代价模型、缓存与索引，而不是换上二部图名称。

<a id="s08"></a>

### [S08] Don’t Forget to Connect! Improving RAG with Graph-based Reranking（G-RAG；2024 预印本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2405.18414)；`system-sources/GraphRerank.pdf`；读 §3.1–3.2.4、§4、排序指标。某些资源列表写 ACL 2023，时间上与此 arXiv 不符，本文不沿用该标签。
- **技术总结**：先用 DPR 召回 100 段，对每个 question–passage 用 AMRBART 解析 AMR；共享 AMR 概念的段落在文档图连边。节点特征拼接原文与从 AMR 的 question 节点出发的最短路径概念；边特征是共享概念／边数。两层 GNN 同时聚合节点、边，最终以 query 向量与节点向量内积排序，用交叉熵或正负片段 pairwise margin loss 训练；作者发现排序损失对不平衡正负样本较好。
- **优点**：将候选间依赖作为 reranker 的输入，无需重建整个外部 KG；NQ、TriviaQA 的排序实验及特征／GNN／encoder 对照表明跨文档连接能提供信号。另讨论 LLM 离散评分导致并列名次的公平评价。
- **不足**：第一阶段漏掉的文档无法被 rerank 找回，且实现会移除孤立候选，有丢失稀有关键证据的风险；AMR 按 query–document 重解析的真实延迟不能只看 GNN 层数。主证据集中于候选排序，不等同于已证明端到端复杂多跳生成优势。分析：二部图证据压缩也必须保留低度／孤立救援通道。

## 树、超图、稀疏图与适应性推理

<a id="n01"></a>

### [N01] RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval（2024，ICLR）

- **原文与阅读依据**：[论文](https://arxiv.org/abs/2401.18059)；本地全文 `recent-sources/RAPTOR-paper.pdf`、同名 `.txt`；阅读 §3 Methods、§4 Experiments、附录 A–F。归类：层次摘要树，属于广义图索引，不能等同于实体关系 KG。
- **技术总结**：先按约 100 tokens 切块并以 SBERT 编码；UMAP 降维后进行全局和局部 GMM 软聚类，BIC 选簇数，因此一个块可属于多个主题。对每簇用 GPT-3.5-turbo 生成摘要，再编码、聚类、摘要，递归形成多层索引。比较逐层 top-k 遍历与 collapsed-tree：后者把各层节点放入同一向量检索池，在 token 预算内选择不同抽象层次的内容。主实验使用 2,000-token 预算；UnifiedQA 因窗口较小使用 400 tokens，并与基线保持同预算。
- **作者证据与优点**：在 NarrativeQA、QASPER、QuALITY 验证多层摘要对跨段落和全局理解有帮助；collapsed-tree 在选取的 QASPER 子集优于固定层次遍历。聚类不是按原文相邻位置分组，可以汇聚散布的同主题证据。作者还专门检查摘要幻觉，样本约 4% 存在轻微幻觉，报告未明显影响该评测。
- **局限／研判**：摘要生成成本及事实遗漏是索引开销，跨层内容也会重复；collapsed-tree 的效果不能证明“沿树搜索”优越。软聚类意味着实现更接近有共享子节点的层次结构，引用其树模型时应交代。论文没有证明动态更新、删除传播及来源级可追溯性，适合作为多粒度摘要检索基线，不能替代原文证据验证。

<a id="n02"></a>

### [N02] HyperGraphRAG: Retrieval-Augmented Generation via Hypergraph-Structured Knowledge Representation（2025，NeurIPS）

- **原文与阅读依据**：[正式论文](https://proceedings.neurips.cc/paper_files/paper/2025/file/df55ee6e59f8ac4a625219e11fe9ddba-Paper-Conference.pdf)；本地 `recent-sources/HyperGraphRAG-paper.pdf/.txt`；阅读 §3–5、附录的抽取提示与表示证明。归类：n 元事实／超图／二部关联图。
- **技术总结**：LLM 把文本拆成自然语言描述的 n 元事实，超边保存事实描述与置信度，关联实体保存名称、类型、解释和置信度。物理存储采用实体侧与超边侧的二部图，另建实体和超边向量索引。查询既检索问题实体，也直接检索超边；相似度结合抽取分数与阈值过滤，再执行实体→关联超边、超边→全部实体的双向扩展，合并传统 chunk 检索后生成。主设置两侧各取至多 60，chunk 取 5。
- **作者证据与优点**：在医学、农业、计算机、法律、混合五域区分 Binary/N-ary 来源，评测答案 F1、检索语义相似度及 LLM 判分；医学总体 F1 为 35.35，StandardRAG 为 27.90。消融显示实体、超边和原文块融合均有贡献。二部图无损保存“实体属于哪个事实”，这是直接连接 BCviz 的重要表示。
- **局限／研判**：优势不是“二元图不能表示 n 元事实”的绝对结论——增加事实节点同样能无损编码，本文自身正如此实现。自然语言超边和 LLM 自报置信度缺乏严格的概率校准；邻接扩展可能由高频实体带来巨大候选。数据部分按抽取知识生成问题，应补独立人工问题。未提供最大 biclique 索引、去重优化、跨源独立性或有界预算选择保证；这些是可研究空隙，而非已被该论文解决。

<a id="n03"></a>

### [N03] LinearRAG: Linear Graph Retrieval-Augmented Generation on Large-scale Corpora（2025 预印本；ICLR 2026，作者仓库确认录用）

- **原文与阅读依据**：[论文](https://arxiv.org/abs/2510.10114)、[作者录用说明](https://github.com/DEEP-PolyU/LinearRAG)；本地 `recent-sources/LinearRAG-paper.pdf/.txt`；阅读 §3–4、附录规模与复杂度讨论。归类：免关系抽取、实体—句子／段落二部图。
- **技术总结**：使用句子切分与 spaCy NER 构建 Tri-Graph，实际核心为实体—句子 mention 矩阵 M 和实体—段落 contain 矩阵 C；不调用 LLM 抽取关系。查询实体匹配得到初始激活向量；句子与完整问题的相似度加权实体→句子→实体传播，以逐轮 max 合并、阈值剪枝发现桥接实体。第二阶段以这些激活及段落语义分数初始化实体—段落图的重要性，用 PPR 排序段落。稀疏矩阵与小步数传播是效率来源。
- **作者证据与优点**：在 HotpotQA、2Wiki、MuSiQue 和医学数据评测，统一 all-mpnet-base-v2、GPT-4o-mini 和 top-5；2Wiki 的 GPT 判分为 63.70%。效率表报告索引 249.78 秒、检索 0.093 秒，索引／检索无 LLM token；此数字不包含最终答案生成的 token。两阶段各自消融会降分，说明简单二部表示可支撑多跳检索。
- **局限／研判**：线性结论依赖稀疏关系、固定传播轮数及模型推理成本口径，不表示任意查询为常数时间；全量句子相似度仍随语料增长。NER 的别名、指代和领域迁移错误未消失，缺显式关系语义也可能混淆“提到同一实体”与“支持同一事实”。它已占据“二部图更省钱”的基本贡献，BCviz 后续必须证明更强的检索算子或索引优势。

<a id="n04"></a>

### [N04] You Don’t Need Pre-built Graphs for RAG: Retrieval Augmented Generation with Adaptive Reasoning Structures（LogicRAG；2025 预印本，AAAI 2026）

- **原文与阅读依据**：[论文](https://arxiv.org/abs/2508.06105)、[AAAI 版本](https://openreview.net/forum?id=ov1bwU35Mf)；本地 `recent-sources/LogicRAG-paper.pdf/.txt`；阅读框架、Query Logic Dependency Graph、剪枝、Sampling Strategy、实验。归类：查询时规划 DAG，而非离线语料图。
- **技术总结**：LLM 将问题拆为子问题、推断依赖并生成 DAG，以拓扑排序检查无环并安排执行；后续检索显式使用前驱子问题答案。信息不足时动态增加节点／依赖。上下文剪枝将历史检索内容压缩成与查询相关的 rolling memory；图剪枝把同一拓扑层的子问题合成统一查询，减少重复调用。默认不放回地处理子问题，避免 agent 犹豫并反复产生近似查询，最后进行完备性反思。
- **作者证据与优点**：从 HotpotQA、2Wiki、MuSiQue 各取 1,000 题，使用统一 MiniLM、GPT-4o-mini，每轮 top-3。2Wiki 的字符串包含准确率／LLM 判分为 64.7／62.5，HippoRAG2 为 50.0／47.1；MuSiQue 为 30.4／37.5。方法免去语料关系图预构建，适合变化快的语料；剪枝与采样实验支持减少重复 token。
- **局限／研判**：这是把成本移动到每次查询，复杂问题仍需多轮串行 LLM；拓扑无环只验证结构合法，不验证子问题或依赖语义正确。压缩记忆可能删除后续需要的证据，强制前进可能保留早期误答；相同拓扑层也不等于语义相近。作者基准是选取问题形成的中等语料，尚不足证明超大规模在线系统的吞吐与更新优势。

<a id="n05"></a>

### [N05] PathRAG: Pruning Graph-Based Retrieval Augmented Generation with Relational Paths（2025，所读 arXiv 版本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2502.14902)；`recent-sources/PathRAG-paper.pdf`；读 Methodology、Complexity Analysis、实验与消融（PDF pp.3–7）。
- **技术总结**：LLM 抽 query 关键词，向量匹配 N 个实体；对实体对传播资源 `S(v)=Σ αS(u)/outdeg(u)`，当单条外流资源小于 θ 时停止，每节点最多更新一次，减少长／高分叉路径。按路径资源得分保留全局 top-K，将节点及关系描述按路径线性化。问题放开头，最可靠路径放末尾，以应对 lost-in-the-middle。复杂度界针对这种有衰减、阈值的资源传播，不能理解为枚举全部简单路径的多项式算法。
- **优点**：把关系路径作为最终上下文而非仅导航手段；在六个语料上用统一模型、8k 输入预算，测路径格式、资源剪枝及图稀疏性，说明格式和候选选择都影响生成。
- **不足**：主要比较无真值问题的 LLM 成对偏好，不能以胜率证明事实正确；“reliability”是结构传播分数，不是校准可信概率。多个路径重复实体／边会占 token；阈值和每节点一次更新会牺牲某些长桥接路径，需用金标准证据召回单独测量。

<a id="n06"></a>

### [N06] MemGraphRAG: Memory-based Multi-Agent System for Graph Retrieval-Augmented Generation（2026，KDD，所读作者版）

- **原文与阅读**：[论文](https://arxiv.org/abs/2606.00610)、[DOI](https://doi.org/10.1145/3770855.3818074)；`recent-sources/MemGraphRAG-paper.pdf`；读 §4.1–4.3、§5、冲突分类附录；页首含 KDD 2026 会议信息。
- **技术总结**：持久 global memory 分 ontology、fact、passage 三层；抽取 agent 同时产生 schema、事实和出处，schema 频次达阈值才稳定并激活事实。检测 agent 以语义相似和 schema 约束找冲突，处理 agent 回原文判定删除、归并或时间／粒度修正。最终连接类型、事实、原文图并补类型／相似边。查询并行召回 schema／fact／passage，实体按相关 fact 赋初始值，类型乘 log-degree 罚，原文结合 IDF 信息密度，再 PPR 返回片段；无结构候选则退回文本检索。
- **优点**：已正面处理图抽取碎片、冲突、provenance 与动态演化，五类问答及图复用／消融提供支持；是未来“持续维护 GraphRAG”必须补的强先行工作。
- **不足**：LLM 冲突裁决和高频 schema 筛选是启发式，高频不等于正确，罕见关系可能失活。论文未给出数据库 snapshot isolation、撤回后派生证据失效传播的形式语义或局部更新代价界；“global coherence”的描述不能当一致性定理。以其强基线定位版本一致索引才可能形成区别。

<a id="n07"></a>

### [N07] PolyG: Adaptive Graph Traversal for Diverse GraphRAG Questions（2025，所读 arXiv v2）

- **原文与阅读**：[论文](https://arxiv.org/abs/2504.02112)；`recent-sources/PolyG-paper.pdf`；读 §3–6，尤其查询 taxonomy、Cypher 规划执行与表 4。
- **技术总结**：以 `(s,p,o)` 已知／未知归纳四种基本问题及其嵌套。LLM 先分类、分解依赖步骤，再根据中间结果实例化子问题；不同模式分别生成 BFS 邻扩展、meta-path walk、top-k 最短路径／带条件路径的 Cypher。执行失败或空结果回传自纠，最多三次重试；将实体表、关系表和必要路径作为上下文，合成回答。PolyBench 在三个真实图上用 73 模板造 1,200 题并改写。
- **优点**：将选择检索算子和查询计划明确化，不只比较一个固定 PPR；有直接生成 Cypher、Graph-CoT 等对照以及真实延迟／token 成本。
- **不足**：原文也承认自然语言问题不被简单 taxonomy 全覆盖，不能把其命题解读为完备自然语言逻辑；仅部分模板有精确答案，其余主要用 LLM 偏好。执行成功只能证明语法／schema 合法，不保证语义正确。它已经研究“自适应图查询计划”，BCviz 应贡献特定算子及代价估计，而非重复提出 planner。

## 专业领域、代理、强化学习与路由

<a id="x01"></a>

### [X01] KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation（2024 预印本；所读版本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2409.13731)；`extra-sources/KAG.pdf`；读 §2.1–2.4、logical-form reasoner、§3 实验／索引消融，未将框架所有业务组件视为已逐一复现。
- **技术总结**：LLMFriSPG 将严格 schema 的知识层、开放抽取图层、原文 chunk 层与概念树结合；双向索引保留出处与上下文，注入专业术语，做实例归并和概念关系补全。solver 把问题规划为 Retrieval、Sort、Math、Deduce、Output 等逻辑函数，变量传递表示依赖；先执行图检索，置信不足则用 hybrid 文本检索补充，生成器判断是否继续分解。另有面向检索、生成的模型训练模块。
- **优点**：把精确约束、计算和模糊语义检索分开，适合专业知识与业务数据；多跳 QA 上给出图对齐和 logical-form solver 消融，算法不止“把 triples 放提示”。
- **不足**：严格知识层需专家与 schema 成本，概念补边和 LLM 推理不自动获得逻辑可靠性；系统多模块使增益归因困难，必须对齐 backbone 后比较。已存在图文双向索引、逻辑算子与混合求解，因此 BCviz 后续应明确新数据结构和查询语义，不能泛称首次结合符号与 RAG。

<a id="x02"></a>

### [X02] Medical Graph RAG: Towards Safe Medical Large Language Model via Graph Retrieval-Augmented Generation（MedGraphRAG；2024 预印本，CVPR 2025，所读作者版）

- **原文与阅读**：[论文](https://arxiv.org/abs/2408.04187)；`extra-sources/MedicalGraphRAG.pdf`；读 §2 全流程、§3 与临床人员评测。
- **技术总结**：语义滑窗切文档，抽带 UMLS 类型和上下文描述的实体；用户原文图通过相似度链接到医学文献／教材图，再链接到定义词典图，形成来源—定义参考链。对 meta-graph 生成预定义症状、病史等 tag，凝聚层次归并 tag summary。U-Retrieval 自顶向下定位相关 meta-graph，扩实体及跨层邻居得到初答，再沿 tag 层次自底向上改进答案。
- **优点**：专业术语和原始证据／权威定义的区分清楚；多种医学选择题、事实核验及长回答人工评价，比只有模型偏好更接近领域需求。
- **不足**：相似度建立的 reference-of 不是原始文献真正引用／蕴含关系，“safe”标题不代表临床安全证明；tag 抽象、16-hop 邻域等设置可能产生很大候选。定义一致也不保证具体患者结论正确。分析：如果研究来源约束，须把“语义相似链接”和“真实出处”分为不同边类型。

<a id="x03"></a>

### [X03] DALK: Dynamic Co-Augmentation of LLMs and KG to answer Alzheimer’s Disease Questions with Scientific Literature（2024，EMNLP）

- **原文与阅读**：[论文](https://arxiv.org/abs/2405.04819)；`extra-sources/DALK.pdf`；读 §3–5、时间切片与构图消融。
- **技术总结**：以 2011–2021 文献按年份扩充疾病 KG，PubTator 识别实体；对比逐实体对问关系和一次生成所有支持关系两类 LLM 抽取。问题实体链接后检索 k-hop 连接路径及相关邻居，再由回答 LLM 自己重排，仅保留 top-k 事实作答。ADQA 从四个医学考试数据集按领域词及 LLM 判定筛出。
- **优点**：在逐年扩图而非一次静态图中测质量，揭示生成式抽取的较小图可能优于数量更大的噪声图；self-aware rerank 有消融与 k 敏感性。
- **不足**：逐年增加已发表知识不是显式 valid-time／transaction-time 查询，也不覆盖事实撤回和原文删除；self-rerank 在部分短问题反而退化。领域筛选与医学考试题有限，不应外推真实诊断。它已占据“动态图持续加文献”动机，未来需更明确的一致性与维护代价问题。

<a id="x04"></a>

### [X04] GraphReader: Building Graph-based Agent to Enhance Long-Context Abilities of Large Language Models（2024，Findings of EMNLP）

- **原文与阅读**：[正式论文](https://aclanthology.org/2024.findings-emnlp.746/)；`extra-sources/GraphReader.pdf`；读 §3–4、成本／支持事实召回分析及探索工具。
- **技术总结**：文档切块后提取 atomic facts 与 key elements，key element 节点挂原子事实及原文 chunk ID，事实共现连接节点。agent 先计划并选多个起点，按“读节点原子事实→决定读哪些原文块→读相邻块／换邻居／终止”探索，每条路径维护 notebook；最终合并各 notebook 形成答案。粗到细原文读取避免只靠摘要作答。
- **优点**：真实提供检索后回原文的执行过程，支持长上下文下的证据召回；有 chunk size、初始点数与图构建成本分析。
- **不足**：原子事实抽取会遗漏信息，起点和停止策略由 LLM 决定；4k 是单次输入窗口而非完整任务 token，长任务探索平均可消耗数万 token。notebook 汇总／多数票无法保证出处独立或事实正确。未来“可解释阅读工具”不能忽略该类既有 agent 系统。

<a id="x05"></a>

### [X05] Youtu-GraphRAG: Vertically Unified Agents for Graph Retrieval-Augmented Complex Reasoning（2025，所读 arXiv 版本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2508.19855)；`extra-sources/YoutuGraphRAG.pdf`；读 §3.1–3.3、§4 双模式及匿名评测。
- **技术总结**：以实体／关系／属性 schema 约束抽取并允许高置信扩展；上下文 triple 编码后初始 K-means，融合关系重叠与语义相似做社区归并，组织 community、keyword、triple、attribute 四层。retrieval agent 按 schema 拆子问题，结合实体匹配、三元组匹配、社区筛选和有深度界 DFS 多路取证，随历史反思继续。评估区分证据不足必须拒答的 Reject mode 和允许参数知识的 Open mode，并匿名化实体削弱预训练记忆捷径。
- **优点**：把构图 schema 与检索计划联动，强调参数知识污染；是“垂直统一系统”和多粒度路由的重要对照。
- **不足**：schema 合法不等于查询分解语义正确，置信扩展／社区阈值仍需校准；匿名化改善检索归因但可能改变语言自然性。相同任务不同拒答提示会改变排名，因此未来实验必须固定生成协议，不能只换索引后沿用不同 prompt。

<a id="x06"></a>

### [X06] GraphRAG-R1: Graph Retrieval-Augmented Generation with Process-Constrained Reinforcement Learning（2025 预印本，WWW 2026）

- **原文与阅读**：[论文](https://arxiv.org/abs/2507.23581)、[正式 DOI](https://doi.org/10.1145/3774904.3792589)；`extra-sources/GraphRAG-R1-correct.pdf`；读 §3.1–3.3、§4、奖励消融。作者 README 徽章文字与目标链接不一致，以上 ID 经 PDF 标题确认。
- **技术总结**：LLM rollout 中生成检索标签时暂停，调用 HippoRAG2 等图文 hybrid 工具，把返回内容放回历史；policy loss 屏蔽外部检索 token。先冷启动 SFT，再用格式奖励＋PRA 训练调用行为，最后以 `F1·a·exp(−bN)` 的 CAF 奖励优化质量／调用数。PRA 累加几何衰减的调用奖励，鼓励不止一次检索但限制额外收益；与早年路径排名 PRA 是不同缩写。
- **优点**：奖励设计直接针对浅检索和过多调用，有阶段、奖励、图文输入消融及域外 PopQA 测试；使何时调用结构检索成为可学习动作。
- **不足**：调用数奖励不是实际 token、总延迟或建图费用；有界累计奖励不等于对调用次数的硬约束。F1 奖励也不验证引用忠实性，可能依赖答案形式。论文对其它方法“只能单跳”的概括不可直接沿用，HippoRAG 的 PPR 已能聚合多跳结构。

<a id="x07"></a>

### [X07] GraphRAG-Router: Learning Cost-Efficient Routing over GraphRAGs and LLMs with Reinforcement Learning（2026，预印本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2604.16401)；`extra-sources/GraphRAG-Router.pdf`；读 §4.1–4.4、§5、成本分析与路由消融。
- **技术总结**：每轮先选 GraphRAG backend，再选生成模型，可多轮切换；由合成单轮及自反思轨迹作 SFT，再以 GRPO 学格式和最终 EM；第二阶段对成功轨迹惩罚不必要的大模型。训练先重复调用模型池，以最小可靠成功模型定义问题难度和最小所需成本，容易题更强惩罚过度用大模型；测试输入新模型描述以评估泛化。
- **优点**：联合考虑检索基础设施和生成器，而非固定 GraphRAG 加任意 LLM；六类 QA 与成本／准确率及未见 backend 测试，对未来 planner 方向形成直接约束。
- **不足**：训练标签需跨模型／backend 试跑；模型规模成本代理不等于真实 token／队列延迟，离线多图索引成本与调用者体验仍需独立计量。分析：仅做“按问题选 GraphRAG 和模型”已缺乏新意；BCviz 应下沉到证据算子或可证剪枝，而非再训练相似 router。

<a id="x08"></a>

### [X08] Do We Still Need GraphRAG? Benchmarking RAG and GraphRAG for Agentic Search Systems（RAGSearch；2026，预印本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2604.09666)；`extra-sources/AgenticGraphRAGBenchmark.pdf`；读 §4.1–4.4、§5，特别是固定 agent 改 backend 的协议。所读 PDF 含未替换 ACM 模板占位，不能据其模板年份／会议名认定正式发表。
- **技术总结**：统一 think/search/information/answer 接口，把文本 dense、GraphRAG、RAPTOR、HippoRAG2、HyperGraphRAG、LinearRAG 作为可互换工具；分别在 training-free Search-o1／GraphSearch 与 GRPO 优化的 agent 下比较，固定交互奖励，使 agent 控制和图基础设施的作用可拆开。六 QA 任务区分通用事实和多跳。
- **优点**：回答“图的收益是否只是因为多次检索”这一关键混淆，显示复杂多跳与普通 QA 结论不同；对设计受控实验和强 agentic 文本基线有直接价值。
- **不足**：部分汇总表取五种图系统中最优值，不能解释成单一固定系统跨所有题一致胜出；Contain EM 与严格 EM 不同。学习策略、query corpus 和构图质量仍会影响结论；不能由标题反问推断图已无用或总是必要。

<a id="x09"></a>

### [X09] MiniRAG: Towards Extremely Simple Retrieval-Augmented Generation（2025，所读 arXiv v3）

- **原文与阅读**：[论文](https://arxiv.org/abs/2501.06713)；`sources/core/minirag.pdf`；读 §2.1–2.2、§3 与路径评分。
- **技术总结**：构实体和 chunk 两类节点，同时存实体关系边与带局部语义描述的实体—chunk 边。SLM 提取查询实体并预测答案类型，得到起点及候选答案节点；按 k-hop 邻域包含的起点／答案节点数选关键边，再以起点相似度、答案节点覆盖和关键边得分给无环路径排序；沿路径实体取关联 chunk，与初始文本候选相交重排，组合关系、答案类型节点和原文生成。
- **优点**：针对小模型的噪声敏感和摘要能力不足保留原文，个人对话／轻量文档场景提供更贴近低资源部署的对照。
- **不足**：实体—chunk 和类型引导已不是空白；无环路径候选随长度、度数可能组合爆炸，论文的轻量场景不提供通用线性查询保证。分析：为 BCviz 设计救援通道时应与该类路径／类型策略比较，不能以小模型效果自动推出索引更优。

## 近期研究：结构、时间、最小证据与溯源

<a id="f01"></a>

### [F01] LEGO-GraphRAG: Modularizing Graph-Based Retrieval-Augmented Generation for Design Space Exploration（2024 预印本；PVLDB 2025）

- **原文与阅读**：[论文](https://arxiv.org/abs/2411.05844)、[DOI](https://doi.org/10.14778/3748191.3748194)；`frontier-sources/LEGO-GraphRAG.pdf`；读 §3 设计空间、§4–5 成本／质量及图规模实验。
- **技术总结**：把检索拆为可选的 subgraph extraction 与 path retrieval；前者用 RW、k-hop、PPR 或语义模型按点／边／三元组剪枝；后者用枚举、最短路径、一次语义重排或交互式逐跳语义剪枝。以结构／小模型／LLM 在两模块的组合形成 15 个实例，在多个 KGQA 上比较正确率、候选覆盖、时间、token、显存，分析如何把昂贵语义处理放在真正有收益的阶段。
- **优点**：直接揭示抽候选图本身可成为系统瓶颈，支持“先有轻量索引剪枝、后语义评估”的设计动机；可作为组件替换的受控底座。
- **不足**：其主设计空间较偏路径式 KGQA，“PR 必要”是该框架定义，不适用于所有 PPR 直接返回原文系统；多模块优劣仍依赖图和问题分布。只做可组合框架或更换已有子图提取器不足以构成独立创新。

<a id="f02"></a>

### [F02] Core-based Hierarchies for Efficient GraphRAG（2026，KDD）

- **原文与阅读**：[论文](https://arxiv.org/abs/2603.05207)、[DOI](https://doi.org/10.1145/3770855.3818007)；`frontier-sources/CoreHierarchy.pdf`；读 §2.2–6、算法 1–2、RRTC、统计分析，页首确认 KDD 2026。
- **技术总结**：用 k-core 层次替换 Leiden 社区；RkH 将每层分为高 core 连通块和 residual，小块保留、大块按最大簇规模拆分，孤点按 2-hop anchor 归并。M2hC／MRC 进一步合并两点小簇；RRTC 在 leaf communities 之间 round-robin，按 k-shell 与边两端度选择代表边，直到 token 预算用尽，再接原 GraphRAG 摘要／全局回答流程。
- **优点**：以凝聚子图驱动 GraphRAG 层次已成为直接先行研究，不能忽略；多语料、不同模型／裁判、post-cutoff 筛选和人工小样本验证，另测 hierarchy 时间和摘要调用数。
- **不足**：主要研究全局 sensemaking，而非 query-specific 多跳原文证据检索；度数／core 不是语义支持。**理论边界**：core 分解的唯一性不等于对改边全局稳定；一个 n-cycle 删除一条边会使全部节点退出 2-core，可反驳一般性的“少量边只影响同比节点数”外推。其核心算法含大小约束和归并启发式，也不能由标准 O(m) peeling 直接断言整个层次／摘要流程 O(m)。BCviz 的机会应在二部证据算子和查询／维护保证，而非再换凝聚指标造摘要。

<a id="f03"></a>

### [F03] Retrieving Minimal and Sufficient Reasoning Subgraphs with Graph Foundation Models for Path-aware GraphRAG（Gfm-Retriever；2026，预印本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2603.07179)；`frontier-sources/MinimalSubgraph.pdf`；读 §4.1–4.3、§5、命题 4.2–4.4。
- **技术总结**：多域 query-conditioned GFM 先做 KG completion，再加 domain prototype 对比及信息增益正则；冻结 backbone，用 query prompt 和 Gumbel-Sigmoid 门选实体子图。以 query–subgraph InfoNCE、选点 size 和拉普拉斯平滑 penalty 作 label-free IB 代理，与相关实体 BCE／rank 监督一起微调。实体—chunk 倒排聚合时乘门概率、频次倒数与路径参与数，再将有界 DFS 路径和文档一起给 reader。
- **优点**：直接优化 query-conditioned 子图紧凑性与结构，对“最小充分证据子图”形成强近邻；多跳、跨域、检索和问答实验及选择器消融较完整。
- **不足**：IB 的 label-free 代理不意味着整个系统无监督，最终训练仍用相关实体标注；命题依赖 Markov 等假设，信息界不保证某个问题的硬 token 最优、证据蕴含充分或全局最小子图。代码在所读版本承诺发表后开放，复现可得性需核验。后续必须证明不同的查询算子／物理索引，而非重复写 minimal+sufficient 的目标。

<a id="f04"></a>

### [F04] T-GRAG: A Dynamic GraphRAG Framework for Resolving Temporal Conflicts and Redundancy in Knowledge Retrieval（2025，ACM Multimedia）

- **原文与阅读**：[论文](https://arxiv.org/abs/2508.01680)、[DOI](https://doi.org/10.1145/3746027.3755628)；`frontier-sources/T-GRAG.pdf`；读 §2–4、Time-LongQA 与三层检索消融。
- **技术总结**：按文献时间片抽取知识，实体／关系保留各时间的描述；LLM 将多时间条件问题拆为单时间子题。查询先限制时间子图，再匹配节点，再在节点内部检索细粒度知识；根据相关节点及其邻居给 source chunks 打分，原文和结构共同回答，各子题最后聚合。Time-LongQA 来自跨年的 Audi 报告，区分单／双／多时间和无时间问题。
- **优点**：明确测知识演变与时间混淆，对时间筛选、内部知识粒度和 query decomposition 分别消融。
- **不足**：时间片描述和查询拆解不等于双时间数据库语义；来源发布日期不一定等于事实有效时间，LLM 解析也会出错。当前实验不提供撤回／迟到更正的可验证维护协议，不能把“动态”理解为所有更新操作已解决。

<a id="f05"></a>

### [F05] LineageRAG: Harnessing GraphRAG by Constructing Evidence Lineages with Source Grounding（2026，预印本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2608.16004)；`frontier-sources/LineageRAG.pdf`；读 §3–5、set-wise selection、Valid 条件与成本／消融。
- **技术总结**：先把问题转为至多五个 Evidence Demands，记录输入／输出变量和固定 demand ID；各 demand 独立用 HippoRAG2 式 PPR 检索，保留 demand→passage 的所有排名 provenance。LLM 联合挑 k 个互补片段，考虑需求覆盖、重复暴露和同标题冗余；再为每 demand 抽原文 span，校验源片段属于已选集、规范化后为原文子串、类型合法且存在对应检索 provenance。开放需求保持未满足，不强造 span。
- **优点**：需求—片段关系贯穿发现、选集和出处，是二部图 coverage 方向的直接竞争者；匹配同一图索引后做消融，有原文 span 支持审计。
- **不足**：集合选择和 demand 语义仍依赖 LLM，子串存在只证明确有文本而不证明蕴含；k 个片段不等于真实 token 预算。部分对照直接引用不同 reader 的原报告，不能视为完全受控比较。后续研究需明确比其新增的是紧凑物理索引、候选剪枝、可验证约束或更新代价，而不是再提出 provenance+coverage。

<a id="f06"></a>

### [F06] post-graph-rag: A PostgreSQL-Native Bi-Temporal Graph RAG Engine with Temporal Grounding at Synthesis（2026，预印本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2608.24921)；`frontier-sources/PostGraphRAG.pdf`；读 §3–7、§8 评测协议、§9 Limitations，尤其 §5.1–5.5。
- **技术总结**：chunk、entity、community 向量及关系／mention／membership 边同存 PostgreSQL；写入端先验证抽取字段、谓词和否定。关系携带 valid interval、belief-time 创建／失效时间，按显式互斥谓词组与文档顺序 supersede；支持 as-of 与 as-believed-at 过滤。重索引按 doc_key/content_hash 幂等替换，失去最后原文支持的实体／关系 dormancy 而非硬删。检索混合有界 SQL 图扩展、关系向量和词法通道，并把关系有效期放入生成提示。
- **优点**：已有 PostgreSQL 统一存储、双时间、历史保留、可追溯写入，说明这些不能再单独作为未来首次贡献；原文较清楚披露单次实验、基线模型不匹配和重复索引波动。
- **不足**：作者明确指出 entity descriptions 仍是活摘要、未按 belief time 版本化，历史查询可能见到未来编辑的描述；多数机制消融来自修复前 assembler，部分未重跑。默认无时间关系始终有效、按文档顺序 supersession 都有适用前提。它没有证明压缩证据组索引的增量维护或所有派生摘要的一致快照，因此仍留下需严格界定的数据库问题。

## 基准与统一分析

<a id="n08"></a>

### [N08] STARK: Benchmarking LLM Retrieval on Textual and Relational Knowledge Bases（2024，NeurIPS）

- **原文与阅读**：[论文](https://arxiv.org/abs/2404.13207)；`recent-sources/STaRK/media/stark.pdf`；读 §2 构建、§3 评测与附录模板／人工验证。
- **技术总结**：定义 semi-structured KB：图节点关联文本，返回同时满足关系条件和文本条件的节点集合。Amazon、MAG、Prime 三库；先抽关系模板得到候选，选一个答案节点提取文本属性，多 LLM 合成自然问题，再对关系候选逐个验证文本条件，扩充多答案真值。另有 81/84/98 个人工查询测试集；比较向量检索、multi-vector 和 LLM rerank 等。
- **优点**：百万节点、数千万关系与长文本，是测试结构过滤＋语义评分的重要系统负载；MRR、Hit@k、Recall@k 衡量候选检索，不混同生成流畅度。多答案查询能暴露只命中一个答案的偏差。
- **不足**：合成查询与 LLM 过滤可能有分布和不完整标注偏差，人工查询集较小；它并非完整文档生成／引用 benchmark。若 BCviz 输入是实体—chunk 图，不能原样照搬 KG schema，应明确映射、查询类型和答案语义。

<a id="n09"></a>

### [N09] When to Use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation（GraphRAG-Bench；2025 预印本，ICLR 2026）

- **原文与阅读**：[论文](https://arxiv.org/abs/2506.05690)；`recent-sources/GraphRAG-Bench-paper.pdf`（v3）；读 §3 数据构建／指标、§4 结果与附录证据生成。早期标题含“GraphRAG-Bench”，按同一 arXiv ID 合并，不算两篇。
- **技术总结**：将医学指南与旧小说构成密集／松散语料，从结构化证据生成问题，分事实、复杂推理、上下文摘要、创造性生成四级；分阶段测图节点／边／度／聚类系数、检索 relevance／evidence recall、答案 accuracy／faithfulness／coverage，比较七种 GraphRAG 与 rerank 文本 RAG。
- **优点**：显示简单事实上文本 RAG 可以相当或更好，图方法的相对优势随任务而变；将检索召回和无关内容分开，适合构造质量—成本 Pareto 而不是只报答案均分。
- **不足**：节点更多、度更高不是图质量真实性证明；二部图天然无三角，不能直接用普通聚类系数对实体—事实图判优劣。问题由抽取结构生成，可能偏向构图范式；creative task 的偏好／忠实度不等于可执行事实查询。评测中的 LLM 判分与人工金标准须区分。

<a id="n10"></a>

### [N10] CRAG — Comprehensive RAG Benchmark（2024，NeurIPS Datasets and Benchmarks）

- **原文与阅读**：[论文](https://arxiv.org/abs/2406.04744)；`recent-sources/CRAG-paper.pdf`；读 §2–5、QA 构建与评分；**与 Corrective RAG 同缩写但不同论文。**
- **技术总结**：4,409 题、五域、八种问题，覆盖时间变化、长尾、聚合和错误前提。Task1 给少量网页，Task2 再给 mock KG API，Task3 给更多网页和 API；数据包含 2,425 web 题、1,984 KG 题，以题模板与人工写题混合构造。评测正确、错误／幻觉、缺答，允许拒答；多候选测试排名和异源证据融合。
- **优点**：公开固定 API 场景与时间基准，可测旧信息污染和结构／文本组合，避免只在静态 Wikipedia 多跳上宣称可靠。
- **不足**：原任务本身不覆盖真实在线 search retrieval，网页候选已经给定；固定 mock 服务不等同持续更新的数据库实验。对 BCviz 的动态研究可复用问答类型，但仍需另造可重复的插入／删除／更正 workload 和有效时间真值。

<a id="n11"></a>

### [N11] In-depth Analysis of Graph-based RAG in a Unified Framework（DIGIMON；PVLDB 18(13):5623–5637，2025；所读 arXiv v2 于 2026 更新）

- **原文与阅读**：[论文](https://arxiv.org/abs/2503.04338)、[DOI](https://doi.org/10.14778/3773731.3773738)；`recent-sources/DIGIMON-paper.pdf`；读 §3–7、表 2–6 及模块实验。DIGIMON 是框架名，并非论文标题。
- **技术总结**：将管线拆为 graph building、index construction、operator configuration、retrieval & generation；比较 passage graph／tree／KG／textual KG／rich KG，节点／关系／社区索引和 19 个检索算子。重实现代表系统，统一 Llama3-8B、BGE-M3、上下文设置，在具体与抽象 QA 测质量、构图／索引 token、查询成本，并重组已有算子寻找更好配置。
- **优点**：直接面向数据库系统研究的模块归因；指出保留原文、切块、检索粒度和任务类型会改变结论，提供框架作为受控实验底座。
- **不足**：统一重实现不等同各官方系统的最佳配置；较大语料上的 RAPTOR 改为 K-means，超时项缺失，不能无条件比较为原算法。19 算子覆盖的是所研究实现，不是未来算法完备集合。后续只贡献模块化或“组合现有算子”很容易与该文重合，需要新的结构算子／理论／更新协议。

## 综述与文献入口

<a id="v01"></a>

### [V01] Graph Retrieval-Augmented Generation: A Survey（2024 起，所读更新版）

- **原文与阅读**：[论文](https://arxiv.org/abs/2408.08921)；`recent-sources/Survey-Graph-paper.pdf`；重点核对 §5–7 的索引、检索、生成分类与定义，结合 KBQA 边界和训练讨论。
- **内容与技术结构**：以 graph-based indexing → graph-guided retrieval → graph-enhanced generation 组织；索引区分图／文本／向量／混合，检索区分非参数／LM／GNN、单次／多阶段／迭代、节点／三元组／路径／子图粒度；生成又区分图模型、语言模型及串并联组合。
- **优点**：提供跨命名方法的可比组件和反向引用入口，适合检查是否遗漏某个算法族。
- **局限**：分类不是新检索算法，没有统一重跑的质量—成本对照；其引用和版本截止限制后续覆盖。不能用综述的概括代替对具体方法原文的核对，本文核心条目另列实际正文证据。

<a id="v02"></a>

### [V02] A Survey of Graph Retrieval-Augmented Generation for Customized Large Language Models（2025，所读 v3）

- **原文与阅读**：[论文](https://arxiv.org/abs/2501.13958)、[持续维护列表](https://github.com/DEEP-PolyU/Awesome-GraphRAG)；`recent-sources/Survey-GraphRAG-paper.pdf`；重点读 knowledge organization、retrieval techniques/strategies、integration 及比较表。
- **内容与技术结构**：按图作为 knowledge carrier、作为原文索引、hybrid 三种角色划分；检索从相似匹配、逻辑、GNN、LLM、RL 分解，另区分多轮／后处理／混合策略；将路径／子图微调与 ICL 图增强推理、图协同修正分别讨论。
- **优点**：特别适合定位 BCviz 是“底层索引／检索算子”贡献，而不是另造领域知识载体；资源表有较丰富长尾方法。
- **局限**：同一方法跨栏出现不能算多篇；不同资源版本对方法角色的描述有差异，须按实际管线判断。列表中的年份／venue 和链接偶有不一致，本调研以原文及正式记录校正。

<a id="v03"></a>

### [V03] Retrieval-Augmented Generation with Graphs (GraphRAG)（2025，所读综述版本）

- **原文与阅读**：[论文](https://arxiv.org/abs/2501.00309)、[资源列表](https://github.com/Graph-RAG/GraphRAG)；`recent-sources/Survey-Graphs-paper.pdf`；重点核对通用框架的 query processor、retriever、organizer、generator 与领域分类，而非声称逐篇重读其全部数百条引用。
- **内容与技术结构**：把 query 结构化／分解、关系匹配、学习图表示检索、图剪枝及格式化作为独立层；按 KG、文档、科学、社交、规划等领域讨论不同图输入及生成目标。包括节点分类、分子图生成等宽义任务，因此其 GraphRAG 边界比“文档知识问答”更宽。
- **优点**：最适合排查跨领域遗漏和区别 organizer 与 retriever 的收益，提示图数据的归纳偏置与迁移问题。
- **局限**：不能将其全部广义图学习工作都计入现代文档 RAG；它既不是检索系统的统一实验排行榜，也不保证截至今天全部新论文。本文明确缩小主语料到与证据检索／问答／摘要直接相关的方法。

## 与用户研究的连接：BCviz

<a id="bc01"></a>

### [BC01] BCviz: A Linear-Space Index for Mining and Visualizing Cohesive Bipartite Subgraphs（PACMMOD / SIGMOD 2025）

- **来源与阅读**：[正式记录](https://doi.org/10.1145/3709666)。用户提供的 27 页正式 PDF；已核对 §2–8，重点 Definition 3.1、Theorem 3.2/4.1/4.2/5.4、Algorithm 1–4、§7 限制和 §8 实验。本文不是 GraphRAG 方法，而是后续研究可以继承的二部图索引基础。
- **技术总结**：对 MEB/MVB/MBB 分别定义包含一条边的最大 biclique 大小 σ(u,v)。用优先队列按顶点与已经排序邻居的最大边凝聚度决定排列 π；保存两个长度为 n=|U|+|V| 的数组 V、C，C 是相对先前邻居的局部最大凝聚度。阈值 θ 的 peak interval 定位包含足够大 biclique 的候选诱导子图；结合 (t,s)-core 剥离、初始 biclique 下界和现有精确搜索逐步缩小候选。原始 BCviz 的索引是 Θ(n) 空间，但计算精确边凝聚度很贵。BCviz+ 在邻居诱导二部图上逐步提高 core 阈值，利用对侧第 α 大度给出 biclique 大小上界；Algorithm 3 对单个该诱导图的 m 条边耗时 O(m)。保守上界允许继续精确查询。BCviz− 的 one-spot 策略进一步省略部分凝聚度更新，属于近似索引，不能继承相同的无条件精确性。
- **优点**：将结构化候选削减与具体 biclique 求解器解耦；两数组索引适合重复改变规模阈值的查询和凝聚度曲线浏览。Theorem 4.1/4.2 给出最大 biclique 的候选保留及停止依据；BCviz+ 有理论安全的上界替换。8 个真实二部图及 2,000 组参数的重复查询实验覆盖建索引摊销，且给出了不占优的情形。
- **不足与边界**：Θ(n) 指额外索引，不包括原图、语料和 embedding。BCviz+ 整体构建界为 O(|E| log n+|E|·|H|)，|H| 是最大邻居诱导子图边数，不能说全局构建线性。BCviz− 在本文实验都找到精确解，并不等于对任意输入有确定性精确保证；§6 的结构相关概率分析也不能替代最坏情况证明。§7 明确指出顶点排序难并行、微观信息表达有限，单边更新可能要求对所在连通分量全面重排。论文检索目标是 biclique 大小，而非问题相关性、独立证据或多跳答案充分性；现有定理不能直接迁移为 GraphRAG 召回保证。实验没有语言问答和动态时态一致性验证。


## 工程资料与论文的区别

Microsoft DRIFT、LazyGraphRAG、Fast-GraphRAG 等实现/博客可用于选基线和理解后续工程演进；本报告不将其自动计为独立同行评议论文，也不把软件后续功能追溯为原始论文的算法。引用时应固定实现版本及配置。

## 扩展候选目录：仅元数据发现，尚未逐篇精读

下表用于暴露覆盖缺口，**不具备上文方法核对的证据等级**。来自上述有限 OpenAlex 批次并按标题筛选；可能包含与正文同一工作的不同版本、领域应用或较弱相关记录。出版日期与 venue 未逐项核验，因此只标索引年份；标题不能用来推断算法或优缺点。正文未读条目不能被理解为已经完成全文评述。下一轮应优先补充 2026 年新论文、领域工作和安全评测，持续沿引用链扩展。

| 索引年份 | 标题 | 记录/原文入口 |
|---|---|---|

| 2026 | mKG-RAG: Leveraging Multimodal Knowledge Graphs in Retrieval-Augmented Generation for Knowledge-intensive VQA | [入口](https://doi.org/10.1145/3805712.3809680) |

| 2026 | WildGraphBench: Benchmarking GraphRAG with Wild-Source Corpora | [入口](https://doi.org/10.18653/v1/2026.findings-acl.679) |

| 2026 | WiGRAG: Wireless Graph Retrieval-Augmented Generation for LLM-based Communication Decision-Making | [入口](https://doi.org/10.13140/rg.2.2.17133.35049) |

| 2026 | When to Trust: A Causality-Aware Calibration Framework for Accurate Knowledge Graph Retrieval-Augmented Generation | [入口](http://arxiv.org/abs/2601.09241) |

| 2026 | When Should RAG Use Graphs? Complexity-Aware GraphRAG Routing and Answer Quality Prediction on GraphRAG-Bench-H | [入口](https://doi.org/10.66372/jger.v4i2.5) |

| 2026 | UnWeaving the knots of GraphRAG -- turns out VectorRAG is almost enough | [入口](https://doi.org/10.48550/arxiv.2603.29875) |

| 2026 | TruthfulRAG: Resolving Factual-level Conflicts in Retrieval-Augmented Generation with Knowledge Graphs | [入口](https://doi.org/10.1609/aaai.v40i38.40489) |

| 2026 | Towards Self-cognitive Exploration: Metacognitive Knowledge Graph Retrieval Augmented Generation | [入口](https://doi.org/10.1145/3770854.3780156) |

| 2026 | Toward Robust GraphRAG: Mitigating Retrieval Drift and Hallucination from Imperfect Knowledge Graphs | [入口](https://doi.org/10.48550/arxiv.2603.14828) |

| 2026 | TopoGraphRAG-Bench: Evaluating Multimodal GraphRAG on Layout-Grounded Evidence Reasoning | [入口](https://doi.org/10.48550/arxiv.2610.09360) |

| 2026 | Temporal-spatial reasoning over hypergraph knowledge structures for multimodal retrieval-augmented generation | [入口](https://doi.org/10.1038/s41598-026-63525-9) |

| 2026 | TagRAG: Tag-guided Hierarchical Knowledge Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.18653/v1/2026.findings-acl.321) |

| 2026 | Stepwise Contrastive Reasoning for Retrieval-Augmented Generation over Knowledge Graphs | [入口](https://doi.org/10.1609/aaai.v40i18.38549) |

| 2026 | Signal or Noise? Modality Contribution and Cooperation in Multimodal GraphRAG | [入口](https://doi.org/10.48550/arxiv.2609.35304) |

| 2026 | Search Broadly, Seek Evidence on Both Sides, Decide Narrowly: Evidence-Admissible GraphRAG for Longitudinal Clinical Event Verification | [入口](https://doi.org/10.48550/arxiv.2608.22062) |

| 2026 | Rules-Guided Retrieval-Augmented Generation for Temporal Knowledge Graph Reasoning | [入口](https://doi.org/10.1007/978-981-95-5640-3_29) |

| 2026 | Relink: Constructing Query-Driven Evidence Graph On-the-Fly for GraphRAG | [入口](http://arxiv.org/abs/2601.07192) |

| 2026 | RAGU: A Multi-Step GraphRAG Engine with a Compact Domain-Adapted LLM | [入口](https://doi.org/10.48550/arxiv.2607.11683) |

| 2026 | RAG vs. GraphRAG: A Systematic Evaluation and Key Insights | [入口](https://doi.org/10.1145/3770855.3817575) |

| 2026 | Query-adaptive graph retrieval-augmented generation for traceable power-quality knowledge reasoning | [入口](https://doi.org/10.1016/j.egyai.2026.100909) |

| 2026 | Query-Efficient Agentic Graph Extraction Attacks on GraphRAG Systems | [入口](https://arxiv.org/abs/2601.14662) |

| 2026 | Quantifying Retrieval Quality in GraphRAG: A Schema-Agnostic Approach | [入口](https://doi.org/10.63317/5h4oct2t73a2) |

| 2026 | Privacy-protected Retrieval-Augmented Generation for Knowledge Graph Question Answering | [入口](https://doi.org/10.1609/aaai.v40i38.40534) |

| 2026 | PoP-RAG: Holistic Query Planning for GraphRAG | [入口](https://doi.org/10.53941/tgina.2026.100006) |

| 2026 | Plasma GraphRAG: Physics-Grounded Parameter Selection for Gyrokinetic Simulations | [入口](https://doi.org/10.1109/tps.2026.3726786) |

| 2026 | Pipeline Selection for GraphRAG under Budgets | [入口](https://doi.org/10.2139/ssrn.7514460) |

| 2026 | PathRouter: Aligning Rewards with Retrieval Quality in Agentic Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2606.16409) |

| 2026 | Pairwise Ranking and Explicit Feature Interaction for Lightweight Knowledge Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/scecs69812.2026.11565843) |

| 2026 | OptGraph: Large Language Models Enhanced Evolutionary Optimization Via Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2607.27918) |

| 2026 | Operationalizing Cyber Threat Intelligence with GraphRAG | [入口](https://doi.org/10.48550/arxiv.2608.13050) |

| 2026 | Ontology-guided neuro-symbolic GraphRAG for grounded query answering | [入口](https://doi.org/10.1007/s00521-026-12495-0) |

| 2026 | Ontology-aware knowledge graph retrieval-augmented generation for clinical decision support | [入口](https://doi.org/10.36922/aih026210049) |

| 2026 | OMD-GraphRAG: Enhancing GraphRAG with Ontology-Guided Extraction, Multi-Dimensional Clustering and Dual-Channel Fusion | [入口](https://doi.org/10.48550/arxiv.2603.25152) |

| 2026 | NS-ST-GraphRAG: Neuro-Symbolic Spatio-Temporal GraphRAG for Literary Knowledge Processing | [入口](https://doi.org/10.48550/arxiv.2609.05139) |

| 2026 | Multimodal Scene Graph Retrieval-Augmented Generation for Visual Question Answering | [入口](https://doi.org/10.13140/rg.2.2.28958.91202) |

| 2026 | Mixture-of-Experts Knowledge Graph Retrieval-Augmented Generation for Multi-Agent LLM-based Recommendation | [入口](https://doi.org/10.1145/3770855.3817630) |

| 2026 | MixRAG: a Low-cost alternative to a Graph RAG for scientific papers | [入口](https://doi.org/10.5753/bresci.2026.249338) |

| 2026 | MetaRAG: Identifying Website Owner Using Meta-Path-Guided Dynamic Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1145/3800961) |

| 2026 | MegaRAG: Multimodal Knowledge Graph-Based Retrieval Augmented Generation | [入口](https://doi.org/10.18653/v1/2026.acl-long.2218) |

| 2026 | MeAI: Integrating Reinforcement Learning in Graph Retrieval Augmented Generation to Enhance the Performance of Question Answering System | [入口](https://doi.org/10.1007/978-3-032-24399-7_10) |

| 2026 | MeAI++: Improving answer quality with reinforcement learning for graph retrieval-augmented generation | [入口](https://doi.org/10.1177/18758967261468810) |

| 2026 | MOSAIC: Query-Aware Exploration Policy Adaptation for GraphRAG | [入口](https://doi.org/10.48550/arxiv.2609.11065) |

| 2026 | MED-COPILOT: A Medical Assistant Powered by GraphRAG and Similar Patient Case Retrieval | [入口](http://arxiv.org/abs/2603.00460) |

| 2026 | LogicPoison: Logical Attacks on Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48448/0tad-2j49) |

| 2026 | Leveraging GraphRAG for Human–Robot Collaborative Disassembly Sequence Planning in Remanufacturing | [入口](https://doi.org/10.1016/j.procir.2026.02.217) |

| 2026 | LegalGraphRAG: Multi-Agent Graph Retrieval-Augmented Generation for Reliable Legal Reasoning | [入口](https://arxiv.org/abs/2605.28120) |

| 2026 | LEGO: Synergizing Expert GraphRAG and Expert Chain-of-Thought for Legal Reasoning | [入口](https://doi.org/10.48550/arxiv.2609.27009) |

| 2026 | Knowledge-enhanced large language model construction for garlic cultivation using GraphRAG | [入口](https://doi.org/10.3389/fpls.2026.1912355) |

| 2026 | Knowledge Graph-Enhanced Retrieval-Augmented Generation for Nutrigenetics | [入口](https://doi.org/10.1007/978-3-032-17216-7_8) |

| 2026 | Knowledge Graph-Augmented Generation and GraphRAG | [入口](https://doi.org/10.1007/978-981-95-7346-2_9) |

| 2026 | KGiRAG: An Iterative GraphRAG Approach for Responding Sensemaking Queries | [入口](https://arxiv.org/abs/2604.20859) |

| 2026 | KEPo: Knowledge Evolution Poison on Graph-based Retrieval-Augmented Generation | [入口](http://arxiv.org/abs/2603.11501) |

| 2026 | Improving the Reliability of Port Equipment Maintenance Decision Support via Context-Aware Knowledge Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/tr.2026.3696706) |

| 2026 | Hybrid GraphRAG framework for semantic integration and querying of levee infrastructure data | [入口](https://doi.org/10.1007/s12145-026-02234-3) |

| 2026 | Hybrid GraphRAG for Cross-Lingual Legal Citation Retrieval: A Multi-Signal Fusion Approach for Swiss Legal Information Systems | [入口](https://doi.org/10.18535/ijecs/v15i03.5461) |

| 2026 | Hop-Decayed Influence: New Vulnerabilities of Structural Auxiliary Indexing in GraphRAG Pipelines with LLM | [入口](https://doi.org/10.1007/978-3-032-27993-4_24) |

| 2026 | HierCache-RAG: Fast Retrieval-Level Caching for GraphRAG | [入口](https://doi.org/10.5281/zenodo.21839987) |

| 2026 | HVM-GraphRAG: Holistic-View Multimodal Graph Retrieval-Augmented Generation on Complex Document | [入口](https://doi.org/10.48550/arxiv.2607.24861) |

| 2026 | Graphing the European Green Deal: A Graph Retrieval-Augmented Generation Pipeline for Policy Documents Analysis | [入口](https://doi.org/10.3390/su18126193) |

| 2026 | GraphRAG-Vet: A Knowledge Graph-Augmented Large Language Model for Precision Bovine Disease Diagnosis | [入口](https://doi.org/10.3390/computers15040203) |

| 2026 | GraphRAG-Rad: Concept-Aware Radiology Report Generation via Latent Visual-Semantic Retrieval | [入口](https://doi.org/10.18653/v1/2026.eacl-srw.34) |

| 2026 | GraphRAG-LTM: A Layered Threat Modeling Framework for Attacks on Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2610.19549) |

| 2026 | GraphRAG-Induced Dual Knowledge Structure Graphs for Personalized Learning Path Recommendation | [入口](https://doi.org/10.1609/aaai.v40i17.38479) |

| 2026 | GraphRAG-IRL: Personalized Recommendation with Graph-Grounded Inverse Reinforcement Learning and LLM Re-ranking | [入口](https://doi.org/10.48550/arxiv.2604.19128) |

| 2026 | GraphRAG in Healthcare: A Scoping Review of an Emerging Approach | [入口](https://doi.org/10.17605/osf.io/udrme) |

| 2026 | GraphRAG for Context-Aware Question Answering | [入口](https://pratibodh.org/index.php/pratibodh/article/view/498) |

| 2026 | GraphRAG and Knowledge Grounding for Agentic Systems in SAP Environments | [入口](https://doi.org/10.14293/pr2199.004145.v1) |

| 2026 | GraphRAG Under Fire | [入口](https://doi.org/10.1109/sp63933.2026.00070) |

| 2026 | GraphRAG In The Field Of General Question Answering: A Survey | [入口](https://doi.org/10.5281/zenodo.19820517) |

| 2026 | Graph-Enhanced Retrieval-Augmented Generation for Postoperative Patient Question Answering: A Comparative Evaluation of Knowledge Graph, Retrieval-Augmented Generation, and Hybrid GraphRAG Approaches | [入口](https://doi.org/10.3390/bioengineering13101097) |

| 2026 | GalaxyRAG: Graph Retrieval-Augmented Generation for Enterprise Knowledge Systems | [入口](https://doi.org/10.1109/icde65706.2026.00302) |

| 2026 | GRAPH RETRIEVAL-AUGMENTED GENERATION FOR EXPLAINABLE BUSINESS PROCESS COMPLIANCE CHECKING | [入口](https://doi.org/10.13140/rg.2.2.10696.07683) |

| 2026 | GRAG4PM: Graph Retrieval Augmented Generation Framework Adapted for Process Mining | [入口](https://doi.org/10.3390/app16105152) |

| 2026 | From social interaction graphs to knowledge graphs: enabling GraphRAG for LLM-based analysis of online conversations | [入口](https://doi.org/10.59476/ilpmt2026.v2i1.793) |

| 2026 | From Static to Streaming: A Systematic Review and Event-Sourced Framework for GraphRAG in AIOps | [入口](https://doi.org/10.32604/cmc.2026.081005) |

| 2026 | From Node2Vec to GPT-based GraphRAG: scientific impact prediction across graph and language models | [入口](https://doi.org/10.48550/arxiv.2605.18410) |

| 2026 | From Flat to Structural: Enhancing Automated Short Answer Grading with GraphRAG | [入口](http://arxiv.org/abs/2603.19276) |

| 2026 | From Evidence-Based Medicine to Knowledge Graph: Retrieval-Augmented Generation for Sports Rehabilitation and a Domain Benchmark | [入口](https://doi.org/10.48550/arxiv.2601.00216) |

| 2026 | FinReflectKG -- HalluBench: GraphRAG Hallucination Benchmark for Financial Question Answering Systems | [入口](https://doi.org/10.48550/arxiv.2603.20252) |

| 2026 | FinAgent: A Privacy-Preserving Multi-Agent Financial Intelligence System with Context-Aware Governance and GraphRAG Reasoning | [入口](https://doi.org/10.22214/ijraset.2026.77845) |

| 2026 | EyeRAG: graph retrieval-augmented generation for safe and accurate clinical dialogue in ophthalmology | [入口](https://doi.org/10.1038/s41746-026-02860-7) |

| 2026 | Exposing Privacy Risks in Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.18653/v1/2026.findings-acl.899) |

| 2026 | Expert Agents for Social and Emotional Learning: An Agentic Graph Retrieval Augmented Generation Approach | [入口](https://doi.org/10.1109/access.2026.3671870) |

| 2026 | Ex-GraphRAG: Interpretable Evidence Routing for Graph-Augmented LLMs | [入口](https://doi.org/10.48550/arxiv.2605.21994) |

| 2026 | Evidence-Informed Occupational Therapy Decision Support Using Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1177/15394492261476597) |

| 2026 | Evaluating Knowledge Graph Based Retrieval Augmented Generation Methods under Knowledge Incompleteness | [入口](https://doi.org/10.65236/iris-ai/proceedings/2025/article/1) |

| 2026 | Evaluating GraphRAG for industrial safety: a case study on LOTO procedure failures | [入口](https://doi.org/10.1016/j.procs.2026.02.243) |

| 2026 | Evaluating GraphRAG for Traceable and Interpretable Question Answering | [入口](https://doi.org/10.1109/acdsa67686.2026.11468256) |

| 2026 | EntropyRAG: Entropy-Aware Retrieval-Augmented Generation for Knowledge Graph Question Answering | [入口](https://doi.org/10.2139/ssrn.6794971) |

| 2026 | Enhancing GraphRAG Using LLM Generated Ontology from Text | [入口](https://doi.org/10.1007/978-3-032-29003-8_25) |

| 2026 | EHRAG: Bridging Semantic Gaps in Lightweight GraphRAG via Hybrid Hypergraph Construction and Retrieval | [入口](https://arxiv.org/abs/2604.17458) |

| 2026 | Dynamic Graph-Retrieval Augmented Generation for Reliable and Explainable Consumer Electronics Recommendation | [入口](https://doi.org/10.48448/168c-2j81) |

| 2026 | DyRAG-KT: Generative Student Simulation via Dynamic Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.2139/ssrn.6676577) |

| 2026 | Design and Implementation of a Semiconductor Supply Chain Knowledge Graph for Developing a GraphRAG-Based Question Answering Model | [入口](https://doi.org/10.24251/hicss.2026.577) |

| 2026 | Defense Against Knowledge Poisoning Attack on GraphRAG | [入口](https://doi.org/10.18653/v1/2026.acl-short.47) |

| 2026 | Deep GraphRAG: A Balanced Approach to Hierarchical Retrieval and Adaptive Integration | [入口](https://doi.org/10.1145/3774905.3795599) |

| 2026 | Cyber-Physical GraphRAG: Safe, Real-Time, and Scalable Orchestration of Large-Scale Autonomous Fleets | [入口](https://doi.org/10.1109/access.2026.3706610) |

| 2026 | CuraView: A Multi-Agent Framework for Medical Hallucination Detection with GraphRAG-Enhanced Knowledge Verification | [入口](https://doi.org/10.48550/arxiv.2605.03476) |

| 2026 | CuraView: A Knowledge-Based Multi-Agent Framework for Patient-Grounded Medical Hallucination Detection with GraphRAG-Enhanced Evidence Verification | [入口](https://doi.org/10.2139/ssrn.7065322) |

| 2026 | Correction to: Research on graph-retrieval augmented generation based on historical text knowledge graphs | [入口](https://doi.org/10.1093/llc/fqag111) |

| 2026 | Corpus-Guided Dual-Path Propagation for Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2609.37661) |

| 2026 | ColGraphRAG: Late-Interaction Evidence Retrieval for Multimodal GraphRAG | [入口](https://doi.org/10.48550/arxiv.2607.16208) |

| 2026 | Cascading automata to improve efficiency of large language models agents with GraphRAG for error analysis | [入口](https://doi.org/10.11591/ijra.v15i1.pp149-161) |

| 2026 | CLG-RAG: Cross-lingual Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/cscwd68734.2026.11582289) |

| 2026 | BubbleRAG: Evidence-Driven Retrieval-Augmented Generation for Black-Box Knowledge Graphs | [入口](https://doi.org/10.48550/arxiv.2603.20309) |

| 2026 | Blast Radius Characterization of Triple-Level Poisoning Attacks in Knowledge Graph Retrieval-Augmented Generation Systems | [入口](https://doi.org/10.21203/rs.3.rs-10016017/v1) |

| 2026 | Beyond Chunks and Graphs: Retrieval-Augmented Generation through Triplet-Driven Thinking | [入口](https://doi.org/10.18653/v1/2026.findings-acl.1310) |

| 2026 | Beyond Chunk-Local Extraction: Cross-Chunk Graph Augmentation for GraphRAG | [入口](https://doi.org/10.48550/arxiv.2605.28004) |

| 2026 | BEACON-SP: Ontology-Grounded GraphRAG Framework for Clinical Suicide Risk Assessment | [入口](https://doi.org/10.48550/arxiv.2610.09026) |

| 2026 | Application of Knowledge Graph-Based GraphRAG in Intelligent Question Answering Systems | [入口](https://doi.org/10.54254/2755-2721/2026.ast36546) |

| 2026 | An explainable graph retrieval augmented generation framework for personalized nutrition recommendation | [入口](https://doi.org/10.3389/frai.2026.1808444) |

| 2026 | Agentic Graph Retrieval-Augmented Generation for Auditable Commercial Registry Analysis | [入口](https://doi.org/10.1109/access.2026.3731447) |

| 2026 | AGE: Adaptive-masking for Graph Embedding in Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2607.00052) |

| 2026 | ACE-GraphRAG: Agentic Context Engineering for Hierarchical GraphRAG | [入口](https://doi.org/10.48550/arxiv.2608.01269) |

| 2026 | ABAI at COLIEE 2026 Task 1: Multi-Stage Retrieval with GraphRAG-Enhanced Meta-Learning, and a Post-Hoc Study of the Cross-Validation-to-Test Gap | [入口](https://doi.org/10.48550/arxiv.2609.26237) |

| 2026 | A study on the GraphRAG semantic retrieval algorithm for multimodal data | [入口](https://doi.org/10.1007/s44163-026-02023-3) |

| 2026 | A graph retrieval-augmented generation pipeline for systematic drug target discovery: validation and application to ocular neovascularization | [入口](https://doi.org/10.1093/bib/bbag343) |

| 2026 | A Unified Framework for Context-Aware and Relation-Aware Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1145/3774904.3792720) |

| 2026 | A Multi-Agent and synergistic Knowledge Graph retrieval-augmented generation framework for intelligent maintenance | [入口](https://doi.org/10.1016/j.jmsy.2026.02.016) |

| 2026 | A Hybrid GraphRAG Approach to Generating Explainable Recommendations | [入口](https://doi.org/10.15439/2026f3730) |

| 2026 | A GraphRAG-Based Question-Answering System for Explainable and Advanced Reasoning over Air Quality Insights | [入口](https://doi.org/10.3390/air4010006) |

| 2026 | A Graph Retrieval-Augmented Generation Framework for AI-Powered Supplier Discovery | [入口](https://doi.org/10.17148/ijarcce.2026.15618) |

| 2026 | A Five-Layer Reference Architecture for First-Party Enterprise Knowledge Graphs with GraphRAG Integration and Governance Controls | [入口](https://doi.org/10.53941/aieng.2026.100014) |

| 2026 | 222P A hybrid text-knowledge graph retrieval-augmented generation system for clinical decision support in soft tissue sarcoma | [入口](https://doi.org/10.1016/j.esmorc.2026.100428) |

| 2025 | mmRAG: A Modular Benchmark for Retrieval-Augmented Generation over Text, Tables, and Knowledge Graphs | [入口](https://doi.org/10.1007/978-3-032-09530-5_1) |

| 2025 | VAT-KG: Knowledge-Intensive Multimodal Knowledge Graph Dataset for Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2506.21556) |

| 2025 | Using Retrieval Augmented Generation and Knowledge Graphs to Understand Climate Obstruction | [入口](https://doi.org/10.1109/ghtc66843.2025.11266223) |

| 2025 | UKRAG: A Unified Knowledge Graph to Enhance Retrieval Augmented Generation Performance | [入口](https://doi.org/10.1007/978-3-031-82931-4_1) |

| 2025 | Towards the Application of GraphRAG to Network Security | [入口](https://doi.org/10.32473/flairs.38.1.138895) |

| 2025 | Towards Robust Retrieval-Augmented Generation Based on Knowledge Graph: A Comparative Analysis | [入口](https://doi.org/10.1109/smc58881.2025.11343466) |

| 2025 | Towards Explainable Transaction Risk Analysis With Dual Graph Retrieval Augmented Generation | [入口](https://doi.org/10.1145/3746252.3761562) |

| 2025 | Term-extract-enhanced Python-Programming question answering with GraphRAG | [入口](https://doi.org/10.1049/icp.2025.2838) |

| 2025 | Structured reflective reasoning for precise medical knowledge graph retrieval augmented generation | [入口](https://doi.org/10.1007/s13755-025-00390-2) |

| 2025 | Structured Knowledge for Multi-hop QA: A Comparative Study of GraphRAG and RAG | [入口](https://doi.org/10.21203/rs.3.rs-8283065/v1) |

| 2025 | SkewRoute: Training-Free LLM Routing for Knowledge Graph Retrieval-Augmented Generation via Score Skewness of Retrieved Context | [入口](https://doi.org/10.48448/5z2x-6t49) |

| 2025 | SimGRAG: Leveraging Similar Subgraphs for Knowledge Graphs Driven Retrieval-Augmented Generation | [入口](https://doi.org/10.18653/v1/2025.findings-acl.163) |

| 2025 | SSFGraphRAG: Semantic-Structure Fusion Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/icvisp68610.2025.11451238) |

| 2025 | Right Answer at the Right Time - Temporal Retrieval-Augmented Generation via Graph Summarization | [入口](https://doi.org/10.48550/arxiv.2510.16715) |

| 2025 | Review of Graph Retrieval-Augmented Generation Research | [入口](https://doi.org/10.12677/airr.2025.142040) |

| 2025 | Retrieval-Augmented Generation using Knowledge Graphs for Manufacturing Problem-Solving | [入口](https://doi.org/10.1109/case58245.2025.11164057) |

| 2025 | Retrieval-Augmented Generation for Entity Alignment in Knowledge Graphs: An Incipient Experiment | [入口](https://doi.org/10.1007/978-3-031-94931-9_5) |

| 2025 | Retrieval-Augmented Generation and Knowledge Graphs for Intelligent Ayurvedic Chatbots | [入口](https://doi.org/10.1109/siscon66686.2025.11409308) |

| 2025 | Research on the Reform of Teaching Compiler Principles Empowered by GraphRAG | [入口](https://doi.org/10.1145/3785987.3786106) |

| 2025 | Research on Graph-Retrieval Augmented Generation Based on Historical Text Knowledge Graphs | [入口](https://doi.org/10.48550/arxiv.2506.15241) |

| 2025 | ReGraphRAG: Reorganizing Fragmented Knowledge Graphs for Multi-Perspective Retrieval-Augmented Generation | [入口](https://doi.org/10.18653/v1/2025.findings-emnlp.290) |

| 2025 | Ransomware Detection using LLMs and GraphRAG | [入口](https://doi.org/10.1109/cars67163.2025.11337864) |

| 2025 | ROGRAG: A Robustly Optimized GraphRAG Framework | [入口](https://doi.org/10.18653/v1/2025.acl-demo.58) |

| 2025 | RAG4GFM: Bridging Knowledge Gaps in Graph Foundation Models through Graph Retrieval Augmented Generation | [入口](https://doi.org/10.52202/085713-0281) |

| 2025 | Query-Driven Multimodal GraphRAG: Dynamic Local Knowledge Graph Construction for Online Reasoning | [入口](https://doi.org/10.18653/v1/2025.findings-acl.1100) |

| 2025 | Query-Centric Graph Retrieval Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2509.21237) |

| 2025 | Personalizing Large Language Models using Retrieval Augmented Generation and Knowledge Graph | [入口](https://doi.org/10.1145/3701716.3715473) |

| 2025 | Patient Subset Classification Using Encoded Embeddings And Knowledge Graph Retrieval-Augmented Generation | [入口](https://corescholar.libraries.wright.edu/etd_all/3028) |

| 2025 | Path Pooling: Training-Free Structure Enhancement for Efficient Knowledge Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2503.05203) |

| 2025 | Multilingual graph retrieval-augmented generation for product design using design knowledge | [入口](https://doi.org/10.1080/09544828.2025.2537464) |

| 2025 | Multi-Level Graph Pruning-Based Framework for Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/icme59968.2025.11209364) |

| 2025 | Multi-Agent GraphRAG: A Text-to-Cypher Framework for Labeled Property Graphs | [入口](https://doi.org/10.48550/arxiv.2511.08274) |

| 2025 | Medical Graph RAG: Evidence-based Medical Large Language Model via Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.18653/v1/2025.acl-long.1381) |

| 2025 | MedSumGraph: enhancing GraphRAG for medical QA with summarization and optimized prompts | [入口](https://doi.org/10.1016/j.artmed.2025.103311) |

| 2025 | MedRAG: Enhancing Retrieval-augmented Generation with Knowledge Graph-Elicited Reasoning for Healthcare Copilot | [入口](https://doi.org/10.1145/3696410.3714782) |

| 2025 | Leveraging Graph Retrieval-Augmented Generation to Support Learners’ Understanding of Knowledge Concepts in MOOCs | [入口](https://doi.org/10.1007/978-3-032-00056-9_10) |

| 2025 | LeAK-GraphRAG: A Legal Academic Knowledge GraphRAG Framework with Hybrid Retrieval for Mitigating Hallucinations | [入口](https://doi.org/10.3233/faia251624) |

| 2025 | Knowledge graph-extended retrieval augmented generation for question answering | [入口](https://doi.org/10.1007/s10489-025-06885-5) |

| 2025 | Knowledge graph enhanced retrieval-augmented generation for failure mode and effects analysis | [入口](https://doi.org/10.1016/j.jii.2025.100807) |

| 2025 | Knowledge Graph-based Retrieval-Augmented Generation for Schema Matching | [入口](https://doi.org/10.48550/arxiv.2501.08686) |

| 2025 | Knowledge Graph Retrieval-Augmented Generation for LLM-based Recommendation | [入口](https://doi.org/10.18653/v1/2025.acl-long.1317) |

| 2025 | Knowledge Graph Combined with Retrieval-Augmented Generation for Enhancing LMs Reasoning: A Survey | [入口](https://doi.org/10.54097/h21fky45) |

| 2025 | KGSRAG: Retrieval-Augmented Generation System for Biomedical Information Retrieval and Reasoning Based on Knowledge Graphs and Statements | [入口](https://doi.org/10.36227/techrxiv.175735355.54231550/v1) |

| 2025 | Intelligent Ventilation Knowledge Service System Based on Retrieval-Augmented Generation of Knowledge Graph | [入口](https://doi.org/10.1007/978-3-031-96732-0_41) |

| 2025 | Intelligent Question-Answering on Geomorphology Knowledge Based on Knowledge Graph Retrieval-Augmented Generation Technology | [入口](https://doi.org/10.21203/rs.3.rs-6288322/v1) |

| 2025 | Integrating Knowledge Graph with Retrieval-Augmented Generation for Vietnamese Legal Question Answering | [入口](https://doi.org/10.59232/dst-v5i1p101) |

| 2025 | Integrating Graph Retrieval-Augmented Generation into Prescriptive Recommender Systems | [入口](https://doi.org/10.3390/bdcc9100261) |

| 2025 | Implementing a Knowledge Management System with GraphRAG: A Physical Internet Example | [入口](https://doi.org/10.3390/electronics14244948) |

| 2025 | IRG-RAG: An Iterative Reflective Graph Retrieval-Augmented Generation Method for Chinese Medicine | [入口](https://doi.org/10.1109/bibm66473.2025.11356941) |

| 2025 | Hybrid Multi-Agent GraphRAG for E-Government: Towards a Trustworthy AI Assistant | [入口](https://doi.org/10.3390/app15116315) |

| 2025 | HyP-KGRAG: Hypothetical Path-Based Knowledge Graph Retrieval Augmented Generation with DeepSeek | [入口](https://doi.org/10.5445/ir/1000188236) |

| 2025 | How Significant Are the Real Performance Gains? An Unbiased Evaluation Framework for GraphRAG | [入口](https://doi.org/10.48550/arxiv.2506.06331) |

| 2025 | Hierarchical knowledge graph-based QA systems with retrieval-augmented generation | [入口](https://doi.org/10.1080/17517575.2025.2580477) |

| 2025 | GraphRAG-based Sleep Staging Method Using Multi-Strategy Adaptive Reinforcement Reward Learning and Multilevel Distillation Pruning | [入口](https://doi.org/10.25103/jestr.181.23) |

| 2025 | GraphRAG-Enhanced Dialogue Engine for Domain-Specific Question Answering: A Case Study on the Civil IoT Taiwan Platform | [入口](https://doi.org/10.3390/fi17090414) |

| 2025 | GraphRAG-Enabled Local Large Language Model for Gestational Diabetes Mellitus: Development of a Proof-of-Concept | [入口](https://doi.org/10.2196/76454) |

| 2025 | GraphRAG-Bench: Challenging Domain-Specific Reasoning for Evaluating Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2506.02404) |

| 2025 | GraphRAG-Augmented Mastery Modeling for Student Programming Learning Trajectory Prediction and Explanation Via Fuzzy Clustering | [入口](https://doi.org/10.1109/icdmw69685.2025.00441) |

| 2025 | GraphRAG Makes it Possible to Digest Convoluted Legal Jargon | [入口](https://doi.org/10.1109/cai64502.2025.00268) |

| 2025 | Graph Retrieval-Augmented Generation for Automated Extraction and Classification of Medical Claims | [入口](https://doi.org/10.1109/ictaacs69003.2025.11399366) |

| 2025 | Graph Retrieval Augmented Generation for Privacy-Sensitive Information | [入口](https://doi.org/10.1007/978-3-032-10344-4_28) |

| 2025 | Graph RAG- Enhancing Retrieval-Augmented Generation with Knowledge Graphs | [入口](https://doi.org/10.51219/jaimld/sunil-karthik-kota/664) |

| 2025 | GRAPHxx: DSML engineering for knowledge graph building and streamlining with GraphRAG | [入口](https://doi.org/10.1007/s10270-025-01297-y) |

| 2025 | GRAG-ProSafe QAS: Graph retrieval-augmented generation for process production safety intelligent question and answer system | [入口](https://doi.org/10.1016/j.eswa.2025.129947) |

| 2025 | GRAFT - Graph Retrieval Augmented Generation Fine-Tuning Approach | [入口](https://doi.org/10.1109/bigdata66926.2025.11401495) |

| 2025 | FrOG:Framework of Open GraphRAG | [入口](https://research.wu.ac.at/de/publications/68063797-5c8a-4276-a4e8-a76026ca566f) |

| 2025 | FRAG: A Flexible Modular Framework for Retrieval-Augmented Generation based on Knowledge Graphs | [入口](https://doi.org/10.18653/v1/2025.findings-acl.321) |

| 2025 | Enhancing Public Contract Code analysis with Graph Retrieval-Augmented Generation | [入口](https://hdl.handle.net/11586/556622) |

| 2025 | Enhancing Policy Generation with GraphRAG and YouTube Data: A Logistics Case Study | [入口](https://doi.org/10.3390/electronics14071241) |

| 2025 | Enhance AI agents with GraphRAG on Spanner | [入口](https://doi.org/10.13140/rg.2.2.21854.09287) |

| 2025 | Enabling retrieval-augmented generation and knowledge graphs with discourse analysis | [入口](https://doi.org/10.1016/b978-0-443-30046-2.00003-x) |

| 2025 | Empowering GraphRAG with Knowledge Filtering and Integration | [入口](https://doi.org/10.18653/v1/2025.emnlp-main.1293) |

| 2025 | DyG-RAG: Dynamic Graph Retrieval-Augmented Generation with Event-Centric Reasoning | [入口](https://doi.org/10.48550/arxiv.2507.13396) |

| 2025 | DoraReviewer: Vietnamese Virtual Reviewer with GraphRAG and LLM | [入口](https://doi.org/10.1109/rivf68649.2025.11365128) |

| 2025 | Document GraphRAG: Knowledge Graph Enhanced Retrieval Augmented Generation for Document Question Answering Within the Manufacturing Domain | [入口](https://doi.org/10.3390/electronics14112102) |

| 2025 | DietQA: A Comprehensive Framework for Personalized Multi-Diet Recipe Retrieval Using Knowledge Graphs, Retrieval-Augmented Generation, and Large Language Models | [入口](https://doi.org/10.3390/computers14100412) |

| 2025 | Developing a GraphRAG-enabled local-LLM for Gestational Diabetes Mellitus | [入口](https://doi.org/10.1101/2025.04.28.25326568) |

| 2025 | Detecting Hallucinations in Graph Retrieval-Augmented Generation via Attention Patterns and Semantic Alignment | [入口](https://doi.org/10.48550/arxiv.2512.09148) |

| 2025 | Design-on-Graph: A Graph Retrieval-Augmented Generation-Based Method to Support Manufacturing System Design | [入口](https://doi.org/10.1007/978-3-032-03550-9_27) |

| 2025 | DepCache: A KV Cache Management Framework for GraphRAG with Dependency Attention | [入口](https://doi.org/10.1145/3769778) |

| 2025 | DEMENTIA-PLAN: An Agent-Based Framework for Multi-Knowledge Graph Retrieval-Augmented Generation in Dementia Care | [入口](https://doi.org/10.48550/arxiv.2503.20950) |

| 2025 | Construction of a Maritime Knowledge Graph Using GraphRAG for Entity and Relationship Extraction from Maritime Documents | [入口](https://doi.org/10.4236/jcc.2025.132006) |

| 2025 | Combining Knowledge Graphs and Retrieval Augmented Generation for Enterprise Resource Planning | [入口](https://doi.org/10.1007/978-3-031-88720-8_19) |

| 2025 | BuildingGPT: Query building semantic data using large language models and vector-graph retrieval-augmented generation | [入口](https://doi.org/10.1016/j.buildenv.2025.113855) |

| 2025 | Best Practices for Constructing Knowledge Graphs in Retrieval-Augmented Generation (RAG) Systems | [入口](https://doi.org/10.1109/iccams65118.2025.11234485) |

| 2025 | Automated analysis of construction safety accident videos using a large multimodal model and graph retrieval-augmented generation | [入口](https://doi.org/10.1016/j.autcon.2025.106363) |

| 2025 | Application of GraphRAG to a CAE database | [入口](https://doi.org/10.1299/jsmecmd.2025.38.os24-3) |

| 2025 | Align-GRAG: Anchor and Rationale Guided Dual Alignment for Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2505.16237) |

| 2025 | Advancing engineering research through context-aware and knowledge graph–based retrieval-augmented generation | [入口](https://doi.org/10.3389/frai.2025.1697169) |

| 2025 | Advancing Marketing Video Analysis with Multimodal LLMs and Context-Aware GraphRAG | [入口](https://doi.org/10.2139/ssrn.5517439) |

| 2025 | Addressing the information silo of construction planning constraints – a graph retrieval augmented generation approach | [入口](https://doi.org/10.1108/ecam-08-2024-1066) |

| 2025 | Adaptive GenAI-Empowered Manufacturing Training Using LLMs and GraphRAG | [入口](https://doi.org/10.1115/imece2025-167138) |

| 2025 | A Survey of Knowledge Graph Enhanced Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/icei68356.2025.11603750) |

| 2025 | A Knowledge Graph-Driven Approach for Halal Culinary Recommendation with GraphRAG | [入口](https://doi.org/10.1109/dasa68193.2025.11499031) |

| 2025 | A Graph-Retrieval-Augmented Generation Framework Enhances Decision-Making in the Circular Economy | [入口](https://doi.org/10.21203/rs.3.rs-6795706/v1) |

| 2025 | A Comparative Study of Retrieval-Augmented Generation, Graph Retrieval-Augmented Generation, and Fine-Tuned Large Language Models for Fire Engineering Knowledge Retrieval | [入口](https://doi.org/10.2139/ssrn.5253805) |

| 2024 | TKG-RAG: A Retrieval-Augmented Generation Framework with Text-chunk Knowledge Graph | [入口](https://doi.org/10.1109/acit62805.2024.10877117) |

| 2024 | TCM MLKG-RAG: Traditional Chinese Medicine Intelligent Diagnosis Based on Multi-Layer Knowledge Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/eiecc64539.2024.10929529) |

| 2024 | StructuGraphRAG: Structured Document-Informed Knowledge Graphs for Retrieval-Augmented Generation | [入口](https://doi.org/10.1609/aaaiss.v4i1.31798) |

| 2024 | Speech Recognition Method Based on GraphRAG | [入口](https://doi.org/10.25103/jestr.176.01) |

| 2024 | Soccer-GraphRAG: Applications of GraphRAG in Soccer | [入口](https://doi.org/10.1007/978-3-031-71382-8_1) |

| 2024 | Retrieval-Augmented Generation with Knowledge Graphs for Customer Service Question Answering | [入口](https://doi.org/10.1145/3626772.3661370) |

| 2024 | Nanjing Yunjin intelligent question-answering system based on knowledge graphs and retrieval augmented generation technology | [入口](https://doi.org/10.1186/s40494-024-01231-3) |

| 2024 | Myanmar Law Cases and Proceedings Retrieval with GraphRAG | [入口](https://doi.org/10.1109/bigdata62323.2024.10825155) |

| 2024 | Leveraging LLM based Retrieval-Augmented Generation for Legal Knowledge Graph Completion | [入口](https://doi.org/10.1109/dsc63484.2024.00033) |

| 2024 | Integrating Graph Retrieval-Augmented Generation With Large Language Models for Supplier Discovery | [入口](https://doi.org/10.1115/1.4067389) |

| 2024 | HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction | [入口](https://doi.org/10.1145/3677052.3698671) |

| 2024 | Hierarchical Matching: An Efficient Knowledge Graph Retrieval Method for Retrieval-Augmented Generation | [入口](https://doi.org/10.2139/ssrn.4924672) |

| 2024 | Graph Retrieval-Augmented Generation for Large Language Models: A Survey | [入口](https://doi.org/10.1109/aixset62544.2024.00030) |

| 2024 | Equipping Large Language Models with Memories: A GraphRAG Based Approach | [入口](https://doi.org/10.1109/smc54092.2024.10831551) |

| 2024 | Enhancing Vector based Retrieval Augmented Generation with Contextual Knowledge Graph Construction | [入口](https://doi.org/10.1109/idicaiei61867.2024.10842699) |

| 2024 | Enhancing Startup Success Predictions in Venture Capital: A GraphRAG Augmented Multivariate Time Series Method | [入口](https://doi.org/10.48550/arxiv.2408.09420) |

| 2024 | Enhancing Retrieval Augmented Generation Systems with Knowledge Graphs | [入口](https://doi.org/10.1109/icecet61485.2024.10698122) |

| 2024 | Enhancing Data Traceability: A Knowledge Graph Approach with Retrieval-Augmented Generation | [入口](https://doi.org/10.1109/isriti64779.2024.10963652) |

| 2024 | DynaGRAG / Exploring the Topology of Information for Advancing Language Understanding and Generation in Graph Retrieval-Augmented Generation | [入口](https://doi.org/10.48550/arxiv.2412.18644) |

| 2024 | Document Knowledge Graph to Enhance Question Answering with Retrieval Augmented Generation | [入口](https://doi.org/10.1109/etfa61755.2024.10711054) |

| 2024 | CommunityKG-RAG: Leveraging Community Structures in Knowledge Graphs for Advanced Retrieval-Augmented Generation in Fact-Checking | [入口](https://doi.org/10.48550/arxiv.2408.08535) |

| 2024 | Causal Reasoning in Large Language Models using Causal Graph Retrieval Augmented Generation | [入口](https://doi.org/10.1109/hsi61632.2024.10613566) |


本次候选表共 242 条；该数量只是发现记录数，不是独立已读论文数。部分重命名版本仍可能重复。

## 阅读证据与复核边界

正文包含 74 个唯一编号，其中 BC01 为本次上传全文，V01–V03 为综述分类阅读。每条附来源和具体方法描述；本地全文/文本的路径在条目中给出。检索未覆盖所有数据库分页，也未逐篇精读全部候选；因此不能将此报告称为无遗漏的系统综述。未来新增论文应记录检索日期、规范标题、DOI/arXiv ID、版本、方法章节、实验前提和不支持的推断，再更新方向重叠矩阵。

特别校正：BCviz 为 SIGMOD/PACMMOD 2025；LightRAG 为 Findings of EMNLP 2025；GraphRAG-R1 正文使用 arXiv 2507.23581。发现过程中的错误 PDF（曾命名 cogqa.pdf、GraphRAG-R1.pdf）不作为证据，已使用标题核对后的正确全文。GFM-RAG 与 G-reasoner 的 R@k 对比需注意后者明确提及的前者实现问题，不能直接混用不同版本结果。

研究展望见 [future-graph4RAG.md](future-graph4RAG.md)。
