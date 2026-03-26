# 🛡️ 安全版微信文章抓取器

> 本地运行，保护隐私 - 不发送数据到第三方 API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18-green.svg)](https://nodejs.org/)
[![Puppeteer](https://img.shields.io/badge/puppeteer-core-blue.svg)](https://pptr.dev/)

---

## ✨ 特性

- ✅ **本地运行** - 不发送数据到第三方 API，保护隐私
- ✅ **完整源代码** - 可审查无后门
- ✅ **移动端 UA 伪装** - 绕过微信反爬机制
- ✅ **JavaScript 渲染支持** - 完整获取动态内容
- ✅ **自动保存** - 全文提取并保存为文本文件
- ✅ **错误处理** - 超时保护和详细错误信息
- ✅ **100% 测试通过** - 已验证多篇长文抓取

---

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 运行

```bash
# 方式 1: 直接运行（修改脚本中的 URL）
node fetch-wechat-article.js

# 方式 2: 命令行参数（推荐）
node fetch-wechat-article.js https://mp.weixin.qq.com/s/YOUR_ARTICLE_ID
```

### 3. 查看结果

控制台输出 + 自动保存到 `article-wechat-{timestamp}.txt`

---

## 📋 输出示例

```
========== 文章信息 ==========

标题：全网都在养的小龙虾，正在没有人类的论坛里进化？
作者：差评 X.PIN
时间：差评君

========== 文章内容 ==========

要说最近最火的电子宠物是啥，肯定是那只全网都在养的小龙虾...
（正文内容）
...

========== 文章结束 ==========

内容已保存到：./article-wechat-1774081600976.txt
```

---

## 📦 文件结构

```
wechat-article-fetcher-safe/
├── fetch-wechat-article.js     # 主脚本
├── package.json                # npm 配置
├── README.md                   # 本文件
├── SKILL.md                    # 完整技能文档
├── UPLOAD.md                   # 上传指南
├── .gitignore                  # Git 配置
└── tests/
    └── run-tests.js            # 测试脚本
```

---

## 🧪 测试记录

| 文章 | 结果 | 字数 | 耗时 |
|------|------|------|------|
| Evolver + EvoMap 实战 | ✅ | ~15000 | ~5s |
| 小龙虾 Skills 推荐 | ✅ | ~100 | ~3s |
| 全网都在养小龙虾 | ✅ | ~3000 | ~4s |

**成功率**: 100% (3/3)

---

## ⚙️ 技术实现

### 核心步骤

1. **启动 Chrome 无头模式**
   ```javascript
   puppeteer.launch({
     executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
     headless: true,
     args: ['--no-sandbox', '--disable-gpu']
   })
   ```

2. **设置移动端 User-Agent**
   ```javascript
   page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 MicroMessenger/8.0.0')
   ```

3. **等待页面加载**
   ```javascript
   page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 })
   ```

4. **提取内容**
   ```javascript
   page.evaluate(() => {
     const title = document.querySelector('#activity-name')?.innerText
     const content = document.querySelector('#js_content')?.innerText
     return { title, content }
   })
   ```

---

## ❓ 常见问题

### Q: 找不到 Chrome 路径？

**解决:**
```bash
# Windows
where chrome

# 修改脚本中的 chromePath
```

### Q: 抓取内容为空？

**解决:**
```javascript
// 增加等待时间
await page.waitForSelector('#js_content', { timeout: 30000 });

// 添加额外等待
await new Promise(r => setTimeout(r, 3000));
```

### Q: 被微信反爬拦截？

**解决:**
1. ✅ 使用移动端 User-Agent（已内置）
2. ✅ 添加随机延迟
3. ✅ 限制抓取频率（建议间隔 >5 秒）

---

## 🔒 安全性说明

### 与现有技能的区别

| 特性 | 安全版（本仓库） | 其他版本 |
|------|-----------------|---------|
| 本地运行 | ✅ 是 | ❌ 可能使用第三方 API |
| 源代码审查 | ✅ 完整公开 | ⚠️ 可能不透明 |
| 数据发送 | ❌ 不发送 | ⚠️ 可能发送到第三方 |
| 依赖 | ✅ 仅 Puppeteer | ⚠️ 可能有额外依赖 |

### 隐私保护

- ✅ 所有操作在本地完成
- ✅ 不发送数据到任何服务器
- ✅ 不收集任何用户信息
- ✅ 可完整审查源代码

---

## 📄 许可证

MIT License - 可自由使用、修改、分发

---

## 🙏 致谢

感谢以下测试素材提供者：
- Captain AI 实验室
- 差评君
- 其他微信公众号创作者

---

## 📞 反馈

如有问题或建议，欢迎提交 Issue 或 PR！

---

**最后更新**: 2026-03-21  
**维护者**: marld
