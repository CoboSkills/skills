# Anti-Detection — 反爬策略

## 反爬类型与解决方案

| 反爬类型 | 解决方案 | 状态 |
|---------|---------|------|
| 普通网站 | agent-browser 直接访问 | ✅ |
| 需要登录 | CDP + Cookie 持久化 | ✅ 已验证 |
| 简单验证码 | 手动点一次，后续复用 Cookie | ✅ |
| Cloudflare 盾 | Camoufox / Nodriver(py3.12) | ✅ 已验证 |
| 强指纹检测 | Camoufox / Nodriver | ✅ 已验证 |
| IP 封禁 | 代理池（http://127.0.0.1:1087） | ✅ |

## 已验证反爬层

### Camoufox

- **类型**: Firefox modified
- **bypass 率**: ~80%
- **适用**: Cloudflare 盾、指纹检测

### Nodriver (py3.12)

- **类型**: Chrome/Chromium
- **bypass 率**: ~90%
- **适用**: 强反爬场景

## 云 fallback 排序

1. **Zyte**（首选）
2. **Browserless**（次选）
3. **Hyperbrowser**（第三）

## 代理配置

```bash
HTTP 代理：http://127.0.0.1:1087
SOCKS 代理：socks5://127.0.0.1:1080
```
