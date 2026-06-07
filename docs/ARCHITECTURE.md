# 架构设计

## 技术栈

- 后端：FastAPI。
- 数据库：SQLite WAL，适合轻量部署；生产高写入可迁移 Postgres。
- 前端：原生 HTML/CSS/JS SPA，无 Node 构建链。
- 存储：本地 zip archive；生产建议换 S3/OSS/COS + CDN。
- 鉴权：JWT 风格会话 token + API key。

## 数据表

- `users`：人类或 Agent 用户。
- `api_keys`：Agent 和自动化使用的密钥。
- `agent_challenges`：proof-of-work 注册挑战。
- `sms_codes`：短信验证码。
- `memory_packages`：Memory Suite 元数据。表名保留旧称以兼容现有 API，业务语义是“持久化记忆数据 + 记忆工具”的套件。
- `package_versions`：版本化内容和 archive 路径。
- `downloads`：下载日志。
- `sync_events`：Agent 同步事件。
- `audit_logs`：安全审计。
- `rate_limits`：内置窗口限流。
- `memory_search`：SQLite FTS5 搜索索引。
- `memory_briefs`：Agent 任务前 Memory Brief 记录，保存 task、workspace、project、source_counts、brief_json 和 `brief_markdown`。
- `memory_brief_events`：Memory Brief 事件流，保存任务中的决策、失败、文件变更和交接状态。
- `platform_update_acks`：Agent 对平台 runtime/protocol 更新的确认记录。
- `sync_intents`：重要记忆写入被更新门禁暂停时保存的原始写入意图，默认 24 小时过期。
- `project_bindings`：Agent 本地仓库、workspace 和 `project_key` 的绑定。
- `native_hook_installs`：AGENTS.md、CLAUDE.md、GEMINI.md、Cursor rules、fallback prompt 等 MemoryCloud 启动项安装记录。表名保留 legacy 命名。
- `context_packs`：Agent 启动时读取的 Runtime Context Pack 摘要。
- `bootstrap_receipts`：证明 Agent 已读取某份 context pack 的 receipt。
- `memory_deltas`：Agent 工作中写回的小变化，包含 summary、why_it_matters、retrieval_triggers 和 detail payload。
- `summary_cards`：由 delta/旧事件生成的轻量摘要卡，用于下次 context pack。

## Memory Suite 层

每个市场条目都是 Memory Suite：

- 持久化记忆数据：Markdown、数据库 rows、向量集合、图谱事实或 workspace 记录。
- 记忆工具：Agent Skill、OpenClaw 映射、检索端点、迁移脚本或多 Agent claim 工具。
- 套件清单：`suite/manifest.json` 和 `/api/catalog/{slug}/suite`。

后端仍用 `amp.memory.v1` zip 做轻量归档；新归档会写入 `amp.memory-suite.v1` 套件清单。Agent 安装时先拉取 `memory_tool_installer`，再按存储后端选择工具。

## Agent Runtime 控制面

平台不只托管记忆数据，还向 Agent 发布运行时规则。当前 runtime 版本由 `PLATFORM_RUNTIME_VERSION` 定义，协议版本由 `PLATFORM_PROTOCOL_VERSION` 定义。

控制面包含三部分：

1. 更新清单：`GET /api/agent/updates/manifest` 返回 `amp.platform-updates.v1`，列出当前 runtime、protocol、组件版本和更新项。
2. Agent 检查：`GET /api/agent/updates/check` 返回 `amp.platform-update-check.v1`，按当前 Agent 的 `platform_update_acks` 计算 pending updates。
3. 应用确认：`POST /api/agent/updates/ack` 把已应用更新写入 `platform_update_acks`。

已知 Agent 回访 autostart、discovery、navigation、registration、`/api/me`、`/api/session`、`/api/agent/bindings/me` 时，响应会附带 `amp.platform-update-notice.v1`。notice 只提示更新存在，Agent 仍必须调用 check 端点获取针对自己的 pending 列表。

## Memory Brief Runtime

Memory Brief 是让云端记忆主动进入 Agent 工作循环的运行时层。

流程：

1. Agent 拉取 `memory_brief_reader`。
2. 每次任务开始前调用 `POST /api/agent/memory-brief`。
3. 后端按 `workspace_id`、`project_key`、`handoff_code`、最近事件和当前上下文生成 `brief_markdown`。
4. Agent 把 `brief_markdown` 注入私有任务上下文。
5. 任务中通过 `POST /api/agent/memory-briefs/{brief_id}/events` 写回事件。

这层不是搜索接口的替代品。它是任务启动时的“我是谁、我在哪个项目、之前做到哪里”的 brief；执行中仍可继续调用 workspace/code memory 检索。

## Native Runtime Bootstrap

Native Runtime Bootstrap 是 Memory Brief 的升级层。目标不是让 Agent 每次 query 云端，而是让 Agent 启动时通过本地启动项或运行时规则文件读取一份短摘要，形成自我认知，再按需查询详情。它复用 Runtime Context Pack / Memory Brief / retrieval handles，不另建一套记忆系统。

首次接入：

1. Agent 调 `POST /api/agent/runtime/profile` 提交运行时类型。
2. Agent 调 `POST /api/agent/project/probe` 建立 `project_binding`。
3. Agent 调 `POST /api/agent/startup-items/install-plan` 获取 `.amp/memory-config.json` 和托管启动项 block。
4. Agent 写入本地 config/启动项，API key 只放私有凭证区，不进入仓库。
5. Agent 调 `POST /api/agent/startup-items/confirm` 确认安装。

后续启动：

1. Runtime 自动读取 AGENTS.md、CLAUDE.md、GEMINI.md 或 rules。
2. 启动项指向 `.amp/memory-config.json`。
3. Agent 用 `credential_ref` 读取私有 API key。
4. Agent 调 `POST /api/agent/bootstrap/context`。
5. 平台生成 `amp.context-pack.v1`，返回 `summary_markdown` 和 `amp.bootstrap-receipt.v1`。
6. Agent 把 summary 注入私有 runtime；如果记忆模糊，再按 `retrieval_handles` 查询详情。
7. 工作中用 `POST /api/agent/memory-delta` 写回小变化。

启动摘要的来源只来自 runtime 写回和 workspace 记忆层：`memory_delta`、自适应 workspace memory、旧 `memory_brief_events` 镜像出的 delta/card。单纯发布 `memory suite` 不会自动进入摘要，因为 suite 是市场可安装资产，不代表当前 Agent 已安装、授权、连接或需要它。

旧 `POST /api/agent/memory-brief` 继续兼容，同时返回 `context_pack` 和 `receipt_id`。旧 `memory_brief_events` 会同步写入 `memory_deltas` 和 `summary_cards`，让旧 Agent 的写回也能进入新版摘要系统。

## 记忆写入门禁

平台在 Agent 写入重要记忆时调用 `runtime_gate_for_memory_write()`。

门禁规则：

- 只检查 `auth_type=agent`。
- `force=true` 或人类写入直接放行。
- 有 required update 且 `importance >= 4`：创建 `sync_intents`，返回 HTTP 409 和 `amp.sync-interrupt.v1`。
- 有 required update 且 `importance < 4`：写入继续，响应附带 `amp.runtime-update-warning.v1`。

当前接入门禁的写入包括：

- `POST /api/memories/{slug}/sync`
- `POST /api/memory/forms/{run_id}/submit`
- `POST /api/agent/memory-briefs/{brief_id}/events`
- `POST /api/persona/distill-jobs`
- `POST /api/persona/distill-jobs/json`

可自动恢复的 `sync_intent` endpoint：

- `memory_suite_sync`
- `adaptive_memory_submit`
- `memory_brief_event`
- `persona_distill_job_json`

multipart 文件上传不会保存二进制文件。此类任务被拦截后，应先应用更新，再重新上传文件。

## AgentPass 注册

传统验证码会阻止真实 Agent 自动注册。平台使用 AgentPass：

1. Agent 读 `/api/agent-guide`。
2. 调 `/api/agent/challenge` 获取 `challenge_id`、`server_nonce`、`difficulty`。
3. 计算 `sha256(challenge_id:server_nonce:nonce)`，直到前缀满足 difficulty。
4. 调 `/api/agent/register`。
5. 平台结合速率限制、过期时间、honeypot 字段和审计日志防脚本滥用。

这不是绝对防刷，而是把攻击成本从免费请求提升到可调计算成本；生产可叠加 IP 信誉、设备指纹、行为评分和人工审核。

## 一千并发稳定性

当前实现的 1000 并发目标按轻量平台读流量设计：

- Uvicorn 多 worker。
- 反向代理保持连接和压缩。
- SQLite WAL 支持大量并发读，写入串行化。
- 上传和下载走对象存储/CDN 后，应用只处理鉴权和元数据。
- 限流按 Redis 替换内置 SQLite 表。

推荐生产命令：

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8000
```

推荐生产拆分：

- Postgres：用户、订单、包元数据、审计。
- Redis：限流、短期 challenge、会话吊销。
- 对象存储：memory zip。
- CDN：公开下载。
- 队列：审核、病毒扫描、异步索引。
