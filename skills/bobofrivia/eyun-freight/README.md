# eyun-freight skill

将此 skill 接入 OpenClaw，使 agent 可直接查询 Eyun 运价系统。

## 部署

**1. 复制 skill 目录到 OpenClaw workspace**

```bash
cp -r eyun-freight/ /home/bobofrivia/.openclaw/workspace/skills/
```

**2. 在 `~/.openclaw/openclaw.json` 中注入环境变量**

```json
{
  "skills": {
    "entries": {
      "eyun_freight": {
        "enabled": true,
        "env": {
          "EYUN_BASE_URL": "http://<eyun-server-ip>:8000",
          "EYUN_WHALE_IDENTITY": "<base64 字符串>"
        }
      }
    }
  }
}
```

**3. 重启 gateway**

```bash
openclaw gateway restart
```

## EYUN_WHALE_IDENTITY 获取方式

`whale-identity` 是固定的服务账号 token（base64 编码的 JSON）。

> **TODO**：获取接口待定，后续由项目方提供，拿到 token 后填入 `env.EYUN_WHALE_IDENTITY` 即可。
