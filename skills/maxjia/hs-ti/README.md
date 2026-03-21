# hs-ti - 云瞻威胁情报查询技能 / Hillstone Threat Intelligence Skill

## 概述 / Overview
hs-ti是一个OpenClaw技能，提供与山石网科云瞻威胁情报平台的集成。它允许用户查询IP地址、域名、URL和文件哈希的威胁情报。

hs-ti is an OpenClaw skill that provides integration with Hillstone Threat Intelligence Platform. It allows users to query threat intelligence for IP addresses, domains, URLs, and file hashes.

## 功能特性 / Features

### 支持的IOC类型 / Supported IOC Types

#### 中文 / Chinese
- **IP地址**：查询IPv4或IPv6地址的威胁情报
- **域名**：查询域名的威胁情报
- **URL**：查询完整URL的威胁情报
- **文件哈希**：支持MD5、SHA1、SHA256格式的文件哈希查询

#### English
- **IP Address**: Query threat intelligence for IPv4 or IPv6 addresses
- **Domain**: Query threat intelligence for domain names
- **URL**: Query threat intelligence for complete URLs
- **File Hash**: Support file hash queries in MD5, SHA1, SHA256 formats

### 高级功能 / Advanced Features

#### 中文 / Chinese
- **批量查询**：支持逗号分隔的多个IOC同时查询
- **实时响应时间统计**：显示本次调用的平均、最大、最小、中位数响应时间
- **累计性能监控**：跟踪所有历史调用的性能指标
- **详细威胁信息**：返回威胁类型、可信度、具体分类等信息

#### English
- **Batch Query**: Support for querying multiple IOCs at once (comma-separated)
- **Real-time Response Time Statistics**: Display average, max, min, and median response times for current query
- **Cumulative Performance Monitoring**: Track performance metrics for all historical queries
- **Detailed Threat Information**: Return threat type, credibility, and specific classification

## 语言切换 / Language Switching

默认语言：英文 / Default Language: English

切换到中文 / Switch to Chinese:
```
/hs-ti cn
```

切换到英文 / Switch to English:
```
/hs-ti en
```

## 安装 / Installation

### 通过OpenClaw安装 / Install via OpenClaw

#### 中文 / Chinese
```bash
# 在OpenClaw配置文件中添加技能
{
  "skills": {
    "entries": {
      "hs-ti": {
        "enabled": true
      }
    }
  }
}
```

#### English
```bash
# Add skill to OpenClaw configuration file
{
  "skills": {
    "entries": {
      "hs-ti": {
        "enabled": true
      }
    }
  }
}
```

### 手动安装 / Manual Installation

#### 中文 / Chinese
1. 将hs-ti目录复制到OpenClaw的skills目录
2. 配置API密钥（见下文）
3. 重启OpenClaw服务

#### English
1. Copy hs-ti directory to OpenClaw's skills directory
2. Configure API key (see below)
3. Restart OpenClaw service

## 配置 / Configuration

在 `config.json` 中配置有效的 API Key：
You need to configure a valid API Key in `config.json`:

**注意 / Note**: 复制 `config.example.json` 为 `config.json` 并填入您的API密钥。
Copy `config.example.json` to `config.json` and fill in your API key.

```json
{
  "api_key": "your-api-key-here",
  "api_url": "https://ti.hillstonenet.com.cn"
}
```

**获取API密钥 / Get API Key**：
#### 中文 / Chinese
- 访问山石网科云瞻威胁情报平台
- 注册账号并申请API访问权限
- 获取API密钥并配置到config.json中

#### English
- Visit Hillstone Threat Intelligence Platform
- Register account and apply for API access permission
- Get API key and configure it in config.json

## 使用方法 / Usage

### 命令调用 / Command Invocation

#### 中文 / Chinese
```
/threat-check 45.74.17.165
/threat-check deli.ydns.eu
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
```

#### English
```
/threat-check 45.74.17.165
/threat-check deli.ydns.eu
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
```

### 别名支持 / Alias Support

#### 中文 / Chinese
- `/threat-check` - 威胁检查
- `/hs-ti` - 云瞻威胁情报
- `/threat` - 威胁情报

#### English
- `/threat-check` - Threat check
- `/hs-ti` - Hillstone threat intelligence
- `/threat` - Threat intelligence

### Python API调用 / Python API Call

```python
from yunzhan_plugin import YunzhanThreatIntel

intel = YunzhanThreatIntel()
result = intel.query_ioc('45.74.17.165', 'ip')
print(result)
```

## 响应格式 / Response Format

### 成功响应 / Success Response

```json
{
  "data": {
    "result": "malicious",
    "threat_type": ["Scanner", "Exploit"],
    "flow_direction": 1,
    "credibility": 33,
    "lifecycle": {
      "status": 1,
      "start_time": 1766801777913,
      "window_ms": 7776000000
    },
    "ip_address": "45.74.17.165"
  },
  "response_code": 0,
  "response_msg": "OK",
  "response_time_ms": 207
}
```

### 字段说明 / Field Description

#### 中文 / Chinese
- `result`: 查询结果（malicious/benign/unknown）
- `threat_type`: 威胁类型列表
- `credibility`: 可信度评分（0-100）
- `response_time_ms`: 响应时间（毫秒）

#### English
- `result`: Query result (malicious/benign/unknown)
- `threat_type`: List of threat types
- `credibility`: Credibility score (0-100)
- `response_time_ms`: Response time in milliseconds

## 性能统计 / Performance Statistics

每次查询都会显示详细的性能统计：
Each query displays detailed performance statistics:

### 单次查询 / Single Query

#### 中文 / Chinese
- 显示本次调用的响应时间

#### English
- Display response time for current call

### 批量查询 / Batch Query

#### 中文 / Chinese
- 显示本次批量的统计（平均/最大/最小/中位数）

#### English
- Display statistics for current batch (avg/max/min/median)

### 累计统计 / Cumulative Statistics

#### 中文 / Chinese
- 显示所有历史调用的累计统计和总调用次数

#### English
- Display cumulative statistics and total call count for all historical queries

## 依赖项 / Dependencies

#### 中文 / Chinese
- Python 3.8+
- requests库（Python标准库，无需额外安装）
- 山石网科云瞻威胁情报API访问权限

#### English
- Python 3.8+
- requests library (Python standard library, no additional installation required)
- Hillstone Threat Intelligence API access permission

## API端点 / API Endpoints

#### 中文 / Chinese
- IP查询: `/api/ip/reputation?key={ip}`
- 域名查询: `/api/domain/reputation?key={domain}`
- URL查询: `/api/url/reputation?key={url}`
- 文件哈希查询: `/api/file/reputation?key={hash}`

#### English
- IP Query: `/api/ip/reputation?key={ip}`
- Domain Query: `/api/domain/reputation?key={domain}`
- URL Query: `/api/url/reputation?key={url}`
- File Hash Query: `/api/file/reputation?key={hash}`

## 故障排除 / Troubleshooting

### API Key无效 / Invalid API Key

#### 中文 / Chinese
**症状**：查询返回认证错误
**解决**：确保使用有效的云瞻API Key

#### English
**Symptoms**: Query returns authentication error
**Solution**: Ensure you are using a valid Hillstone API Key

### 网络连接问题 / Network Connection Issues

#### 中文 / Chinese
**症状**：查询超时或连接失败
**解决**：检查能否访问 `https://ti.hillstonenet.com.cn`

#### English
**Symptoms**: Query timeout or connection failure
**Solution**: Check if you can access `https://ti.hillstonenet.com.cn`

### 查询超时 / Query Timeout

#### 中文 / Chinese
**症状**：查询长时间无响应
**解决**：默认超时30秒，可在代码中调整

#### English
**Symptoms**: Query takes long time without response
**Solution**: Default timeout is 30 seconds, can be adjusted in code

### 编码问题 / Encoding Issues

#### 中文 / Chinese
**症状**：中文显示乱码
**解决**：确保系统支持UTF-8编码

#### English
**Symptoms**: Chinese characters display as garbled text
**Solution**: Ensure your system supports UTF-8 encoding

## 示例 / Examples

### 查询单个IP / Query Single IP

#### 中文 / Chinese
```
/threat-check 8.8.8.8
```

#### English
```
/threat-check 8.8.8.8
```

### 批量查询 / Batch Query

#### 中文 / Chinese
```
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
```

#### English
```
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
```

### 查询域名 / Query Domain

#### 中文 / Chinese
```
/threat-check example.com
```

#### English
```
/threat-check example.com
```

### 查询URL / Query URL

#### 中文 / Chinese
```
/threat-check https://example.com/malware
```

#### English
```
/threat-check https://example.com/malware
```

### 查询文件哈希 / Query File Hash

#### 中文 / Chinese
```
/threat-check d41d8cd98f00b204e9800998ecf8427e
```

#### English
```
/threat-check d41d8cd98f00b204e9800998ecf8427e
```

## 许可证 / License

MIT License

## 作者 / Author

Hillstone

## 版本历史 / Version History

详见 [CHANGELOG.md](CHANGELOG.md) / See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 贡献 / Contributing

欢迎提交Issue和Pull Request！
Welcome to submit Issues and Pull Requests!

## 联系方式 / Contact

如有问题或建议，请联系Hillstone技术支持团队。
For questions or suggestions, please contact Hillstone technical support team.