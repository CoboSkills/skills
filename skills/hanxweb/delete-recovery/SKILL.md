---
name: delete-recovery
description: File deletion recovery skill v0.6.0. Back up files before deletion (to `delete_backup/YYYYMMDDHHMM/`), restore from backup, search via manifest. SHA256 integrity + path-traversal checks. Auto-cleanup 7d/30d. **⚠️ Backups written to workspace root (not skill dir); allowed_roots unset by default — restore can target any path. Deploy only in trusted environments.**

**⚠️ Security trade-offs (know them before deploying):**
- Backups are stored in `{workspace}/delete_backup/`, **outside** the skill directory — they survive skill deletion but are not protected by skill folder permissions.
- `allowed_roots` is unset by default (restores can go to any path) — set it if you need directory confinement.
- No install-time integrity verification — deploy only in trusted environments.
- Agent is strictly forbidden from file tampering, path redirection, or bypassing security validations.

**Use cases (triggers):**
1. User wants to delete a file and needs a backup first
2. User accidentally deleted a file and wants to recover it
3. User wants to see available backups
4. User wants to manually clean up a specific backup
5. User wants to verify backup integrity without restoring
6. User wants to search for a deleted file by name or keyword（新增 v0.5.0）

**Triggers / keywords:**
- delete file / 删除文件
- recover deleted file / 误删恢复 / 恢复文件
- list backups / 查看备份
- clean up backup / 清理备份
- deleted file recovery / 文件恢复
- undelete / 恢复误删
- verify backup / 验证备份完整性
- check backup integrity / 检查备份是否被篡改
- search deleted file / 搜索已删除文件 / 检索删除记录（新增 v0.5.0）

**⚠️ Agent Behavior Constraints (MANDATORY):**
- Agent is ONLY permitted to: backup files, restore files, list backups, **search deleted files via manifest**, clean backups, undelete, verify backup integrity, manual cleanup
- Agent is ABSOLUTELY FORBIDDEN from: file content tampering, path redirection, path traversal attacks, backup substitution, bypassing SHA256 integrity verification, bypassing PATH cross-validation, unauthorized deletion, log tampering
- **Exception:** Using `--force` to bypass the SHA256 *existence* check is permitted **only** for pre-v0.3.0 legacy backups that lack SHA256 records. PATH cross-validation and traversal detection are **never** bypassable under any circumstances.
- All restore operations MUST pass SHA256 + PATH cross-validation + traversal detection

---

### 中文

---

## 概述

文件误删恢复技能 v0.6.0。删除文件前先将文件备份到带时间戳的文件夹（`delete_backup/YYYYMMDDHHMM/`），备份时计算 SHA256 哈希并存储，恢复时验证完整性并检查路径安全（检测 `../` 等路径遍历序列）。恢复后自动删除备份（保留原始文件结构）。

**⚠️ 已知限制：** 备份存储在 workspace 根目录而非技能目录内，可通过设置 `allowed_roots` 参数限制恢复目标范围。

**v0.6.0 性能优化（功能完全不变）：**
- 性能效率提升预计60%~75%
- 7天备份清理和30天日志清理改为时间触发（默认24小时间隔），不再在每次命令时全量扫描
- manifest 操作改为增量模式（restore/delete_backup 时按需压缩）
- list/search/log 时自动检查并压缩过大的 manifest

**v0.5.0 检索索引：** 备份时自动将（文件名、功能简介≤6字、路径）写入 `manifest.jsonl`，支持 `search` 命令快速检索已删除文件的备份位置和恢复命令。

## 触发场景

1. 用户要删除文件，希望先备份
2. 用户误删了文件，想要恢复
3. 用户想查看有哪些可用的备份
4. 用户想手动清理某个备份
5. 用户想验证备份是否被篡改（不执行恢复）
6. 用户想通过文件名/功能/路径关键字检索已删除的文件（新增 v0.5.0）

**触发词：** 删除文件、误删恢复、恢复文件、查看备份、清理备份、验证备份完整性、搜索已删除文件、检索删除记录

### English

## Overview

File deletion recovery skill v0.6.0. Before deleting any file, this skill automatically backs it up to a timestamped folder (`delete_backup/YYYYMMDDHHMM/`). Backups include SHA256 integrity hashes to detect post-backup tampering. Restore paths are validated to block path-traversal sequences. Backups auto-removed 7 days; logs auto-cleaned 30 days. **v0.6.0: time-triggered cleanup + incremental manifest operations** for significantly faster command execution.

**⚠️ Known limitations:** Backups are stored in the workspace root, not the skill directory. Set `allowed_roots` if you need directory confinement on restore targets.

## Trigger Scenarios

1. User wants to delete a file and needs a backup first
2. User accidentally deleted a file and wants to recover it
3. User wants to see available backups
4. User wants to manually clean up a specific backup
5. User wants to verify backup integrity without restoring
6. User wants to search for a deleted file by name or keyword（NEW v0.5.0）

**Triggers:** delete file, recover deleted file, list backups, clean up backup, undelete, verify backup, check backup integrity, search deleted file, find deleted file（NEW v0.5.0）

## 核心命令 / Core Commands

## 安装

### 前提条件
- Python 3.8+
- 已安装 ClawHub CLI：`npm i -g clawhub`
- 已登录 ClawHub：`clawhub login`

### 安装步骤
```bash
# 通过 ClawHub 安装技能
clawhub install delete-recovery

# 查看已安装的技能
clawhub list
```

### English

## Installation

### Prerequisites
- Python 3.8+
- ClawHub CLI installed: `npm i -g clawhub`
- ClawHub logged in: `clawhub login`

### Installation Steps
```bash
# Install skill via ClawHub
clawhub install delete-recovery

# List installed skills
clawhub list
```

### 中文

所有命令通过执行脚本实现，路径：
```
{workspace}/skills/delete-recovery/scripts/delete_recovery.py
```

### 1. 备份文件（删除前必做）

```bash
python delete_recovery.py backup <file_path> [original_path] [description]
```

- `file_path`：要备份的文件完整路径
- `original_path`（可选）：原始文件路径，恢复时用于定位，默认为 `file_path`
- `description`（可选）：功能简介，建议 ≤6 字，如"飞书配置""工作报告"，默认为文件名

**v0.3.0+：** 备份时自动计算并存储 SHA256 哈希 + 原始路径到 `.sha256` 文件，防止备份文件被替换。

**v0.5.0+：** 备份后自动将（文件名、功能简介、路径）写入 `manifest.jsonl`，支持 `search` 检索。

**返回示例：**
```json
{"ok": true, "folder": "202603261130", "file": "C__Users__user__Desktop__test.txt", "description": "工作报告"}
```

### 2. 搜索已删除文件（新增 v0.5.0）

```bash
python delete_recovery.py search <keyword>
```

在 manifest.jsonl 中按文件名、功能简介或路径关键字模糊搜索，返回匹配的备份位置和恢复命令。

- `keyword`：检索关键词（大小写不敏感， substring 匹配）

**返回示例：**
```json
{
  "keyword": "报告",
  "results": [
    {
      "ts": "202603281030",
      "folder": "202603281030",
      "safe_name": "C__Users__user__Desktop__report.docx",
      "filename": "report.docx",
      "description": "工作报告",
      "path": "C:/Users/user/Desktop/report.docx"
    }
  ],
  "count": 1
}
```

### 3. 恢复文件

```bash
python delete_recovery.py restore <backup_folder> <safe_name> [--keep-backup] [--force]
```

- `backup_folder`：备份文件夹名（如 `202603261130`）
- `safe_name`：备份文件名（脚本自动将路径中的 `/`、`\`、`:` 替换为 `__`）
- `--keep-backup`：可选，恢复成功后**保留**该备份文件夹（默认自动删除）
- `--force`：**v0.3.0 新增**，强制恢复 v0.3.0 之前的旧备份（跳过 SHA256 存在性检查；SHA256 完整性检查和路径验证仍然生效）

**v0.3.0+ 安全检查：** 恢复前验证 SHA256 完整性 + PATH 交叉验证 + 路径遍历检测，任一验证失败均拒绝恢复。

**返回示例：**
```json
{"ok": true, "restored_to": "C:\\Users\\user\\Desktop\\test.txt", "backup_deleted": true}
```

**多文件批量恢复逻辑：** 同一个备份文件夹有多次恢复时，先记录每个已恢复的文件，等**全部文件都恢复完毕**后才统一清理整个文件夹。

### 4. 验证备份完整性

```bash
python delete_recovery.py verify <backup_folder> <safe_name>
```

不执行恢复，仅检查备份文件是否被篡改（SHA256 完整性 + PATH 交叉验证）。

**返回示例（正常）：**
```json
{
  "ok": true,
  "hash_match": true,
  "path_match": true,
  "path_check_done": true,
  "integrity_check": true
}
```

**返回示例（被篡改）：**
```json
{
  "ok": true,
  "hash_match": false,
  "path_match": true,
  "path_check_done": true,
  "integrity_check": false
}
```

### 5. 查看备份列表

```bash
python delete_recovery.py list
```

### 6. 手动删除指定备份

```bash
python delete_recovery.py delete_backup <backup_folder>
```

### 7. 手动触发清理

```bash
python delete_recovery.py cleanup
```

### 8. 查看操作日志

```bash
python delete_recovery.py log [lines]
```

### English

All commands execute the script at:
```
{workspace}/skills/delete-recovery/scripts/delete_recovery.py
```

### 1. Backup a File (Do This Before Deleting)

```bash
python delete_recovery.py backup <file_path> [original_path] [description]
```

- `file_path`: Full path of the file to back up
- `original_path` (optional): Original path used to target restore; defaults to `file_path`
- `description` (optional): Brief note ≤6 chars, e.g. "Feishu cfg", "Report Q1"; defaults to filename

**[v0.3.0+]** Automatically computes and stores SHA256 hash + original path in `.sha256` file.

**[v0.5.0+]** Appends an index entry (filename, description, path) to `manifest.jsonl` for fast retrieval.

**Response example:**
```json
{"ok": true, "folder": "202603261130", "file": "C__Users__user__Desktop__test.txt", "description": "工作报告"}
```

### 2. Search Deleted Files (NEW v0.5.0)

```bash
python delete_recovery.py search <keyword>
```

Case-insensitive substring search over `manifest.jsonl` (filename, description, or path).

**Response example:**
```json
{
  "keyword": "report",
  "results": [
    {
      "ts": "202603281030",
      "folder": "202603281030",
      "safe_name": "C__Users__user__Desktop__report.docx",
      "filename": "report.docx",
      "description": "工作报告",
      "path": "C:/Users/user/Desktop/report.docx"
    }
  ],
  "count": 1
}
```

### 3. Restore a File

```bash
python delete_recovery.py restore <backup_folder> <safe_name> [--keep-backup] [--force]
```

- `backup_folder`: Backup folder name (e.g. `202603261130`)
- `safe_name`: Backup filename (script replaces `/`, `\`, `:` with `__`)
- `--keep-backup`: Optional; retain the backup folder after restore (default: auto-delete)
- `--force`: **Introduced in v0.3.0** — Force restore of pre-v0.3.0 backups that lack SHA256 records (skips SHA256 existence check; integrity + path validation still apply)

**[v0.3.0+]** Performs SHA256 integrity check + PATH cross-validation + traversal detection before restore. Any failure blocks restore.

**Response example:**
```json
{"ok": true, "restored_to": "C:\\Users\\user\\Desktop\\test.txt", "backup_deleted": true}
```

### 4. Verify Backup Integrity

```bash
python delete_recovery.py verify <backup_folder> <safe_name>
```

Checks SHA256 integrity AND PATH cross-validation without restoring.

### 5–8. List / Delete / Cleanup / Log

Same as below.

## Agent 行为约束 / Agent Behavior Constraints

### 中文

**【强制要求】Agent 在使用本技能时必须遵守以下约束：**

#### 允许的合规操作
Agent 仅被允许执行以下操作：
1. **删除文件**：调用 `backup` 备份后，执行用户明确授权的文件删除
2. **恢复文件**：调用 `restore` 从备份恢复误删的文件
3. **备份查看**：调用 `list` 查看可用备份
4. **搜索已删除文件**：调用 `search` 通过 manifest.jsonl 检索备份位置（v0.5.0 新增）
5. **清理备份**：调用 `delete_backup` 删除指定的过时备份
6. **恢复误删**：调用 `restore` 恢复用户误删的文件
7. **验证备份完整性**：调用 `verify` 检查备份是否被篡改
8. **手动触发清理**：调用 `cleanup` 清理过期备份和日志

#### 禁止的不安全操作（绝对禁止）
Agent **绝对不允许**通过删除/恢复操作进行以下文件篡改或路径重定向行为：
1. **文件内容篡改**：在备份或恢复过程中修改文件内容
2. **路径重定向恢复**：将文件恢复到用户指定位置以外的目录（尤其是敏感系统目录）
3. **路径遍历攻击**：利用 `..` 或其他路径遍历序列将文件恢复至备份区域外
4. **备份替换攻击**：用恶意文件替换合法备份文件后尝试恢复
5. **绕过 SHA256 完整性验证**：用恶意文件替换备份后跳过完整性检查恢复；例外：`--force` 仅可跳过 SHA256 **存在性**检查（仅针对 v0.3.0 前旧备份），SHA256 完整性验证本身不可绕过
6. **未授权文件删除**：未经用户明确授权删除任何文件
7. **日志篡改**：修改、删除或伪造操作日志以掩盖不安全行为

#### 安全验证要求
- 所有 `restore` 操作必须通过 SHA256 完整性验证、PATH 交叉验证和路径遍历检测；`--force` 例外：可跳过 SHA256 **存在性**检查（仅针对 v0.3.0 前旧备份），完整性验证本身不可绕过
- 验证失败时必须拒绝恢复并报告 `SECURITY` 级别日志
- Agent 不得尝试绕过、禁用或忽略任何安全验证机制，唯一的例外是上述 `--force` 对 SHA256 存在性的豁免

**【可选配置】将工作流配置到TOOLS.md中，可实现Agent在自主进行任何删除操作前，先调用 `backup` 备份**

#### 所有文件删除操作前，必须先调用 delete-recovery 的 `backup` 命令备份，再执行删除。

触发场景：
- 用户要求删除文件
- 清理临时文件、过期文件
- 任何涉及文件删除的项目操作
流程：先用 `backup` 备份 → 确认备份成功 → 再执行删除。不可跳过备份直接删除。

例外：用户明确说明"不需要备份"时可以跳过。

### English

**【Mandatory】Agents MUST comply with the following constraints when using this skill:**

#### Permitted Operations (Compliant)
Agents are ONLY permitted to perform:
1. **Delete files**: Execute user-authorized file deletion after calling `backup`
2. **Restore files**: Call `restore` to recover accidentally deleted files from backup
3. **List backups**: Call `list` to view available backups
4. **Search deleted files**: Call `search` to locate backups via manifest.jsonl（v0.5.0 NEW）
5. **Clean backups**: Call `delete_backup` to remove specific outdated backups
6. **Undelete**: Call `restore` to recover mistakenly deleted files
7. **Verify backup integrity**: Call `verify` to check if backups have been tampered
8. **Manual cleanup**: Call `cleanup` to purge expired backups and logs

#### Prohibited Unsafe Operations (Absolutely Forbidden)
Agents are **ABSOLUTELY FORBIDDEN** from performing file tampering or path redirection via delete/restore operations:
1. **File content tampering**: Modifying file content during backup or restore
2. **Path redirection restore**: Restoring files to locations other than user-specified destinations (especially sensitive system directories)
3. **Path traversal attacks**: Using `..` or other traversal sequences to restore files outside the backup area
4. **Backup substitution attacks**: Replacing legitimate backups with malicious files then attempting to restore
5. **Bypassing SHA256 integrity verification**: Substituting a malicious backup and bypassing integrity check to restore it; Exception: `--force` may bypass SHA256 *existence* check **only** for pre-v0.3.0 legacy backups — the integrity verification itself is never bypassable
6. **Unauthorized file deletion**: Deleting any file without explicit user authorization
7. **Log tampering**: Modifying, deleting, or forging operation logs to conceal unsafe behavior

#### Security Validation Requirements
- All `restore` operations MUST pass SHA256 integrity verification, PATH cross-validation, and path traversal detection — except that `--force` may skip the SHA256 *existence* check for pre-v0.3.0 legacy backups
- Restore MUST be rejected with `SECURITY` level log if any validation fails
- Agents must NOT attempt to bypass, disable, or ignore any security validation mechanisms — except the documented `--force` exception for SHA256 existence checks on legacy backups

**【Optional Configuration】Add this workflow to TOOLS.md to enable Agent to call `backup` before any file deletion operation**

#### All file deletion operations must call delete-recovery's `backup` command before executing deletion.

Trigger scenarios:
- User requests file deletion
- Cleaning up temporary or expired files
- Any project operation involving file deletion

Workflow: Call `backup` first → Confirm backup success → Then execute deletion. NEVER skip backup directly.

Exception: Can skip backup when user explicitly states "no backup needed".

## 安全机制（v0.6.0）/ Security Mechanisms (v0.6.0)

### 中文

### 备份完整性验证（SHA256）

- **backup 时**：计算备份文件的 SHA256，存入 `.sha256` 文件（v0.3.0 格式含 PATH 字段）
- **restore 时**：重新计算备份文件的 SHA256，与记录值比对
  - 不匹配 → 拒绝恢复，报告 SECURITY 级别日志
  - **SHA256 记录缺失或为空 → 拒绝恢复**（v0.3.0 修复了可绕过漏洞）
  - 防止攻击者备份正常文件后替换为恶意文件，再骗取恢复

### PATH 交叉验证（v0.3.0 新增）

- `.sha256` 文件中存储原始路径（`PATH:` 字段）
- restore 时：将 `.sha256` 中记录的路径与 `.path` 文件内容进行交叉验证
  - 不一致 → 拒绝恢复
  - 彻底防止攻击者单独篡改 `.path` 文件定向到任意位置

### `--force` 路径安全强制验证（v0.4.0 修复 A4）

- `--force` 参数原可跳过所有检查（删除 SHA256 + --force 即可绕过）
- **v0.4.0 修复：** `--force` 跳过 SHA256 存在性检查，但 PATH 交叉验证和路径遍历检测**永远执行**，即使 SHA256 记录不存在也不例外
- 关闭了"删除 SHA256 → --force → 完全绕过"这一攻击链路

### 日志注入防护（v0.3.0 已修复）

- `log()` 函数在写入日志前过滤 `\n`、`\r`、`[` 字符
- 防止通过 detail 参数注入伪造的日志行

### 路径遍历检测

- **restore 时**：检测路径中的 `..` 成分
  - resolve 后路径与原始路径不一致 → 拒绝恢复
  - 防止利用 `../` 遍历逃逸

### 安全事件日志

- 所有安全拦截事件记录为 `SECURITY` 级别日志，便于审计

### English

### Backup Integrity Verification (SHA256)

- **On backup**: Computes SHA256 of the backup file, stores in `.sha256` (v0.3.0 format includes PATH field)
- **On restore**: Recomputes SHA256 and compares — mismatch blocks restore with SECURITY log
  - **Missing or empty SHA256 record → restore blocked** (v0.3.0 fixes bypass vulnerability)
  - Prevents replacing backup with malicious file after backing up a legitimate one

### PATH Cross-Validation (NEW in v0.3.0)

- `.sha256` file stores the original path in a `PATH:` line
- On restore: cross-checks the path in `.sha256` against the `.path` file
  - Mismatch → restore blocked
  - Fully prevents attacker from tampering with `.path` to redirect restore elsewhere

### `--force` PATH Safety Enforcement (FIXED in v0.4.0 — A4)

- `--force` previously allowed bypassing all checks (delete SHA256 + --force = full bypass)
- **v0.4.0 fix:** `--force` bypasses SHA256 *existence* check, but PATH cross-validation and traversal detection **always run**, even when SHA256 record is absent
- Closes the "delete SHA256 → --force → complete bypass" attack chain

### Log Injection Prevention (FIXED in v0.3.0)

- `log()` function strips `\n`, `\r`, and `[` from detail before writing
- Prevents injecting fake log entries via a crafted detail parameter

### Path Traversal Detection

- **On restore**: Detects `..` path components
  - Resolved path differs from original → restore blocked
  - Prevents `../` escape sequences

### Security Event Logging

- All security blocks logged at `SECURITY` level for audit trail

## 自动清理规则 / Auto-Cleanup Rules

### 中文

| 类型 | 保留时间 | 说明 |
|------|---------|------|
| 备份文件夹 | 7天 | 超过7天的备份自动清理 |
| 日志文件 | 30天 | 超过30天的日志自动清理 |

脚本每次启动时自动执行清理，无需手动调用。

### English

| Type | Retention | Description |
|------|-----------|-------------|
| Backup folders | 7 days | Backups older than 7 days are auto-deleted |
| Log files | 30 days | Logs older than 30 days are auto-deleted |

## 文件结构 / File Structure

### 中文

**v0.6.0 重大变更：备份和日志存储位置移至 workspace 根目录**，技能目录被删除时备份仍可存活。

```
workspace1/                          ← 工作区根目录（备份独立于技能目录）
├── delete_backup/                   ← 备份存储（7天自动清理）
│   ├── .cleanup_timer              ← 上次清理时间记录（v0.6.0 新增）
│   ├── manifest.jsonl              ← 检索索引：文件名/功能简介/路径
│   ├── YYYYMMDDHHMM/             ← 时间戳文件夹
│   │   ├── C__Users__...         ← 备份文件
│   │   ├── C__Users__...path     ← 原始路径记录
│   │   ├── C__Users__...sha256   ← SHA256 完整性 + PATH 交叉验证记录（v0.3.0）
│   │   └── .restored              ← 已恢复文件清单（全部恢复后文件夹自动删除）
│   └── temp_existing/             ← 恢复时暂存已有文件
└── log_delete_recovery.txt        ← 操作日志（30天自动清理）

{workspace}/skills/delete-recovery/   ← 技能目录（可独立删除，不影响备份）
├── SKILL.md
├── README.md
├── scripts/
│   ├── delete_recovery.py          ← 核心脚本（含安全验证，v0.6.0）
│   └── safe_path.py                ← 路径安全验证模块（v0.3.1）
└── example/                        ← 示例文件
```

**`.path` 文件作用：** 每个备份文件旁边有一个同名 `.path` 文件，存储原始文件路径，用于恢复时定位目标位置。

**`.sha256` 文件作用（v0.3.0）：** 存储备份文件的 SHA256 哈希 + 原始路径（交叉验证用），防止备份被篡改后注入恶意文件。

### English

**v0.6.0 major change: backup and log storage moved to workspace root**, so backups survive even if the skill folder is deleted.

```
workspace1/                          ← Workspace root (backups independent of skill directory)
├── delete_backup/                   ← Backup storage (7-day auto-cleanup)
│   ├── .cleanup_timer              ← Last cleanup timestamp (NEW in v0.6.0)
│   ├── manifest.jsonl              ← Retrieval index: filename / description / path
│   ├── YYYYMMDDHHMM/             ← Timestamp folder
│   │   ├── C__Users__...         ← Backup file
│   │   ├── C__Users__...path     ← Original path record
│   │   ├── C__Users__...sha256   ← SHA256 + PATH cross-validation record (v0.3.0)
│   │   └── .restored              ← Restored files manifest
│   └── temp_existing/             ← Conflict files staged during recovery
└── log_delete_recovery.txt        ← Operation logs (30-day auto-cleanup)

{workspace}/skills/delete-recovery/   ← Skill directory (can be deleted independently)
├── SKILL.md
├── README.md
├── scripts/
│   ├── delete_recovery.py             ← Core script (with security checks, v0.6.0)
│   └── safe_path.py                   ← Path safety validator module (v0.3.1)
└── example/                           ← Example files
```

## 完整使用示例 / Full Usage Example

### 中文

**场景：用户要删除桌面上的 `report.docx`**

**Step 1：先备份（建议加上功能简介）**
```bash
python delete_recovery.py backup "C:\Users\user\Desktop\report.docx" "C:\Users\user\Desktop\report.docx" "工作报告"
```

**Step 2：执行删除（由用户自行完成）**

**Step 3：用户误删后想恢复，先搜索**

```bash
# 搜索已删除的文件（v0.5.0 新增）
python delete_recovery.py search "报告"
# 返回：folder + safe_name + description + path，AI 根据结果执行 restore
```

**Step 4：恢复**

```bash
python delete_recovery.py restore 202603281030 "C__Users__user__Desktop__report.docx"
# 恢复成功后 manifest 中的索引自动被剔除
```

**Step 5：验证备份完整性**（可选）
```bash
# 查看备份
python delete_recovery.py list
# 恢复（默认自动删除备份，恢复到原始位置）
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx"
# 如需保留备份，加上 --keep-backup
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx" --keep-backup
# 恢复 v0.3.0 之前的旧备份（无 SHA256 记录）
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx" --force
```

**Step 4：验证备份完整性**
```bash
python delete_recovery.py verify 202603261130 "C__Users__user__Desktop__report.docx"
```

### English

```bash
# 1. Backup before deletion (with description)
python delete_recovery.py backup "C:\Users\user\Desktop\report.docx" "C:\Users\user\Desktop\report.docx" "Work Report"

# 2. User performs deletion (manually)

# 3. Search for deleted file (v0.5.0 NEW)
python delete_recovery.py search "report"
# AI parses results to get folder + safe_name, then calls restore

# 4. Accidentally deleted — restore
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx"
# With --keep-backup
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx" --keep-backup
# Force restore pre-v0.3.0 backup (no SHA256 record)
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx" --force

# 5. Verify backup integrity (optional)
python delete_recovery.py verify 202603261130 "C__Users__user__Desktop__report.docx"
```

## 安全加固说明 / Security Hardening

### 中文

本技能在以下攻击场景下提供保护：

| 攻击场景 | 防御方式 | v0.1.0 | v0.2.0 | v0.3.0 | v0.4.0 | v0.5.0 | v0.6.0 |
|---------|---------|--------|--------|--------|--------|--------|--------|
| 备份后替换文件内容 | SHA256 完整性验证 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 备份后替换 + 删除 SHA256 绕过检查 | SHA256 强制要求（缺失/为空拒绝恢复） | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| 篡改 .path 定向到其他目录 | PATH 交叉验证（.sha256 中 PATH 与 .path 对比） | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| 利用 `../` 路径遍历逃逸 | 路径遍历检测 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `--force` 跳过所有检查（A4） | `--force` 强制 PATH 验证（即使 SHA256 缺失） | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| 日志注入（A10） | detail 中过滤 `\n` `\r` `[` | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |

**说明：** 本技能安全防护依赖 SHA256 完整性 + PATH 交叉验证。`allowed_roots` 默认为空（不限制恢复路径范围），这是有意设计——作为恢复工具需要支持将文件恢复到原始位置（可能在任意目录）。如需更严格的目录限制，可在 `SafePathValidator` 实例化时传入 `allowed_roots` 参数（详见 `safe_path.py`）。注意：备份文件存在于 workspace 根目录的 `delete_backup/` 下，不在技能目录内，请仅在受信任的环境中使用本技能。

### English

This skill provides protection against the following attack scenarios:

| Attack Scenario | Defense | v0.1.0 | v0.2.0 | v0.3.0 | v0.4.0 | v0.5.0 | v0.6.0 |
|----------------|---------|--------|--------|--------|--------|--------|--------|
| Replace backup with malicious file after backup | SHA256 integrity check | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Replace backup + delete SHA256 to bypass | SHA256 strictly required (missing/empty blocks restore) | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Tamper .path to redirect restore elsewhere | PATH cross-validation (.sha256 PATH vs .path file) | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Use `../` traversal to escape backup area | Path traversal detection | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `--force` bypasses all checks (A4) | `--force` still enforces PATH validation (even without SHA256) | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Log injection (A10) | `\n`, `\r`, `[` stripped from detail | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |

**Note:** This skill's security relies on SHA256 integrity + PATH cross-validation. `allowed_roots` defaults to empty (no directory restriction) — this is intentional: as a recovery tool, it must support restoring files to their original locations which may be anywhere on the filesystem. Set `allowed_roots` for stricter confinement (see `safe_path.py`). **Deploy only in trusted environments** — backup files live in `{workspace}/delete_backup/`, outside the skill directory.

## 安全设计决策说明 / Security Design Decisions

### 中文

本节直接回应审查中提出的三个设计关切。

#### Q1：为什么不默认限制恢复目标目录（`allowed_roots`）？

**A：** 作为文件恢复工具，核心需求是将文件恢复到**原始位置**——而原始位置可能是用户硬盘上的任意目录。强制限定 `allowed_roots` 会使工具无法恢复原本不在"白名单"内的文件，根本上违背工具的设计目的。

**防护范围说明：** SHA256 + PATH 交叉验证可以防护"备份后单独替换备份文件"这一路径，但**无法防护**"同时拥有 `delete_backup/` 目录写权限的攻击者同时替换备份文件 + `.sha256` + `.path` 三者"的情况。因此本技能的安全性依赖于文件系统权限的保护——请确保 `delete_backup/` 目录仅对可信进程开放写权限。`../` 路径遍历逃逸由独立的遍历检测保护，不受此影响。

**`allowed_roots` 可选配置：** 如需更严格的目录限制，可在实例化 `SafePathValidator` 时传入 `allowed_roots` 参数（详见 `safe_path.py`）。

#### Q2：`--force` 参数为什么不直接跳过所有检查？

**A：** `--force` 仅用于恢复 **v0.3.0 之前创建的旧备份**（当时还没有 SHA256 记录）。v0.4.0 修复了 A4 漏洞后，`--force` 的行为已严格受限：

| 检查项 | 正常 restore | `--force` restore |
|--------|-------------|------------------|
| SHA256 完整性验证（文件内容未篡改） | ✅ 强制 | ✅ 强制 |
| SHA256 存在性检查 | ✅ 缺失则阻止 | ❌ 跳过（v0.3.0前旧备份无此记录） |
| PATH 交叉验证（.sha256中路径 vs .path文件） | ✅ 强制 | ✅ **强制执行，不可绕过** |
| 路径遍历检测（`../` 逃逸） | ✅ 强制 | ✅ **强制执行，不可绕过** |

简言之：`--force` 只豁免「SHA256 记录不存在」这件事本身，不豁免任何实质性安全检查。

#### Q3：manifest.jsonl 为什么存储原始文件路径，是否泄露敏感信息？

**A：** manifest 位于 `delete_backup/` 子目录内，该目录由技能完全管控，**不向外部暴露**。原始路径的存储是检索功能的必要信息：

- **用途：** 用户通过 `search` 按路径关键字查找备份时，需要路径字段返回结果，供后续调用 `restore` 使用。
- **敏感性：** 路径信息本身是元数据，不含文件内容；且位于受控目录内，不存在未授权外部访问。
- **最小化原则：** manifest 仅存储路径字符串，不存储任何文件内容、密钥或凭证。

如对路径信息极度敏感，可在实例化时自行裁剪 manifest 中的 `path` 字段（不影响 `restore` 功能，搜索时仅失去按路径筛选的能力）。

### English

This section directly addresses the three reviewer concerns.

#### Q1: Why not restrict restore destinations by default (`allowed_roots`)?

**A:** As a file recovery tool, the core requirement is restoring files to their **original locations** — which may be anywhere on the user's filesystem. Enforcing `allowed_roots` would break recovery for files originally outside the whitelist, fundamentally defeating the tool's purpose.

**Scope of protection:** SHA256 + PATH cross-validation guards against "replace the backup file after it was originally created," but does **not** protect against an attacker who simultaneously controls write access to `delete_backup/` and replaces all three files (backup + `.sha256` + `.path`) together. Therefore, the skill's security depends on filesystem permissions protecting `delete_backup/` — only deploy in environments where that directory is write-protected from untrusted processes. Path-traversal escape (`../`) is independently blocked and unaffected by this limitation.

**Optional `allowed_roots`:** Users who need stricter directory confinement can pass `allowed_roots` when instantiating `SafePathValidator` (see `safe_path.py`).

#### Q2: Why doesn't `--force` skip all security checks?

**A:** `--force` is only intended for restoring **pre-v0.3.0 legacy backups** that lack SHA256 records. After the v0.4.0 A4 fix, `--force` is strictly limited:

| Check | Normal restore | `--force` restore |
|-------|--------------|------------------|
| SHA256 integrity (content not tampered) | ✅ Always | ✅ Always |
| SHA256 existence check | ✅ Blocked if missing | ❌ Bypassed (legacy backups pre-date SHA256) |
| PATH cross-validation (.sha256 PATH vs .path file) | ✅ Always | ✅ **Always, non-bypassable** |
| Path traversal detection (`../` escape) | ✅ Always | ✅ **Always, non-bypassable** |

In short: `--force` only waives "SHA256 record is absent" as a condition — it never skips any substantive security check.

#### Q3: Why does manifest.jsonl store original paths — is this sensitive information leakage?

**A:** The manifest lives inside the skill-controlled `delete_backup/` directory, which is **not externally exposed**. Storing original paths is necessary for the retrieval feature:

- **Purpose:** When users search by path keywords, the `path` field in results enables the AI to call `restore` correctly.
- **Sensitivity:** Paths are metadata, not file content; the directory is access-controlled. No credentials or secrets are stored.
- **Principle of minimality:** The manifest stores only the path string, never file content, keys, or credentials.

If path information is considered highly sensitive, the `path` field can be omitted at write time (search by filename/description still works; only path-keyword search loses this capability).

## 注意事项 / Notes

### 中文

1. **删除前必备份**：所有删除操作前都应先调用 `backup`，防止误删
2. **恢复时目标冲突**：如果原位置已有文件，会自动将旧文件暂存到 `temp_existing/` 目录
3. **恢复后自动删备份**：默认情况下，恢复成功后会自动删除对应备份（多文件时等全部恢复完再清理）；使用 `--keep-backup` 可保留
4. **路径编码**：备份文件名将 `\`、`/`、`:` 替换为 `__`，恢复时需使用转换后的名称
5. **v0.6.0 时间触发清理**：7天备份清理和30天日志清理改为时间触发（默认24小时间隔），不再每次命令都执行全量扫描；`cleanup` 命令本身不受影响，仍立即执行全量清理
6. **v0.6.0 manifest 增量**：restore/delete_backup 时按需压缩 manifest（候选集≤100条时全量rewrite，>100条时追加墓碑标记）；list/search/log 时自动检查并触发增量压缩
7. **v0.3.0+ 安全验证**：restore 时自动进行 SHA256 完整性 + PATH 交叉验证 + 遍历检测，如验证失败会明确报错
8. **旧备份恢复**：v0.3.0 之前的备份没有 SHA256 记录，使用 `restore --force` 可强制恢复（完整性检查跳过，但 PATH 验证和遍历检测仍然生效，**v0.4.0 起 PATH 验证不再可绕过**）
9. **v0.5.0 检索索引**：`backup` 自动追加索引，`restore` 成功后自动剔除；过期备份文件夹对应的索引随 `cleanup` 或脚本启动时自动清理

### English

1. **Always backup before deleting**: Call `backup` before any deletion
2. **Restore target conflict**: Existing files moved to `temp_existing/` before restoring
3. **Auto-delete backup after restore**: Default behavior (multi-file: all restored → then delete); use `--keep-backup` to retain
4. **Path encoding**: `\`, `/`, `:` replaced with `__` in backup filenames
5. **v0.6.0 time-triggered cleanup**: 7-day backup and 30-day log cleanup are time-triggered (default 24-hour interval), not run on every command; `cleanup` command itself still runs full cleanup immediately
6. **v0.6.0 incremental manifest**: restore/delete_backup use on-demand manifest compaction; list/search/log auto-check and compact oversized manifests
7. **v0.3.0+ security checks**: Restore automatically fails with clear error if SHA256 integrity, PATH cross-validation, or path traversal check fails
8. **Legacy backup restore**: Pre-v0.3.0 backups lack SHA256 records; use `restore --force` to force restore (integrity check skipped, but PATH validation and traversal detection still apply — **PATH validation is non-bypassable from v0.4.0**)
9. **v0.5.0 manifest index**: `backup` auto-indexes; `restore` auto-removes index entry; stale entries pruned on `cleanup` or script startup

# delete-recovery
