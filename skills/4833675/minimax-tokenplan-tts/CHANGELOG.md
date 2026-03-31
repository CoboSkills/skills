# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.9.1] - 2026-03-29

### Fixed

- **API 响应解析错误**：MiniMax API 的状态码位于 `base_resp.status_code`（而非顶层 `code` 字段），修复后正确解析业务状态码和错误信息

### Added

- `scripts/requirements.txt`：显式声明 `requests>=2.28.0` 依赖
- `import requests` 移至文件顶部，缺失时给出友好安装提示
- API Key 占位符检查：未配置时提前报错，避免无效 API 调用
- WAV/PCM 自动检测：检查 `RIFF` magic bytes，避免双重 WAV header
- `--timeout` 命令行参数：API 请求超时时间可配置（默认 60 秒）
- `make_slug` 函数文档补充：明确说明中文字符保留行为及替代方案

### Removed

- 删除未使用的 `URL` 全局变量

## [0.9.0] - 2026-03-27

### Added

- 初始版本
- MiniMax speech-2.8-hd 模型语音合成
- 支持 327 个音色，覆盖 40 种语言
- 语速、音量、音调参数控制
- HEX 解码 + WAV 输出
- stdout/stderr 分离（路径 → stdout，日志 → stderr）
- 语气词标签支持（笑声、咳嗽、呼吸等 18 种）
- 完整的 init 引导流程
