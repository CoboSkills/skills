# 集群配置和调优

## 核心概念

OpenSearch 集群性能取决于硬件资源配置、JVM 设置、节点角色分配和操作系统优化。合理的集群架构和资源分配是保证高可用和高性能的基础。

## 常见问题

### 问题 1: JVM 堆内存配置

**症状**:
- 频繁 GC（垃圾回收）
- OutOfMemoryError
- 查询和索引性能下降
- 节点不稳定

**原因**:
JVM 堆内存配置不当会导致频繁 GC 或内存不足。

**解决方案**:

1. 设置堆内存大小（jvm.options）：
```bash
# 设置为物理内存的 50%，但不超过 32GB
-Xms16g
-Xmx16g
```

2. 配置 GC 参数：
```bash
# 使用 G1GC（推荐）
-XX:+UseG1GC
-XX:G1ReservePercent=25
-XX:InitiatingHeapOccupancyPercent=30
```

3. 监控 GC 日志：
```bash
-Xlog:gc*,gc+age=trace,safepoint:file=/var/log/opensearch/gc.log:utctime,pid,tags:filecount=32,filesize=64m
```

**最佳实践**:
- 堆内存设置为物理内存的 50%
- 不超过 32GB（压缩指针限制）
- Xms 和 Xmx 设置相同值（避免动态调整）
- 预留 50% 内存给操作系统缓存
- 使用 G1GC 垃圾回收器
- 监控 GC 频率和停顿时间

### 问题 2: 节点角色分配

**症状**:
- 集群负载不均衡
- 某些节点过载
- 查询和索引相互影响

**原因**:
所有节点承担所有角色会导致资源竞争。

**解决方案**:

1. 专用主节点（Master Node）：
```yaml
# opensearch.yml
node.roles: [cluster_manager]
node.name: master-node-1
```

2. 专用数据节点（Data Node）：
```yaml
# opensearch.yml
node.roles: [data, ingest]
node.name: data-node-1
```

3. 专用协调节点（Coordinating Node）：
```yaml
# opensearch.yml
node.roles: []
node.name: coordinating-node-1
```

4. 推荐集群架构：
```
小型集群（< 10 节点）:
- 3 个主节点（master）
- N 个数据节点（data + ingest）

中型集群（10-50 节点）:
- 3 个专用主节点
- N 个数据节点
- 2-3 个协调节点

大型集群（> 50 节点）:
- 3 个专用主节点
- N 个热数据节点（hot）
- M 个温数据节点（warm）
- 3-5 个协调节点
```

**最佳实践**:
- 主节点数量为奇数（3, 5, 7）
- 主节点不承担数据和查询任务
- 数据节点专注于存储和查询
- 协调节点处理客户端请求和聚合
- 使用节点标签实现数据分层（hot/warm/cold）

### 问题 3: 分片分配和平衡

**症状**:
- 节点磁盘使用不均衡
- 某些节点负载过高
- 分片分配失败

**原因**:
分片分配策略不当或磁盘水位线触发。

**解决方案**:

1. 配置磁盘水位线：
```yaml
# opensearch.yml
cluster.routing.allocation.disk.threshold_enabled: true
cluster.routing.allocation.disk.watermark.low: 85%
cluster.routing.allocation.disk.watermark.high: 90%
cluster.routing.allocation.disk.watermark.flood_stage: 95%
```

2. 手动分配分片：
```bash
POST /_cluster/reroute
{
  "commands": [
    {
      "move": {
        "index": "my_index",
        "shard": 0,
        "from_node": "node1",
        "to_node": "node2"
      }
    }
  ]
}
```

3. 配置分片分配策略：
```yaml
# opensearch.yml
cluster.routing.allocation.awareness.attributes: zone
cluster.routing.allocation.awareness.force.zone.values: zone1,zone2
```

4. 平衡分片：
```bash
PUT /_cluster/settings
{
  "transient": {
    "cluster.routing.rebalance.enable": "all"
  }
}
```

**最佳实践**:
- 设置合理的磁盘水位线（85%/90%/95%）
- 使用分片分配感知（zone awareness）
- 避免单个节点分片过多（< 1000 个）
- 定期监控分片分布
- 使用 allocation filtering 控制分片位置

### 问题 4: 线程池配置

**症状**:
- 请求被拒绝（rejected）
- 线程池队列满
- 查询或索引延迟高

**原因**:
线程池大小不足以处理并发请求。

**解决方案**:

1. 查看线程池状态：
```bash
GET /_cat/thread_pool?v&h=node_name,name,active,queue,rejected
```

2. 调整线程池大小：
```yaml
# opensearch.yml
thread_pool:
  search:
    size: 30
    queue_size: 1000
  write:
    size: 30
    queue_size: 1000
```

3. 动态调整（临时）：
```bash
PUT /_cluster/settings
{
  "transient": {
    "thread_pool.search.queue_size": 2000
  }
}
```

**线程池类型**:
- `search`: 搜索请求
- `write`: 索引、更新、删除请求
- `get`: Get 请求
- `analyze`: 分析请求
- `snapshot`: 快照操作

**最佳实践**:
- search 线程池: CPU 核心数 * 1.5
- write 线程池: CPU 核心数
- 队列大小: 1000-2000
- 监控 rejected 指标
- 避免无限队列（可能导致 OOM）

### 问题 5: 网络和传输配置

**症状**:
- 节点间通信慢
- 集群状态更新延迟
- 网络超时

**原因**:
网络配置不当或带宽不足。

**解决方案**:

1. 配置网络设置：
```yaml
# opensearch.yml
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300

# 压缩传输数据
transport.compress: true

# 超时设置
cluster.publish.timeout: 30s
discovery.request_peers_timeout: 10s
```

2. 配置 TCP 参数：
```yaml
# opensearch.yml
transport.tcp.keep_alive: true
transport.tcp.reuse_address: true
```

3. 操作系统优化：
```bash
# /etc/sysctl.conf
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_tw_reuse = 1
```

**最佳实践**:
- 使用专用网络进行节点间通信
- 启用传输压缩（transport.compress）
- 配置合理的超时时间
- 监控网络延迟和带宽使用
- 使用高速网络（10Gbps+）

## 配置示例

### 生产环境配置（opensearch.yml）

```yaml
# 集群配置
cluster.name: production-cluster
node.name: data-node-1
node.roles: [data, ingest]

# 网络配置
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300
transport.compress: true

# 发现配置
discovery.seed_hosts: ["master-1:9300", "master-2:9300", "master-3:9300"]
cluster.initial_cluster_manager_nodes: ["master-1", "master-2", "master-3"]

# 路径配置
path.data: /var/lib/opensearch
path.logs: /var/log/opensearch

# 内存配置
bootstrap.memory_lock: true

# 分片分配
cluster.routing.allocation.disk.threshold_enabled: true
cluster.routing.allocation.disk.watermark.low: 85%
cluster.routing.allocation.disk.watermark.high: 90%
cluster.routing.allocation.disk.watermark.flood_stage: 95%

# 线程池
thread_pool:
  search:
    size: 30
    queue_size: 1000
  write:
    size: 30
    queue_size: 1000

# 安全配置
plugins.security.ssl.http.enabled: true
plugins.security.ssl.transport.enabled: true
```

### JVM 配置（jvm.options）

```bash
# 堆内存（设置为物理内存的 50%，不超过 32GB）
-Xms16g
-Xmx16g

# GC 配置
-XX:+UseG1GC
-XX:G1ReservePercent=25
-XX:InitiatingHeapOccupancyPercent=30

# GC 日志
-Xlog:gc*,gc+age=trace,safepoint:file=/var/log/opensearch/gc.log:utctime,pid,tags:filecount=32,filesize=64m

# 堆转储（OOM 时）
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/opensearch/heapdump.hprof

# 性能优化
-XX:+AlwaysPreTouch
-Djava.io.tmpdir=/tmp
```

### 操作系统配置

```bash
# /etc/security/limits.conf
opensearch soft nofile 65535
opensearch hard nofile 65535
opensearch soft memlock unlimited
opensearch hard memlock unlimited

# /etc/sysctl.conf
vm.max_map_count=262144
vm.swappiness=1
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=8192
```

## 性能监控

### 关键指标

1. **集群健康**:
```bash
GET /_cluster/health
```

2. **节点统计**:
```bash
GET /_nodes/stats
```

3. **线程池状态**:
```bash
GET /_cat/thread_pool?v
```

4. **分片分配**:
```bash
GET /_cat/shards?v
```

5. **JVM 内存**:
```bash
GET /_nodes/stats/jvm
```

### 告警阈值

- 集群状态: 非 green
- JVM 堆使用率: > 85%
- GC 时间占比: > 10%
- 磁盘使用率: > 85%
- 线程池拒绝率: > 1%
- 查询延迟: > 500ms
- 索引延迟: > 1s

## 容量规划

### 硬件推荐

**数据节点**:
- CPU: 16-32 核
- 内存: 64-128 GB
- 磁盘: SSD，1-4 TB
- 网络: 10 Gbps

**主节点**:
- CPU: 4-8 核
- 内存: 8-16 GB
- 磁盘: SSD，100-200 GB
- 网络: 1-10 Gbps

**协调节点**:
- CPU: 8-16 核
- 内存: 32-64 GB
- 磁盘: SSD，100-200 GB
- 网络: 10 Gbps

### 容量计算

```
数据节点数 = (总数据量 * (1 + 副本数)) / (单节点磁盘容量 * 0.7)
主节点数 = 3（固定）
协调节点数 = max(2, 数据节点数 / 10)
```

## 故障排查

### 常见问题

1. **集群状态 yellow**:
   - 检查副本分片是否未分配
   - 检查节点数量是否足够

2. **集群状态 red**:
   - 检查主分片是否丢失
   - 检查节点是否离线
   - 查看分片分配失败原因

3. **节点频繁重启**:
   - 检查 JVM OOM
   - 检查磁盘空间
   - 查看系统日志

4. **查询慢**:
   - 检查慢查询日志
   - 分析查询结构
   - 检查缓存命中率

## 参考资源

- [OpenSearch 集群配置](https://opensearch.org/docs/latest/install-and-configure/configuring-opensearch/)
- [性能调优指南](https://opensearch.org/docs/latest/tuning-your-cluster/)
- [容量规划](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/cluster-manager/)
