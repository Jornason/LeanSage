# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Lean 4 在线编辑器集成 LSP 实时编译检查
- LaTeX → Lean 4 双向转换功能
- 证明步骤自然语言解释
- 机构 License 管理后台
- Mathlib 定理收藏夹功能
- 用户证明历史导出（JSON/LaTeX）

### Changed
- 升级 Claude API 至 claude-3-5-sonnet-v2
- 优化向量检索 Top-K 召回率

### Fixed
- 修复含 universe polymorphism 的定理检索遗漏问题

## [0.1.0] - 2026-04-15

### Added
- Mathlib 语义搜索：自然语言查询 → 向量检索返回相关定理名 + 类型签名
- 自然语言 → Lean 4 证明草稿生成（Claude 驱动）
- 证明错误诊断：粘贴报错代码 → AI 解释 + 修复建议
- 用户注册/登录（Supabase Auth, GitHub OAuth）
- 订阅计费系统（Free / Researcher / Lab）
- CodeMirror Lean 4 语法高亮编辑器
- KaTeX 数学公式实时渲染
- Mathlib 4 全量定理 embedding 索引（约 20 万条）
- 基础用量统计仪表盘
- API Rate Limiting（按订阅等级）
