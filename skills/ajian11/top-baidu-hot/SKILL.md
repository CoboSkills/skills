---
name: top-baidu-hot
description: 获取百度热搜榜 TOP 10，包含日期标题和热搜排名 + 标题，格式简洁
homepage: https://top.baidu.com/board?platform=pc
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["browser_use"]}}}
---

# 百度热搜

获取百度热搜榜 TOP 10 热门标题。

## 使用方法

当用户想要获取百度热搜、想知道今天有什么热门话题时使用此 skill。

## 执行步骤

1. 使用 browser_use 打开 https://top.baidu.com/board?platform=pc
2. 等待页面加载完成
3. 获取热搜榜 TOP 10 的标题
4. 获取当前日期
5. 按以下格式输出：

```
2026-03-03 百度热搜 TOP 10

1. xxx
2. xxx
3. xxx
4. xxx
5. xxx
6. xxx
7. xxx
8. xxx
9. xxx
10. xxx
```

## 注意事项

- 不要使用表格边框、竖杠或额外文字
- 只列出排名和标题即可
- 如果页面有弹窗，先关闭再获取内容
