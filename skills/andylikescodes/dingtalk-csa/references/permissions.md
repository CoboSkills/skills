# 钉钉开放平台权限开通指南

## 📋 应用信息

- **AppKey**: `dingsemtijka6uyry5vd`
- **AppSecret**: `U2MnO8Z1i46InyzRuFZCKfpDuHYTwGYKp_G1hxbieJ3vy23MuGQ1rW_rK1-kSkM7`
- **应用类型**: 企业内部应用
- **开通方式**: 管理员在钉钉开放平台操作

## 🔑 权限状态总览

### ✅ 已开通的权限

| # | 权限名称 | 权限标识 | 用途 |
|---|---------|---------|------|
| 1 | 钉盘应用盘空间读 | Storage.Space.Read | 列出/查看空间信息 |
| 2 | 钉盘应用盘空间写 | Storage.Space.Write | 创建空间 |
| 3 | 钉盘应用文件读 | Storage.File.Read | 列出/查询文件 |
| 4 | 钉盘应用文件写 | Storage.File.Write | 上传文件、写入文档 |
| 5 | 钉盘上传信息读 | Storage.UploadInfo.Read | 获取上传凭证 |
| 6 | 通讯录部门用户读 | qyapi_get_department_member | 获取部门成员列表 |

### ❌ 待开通的权限

| # | 权限名称 | 权限标识 | 用途 | 优先级 |
|---|---------|---------|------|--------|
| 7 | 钉盘下载信息读 | Storage.DownloadInfo.Read | 下载文件到本地 | 🔴 高 |
| 8 | 通讯录用户详情读 | qyapi_get_member | 获取用户详细信息 | 🟡 中 |
| 9 | 通讯录部门列表读 | qyapi_get_department_list | 获取部门列表 | 🟡 中 |
| 10 | 个人用户信息读 | Contact.User.Read | 新版API读取用户信息 | 🟡 中 |
| 11 | 钉盘基础权限(旧版) | qyapi_cspace_base | 旧版自定义空间API | ⚪ 低 |

## 📝 开通流程

### 方式一：一键申请链接（推荐）

直接访问以下链接，逐个点击申请：

1. **Storage.DownloadInfo.Read**  
   https://open-dev.dingtalk.com/appscope/apply?content=dingsemtijka6uyry5vd%23Storage.DownloadInfo.Read

2. **qyapi_get_member**  
   https://open-dev.dingtalk.com/appscope/apply?content=dingsemtijka6uyry5vd%23qyapi_get_member

3. **qyapi_get_department_list**  
   https://open-dev.dingtalk.com/appscope/apply?content=dingsemtijka6uyry5vd%23qyapi_get_department_list

4. **Contact.User.Read**  
   https://open-dev.dingtalk.com/appscope/apply?content=dingsemtijka6uyry5vd%23Contact.User.Read

5. **qyapi_cspace_base**（可选，旧版API）  
   https://open-dev.dingtalk.com/appscope/apply?content=dingsemtijka6uyry5vd%23qyapi_cspace_base

### 方式二：在开放平台手动操作

1. 登录 [钉钉开放平台](https://open-dev.dingtalk.com/)
2. 进入 **应用开发** → 找到你的应用
3. 点击 **权限管理**
4. 搜索以下权限名称，逐个申请：
   - 搜索 "下载信息" → 开通 **钉盘应用下载信息读权限**
   - 搜索 "成员详情" → 开通 **通讯录用户详情读权限**
   - 搜索 "部门列表" → 开通 **通讯录部门列表读权限**
   - 搜索 "用户信息" → 开通 **个人用户信息读权限**
   - 搜索 "cspace" → 开通 **企业钉盘基础权限**（可选）
5. 企业管理员审批通过后权限立即生效

### 注意事项

- 企业内部应用的权限申请通常需要 **管理员审批**
- 权限开通后可能需要 **几分钟** 才能生效
- 搜索权限名称时如果在"钉盘"分类下找不到，尝试在"全部权限"中搜索
- `qyapi_cspace_base` 是旧版权限，如果搜不到可以忽略，新版API已覆盖其功能

## 🧪 验证方法

权限开通后，可以让Bayes运行以下命令验证：

```bash
# 获取token后测试
curl -s -X POST "https://api.dingtalk.com/v1.0/storage/spaces/{spaceId}/dentries/{dentryId}/downloadInfos/query" \
  -H "x-acs-dingtalk-access-token: $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"unionId": "iSHgMJf7O6XZNiiGQhmwN4FgiEiE"}'
```

如果返回下载链接而不是权限错误，说明开通成功。