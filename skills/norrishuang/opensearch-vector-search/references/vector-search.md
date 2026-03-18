# 向量搜索和 k-NN 优化

## 核心概念

OpenSearch 的 k-NN（k-Nearest Neighbors）插件支持高效的向量相似度搜索，使用 HNSW（Hierarchical Navigable Small World）算法构建图索引。向量搜索性能取决于索引配置、缓存策略和查询参数。

OpenSearch 支持两种向量索引模式：
- **内存模式（Memory Mode）**: 向量索引存储在内存中，提供最佳性能（< 10ms 延迟）
- **磁盘模式（Disk Mode）**: 向量索引存储在磁盘上，显著降低内存需求和成本，但延迟较高（100-200ms）

**推荐配置**:
- **向量引擎**: FAISS（推荐，性能更优）
- **相似度算法**: cosine（推荐，适用性更广）
- **实例类型**: 7 系列以上（r7g/r8g/c7g/m7g/or2/om2）

<!-- FALLBACK: opensearch, priority=1 -->
<!-- FALLBACK: aws-pricing, priority=2, condition="cost-related" -->

## 常见问题

### 问题 1: 向量查询首次执行很慢（冷启动问题）

**症状**: 
- 首次向量查询耗时数秒甚至更长
- 后续查询速度正常
- 重启集群后问题重现

**原因**: 
向量索引默认不加载到内存，首次查询需要从磁盘读取并构建缓存。

**解决方案**:
1. 使用 warmup API 预加载索引：
```bash
POST /my-vector-index/_warmup
```

2. 在索引设置中启用自动缓存：
```json
{
  "settings": {
    "index.knn.cache.enabled": true
  }
}
```

3. 监控缓存命中率：
```bash
GET /_plugins/_knn/stats
```

**最佳实践**:
- 在索引创建或数据导入完成后立即执行 warmup
- 为 k-NN 缓存预留足够的堆外内存（circuit_breaker.parent.limit）
- 定期监控缓存驱逐率，避免频繁缓存失效

### 问题 2: HNSW 参数如何调优

**症状**:
- 查询速度慢或召回率低
- 索引构建时间过长
- 内存占用过高

**原因**:
HNSW 参数（ef_construction, m）直接影响索引质量和性能。

**解决方案**:

调整 HNSW 参数：
```json
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "cosine",
          "engine": "faiss",
          "parameters": {
            "ef_construction": 512,
            "m": 16
          }
        }
      }
    }
  }
}
```

**参数说明**:
- `ef_construction`: 索引构建时的搜索深度（默认 512）
  - 更高 = 更好的召回率，但构建更慢
  - 推荐范围: 100-1000
- `m`: 每个节点的最大连接数（默认 16）
  - 更高 = 更好的召回率，但内存占用更大
  - 推荐范围: 8-48

**最佳实践**:
- 生产环境: ef_construction=512, m=16（平衡性能和质量）
- 高召回率场景: ef_construction=1000, m=32
- 快速索引场景: ef_construction=128, m=8
- 查询时可调整 ef 参数（ef_search）来平衡速度和召回率

### 问题 3: 向量维度选择和性能影响

**症状**:
- 查询延迟随维度增加而显著增长
- 内存占用过高

**原因**:
向量维度直接影响计算复杂度和存储空间。

**解决方案**:

1. 选择合适的向量维度：
```json
{
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 384,  // 根据模型选择
        "method": {
          "name": "hnsw",
          "space_type": "cosine"
        }
      }
    }
  }
}
```

2. 考虑降维技术：
- PCA（主成分分析）
- 量化（Quantization）

**最佳实践**:
- 使用模型原生维度，避免不必要的填充
- 常见维度: 384（MiniLM）, 768（BERT）, 1536（OpenAI）
- 维度越低，性能越好，但可能损失精度
- 测试不同维度对召回率的影响

### 问题 4: 如何使用磁盘模式（Disk Mode）降低成本

**症状**:
- 内存成本过高
- 大规模向量数据集（> 50M 向量）
- 可接受较高延迟（100-200ms）

**原因**:
内存模式需要将整个向量索引加载到内存，对于大规模数据集成本很高。

**解决方案**:

使用磁盘模式配置：
```json
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "knn_vector",
        "dimension": 768,
        "space_type": "cosine",
        "data_type": "float",
        "mode": "on_disk",
        "compression_level": "32x"
      }
    }
  }
}
```

**参数说明**:
- `mode: "on_disk"`: 启用磁盘模式
- `data_type: "float"`: 磁盘模式仅支持 float 数据类型
- `compression_level`: 压缩级别
  - `"4x"`: 使用 Lucene 引擎，召回率损失最小
  - `"16x"`: 使用 FAISS 引擎，平衡性能和内存
  - `"32x"`: 默认值，最大内存节省，召回率损失 15-20%

**性能影响**:
- QPS: 降低约 98%（从 2000+ 降至 30-70）
- 延迟: 增加约 20 倍（从 10ms 增至 100-200ms）
- 内存占用: 降低 32 倍
- 成本: 降低 50-80%

**自动重评分机制**:
- 磁盘模式默认启用重评分（rescoring）来保持召回率
- 搜索分两阶段：先搜索压缩索引，再用全精度向量重评分
- 默认 `oversample_factor` 为 3.0，可根据需要调整

**最佳实践**:
- 使用高性能 EBS 卷（gp3，9000+ IOPS）
- 配置足够的 EBS 吞吐量（500+ MB/s）
- 监控 IOPS 使用率，避免瓶颈
- 适合批处理或离线分析场景
- 不适合实时低延迟应用
- 仅支持 `float` 数据类型
- 考虑调整 `oversample_factor` 来平衡性能和召回率

**EBS 配置建议**:
```json
{
  "ebs_options": {
    "ebs_enabled": true,
    "volume_type": "gp3",
    "volume_size": 500,
    "iops": 9000,
    "throughput": 500
  }
}
```

### 问题 5: 混合查询（向量 + 关键词）优化

**症状**:
- 同时使用向量搜索和关键词搜索时性能下降
- 结果排序不符合预期

**原因**:
需要合理组合向量相似度分数和文本相关性分数。

**解决方案**:

使用 script_score 或 hybrid query：
```json
{
  "query": {
    "script_score": {
      "query": {
        "bool": {
          "must": [
            {
              "match": {
                "title": "machine learning"
              }
            }
          ],
          "filter": {
            "term": {
              "status": "published"
            }
          }
        }
      },
      "script": {
        "source": "knn_score",
        "lang": "knn",
        "params": {
          "field": "embedding",
          "query_value": [0.1, 0.2, ...],
          "space_type": "cosine"
        }
      }
    }
  }
}
```

**最佳实践**:
- 使用 filter context 进行精确匹配（不影响分数）
- 调整向量和文本分数的权重
- 考虑使用 rescore 进行二次排序
- 测试不同的分数组合策略

## 配置示例

### 完整的向量索引配置（内存模式）

```json
{
  "settings": {
    "index": {
      "knn": true,
      "knn.cache.enabled": true,
      "number_of_shards": 3,
      "number_of_replicas": 1
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "content": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "cosine",
          "engine": "faiss",
          "parameters": {
            "ef_construction": 512,
            "m": 16
          }
        }
      },
      "timestamp": {
        "type": "date"
      }
    }
  }
}
```

### 磁盘模式配置（成本优化）

```json
{
  "settings": {
    "index": {
      "knn": true,
      "number_of_shards": 6,
      "number_of_replicas": 1
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "content": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "space_type": "cosine",
        "data_type": "float",
        "mode": "on_disk",
        "compression_level": "16x",
        "method": {
          "params": {
            "ef_construction": 512
          }
        }
      },
      "timestamp": {
        "type": "date"
      }
    }
  }
}
```

**磁盘模式配置说明**:
- 默认使用 `faiss` 引擎和 `hnsw` 方法
- `compression_level: "16x"` 提供最佳性价比
- `data_type: "float"` 是磁盘模式的必需参数
- 增加分片数量以提升并发性能
- 需要配置高性能 EBS 卷

### 高级磁盘模式配置（自定义参数）

```json
{
  "settings": {
    "index": {
      "knn": true,
      "number_of_shards": 6,
      "number_of_replicas": 1
    }
  },
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "space_type": "cosine",
        "data_type": "float",
        "mode": "on_disk",
        "compression_level": "16x",
        "method": {
          "name": "hnsw",
          "engine": "faiss",
          "params": {
            "ef_construction": 512,
            "m": 16
          }
        }
      }
    }
  }
}
```

### 向量查询示例

```json
{
  "size": 10,
  "query": {
    "knn": {
      "embedding": {
        "vector": [0.1, 0.2, 0.3, ...],
        "k": 10
      }
    }
  }
}
```

### 带过滤的向量查询

```json
{
  "size": 10,
  "query": {
    "bool": {
      "must": [
        {
          "knn": {
            "embedding": {
              "vector": [0.1, 0.2, 0.3, ...],
              "k": 50
            }
          }
        }
      ],
      "filter": [
        {
          "range": {
            "timestamp": {
              "gte": "2024-01-01"
            }
          }
        }
      ]
    }
  }
}
```

### 磁盘模式向量查询（带重评分）

```json
{
  "size": 10,
  "query": {
    "knn": {
      "embedding": {
        "vector": [0.1, 0.2, 0.3, ...],
        "k": 10,
        "method_parameters": {
          "ef_search": 512
        },
        "rescore": {
          "oversample_factor": 10.0
        }
      }
    }
  }
}
```

## 性能监控

### 关键指标

1. **缓存命中率**:
```bash
GET /_plugins/_knn/stats
```
查看 `cache_capacity_reached` 和 `eviction_count`

2. **查询延迟**:
```bash
GET /_nodes/stats/indices/search
```

3. **内存使用**:
```bash
GET /_cat/nodes?v&h=name,heap.percent,ram.percent
```

### 性能基准

- 单次向量查询: < 100ms（热缓存）
- 首次查询（冷启动）: < 2s（使用 warmup 后）
- 缓存命中率: > 95%
- 召回率: > 90%（取决于 HNSW 参数）

## 参考资源

- [OpenSearch k-NN 官方文档](https://opensearch.org/docs/latest/search-plugins/knn/)
- [HNSW 算法论文](https://arxiv.org/abs/1603.09320)
- [向量搜索最佳实践](https://opensearch.org/docs/latest/search-plugins/knn/performance-tuning/)
