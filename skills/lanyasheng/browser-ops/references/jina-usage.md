# Jina AI Reader Usage — Jina 使用指南

## 定位

外部内容提取器，用于快速提取文章/博客/文档正文。

## 使用示例

### 基础用法

```bash
# 提取网页正文为 Markdown
curl -s "https://r.jina.ai/http://example.com/article" | head -100

# 保存到文件
curl -s "https://r.jina.ai/http://example.com/article" > article.md
```

### Python 用法

```python
import requests

def fetch_with_jina(url: str) -> str:
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url, timeout=30)
    return response.text

# 示例
content = fetch_with_jina("http://paulgraham.com/worked.html")
print(content)
```

## 已验证场景

| 场景 | 状态 |
|------|------|
| Paul Graham 博客 | ✅ 实测通过 |
| BBC News | ✅ 实测通过 |
| 技术文档页面 | ✅ 已验证 |
| 公开博客文章 | ✅ 已验证 |

## 限制

- ❌ 无登录态支持
- ❌ 不执行 JavaScript
- ❌ 不适合动态内容

## 适用场景

- ✅ 公开博客文章
- ✅ 技术文档页面
- ✅ 新闻正文
- ✅ 快速原型验证

## 状态

**✅ 已验证主链**（Paul Graham 博客、BBC News 实测通过）

## 失败处理

如果 Jina 失败（403/超时/内容空）：
1. 回退到 `web_fetch`
2. 或升级到 L3（agent-browser）
