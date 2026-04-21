---
name: skillscan-wrapper
description: 使用内置 Rust 引擎审计待安装的 skill 包或归档，并可选桥接外部 scanner。
license: MIT-0
author: CMIC Skill Scanner
---

# Skill Scan Wrapper

当你要在安装一个本地 skill、归档或 release bundle 前做一次快速安全检查时，使用这个 skill。

## ⚠️ Security Notice

This tool operates **locally** and requires user trust in the binary you run. **Always verify the checksum after downloading** (see below). For maximum security, build from source (recommended).

## 安装

### Method 1: Build from Source (Recommended)

This package is open-source (MIT-0). The recommended way to obtain the binary is to build it yourself, so you can verify every line of code:

```bash
git clone https://gitee.com/cmic-team/cmic-skill-scanner.git
cd cmic-skill-scanner
cargo build --release
# Binary will be at: target/release/skillscan
```

Building from source ensures:
- You can audit all code before execution
- No reliance on external binary distribution
- Reproducible builds

### Method 2: Precompiled Binary (Convenience Only)

If you prefer a prebuilt binary, download from the Gitee Release page:

**下载地址**: https://gitee.com/cmic-team/cmic-skill-scanner/releases

> **⚠️ IMPORTANT: You MUST verify the binary after downloading.** The precompiled binary is provided as a convenience only. By downloading it, you accept the risk of trusting an externally-hosted executable.

Download the appropriate binary for your platform. On Linux/macOS, make it executable:

```bash
chmod +x skillscan
```

## 🔒 Verification (Mandatory for Precompiled Binaries)

**⚠️ VERIFICATION IS MANDATORY.** Skipping this step means you are trusting an arbitrary binary without verification.

After downloading, **always** verify the checksum before first use:

```bash
sha256sum skillscan
```

Compare the output against the published checksum on the Gitee Release page.

> **If the checksums do not match, DELETE the binary immediately and do not run it.** An mismatched checksum indicates potential tampering.

Check the Gitee Release page for the **expected SHA-256 checksum** and **version** of the binary you download. Always verify against that official source.

## 前置条件

- 默认不需要任何外部依赖
- `--upload-url` 和 `--engine external` 功能**默认禁用**，仅在用户显式配置时启用

## 信任模型

This is an **open-source (MIT-0) reference package**. The binary download is a **convenience only** — it does not grant any additional trust.

**Your options:**

| Approach | Trust Requirement | Verification |
|----------|------------------|--------------|
| Build from source | None (you control everything) | Manual code review |
| Precompiled binary | You trust the release host | SHA-256 checksum |

**What the tool does NOT do by default:**
- Does NOT upload data anywhere
- Does NOT connect to the network
- Does NOT access credentials, SSH configs, or environment variables
- Does NOT execute external tools unless you explicitly configure `--engine external`

## 工作流程

1. 调用 skillscan：

```bash
skillscan review /path/to/target --format markdown
skillscan review /path/to/skills --output-dir /tmp/skillscan-out
```

2. 阅读输出中的：
   - 输入类型
   - 完整度
   - engine 执行状态
   - findings

3. 如果输入只是 HTML 页面或其他非 scanner-ready 形式，先获取完整本地包再重试。

## 网络上传功能 (默认禁用)

**⚠️ This feature is completely optional and disabled by default.** It requires explicit user configuration via `--upload-url`.

### About --upload-url

**Default behavior**: Disabled. No network calls are made unless you explicitly provide `--upload-url`.

**What gets sent** (only when you configure `--upload-url`):
- A structured JSON report containing detection findings
- An instance identifier you supply via `--instance-id`
- **No skill source code, credentials, or system configuration is ever transmitted**

**Security recommendation**: Only use `--upload-url` with trusted internal infrastructure endpoints.

### About --instance-id

A user-supplied label you choose (e.g., `prod-a1`, `dev-workstation`) for correlating reports across multiple hosts. This is not telemetry — it's a human-readable tag you control entirely. This is only sent if `--upload-url` is configured.

### Example with upload

```bash
skillscan review /path/to/skills \
  --output-dir /tmp/skillscan-out \
  --upload-url https://scanner.example.com/api/report \
  --instance-id prod-a1
```

## 外部引擎集成 (默认禁用)

**⚠️ This feature is completely optional and disabled by default.** It requires explicit user configuration via `--engine external`.

### About --engine external

**Default behavior**: Disabled. The built-in Rust engine is used unless you explicitly set `--engine external`.

**How it works**: Delegates pattern-matching to a user-configured local tool already installed on your system (e.g., your company's internal scanner). This runs **locally** — no remote calls are made.

**What it can access**: Only the files that skillscan itself reads (the target skill paths you specified). The external engine cannot expand beyond what skillscan reads.

**Typical use case**: Organizations with custom rule sets or compliance checks that run through their own tooling pipeline.

### Example with external engine

```bash
skillscan review /path/to/target --engine external --format markdown
```

## Permissions Required

| Scope | Reason |
|-------|--------|
| Read files in target path | To analyze skill source code for patterns |
| Write to `--output-dir` | To save scan reports locally |
| Execute binary | To run the scanner engine |
| Network (optional) | **Only if `--upload-url` is explicitly configured** — sends JSON report only, to user-controlled endpoint |
