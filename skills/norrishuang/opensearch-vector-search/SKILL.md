---
name: opensearch-vector-search
description: |
  Amazon OpenSearch 向量搜索专家知识库。提供向量搜索配置、集群调优、量化压缩、成本优化、实例选型和定价估算的完整指导。

  **当以下情况时使用此 Skill**：
  (1) 用户询问 OpenSearch 向量搜索（k-NN）配置、HNSW 参数调优、磁盘模式
  (2) 用户需要向量搜索集群选型、容量规划、实例配置推荐
  (3) 用户询问量化压缩技术（Binary/Byte/FP16/Product Quantization）
  (4) 用户需要估算 OpenSearch 向量搜索成本、定价查询
  (5) 用户询问 OpenSearch 索引策略、分片规划、查询优化
  (6) 用户提到"向量数据库"、"向量搜索"、"k-NN"、"knn_vector"、"embedding search"、"HNSW"
  (7) 用户提到数据量（如"1亿向量"、"100M vectors"）并需要集群配置建议
  (8) 用户询问 OpenSearch 集群 JVM、内存、线程池配置
  (9) 涉及 Amazon OpenSearch Service 定价、成本计算、实例对比
---

# OpenSearch Vector Search Expert

## 知识库结构

根据问题类型，读取对应的 reference 文件：

| 问题类型 | Reference 文件 | 关键词 |
|---------|---------------|--------|
| 向量搜索、k-NN、HNSW、磁盘模式 | `references/vector-search.md` | vector, knn, hnsw, warmup, disk mode, on_disk |
| 量化压缩技术 | `references/quantization-techniques.md` | quantization, compression, binary, byte, fp16, product quantization |
| 成本优化、实例选型、内存计算 | `references/cost-optimization.md` | cost, pricing, instance, memory calculation, cluster sizing, budget |
| 集群调优、JVM、线程池 | `references/cluster-tuning.md` | JVM, heap, thread pool, node role, shard allocation |
| 性能基准、数据集选型 | `references/performance-benchmarks.md` | benchmark, QPS, latency, recall, dataset size |
| 索引策略、mapping | `references/indexing-strategies.md` | index, mapping, shard, replica, lifecycle |
| 查询优化 | `references/query-optimization.md` | query, filter, aggregation, cache, pagination |

## 核心工作流

### 1. 回答向量搜索配置问题

1. 读取 `references/vector-search.md`
2. 根据用户场景（延迟要求、数据规模、QPS）推荐内存模式或磁盘模式
3. 给出具体的 mapping JSON 配置
4. 推荐引擎 FAISS + cosine 相似度 + 7/8 系列实例

### 2. 容量规划与选型（最常见场景）

用户提供向量数量和维度后：

1. 读取 `references/cost-optimization.md` 获取内存计算公式和案例
2. 使用 HNSW 标准内存公式计算（来源: AWS 官方博客）：
   ```
   无量化（float32）:
     内存 = 1.1 × (4 × d + 8 × m) × num_vectors × (replicas + 1) 字节
   
   量化场景（FAISS 引擎，内存中存储压缩向量）:
     FP16 (2x):    内存 = 1.1 × (2 × d + 8 × m) × num_vectors × (replicas + 1)
     Byte (4x):    内存 = 1.1 × (1 × d + 8 × m) × num_vectors × (replicas + 1)
     Binary 4-bit: 内存 = 1.1 × (d/2 + 8 × m) × num_vectors × (replicas + 1)
     Binary 2-bit: 内存 = 1.1 × (d/4 + 8 × m) × num_vectors × (replicas + 1)
     Binary 1-bit: 内存 = 1.1 × (d/8 + 8 × m) × num_vectors × (replicas + 1)
   
   其中: d=向量维度, m=HNSW 连接数(默认16), num_vectors=向量总数
   ```
3. 应用 OpenSearch 节点内存分配规则：
   ```
   JVM Heap = min(节点内存 × 50%, 32GB)
   剩余内存 = 节点内存 - JVM Heap
   KNN 可用内存 = 剩余内存 × 75%  (knn.memory.circuit_breaker.limit=70% 最佳实践下约 35% 节点内存)
   ```
4. 选择实例类型，确保集群总 KNN 可用内存 > 向量索引内存需求
6. 运行定价脚本获取实时价格（见下方）

### 3. 成本估算（含实时定价）

当用户需要成本估算时：

1. 完成上述容量规划
2. 运行定价脚本获取实时价格：
   ```bash
   python3 scripts/get_opensearch_pricing.py --region <region> --instance-type <type>
   ```
3. 计算月度成本：
   ```
   实例成本 = 单价 × 节点数 × (1 + 副本数)
   EBS 成本 = 容量(GB) × $0.08 + 额外 IOPS 费用
   总成本 = 实例成本 + EBS 成本
   ```
4. 对比不同量化方案的成本差异

### 定价脚本用法

```bash
# 查询指定区域所有实例价格
python3 scripts/get_opensearch_pricing.py --region us-east-1

# 查询特定实例类型（不需要 .search 后缀）
python3 scripts/get_opensearch_pricing.py --region us-east-1 --instance-type r7g.xlarge

# JSON 格式输出（便于计算）
python3 scripts/get_opensearch_pricing.py --region us-east-1 --instance-type r7g.xlarge --format json
```

输出字段：instance_type, vcpu, memory_gib, price_per_hour_usd, price_per_month_usd, network

## 推荐默认配置

回答时始终推荐以下默认值（除非用户有特殊需求）：

- **引擎**: FAISS
- **相似度**: cosine
- **实例系列**: r7g/r8g（内存优化）或 or2/om2（OpenSearch 优化）
- **HNSW 参数**: ef_construction=512, m=16
- **量化首选**: Byte (4x) 用于生产，Binary (32x) 用于极致成本优化
- **磁盘模式阈值**: 数据量 > 50M 向量且可接受 100-200ms 延迟时考虑

## 回答模板

回答成本/选型问题时按以下结构组织：

1. **需求确认**：向量数量、维度、QPS、延迟要求
2. **内存计算**：原始大小 → 量化后大小 → 所需 KNN 内存
3. **集群配置**：实例类型 × 数量、分片、副本
4. **成本估算**：实例费 + EBS 费 = 月度总成本
5. **优化建议**：量化方案对比、Reserved Instance 折扣
