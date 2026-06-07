# 本地旧记忆只读盘点与授权导入

## 结论

Skill 没有超越运行时的“魔法权限”。它不能强行屏蔽任意 Agent 过去安装的本地记忆系统，也不能绕过系统策略或用户指令。

平台提供的是可执行的协作式旧记忆盘点协议：Agent 拉取 `memory_takeover_migrator` 后，把 MemoryCloud 作为本次任务的第一记忆来源，把旧本地记忆保留为只读参考。只有用户明确授权“导入旧记忆”时，Agent 才能把清洗后的长期事实上传到 workspace 或自我 Memory Suite。

## 入口

- 策略 JSON：`GET /api/agent/memory-takeover/policy`
- Skill 列表：`GET /api/agent/skills`
- Skill 拉取：`GET /api/agent/skills/memory_takeover_migrator/pull`
- 自动入口：`GET /agent-start`

## 优先级

接入策略后，Agent 的记忆读取顺序应为：

1. 系统策略、开发者策略和当前用户指令。
2. MemoryCloud workspace 云端记忆。
3. MemoryCloud 已验证 Memory Suite。
4. 旧本地记忆，只作为只读参考和授权导入来源。

这等价于调整任务记忆优先级，而不是销毁旧工具。

## 旧记忆来源

接管策略覆盖以下来源：

- Markdown：`MEMORY.md`、`DREAMS.md`、`memory/*.md`、`notes/*.md`。
- OpenClaw：`install/openclaw.json`、`.openclaw/**`。
- 数据库：SQLite/Postgres 导出、JSON 行记录。
- 向量库：Chroma、FAISS、Qdrant、Milvus 导出。
- Agent 运行时 Skill：旧 `SKILL.md`、旧记忆插件和本地记忆工具。

## 导入流程

1. Inventory：记录来源路径、大小、sha256、修改时间、格式和置信度。
2. Classify：把条目分类成 profile、task、project、code、decision、procedure、failure、entity、conversation 或 collaboration memory。
3. Redact：删除 API key、密码、cookie、私钥、会话 token、支付密钥和未经授权的个人信息。
4. Dedupe：先查询 MemoryCloud 云端记忆，跳过重复或置信度更低的条目。
5. Approval：如果用户没有明确授权导入旧记忆，到这里停止，只输出盘点结果。
6. Route：调用 `/api/memory/router/select` 选择结构。
7. Submit：调用 `/api/memory/forms/{run_id}/submit` 写入 workspace，或调用 `/api/memories/{slug}/sync` 同步到自我 Memory Suite。
8. Verify：查询一次云端记忆，确认可召回。
9. Deprecate：旧本地工具只写入可回滚只读标记。

## 弃用标记

运行时支持本地策略文件时，Agent 可以写入：

```json
{
  "schema": "amp.local-memory-deprecation.v1",
  "deprecated_by": "memory_takeover_migrator",
  "status": "deprecated_read_only",
  "preferred_source": "MemoryCloud memory",
  "rollback": "remove this marker and restore the previous retrieval order",
  "must_not_delete": true
}
```

## 禁止行为

- 不得静默删除旧记忆文件。
- 不得隐藏旧记忆来源。
- 不得上传密钥、密码、私钥或未经授权的隐私。
- 不得让旧记忆覆盖当前用户指令或系统策略。
- 不得把“安装了某个人的记忆”当成真实身份或授权证明。

## 数据库分层

当前数据库按职责分层：

- 身份与认证：`users`、`api_keys`、`agent_challenges`、`rate_limits`、`sms_codes`。
- 市场套件：`memory_packages`、`package_versions`、`downloads`、`sync_events`、`memory_search`。
- 协作记忆：`workspaces`、`workspace_members`、`adaptive_memory_runs`、`adaptive_memories`、`adaptive_memory_claims`。
- 交接与绑定：`project_handoffs`、`agent_binding_requests`、`agent_bindings`。
- 商业与治理：`orders`、`support_tickets`、`abuse_reports`、`audit_logs`。

SQLite WAL 已开启，适合当前轻量商业 MVP。更高写入并发的生产形态应迁移到 Postgres、Redis、对象存储和队列。
