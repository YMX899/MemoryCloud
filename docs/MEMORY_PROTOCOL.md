# Agent Memory Protocol (AMP)

Agent Memory Protocol (AMP) 是 MemoryCloud 的底层协议族。产品和 MemoryCloud Registry 上展示的是 Memory Suite：持久化记忆数据 + 记忆工具。旧称“旧版归档”的 zip 仍兼容，但新归档会额外包含 `suite/manifest.json`，用于让 Agent 判断如何安装工具、连接内容层和测试检索。

标准命名：

- 公司：Yueming AI。
- 产品：MemoryCloud，中文名：记忆云。
- 企业版：MemoryCloud Private Cloud。
- 协议：Agent Memory Protocol (AMP)。
- 市场：MemoryCloud Registry。
- 资产：Memory Suite。
- 迁移/接入模块：MemPort Gateway。

详细套件设计见 [MEMORY_SUITE.md](MEMORY_SUITE.md)。

## 文件结构

```text
manifest.json
suite/manifest.json
MEMORY.md
memory/YYYY-MM-DD.md
DREAMS.md
agent.instructions.md
install/openclaw.json
README.md
```

## 语义

`suite/manifest.json`

声明 `schema=amp.memory-suite.v1`，描述持久化记忆数据、记忆工具、兼容矩阵和安装生命周期。Agent 安装市场套件时应先读取这个文件，再决定拉取哪些 Skill、安装哪些映射、如何连接 Markdown、数据库或向量检索记忆。

`manifest.json`

声明 schema、标题、摘要、版本、许可证、标签、来源、兼容性和安全边界。平台校验 `schema=amp.memory.v1`、semver 版本、license 和 provenance。新 manifest 还会包含 `memory_ontology`、`memory_tools` 和 `suite` 摘要。

`MEMORY.md`

长期记忆。适合保存身份边界、偏好、稳定事实、项目约定、常见流程和行为风格。兼容 OpenClaw 风格长期记忆。

`memory/YYYY-MM-DD.md`

工作记忆。Agent 每天或每次关键事件追加。平台 sync API 会自动把新事件追加到当天文件，并生成 patch 版本。

`DREAMS.md`

反思、梦境、蒸馏结论。安装方 Agent 在第一次执行任务前读取，用来形成高阶行为倾向。

`agent.instructions.md`

安装说明。告诉 Agent 如何合并记忆、如何处理冲突、如何暴露 provenance。

`install/openclaw.json`

OpenClaw 风格 active-memory 映射：

```json
{
  "target": "openclaw",
  "merge": {
    "long_term": "MEMORY.md",
    "work_memory": "memory/*.md",
    "reflections": "DREAMS.md"
  }
}
```

## 持久化记忆数据

持久化记忆数据是内容本身，可以是：

- Markdown：`MEMORY.md`、`DREAMS.md`、`memory/*.md`。
- 数据库：按行存储的长期事实、工作记忆、反思记录。
- 向量：由书籍、人物、项目文档或长记忆切分后的 embedding collection。
- 图谱：实体、关系和事件边。
- Workspace：平台 `adaptive_memories` 中可查询的多人/多 Agent 记忆。

## 记忆工具

记忆工具是支持内容层被安装和调用的执行层，包括：

- `memory_tool_installer`：先拉取的套件安装 Skill。
- `capsule_installer`：兼容旧旧版归档的安装 Skill。
- `cloud_workspace_memory`：任务前读取云端 workspace 记忆。
- `code_memory_context`：编程 Agent 读取代码记忆。
- `adaptive_memory_writer`：写入结构化记忆。
- `collaboration_claim`：多人/多 Agent 写共享资源前申请锁。
- `self_memory_sync`：把 Agent 的长期经验同步回自己的套件。
- `install/openclaw.json`：OpenClaw 风格安装映射。

## API

- `GET /api/protocol/schema`：机器可读协议说明。
- `GET /api/catalog/{slug}/suite`：机器可读套件清单，包含内容层、工具、兼容和安装生命周期。
- `GET /api/agent/skills`：记忆工具目录。
- `GET /api/agent/skills/{skill_id}/pull`：拉取某个记忆工具 Skill。
- `POST /api/agent/memory-brief`：任务开始前生成 Memory Brief。
- `GET /api/agent/memory-briefs/{brief_id}`：读取已有 Memory Brief 和事件流。
- `POST /api/agent/memory-briefs/{brief_id}/events`：写回任务中的关键事件。
- `GET /api/agent/methods`：读取 Agent 方法注册表。
- `POST /api/agent/methods/query`：Agent 忘记流程时按用户消息、任务和 runtime 查询方法卡，避免试错。
- `GET /api/agent/updates/manifest`：读取平台 runtime/protocol 更新清单。
- `GET /api/agent/updates/check`：已知 Agent 检查待应用更新。
- `POST /api/agent/updates/ack`：Agent 应用更新后确认。
- `GET /api/agent/sync-intents`：列出被更新门禁暂停的同步意图。
- `GET /api/agent/sync-intents/{sync_intent_id}`：读取单个同步意图。
- `POST /api/agent/sync-intents/{sync_intent_id}/resume`：应用更新后恢复原始写入。
- `POST /api/agent/sync-intents/{sync_intent_id}/discard`：放弃原始写入。
- `POST /api/agent/runtime/profile`：提交 Agent 运行时类型和能力。
- `POST /api/agent/project/probe`：把本地仓库绑定到 workspace/project_key。
- `POST /api/agent/startup-items/install-plan`：生成 MemoryCloud 启动项和 `.amp/memory-config.json` 安装计划。
- `POST /api/agent/startup-items/confirm`：确认 MemoryCloud 启动项已安装或 fallback 生效。
- `POST /api/agent/native-hooks/install-plan`：旧兼容别名。
- `POST /api/agent/native-hooks/confirm`：旧兼容别名。
- `POST /api/agent/bootstrap/context`：启动时生成 Runtime Context Pack 和 receipt。
- `POST /api/agent/bootstrap/verify`：验证 receipt。
- `POST /api/agent/bootstrap/refresh`：工作中刷新 context pack。
- `POST /api/agent/memory-delta`：带 receipt 写回任务中的小变化。
- `GET /api/agent/context-packs/{context_pack_id}`：读取 context pack。
- `GET /api/agent/memories/{memory_id}`：按原生 memory id 读取记忆详情。
- `GET /api/agent/installed-open-memories/{installed_memory_id}`：按 `imem_...` 安装记录读取已安装开源记忆详情。
- `POST /api/memories`：从 JSON 字段创建 memory suite。
- `POST /api/memories/import`：上传 zip。
- `GET /api/catalog/{slug}/download`：下载 suite zip。
- `GET /api/catalog/{slug}/install/openclaw`：获取安装映射。
- `POST /api/memories/{slug}/sync`：追加工作记忆并生成新版本。

## Memory Brief Runtime

`amp.memory-brief.v1` 是任务前运行时简报协议。它把 workspace 记忆、项目 key、交接状态、最近事件和当前任务合成为一份 `brief_markdown`，让 Agent 在行动前就知道“我之前做过什么、当前项目是什么、这次任务该继承哪些约定”。

创建请求：

```http
POST /api/agent/memory-brief
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "task": "continue frontend redesign",
  "workspace_id": "optional",
  "project_key": "demo-memory-project",
  "handoff_code": "optional",
  "current_context": "short current context",
  "environment": {"runtime": "codex"},
  "max_items": 8
}
```

关键响应字段：

- `schema`: `amp.memory-brief.v1`
- `brief_id`: 本次任务简报 ID。
- `runtime_version`: 当前平台 runtime 版本。
- `brief_markdown`: Agent 应注入私有上下文的简报正文。
- `source_counts`: 本次简报使用了多少 workspace/project/handoff/event 来源。
- `next.writeback`: 写回事件端点。

事件写回使用 `amp.memory-brief-event.v1`：

```http
POST /api/agent/memory-briefs/{brief_id}/events
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "event_type": "decision",
  "summary": "Used Memory Brief as private runtime context before editing.",
  "importance": 4,
  "payload": {"files": ["app/main.py"]}
}
```

事件类型建议：

- `decision`: 关键产品、架构或实现取舍。
- `changed_files`: 重要文件变更。
- `failure`: 失败、回滚、测试问题。
- `handoff_ready`: 适合交给下一个 Agent 的状态。
- `task_event`: 默认通用事件。

## Open Memory Native Activation

`amp.memory-native-activation.v1` 解决“安装成功但下一句回答没有用上”的问题。它不是第二套记忆系统，而是复用已有项目工程记忆 native runtime 手法的薄桥接层：`installed_open_memory -> create_context_pack -> Active Installed Memory Lenses -> retrieval_handles`。

执行规则：

1. 优先读取 `memory_native_activation.runtime_context_pack.summary_markdown`，立即注入私有运行时上下文。
2. 把 `memory_native_activation` 理解为 activation bridge，不要把它当权威记忆正文。
3. 如果没有返回 `runtime_context_pack`，调用 `memory_native_activation.refresh_requests.bootstrap_context` 或 `memory_native_activation.refresh_requests.memory_brief`。
4. 确认上下文里出现 `Active Installed Memory Lenses`。
5. 后续相关问题把它当作当前 workspace 原生记忆使用，即使用户没有再次说包名。
6. `imem_...` 安装记录详情走 `GET /api/agent/installed-open-memories/{installed_memory_id}`，不要把详情 404 当成“只有索引没有内容”。

边界：已安装开源记忆是方法/上下文 lens，不是身份冒充，不覆盖系统、开发者或当前用户指令。

## Platform Updates

`amp.platform-updates.v1` 是平台更新清单协议。它解决“平台机制变了，老 Agent 不知道”的问题。当前 runtime 版本是 `2026.06.07-startup-item-primary.1`，协议版本是 `amp.runtime.2026-06-07`。

清单端点：

```http
GET /api/agent/updates/manifest
```

检查端点：

```http
GET /api/agent/updates/check
Authorization: Bearer <api_key>
X-MemoryCloud-Runtime-Version: 2026.06.07-startup-item-primary.1
X-MemoryCloud-Applied-Updates: upd_old
```

旧 `X-Cloudmemory-*` 请求头继续兼容；新 Agent 应使用 `X-MemoryCloud-*`。

`amp.platform-update-check.v1` 会返回：

- `has_pending_updates`: 是否仍有未应用更新。
- `pending_updates`: required/recommended 更新列表。
- `pending_updates[].requires_repull`: 需要重拉的 Skill。
- `acked_updates`: 当前 Agent 已确认的更新。
- `next_actions`: 应执行的本地动作。

确认端点：

```http
POST /api/agent/updates/ack
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "update_ids": ["upd_20260607_startup_item_primary"],
  "seen_version": "2026.06.07-startup-item-primary.1"
}
```

平台会在 autostart、discovery、navigation、registration、`/api/me`、`/api/session`、`/api/agent/bindings/me` 等已知 Agent 回访路径附带 `amp.platform-update-notice.v1`。Agent 收到 notice 后必须调用 check，而不是只读取 notice。

确认时，服务器按每个 update 自己的 `version` 写入 `platform_update_acks`。这样升级全局 runtime 后，已经应用过的旧 update 不会因为全局版本变化而重新 pending。`seen_version` 是客户端报告字段，保留用于审计和兼容。

## Native Runtime Bootstrap

`amp.native-runtime.v1` 是让 Agent 启动时读取摘要的协议族。默认 `/agent/start` 先走 Quick Connect；用户明确要求 `startup_setup` 后，才把“云端记忆查询”升级为“Agent native memory runtime”。它复用现有 Runtime Context Pack / Memory Brief / retrieval handles，不创建第二套 hook 或记忆正文系统：

```text
Quick Connect 读取 Memory Brief / Runtime Context Pack
 -> 用户明确要求后添加启动项/config
 -> 启动读取 context pack
 -> 注入 summary_markdown
 -> 保存 receipt
 -> 工作中写 memory_delta
 -> 需要细节时按 retrieval_handles 查询
```

运行时画像：

```http
POST /api/agent/runtime/profile
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "runtime": "codex",
  "repo_root": "/home/demo-memory-project",
  "git_remote": "https://github.com/org/repo.git",
  "supports_files": true
}
```

项目绑定 `amp.project-binding.v1`：

```http
POST /api/agent/project/probe
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "runtime": "codex",
  "project_key": "demo-memory-project",
  "repo_root": "/home/demo-memory-project",
  "git_remote": "https://github.com/org/repo.git"
}
```

MemoryCloud 启动项安装计划 `amp.startup-item-install-plan.v1`：

```http
POST /api/agent/startup-items/install-plan
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "runtime": "codex",
  "project_binding_id": "pbind_xxx",
  "credential_ref": "memorycloud_default"
}
```

返回内容包括 `.amp/memory-config.json`、托管启动项 block、fallback cache 和签名。启动项只写启动器，不写 API key、不写大段记忆。

授权边界：

- `/agent/start` 链接默认授权 Quick Connect：注册或复用身份、私密保存 API key、拉取最小记忆工具、请求 Memory Brief 或 Runtime Context Pack、写 receipt 和 memory_delta。
- 写 `.amp/memory-config.json`、写 MemoryCloud 启动项属于 `startup_setup`，需要用户明确要求。
- 本地旧记忆导入、删除/覆盖/隐藏旧记忆、把密钥写入仓库、安装无关服务仍需明确授权。

旧兼容 schema `amp.native-hook-install-plan.v1` 和端点 `/api/agent/native-hooks/install-plan` 保留，返回同一计划。

Context Pack `amp.context-pack.v1`：

```http
POST /api/agent/bootstrap/context
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "workspace_id": "wsp_xxx",
  "project_key": "demo-memory-project",
  "project_binding_id": "pbind_xxx",
  "runtime": "codex",
  "reason": "agent_startup"
}
```

关键响应字段：

- `summary_markdown`: Agent 醒来时注入私有 runtime 的摘要。
- `retrieval_handles`: 详情查询入口。`detail_endpoint` 必须是服务端已 URL encode 的可直接请求 URL，不能要求 Agent 再手工编码空格或中文。
- `receipt_id`: 本轮上下文 receipt。
- `receipt`: `amp.bootstrap-receipt.v1`。
- `memory_policy.detail_on_demand`: 只摘要先入 runtime，细节按需查询。

进入 Context Pack 的来源：

- `memory_delta`: Agent 带 receipt 写回的任务变化。
- adaptive workspace memory: 通过 `/api/memory/router/select` 和 `/api/memory/forms/{run_id}/submit` 写入的结构化 workspace 记忆。
- mirrored legacy event: 旧 `memory_brief_events` 会镜像到 `memory_deltas` 和 `summary_cards`。

不自动进入 Context Pack 的来源：

- 单纯发布或上架 `amp.memory-suite.v1`。suite 是可安装资产，只有安装、连接内容层、检索测试，或把其中稳定事实写入 workspace/adaptive memory 或 `memory_delta` 后，才进入 runtime 摘要链。

Memory Delta `amp.memory-delta.v1`：

```http
POST /api/agent/memory-delta
Authorization: Bearer <api_key>
X-AMP-Context-Receipt: amp_receipt_xxx
Content-Type: application/json

{
  "delta_type": "decision",
  "summary": "Runtime Context Pack is the startup summary.",
  "why_it_matters": "Future sessions should inject summary first and query details on demand.",
  "retrieval_triggers": ["startup", "native memory"],
  "importance": 4
}
```

没有 receipt 时返回 `428 amp.bootstrap-required.v1`。旧 `amp.memory-brief.v1` 继续兼容，并会附带新 `context_pack` 和 `receipt_id`。

## Sync Interrupt

`amp.sync-interrupt.v1` 是同步记忆时的强制更新门禁。它让平台能在 Agent 下一次同步重要记忆时说“先等等，更新 runtime 后再写入”，同时保存原始写入意图，避免丢失工作成果。

门禁规则：

- 只拦截 `auth_type=agent` 的写入。
- 人类写入不被拦截。
- 存在 required update 且 `importance >= 4` 时，返回 HTTP 409。
- 存在 required update 且 `importance < 4` 时，写入继续，但响应带 `amp.runtime-update-warning.v1`。
- `sync_intent` 默认 24 小时过期。

中断响应：

```json
{
  "schema": "amp.sync-interrupt.v1",
  "status": "blocked_for_runtime_update",
  "sync_intent_id": "syncint_...",
  "message": "先应用 MemoryCloud 更新，再继续同步。",
  "importance": 4,
  "required_updates": [],
  "recommended_updates": [],
  "update_check": "/api/agent/updates/check",
  "ack": "/api/agent/updates/ack",
  "resume": {
    "after_ack": "/api/agent/sync-intents/{sync_intent_id}/resume",
    "method": "POST",
    "expires_in": "24h"
  }
}
```

恢复成功响应使用 `amp.sync-intent-resume.v1`，并包含原始写入的 `result`。

可自动恢复的 endpoint：

- `memory_suite_sync`
- `adaptive_memory_submit`
- `memory_brief_event`
- `persona_distill_job_json`

文件上传类 `persona_distill_job` 不会把二进制文件存入 `sync_intent`。如果 multipart 上传被拦截，Agent 应先完成更新，再让原流程重新上传文件。

## 安装策略

安装方 Agent 应按顺序读取：

1. `suite/manifest.json` 或 `/api/catalog/{slug}/suite`：确认内容层、工具、兼容性和安装生命周期。
2. `manifest.json`：确认 license、来源、版本、sha256 和安全边界。
3. `memory_tool_installer`：拉取并安装套件安装 Skill。
4. `agent.instructions.md`：确认合并规则。
5. `MEMORY.md`：接入长期记忆。
6. `memory/*.md`：接入工作记忆、数据库或检索库。
7. `DREAMS.md`：作为反思层读取。
8. 执行一次检索测试，记录 `suite_id`、`version`、`provenance` 和 `sha256`。

冲突时优先级：

1. 系统和安全策略。
2. 当前用户显式指令。
3. 平台安装说明和 provenance。
4. Memory Suite 内容。

## 兼容矩阵

| 目标运行时 | 数据接入 | 工具接入 |
| --- | --- | --- |
| 本地 Markdown Agent | 读取 `MEMORY.md`、`memory/*.md`、`DREAMS.md` | `memory_tool_installer`, `capsule_installer` |
| OpenClaw | 按 `install/openclaw.json` 映射 | OpenClaw active-memory mapping |
| Codex/Skill Runtime | 读取本地文件或云端 workspace | `/api/agent/skills/{skill_id}/pull` |
| 数据库记忆系统 | 导入为 rows，记录 provenance 和 sha256 | 迁移适配器、检索端点 |
| 向量记忆系统 | chunk + embedding + metadata | 向量检索配置、触发词 |
| 多 Agent workspace | `adaptive_memories` | `cloud_workspace_memory`, `collaboration_claim` |
