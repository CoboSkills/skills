# 查询优化技术

## 核心概念

OpenSearch 查询性能优化涉及查询结构设计、缓存利用、聚合优化和分页策略。理解 query context 和 filter context 的区别是优化的关键。

## 常见问题

### 问题 1: Query Context vs Filter Context

**症状**:
- 查询速度慢
- 缓存未生效
- 不必要的相关性计算

**原因**:
Query context 会计算相关性分数，Filter context 只做布尔匹配且可缓存。

**解决方案**:

使用 filter context 进行精确匹配：
```json
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "machine learning"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "status": "published"
          }
        },
        {
          "range": {
            "price": {
              "gte": 10,
              "lte": 100
            }
          }
        }
      ]
    }
  }
}
```

**对比**:
```json
// 慢 - 使用 must（计算分数）
{
  "query": {
    "bool": {
      "must": [
        {"term": {"status": "published"}},
        {"range": {"price": {"gte": 10}}}
      ]
    }
  }
}

// 快 - 使用 filter（不计算分数，可缓存）
{
  "query": {
    "bool": {
      "filter": [
        {"term": {"status": "published"}},
        {"range": {"price": {"gte": 10}}}
      ]
    }
  }
}
```

**最佳实践**:
- 精确匹配使用 `filter`（term, range, exists）
- 全文搜索使用 `must`（match, multi_match）
- 排除条件使用 `must_not`
- Filter 查询会被自动缓存
- 将 filter 放在 bool 查询的 filter 子句中

### 问题 2: 深分页性能问题

**症状**:
- 翻页到后面页码时查询变慢
- 内存占用高
- 查询超时

**原因**:
使用 from/size 分页时，需要在每个分片上排序并跳过前面的结果。

**解决方案**:

1. 使用 search_after 代替 from/size：
```json
// 第一次查询
{
  "size": 10,
  "query": {
    "match_all": {}
  },
  "sort": [
    {"timestamp": "desc"},
    {"_id": "asc"}
  ]
}

// 后续查询
{
  "size": 10,
  "query": {
    "match_all": {}
  },
  "search_after": [1609459200000, "doc_123"],
  "sort": [
    {"timestamp": "desc"},
    {"_id": "asc"}
  ]
}
```

2. 使用 scroll API（适合导出大量数据）：
```json
// 初始化 scroll
POST /my_index/_search?scroll=1m
{
  "size": 1000,
  "query": {
    "match_all": {}
  }
}

// 获取下一批
POST /_search/scroll
{
  "scroll": "1m",
  "scroll_id": "DXF1ZXJ5QW5kRmV0Y2gBAAAAAAAAAD4WYm9laVYtZndUQlNsdDcwakFMNjU1QQ=="
}
```

3. 限制 max_result_window：
```json
{
  "settings": {
    "max_result_window": 10000
  }
}
```

**最佳实践**:
- 避免使用 from > 10000
- 实时分页使用 search_after
- 批量导出使用 scroll API
- 提供"下一页"而不是"跳转到第 N 页"
- 使用唯一字段（如 _id）作为排序的最后一个字段

### 问题 3: 聚合查询优化

**症状**:
- 聚合查询慢
- 内存占用高
- 结果不准确（近似值）

**原因**:
聚合需要在内存中处理大量数据。

**解决方案**:

1. 使用 filter 减少聚合数据量：
```json
{
  "size": 0,
  "query": {
    "bool": {
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
  },
  "aggs": {
    "categories": {
      "terms": {
        "field": "category",
        "size": 10
      }
    }
  }
}
```

2. 使用 composite aggregation 进行分页：
```json
{
  "size": 0,
  "aggs": {
    "my_buckets": {
      "composite": {
        "size": 100,
        "sources": [
          {"category": {"terms": {"field": "category"}}},
          {"date": {"date_histogram": {"field": "timestamp", "calendar_interval": "day"}}}
        ]
      }
    }
  }
}
```

3. 调整精度参数：
```json
{
  "aggs": {
    "categories": {
      "terms": {
        "field": "category",
        "size": 10,
        "shard_size": 50,  // 增加分片级别的桶数量
        "show_term_doc_count_error": true
      }
    }
  }
}
```

**最佳实践**:
- 设置 `size: 0` 不返回文档，只返回聚合结果
- 使用 filter 先过滤再聚合
- 对高基数字段使用 composite aggregation
- 调整 `shard_size` 提高精度
- 使用 `execution_hint: map` 优化内存使用
- 避免嵌套过深的聚合（< 3 层）

### 问题 4: 缓存策略

**症状**:
- 相同查询重复执行很慢
- 缓存命中率低
- 内存占用不合理

**原因**:
未充分利用 OpenSearch 的多级缓存机制。

**解决方案**:

1. 启用 request cache（聚合查询）：
```json
{
  "size": 0,
  "query": {
    "bool": {
      "filter": [
        {"term": {"status": "published"}}
      ]
    }
  },
  "aggs": {
    "categories": {
      "terms": {"field": "category"}
    }
  }
}
```

2. 使用 query cache（filter 查询）：
```json
{
  "query": {
    "bool": {
      "filter": [
        {"term": {"status": "published"}}  // 自动缓存
      ]
    }
  }
}
```

3. 配置缓存大小：
```json
{
  "settings": {
    "index.queries.cache.enabled": true,
    "index.requests.cache.enable": true
  }
}
```

4. 监控缓存效果：
```bash
GET /_stats/request_cache,query_cache
```

**最佳实践**:
- Filter 查询自动使用 query cache
- 聚合查询使用 request cache（size=0）
- 使用 `now` 的查询不会被缓存，使用 `now/d` 向下取整
- 定期监控缓存命中率和驱逐率
- 合理设置缓存大小（默认堆内存的 10%）

### 问题 5: 多字段搜索优化

**症状**:
- 多字段搜索慢
- 相关性排序不理想
- 查询复杂难以维护

**原因**:
需要在多个字段上执行搜索并合并结果。

**解决方案**:

1. 使用 multi_match：
```json
{
  "query": {
    "multi_match": {
      "query": "machine learning",
      "fields": ["title^3", "content", "tags^2"],
      "type": "best_fields",
      "tie_breaker": 0.3
    }
  }
}
```

2. 使用 bool 查询组合：
```json
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "title": {
              "query": "machine learning",
              "boost": 3
            }
          }
        },
        {
          "match": {
            "content": "machine learning"
          }
        }
      ],
      "minimum_should_match": 1
    }
  }
}
```

3. 使用 copy_to 字段：
```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "copy_to": "full_text"
      },
      "content": {
        "type": "text",
        "copy_to": "full_text"
      },
      "full_text": {
        "type": "text"
      }
    }
  }
}

// 查询
{
  "query": {
    "match": {
      "full_text": "machine learning"
    }
  }
}
```

**最佳实践**:
- 使用 `^` 设置字段权重（boost）
- `best_fields`: 最佳字段匹配（默认）
- `most_fields`: 多字段匹配
- `cross_fields`: 跨字段匹配（适合姓名搜索）
- 使用 `tie_breaker` 考虑其他字段的分数
- 对于固定的多字段搜索，使用 copy_to 简化查询

## 配置示例

### 高性能查询模板

```json
{
  "size": 20,
  "from": 0,
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "{{search_term}}",
            "fields": ["title^3", "content"],
            "type": "best_fields"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "status": "published"
          }
        },
        {
          "range": {
            "created_at": {
              "gte": "{{start_date}}",
              "lte": "{{end_date}}"
            }
          }
        }
      ]
    }
  },
  "sort": [
    {"_score": "desc"},
    {"created_at": "desc"}
  ],
  "_source": ["title", "summary", "created_at"],
  "highlight": {
    "fields": {
      "title": {},
      "content": {
        "fragment_size": 150,
        "number_of_fragments": 3
      }
    }
  }
}
```

### 聚合查询模板

```json
{
  "size": 0,
  "query": {
    "bool": {
      "filter": [
        {
          "range": {
            "timestamp": {
              "gte": "now-7d/d",
              "lte": "now/d"
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "daily_stats": {
      "date_histogram": {
        "field": "timestamp",
        "calendar_interval": "day"
      },
      "aggs": {
        "total_amount": {
          "sum": {
            "field": "amount"
          }
        },
        "avg_amount": {
          "avg": {
            "field": "amount"
          }
        }
      }
    },
    "top_categories": {
      "terms": {
        "field": "category",
        "size": 10,
        "order": {"_count": "desc"}
      }
    }
  }
}
```

## 性能监控

### 慢查询日志

配置慢查询阈值：
```json
{
  "settings": {
    "index.search.slowlog.threshold.query.warn": "10s",
    "index.search.slowlog.threshold.query.info": "5s",
    "index.search.slowlog.threshold.query.debug": "2s",
    "index.search.slowlog.threshold.fetch.warn": "1s"
  }
}
```

查看慢查询日志：
```bash
tail -f /var/log/opensearch/my-cluster_index_search_slowlog.log
```

### 查询性能分析

使用 profile API：
```json
{
  "profile": true,
  "query": {
    "match": {
      "title": "machine learning"
    }
  }
}
```

### 关键指标

- 查询延迟: < 100ms（简单查询），< 500ms（复杂查询）
- 缓存命中率: > 80%
- 慢查询数量: < 1%
- 聚合查询: < 1s

## 参考资源

- [OpenSearch 查询 DSL](https://opensearch.org/docs/latest/query-dsl/)
- [性能调优指南](https://opensearch.org/docs/latest/tuning-your-cluster/)
- [缓存机制详解](https://opensearch.org/docs/latest/api-reference/index-apis/clear-cache/)
