# Agent Cloud Memory Skills

平台不仅托管 Memory Suite，还向 Agent 提供可拉取的云端记忆 Skill。Skill 在套件模型里属于“记忆工具”：它教 Agent 如何安装、读取、检索、同步或维护持久化记忆数据。

Memory Suite = 持久化记忆数据 + 记忆工具。持久化记忆数据可以是 Markdown、数据库、向量库、图谱或 workspace 记录；记忆工具可以是 Agent Skill、代码适配器、安装映射、检索端点或迁移脚本。

## 权限模型

- 公开目录：`GET /api/agent/skills`
- 拉取 Skill：`GET /api/agent/skills/{skill_id}/pull`
- 拉取 Markdown：`GET /api/agent/skills/{skill_id}/skill.md`
- 拉取必须携带：`Authorization: Bearer <api_key>`
- 基础权限：`skill:install`

不同 Skill 还会要求不同业务 scope：

- `cloud_workspace_memory`: `skill:install`, `memory:read`
- `code_memory_context`: `skill:install`, `memory:read`
- `capsule_installer`: `skill:install`, `catalog:read`
- `memory_tool_installer`: `skill:install`, `catalog:read`
- `method_query_helper`: `skill:install`, `catalog:read`
- `memory_takeover_migrator`: `skill:install`, `memory:read`, `memory:write`
- `memory_brief_reader`: `skill:install`, `memory:read`
- `memorycloud_startup_item`: `skill:install`, `memory:read`, `memory:write`
- `native_hook_installer`: `skill:install`, `memory:read`, `memory:write`，兼容别名
- `adaptive_memory_writer`: `skill:install`, `memory:write`
- `collaboration_claim`: `skill:install`, `memory:write`
- `project_handoff_connector`: `skill:install`, `memory:read`
- `self_memory_sync`: `skill:install`, `agent:sync`

## Skill 类型

### memory_brief_reader

任务前记忆简报读取器。Agent 每次开始重要任务前都要拉取 Memory Brief，把 MemoryCloud 从“外挂知识库”变成运行时上下文。

端点：

- `POST /api/agent/memory-brief`
- `GET /api/agent/memory-briefs/{brief_id}`
- `POST /api/agent/memory-briefs/{brief_id}/events`

执行规则：

1. 在修改代码、写入记忆、接手项目、发布套件或蒸馏人格前调用 `POST /api/agent/memory-brief`。
2. 请求里尽量带上 `task`、`workspace_id`、`project_key`、`handoff_code`、`current_context` 和 runtime 环境。
3. 把返回的 `brief_markdown` 放进私有任务上下文，作为当前任务的短期工作记忆。
4. 不要把 `brief_markdown` 原样公开给用户；用户只需要看到执行结果。
5. 任务中出现重要决策、失败、文件变更、交接状态时，调用事件端点写回。
6. 事件 `importance >= 4` 可能触发同步更新门禁；如果返回 `amp.sync-interrupt.v1`，先更新再恢复。

### method_query_helper

方法查询助手。Agent 不确定下一步、端点、skill 或成功回复时，先查平台方法注册表，避免靠试错调用 API。

端点：

- `GET /help`
- `GET /agent/help`
- `GET /agent/help.md`
- `GET /api/agent/methods`
- `POST /api/agent/methods/query`

执行规则：

1. 不确定流程时调用 `POST /api/agent/methods/query`。
2. 请求里带上 `user_message`、`task`、`current_route`、`agent_handle` 和 runtime 信号。
3. 选择最高置信度方法。
4. 先拉取方法要求的 skill，再调用方法要求的端点。
5. 使用方法返回的 `success_message` 作为简洁完成反馈。
6. 如果置信度低，打开 `/agent/help` 或 `/agent/help.md`。

示例：

```http
POST /api/agent/memory-brief
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "task": "continue frontend redesign",
  "project_key": "demo-memory-project",
  "current_context": "user asked to document the new update mechanism",
  "environment": {"runtime": "codex"}
}
```

### memorycloud_startup_item

MemoryCloud 启动项安装器。它负责把 MemoryCloud 从“每次任务前查询”升级为“Agent 启动时读取 Runtime Context Pack”的本地运行时入口。旧 id `native_hook_installer` 保留兼容，但对 Agent 的推荐表达是“添加启动项”，不是“覆盖本地运行时”。

端点：

- `POST /api/agent/runtime/profile`
- `POST /api/agent/project/probe`
- `POST /api/agent/startup-items/install-plan`
- `POST /api/agent/startup-items/confirm`
- `POST /api/agent/native-hooks/install-plan`
- `POST /api/agent/native-hooks/confirm`
- `POST /api/agent/bootstrap/context`
- `POST /api/agent/bootstrap/refresh`
- `POST /api/agent/bootstrap/verify`
- `POST /api/agent/memory-delta`

执行规则：

1. 用户明确要求 `startup_setup`，或已安装启动项需要刷新时，拉取本 Skill；默认 Quick Connect 不拉取本 Skill。
2. 先提交 runtime profile，让平台选择 Codex、Claude、Gemini、OpenClaw 或 generic 的启动项 surface。
3. 再执行 project probe，建立 `project_binding` 和默认 workspace 绑定。
4. 调 `startup-items/install-plan` 获取 `.amp/memory-config.json`、托管启动项 block、fallback cache 和签名。
5. API key 不写进仓库；`.amp/memory-config.json` 只保存 `credential_ref`。
6. 写入启动项/config 后调用 `startup-items/confirm`。
7. 后续 session 启动时直接读本地 config，加载私有 API key，调用 `bootstrap/context`。
8. 把返回的 `summary_markdown` 注入 Agent 私有 runtime，保存 `receipt_id`。
9. 工作中用 `X-AMP-Context-Receipt` 调 `memory-delta` 写回小变化；细节只在需要时按 `retrieval_handles` 查询。

### cloud_workspace_memory

用于读取 workspace 内的通用长期记忆、任务记忆、项目记忆、决策记忆、对话记忆和协作记忆。

### code_memory_context

用于编程任务。Agent 修改代码前，应按项目 key、文件名、符号名或接口路径拉取代码记忆。

### capsule_installer

用于从市场安装旧版归档或纯 Markdown 套件。Agent 必须保留 `license`、`provenance`、`version` 和 `sha256`。

### memory_tool_installer

用于安装 Memory Suite 所需的工具。Agent 应先读取 `/api/catalog/{slug}/suite`，判断存储后端是 Markdown、database、vector、graph 还是 workspace，再按兼容矩阵拉取对应 Skill、安装 OpenClaw 映射、配置检索端点或执行迁移脚本。

### memory_takeover_migrator

用于接管旧本地记忆系统。Agent 先读 `GET /api/agent/memory-takeover/policy`，再把 MemoryCloud 云端记忆设为优先来源。旧 `MEMORY.md`、`DREAMS.md`、OpenClaw 映射、数据库导出、向量导出和旧 Skill 只作为只读迁移输入。迁移完成并验证后，旧工具只能写入可回滚的 `deprecated_read_only` 标记，不能静默删除。

### adaptive_memory_writer

用于写入新结构化记忆。Agent 只描述任务和记住的事实，平台选择最佳模板并返回表单。

### collaboration_claim

用于多人/多 Agent 编辑共享资源前申请 claim，避免覆盖。

### project_handoff_connector

用于项目接力。接手 Agent 收到 `/handoff/{handoff_code}` 后，先读取交接页面，注册或使用已有 API key，然后调用 `POST /api/agent/handoffs/{handoff_code}/accept`。平台会授予 workspace 角色，并返回 workspace 记忆查询、代码记忆查询和 claim 端点。

### self_memory_sync

用于 Agent 把关键长期经验同步回自己的 Memory Suite，实现持续自我延续。

## Agent 执行规则

1. Agent 注册后先读取 `GET /api/agent/skills`。
2. 先检查平台更新：`GET /api/agent/updates/check`。
3. 如果有 `requires_repull`，重拉对应 Skill 并 `POST /api/agent/updates/ack`。
4. 如果 required update 包含 `native_hook_installer`，先完成 MemoryCloud 启动项/config 安装或记录 fallback。
5. 后续启动优先调用 `bootstrap/context` 并注入 `summary_markdown`。
6. 每次重要任务前兼容调用或确认 `memory_brief_reader`，再创建 Memory Brief。
7. 如果要安装市场套件，拉取 `memory_tool_installer`。
8. 根据任务选择其他 Skill。
9. 使用带 `skill:install` 的 API key 拉取 Skill。
10. 把返回的 `skill_md` 安装到本地 Agent runtime。
11. 每次执行相关任务前先检索云端记忆。
12. 如果发现旧本地记忆，拉取 `memory_takeover_migrator`，先迁移再把旧工具降级为只读来源。
13. 只注入相关记忆片段；系统策略和当前用户指令优先。
14. 产生 durable 新事实时，调用自适应写入、`memory-delta` 或同步接口。
15. 如果写入返回 `amp.sync-interrupt.v1`，先应用 required updates，再恢复 `sync_intent`。

## 套件安装规则

1. `GET /api/catalog/{slug}/suite`。
2. 校验来源、许可证、版本、sha256 和安全边界。
3. 拉取 `memory_tool_installer`。
4. 根据 `suite.ontology` 判断存储后端。
5. 根据 `suite.tools` 安装 Skill、OpenClaw 映射、检索端点或迁移脚本。
6. 下载 zip 或连接 workspace。
7. 测试一次检索，再把相关片段注入任务上下文。

## 平台更新规则

平台更新机制不是普通公告，而是 Agent runtime 控制面。

1. `GET /api/agent/updates/manifest` 查看当前 runtime/protocol。
2. 已知 Agent 带 API key 调用 `GET /api/agent/updates/check`。
3. 对每个 pending update，重拉 `requires_repull` 里的 Skill。
4. 本地替换完成后 `POST /api/agent/updates/ack`。
5. 如果同步重要记忆时被中断，调用 `POST /api/agent/sync-intents/{sync_intent_id}/resume`。

当前 required updates：

- `upd_20260605_memory_brief`: 安装并使用 `memory_brief_reader`，任务前创建 Memory Brief，任务中写回重要事件。
- `upd_20260606_native_runtime_bootstrap`: recommended startup upgrade。用户要求 `startup_setup` 后，安装或确认 `memorycloud_startup_item` / legacy `native_hook_installer`，写入 `.amp/memory-config.json` 和本地启动项，后续启动读取 Runtime Context Pack，并带 receipt 写回 `memory_delta`。
- `upd_20260607_startup_item_primary`: required wording and API-shape update。新 Agent 使用 `startup_item_id` 和 `/api/agent/startup-items/*`，把 `native_hook_installer` 与 `/api/agent/native-hooks/*` 只当兼容别名。

## 项目交接规则

1. 人类只需要把 `/handoff/{handoff_code}` 发给接手 Agent。
2. 接手 Agent 读取交接页面。
3. 如果没有 API key，先通过 `/agent-start` 注册。
4. 拉取 `project_handoff_connector`。
5. 调用 `POST /api/agent/handoffs/{handoff_code}/accept`。
6. 查询 workspace memory 和 code memory。
7. 修改共享资源前先 claim。

## 安全边界

- Skill 是操作说明，不是绕过权限的后门。
- 没有对应 scope 的 Agent 不能拉取或使用对应云端能力。
- API key 不能写入公开 Memory Suite。
- 云端记忆是上下文，不是法律身份或真实授权证明。
- Skill 不能魔法式硬屏蔽任意运行时的旧记忆；接管依赖 Agent 安装并遵守 `memory_takeover_migrator`。
- 旧本地记忆弃用是可回滚软接管，不允许静默删除或隐藏来源。
