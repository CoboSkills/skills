# 索引策略和最佳实践

## 核心概念

OpenSearch 索引设计直接影响查询性能、存储效率和集群稳定性。合理的 mapping 配置、分片策略和索引生命周期管理是构建高性能搜索系统的基础。

## 常见问题

### 问题 1: 如何选择合适的分片数量

**症状**:
- 查询性能不佳
- 集群负载不均衡
- 索引创建后无法修改分片数

**原因**:
分片数量影响并行度、资源分配和集群扩展性。

**解决方案**:

计算分片数量的经验公式：
```
分片数 = 数据总量(GB) / 目标分片大小(GB)
推荐分片大小: 10-50 GB
```

创建索引时设置分片：
```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}
```

**最佳实践**:
- 小索引（< 50GB）: 1-3 个分片
- 中等索引（50-500GB）: 3-10 个分片
- 大索引（> 500GB）: 10+ 个分片
- 每个分片大小控制在 10-50GB
- 分片数应为数据节点数的倍数（便于均衡分布）
- 避免过度分片（over-sharding）导致资源浪费

### 问题 2: Mapping 字段类型选择

**症状**:
- 查询结果不准确
- 存储空间浪费
- 无法进行某些类型的查询

**原因**:
字段类型决定了数据如何存储和索引。

**解决方案**:

常用字段类型配置：
```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "status": {
        "type": "keyword"
      },
      "price": {
        "type": "float"
      },
      "quantity": {
        "type": "integer"
      },
      "created_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss||epoch_millis"
      },
      "tags": {
        "type": "keyword"
      },
      "description": {
        "type": "text",
        "analyzer": "standard"
      },
      "metadata": {
        "type": "object",
        "enabled": false
      }
    }
  }
}
```

**字段类型选择指南**:
- `text`: 全文搜索字段（会分词）
- `keyword`: 精确匹配、聚合、排序（不分词）
- `integer/long`: 整数
- `float/double`: 浮点数
- `date`: 日期时间
- `boolean`: 布尔值
- `object`: 嵌套对象
- `nested`: 独立索引的嵌套对象（用于复杂查询）

**最佳实践**:
- 需要全文搜索的字段使用 `text`
- 需要精确匹配、聚合、排序的字段使用 `keyword`
- 使用 multi-field 同时支持全文搜索和精确匹配
- 不需要搜索的字段设置 `enabled: false` 节省空间
- 日期字段指定明确的格式
- 避免使用 `_all` 字段（已废弃）

### 问题 3: 动态 Mapping vs 显式 Mapping

**症状**:
- 字段类型不符合预期
- 索引膨胀（字段爆炸）
- 无法控制字段行为

**原因**:
动态 mapping 会自动推断字段类型，可能不符合实际需求。

**解决方案**:

1. 禁用动态 mapping（推荐生产环境）：
```json
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "known_field": {
        "type": "text"
      }
    }
  }
}
```

2. 使用动态模板：
```json
{
  "mappings": {
    "dynamic_templates": [
      {
        "strings_as_keywords": {
          "match_mapping_type": "string",
          "mapping": {
            "type": "keyword"
          }
        }
      },
      {
        "integers": {
          "match_mapping_type": "long",
          "mapping": {
            "type": "integer"
          }
        }
      }
    ]
  }
}
```

**最佳实践**:
- 生产环境使用 `dynamic: "strict"` 防止字段爆炸
- 开发环境可使用 `dynamic: true` 快速迭代
- 使用动态模板统一处理未知字段
- 定期审查 mapping，移除不需要的字段

### 问题 4: 索引别名和零停机重建

**症状**:
- 需要修改 mapping 但无法在线修改
- 重建索引导致服务中断
- 无法平滑切换索引

**原因**:
OpenSearch 不支持修改已有字段的类型，需要重建索引。

**解决方案**:

使用索引别名实现零停机重建：

1. 创建新索引：
```bash
PUT /my_index_v2
{
  "mappings": {
    "properties": {
      "field": {
        "type": "keyword"  // 新的类型
      }
    }
  }
}
```

2. 重新索引数据：
```bash
POST /_reindex
{
  "source": {
    "index": "my_index_v1"
  },
  "dest": {
    "index": "my_index_v2"
  }
}
```

3. 切换别名：
```bash
POST /_aliases
{
  "actions": [
    {
      "remove": {
        "index": "my_index_v1",
        "alias": "my_index"
      }
    },
    {
      "add": {
        "index": "my_index_v2",
        "alias": "my_index"
      }
    }
  ]
}
```

4. 删除旧索引：
```bash
DELETE /my_index_v1
```

**最佳实践**:
- 始终使用别名而不是直接使用索引名
- 索引命名使用版本号（如 my_index_v1）
- 重建索引时使用 `_reindex` API
- 验证新索引数据完整性后再切换别名
- 保留旧索引一段时间以便回滚

### 问题 5: 索引模板管理

**症状**:
- 多个索引配置不一致
- 时间序列索引创建繁琐
- 难以统一管理索引设置

**原因**:
手动创建每个索引容易出错且效率低。

**解决方案**:

创建索引模板：
```json
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "30s"
    },
    "mappings": {
      "properties": {
        "timestamp": {
          "type": "date"
        },
        "level": {
          "type": "keyword"
        },
        "message": {
          "type": "text"
        },
        "host": {
          "type": "keyword"
        }
      }
    }
  },
  "priority": 100
}
```

应用模板：
```bash
PUT /_index_template/logs_template
{
  // 模板配置
}
```

**最佳实践**:
- 为相似的索引创建模板
- 使用通配符匹配索引名称
- 设置合理的优先级（priority）
- 时间序列数据使用索引模板 + 滚动策略
- 定期审查和更新模板

## 配置示例

### 生产环境索引配置

```json
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1,
    "refresh_interval": "30s",
    "max_result_window": 10000,
    "index": {
      "codec": "best_compression",
      "mapping": {
        "total_fields": {
          "limit": 2000
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "category": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "price": {
        "type": "float"
      },
      "stock": {
        "type": "integer"
      },
      "created_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss"
      },
      "updated_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss"
      },
      "metadata": {
        "type": "object",
        "enabled": false
      }
    }
  }
}
```

### 时间序列索引模板

```json
{
  "index_patterns": ["metrics-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "5s",
      "index": {
        "lifecycle": {
          "name": "metrics_policy",
          "rollover_alias": "metrics"
        }
      }
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "metric_name": {
          "type": "keyword"
        },
        "value": {
          "type": "double"
        },
        "host": {
          "type": "keyword"
        },
        "tags": {
          "type": "keyword"
        }
      }
    }
  }
}
```

## 索引生命周期管理

### ISM 策略示例

```json
{
  "policy": {
    "description": "Hot-Warm-Delete policy",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [
          {
            "rollover": {
              "min_index_age": "1d",
              "min_primary_shard_size": "50gb"
            }
          }
        ],
        "transitions": [
          {
            "state_name": "warm",
            "conditions": {
              "min_index_age": "7d"
            }
          }
        ]
      },
      {
        "name": "warm",
        "actions": [
          {
            "replica_count": {
              "number_of_replicas": 0
            }
          },
          {
            "force_merge": {
              "max_num_segments": 1
            }
          }
        ],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "30d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ]
      }
    ]
  }
}
```

## 性能优化建议

1. **批量索引**: 使用 bulk API，批量大小 5-15MB
2. **禁用 refresh**: 批量导入时设置 `refresh_interval: -1`
3. **增加副本**: 导入完成后再增加副本数
4. **使用压缩**: 设置 `codec: best_compression` 节省空间
5. **限制字段数**: 设置 `mapping.total_fields.limit` 防止字段爆炸

## 参考资源

- [OpenSearch Mapping 文档](https://opensearch.org/docs/latest/field-types/)
- [索引设置参考](https://opensearch.org/docs/latest/api-reference/index-apis/create-index/)
- [索引生命周期管理](https://opensearch.org/docs/latest/im-plugin/)
