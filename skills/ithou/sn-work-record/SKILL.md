---
name: sn-work-record
description: 蜀宁 OA 工时管理（凭证加密存储）。当用户提到工时、撤回、修改工时描述、或提到蜀宁科技时触发。用于：查询工时状态、撤回审批中的工时、修改工时描述后自动重新提交。
---

# 蜀宁 OA 工时管理

## 安全说明

凭证使用 **AES-256-CBC** 加密存储在 `memory/sn-work-record-credentials.md.enc`，解密密钥（passphrase）仅存在于内存中，不会落盘。

**首次使用**需要提供：
- 系统地址、账号、密码
- 一个你记住的 passphrase（用于加密/解密凭证）

**重要**：passphrase 必须记住！如果遗忘，只能删除加密文件后重新输入凭证。

## 状态值

- `"10"` = 草稿
- `"20"` = 审批中

## 快速操作

### 查询工时状态

```
GET /sn/timeEntry/get?id=<工时ID>
```

### 撤回（审批中→草稿）

```
POST /sn/timeEntry/cancelApply {"id": "<工时ID>"}
```

### 修改描述（自动重新提交）

```
POST /sn/timeEntry/update {"id": "<工时ID>", "jobDesc": "新描述"}
```

**注意**：修改描述后状态自动变回"审批中"(20)，无需手动再提交。

## 完整流程

1. 确认凭据已加密保存（首次需提供系统地址+账号+密码+passphrase）
2. 获取工时 ID（列表页或日历视图）
3. 输入 passphrase 解密
4. `cancelApply` 撤回
5. `update` 修改描述 → 自动重新提交
6. `get` 验证结果

## 加密/解密命令

```bash
# 加密（存凭证）
openssl enc -aes-256-cbc -salt -in credential_input.txt -out memory/sn-work-record-credentials.md.enc -pass pass:YOUR_PASSPHRASE

# 解密（读凭证）
openssl enc -d -aes-256-cbc -in memory/sn-work-record-credentials.md.enc -pass pass:YOUR_PASSPHRASE
```

## API 详情

See [api.md](references/api.md)