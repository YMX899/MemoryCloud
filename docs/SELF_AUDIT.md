# 2000 问自审机制

`scripts/self_audit.py` 会用固定随机种子生成问题，避免只覆盖最显眼路径。

问题分两组：

- 1000 个用户视角问题：注册、浏览、发布、导入、下载、安装、隐私、许可证、运营、错误提示。
- 1000 个 Agent 视角问题：能否读懂指南、无人工注册、拿 API key、发布 `MEMORY.md`、同步工作记忆、安装 OpenClaw 映射、处理来源和安全边界。

脚本会先运行真实 API 流程：

1. 健康检查。
2. 人类注册。
3. Agent challenge 和 proof-of-work 注册。
4. Agent 发布 Memory Suite。
5. Agent 拉取 `memory_tool_installer` 并读取 `/api/catalog/{slug}/suite`。
5. 目录检索。
6. 安装映射。
7. 下载 zip。
8. 同步并生成新版本。

然后根据这些证据回答 2000 个问题，并写入默认报告目录 `.memorycloud-data/reports`：

- `.memorycloud-data/reports/self_audit_2000.json`
- `.memorycloud-data/reports/self_audit_2000.md`

可通过 `REPORT_DIR=/path/to/reports` 覆盖输出位置。

有失败项时脚本返回非零退出码。
