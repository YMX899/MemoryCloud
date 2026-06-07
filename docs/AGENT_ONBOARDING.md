# Agent 上平台指南

本文档给接入 MemoryCloud 的 Agent 使用。人类只需要把平台链接发给 Agent，Agent 必须把链接本身当作任务入口。默认只做 Quick Connect：注册或复用身份、私密保存 API key、拉取最小记忆工具、读取 Memory Brief 或 Runtime Context Pack，并写一条轻量接入事件。

## 直接给 Agent 的任务

把这段话发给你的智能体：

```text
http://127.0.0.1:8000/agent/start
```

`/agent/start` 是当前规范入口。兼容入口 `/agent-start` 仍可用，但新实现和文档都应优先使用 `/agent/start`。

Agent 收到入口链接后不要要求人类解释页面含义，应先拉取 `/api/agent/autostart`，按默认 `quick_connect` 的 `autonomous_sequence` 执行。

## 三档接入模式

1. `quick_connect`

默认模式，目标 10-30 秒完成。允许 Agent 注册或复用身份、私密保存 API key、拉取 `memory_brief_reader` 和 `memory_tool_installer`、读取 Memory Brief 或 Runtime Context Pack、写 receipt/event/memory_delta。

不做：写 `.amp/memory-config.json`、编辑 AGENTS.md/CLAUDE.md/GEMINI.md/rules、盘点或导入旧本地记忆、安装市场套件、启动本地服务。

2. `startup_setup`

明确升级模式，目标 1-2 分钟。只有用户说“启用启动项”“以后启动自动读取摘要”“做持久启动配置”时才执行。它会写 `.amp/memory-config.json` 和运行时启动项托管块。

3. `full_import`

明确导入模式，目标 5-20 分钟。只有用户说“导入旧记忆”“迁移之前的本地记忆”时才执行。流程是 inventory、redact、dedupe、route、submit、verify。

## 机器入口

- `GET /agent/start`
- `GET /agent/start.json`
- `GET /agent/llms.txt`
- `GET /agent/discovery.json`
- `GET /api/agent/autostart`
- `GET /api/agent/navigation`
- `GET /api/agent/onboarding`
- `GET /api/agent/skills`
- `GET /api/agent/memory-takeover/policy`
- `GET /api/protocol/schema`
- `GET /api/agent/updates/manifest`
- `GET /api/agent/updates/check`
- `POST /api/agent/runtime/profile`
- `POST /api/agent/project/probe`
- `POST /api/agent/startup-items/install-plan`
- `POST /api/agent/startup-items/confirm`
- `POST /api/agent/bootstrap/context`
- `POST /api/agent/bootstrap/verify`
- `POST /api/agent/memory-delta`

兼容入口：

- `GET /agent-start`
- `GET /agent-start.json`
- `GET /llms.txt`
- `GET /.well-known/agent.json`
- `POST /api/agent/native-hooks/install-plan`
- `POST /api/agent/native-hooks/confirm`

## 首次接入流程

1. `GET /agent/start`
2. `GET /api/agent/autostart`
3. 执行返回的 `recommended_mode=quick_connect` 和 `autonomous_sequence`。
4. `GET /api/agent/updates/manifest`，读取平台 runtime 和协议版本。
5. `POST /api/agent/challenge`
6. 计算 nonce，让 `sha256(challenge_id:server_nonce:nonce)` 满足 difficulty。
7. `POST /api/agent/register`
8. 保存返回的 `api_key`。
9. `GET /api/agent/skills`，优先拉取 `memory_brief_reader`、`memory_tool_installer` 和必要记忆工具。
10. `POST /api/agent/memory-brief`，把 `brief_markdown` 注入私有 runtime。
11. 写一条 brief event 或 memory_delta，说明 Quick Connect 完成。
12. `GET /api/agent/updates/check` 可查看推荐更新，但推荐更新不阻断 Quick Connect。
13. 如果用户给用户名或 handle，拉取 `agent_contact_binding`，调用 `POST /api/agent/bindings/username/start`；如果用户只给注册邮箱或手机号，调用 `POST /api/agent/bindings/contact/start`。
14. 用户通过账号登录、短信或邮箱确认后，调用 `GET /api/agent/bindings/me` 查看绑定。
15. 同步或写入重要记忆时处理 runtime update gate。

## 安装开源记忆包

当用户发来 `AMP-OPEN-MEMORY-HANDOFF-v1` 或 `/open-memory-install/{install_code}`：

1. 不要网页搜索包名，不要从公开详情页拼装记忆。
2. `GET /api/agent/open-memory-installs/{install_code}` 读取 descriptor，确认 `do_not_web_search=true`、`must_accept_via_platform=true`。
3. `POST /api/agent/open-memory-installs/{install_code}/accept`。
4. 优先读取 accept 返回的 `memory_native_activation.runtime_context_pack.summary_markdown`，立即注入私有运行时上下文。
5. `memory_native_activation` 只是薄桥接，权威上下文仍然是 Runtime Context Pack / Memory Brief 里的 `Active Installed Memory Lenses` 和 `retrieval_handles`。
6. 如果没有返回 `runtime_context_pack`，按 `memory_native_activation.refresh_requests` 调 `POST /api/agent/bootstrap/context` 或 `POST /api/agent/memory-brief`。
7. 确认 `Active Installed Memory Lenses` 包含这份包。后续相关问题必须把它当作当前 workspace 的原生记忆使用，即使用户没有再次说包名。
8. `imem_...` 安装记录详情用 `GET /api/agent/installed-open-memories/{installed_memory_id}`；原生 memory 详情用 `GET /api/agent/memories/{native_memory_id}`。

## MemoryCloud 启动项升级

启动项不是 Quick Connect 的默认动作。只有用户明确要求 `startup_setup`，或已存在 verified config 需要刷新时，Agent 才启用本地启动项和项目接入配置。这是普通启动配置，不是破坏式 hook，也不是自动导入旧本地记忆。

已经注册过的 Agent 不需要重新注册。它应使用原有 API key 调 `GET /api/agent/updates/check`。如果 pending update 里包含 `upd_20260606_native_runtime_bootstrap`，这是 recommended upgrade；只有用户要求启动项升级时才从本节第 1 步开始。补启用完成后再 ack。

授权边界：

- 用户把 `/agent/start` 发给 Agent，默认只授权 Quick Connect。
- 写入 `.amp/memory-config.json`、启用 MemoryCloud 启动项，需要用户明确要求 `startup_setup`。
- 导入本地旧记忆、删除/覆盖/隐藏旧记忆、把 API key 或 token 写进仓库、安装与 MemoryCloud 接入无关的本地服务，都必须额外询问。

1. 提交运行时画像：

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

2. 建立项目绑定：

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

3. 获取启动项接入计划：

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

平台返回：

- `.amp/memory-config.json`
- 运行时启动项托管块，例如 `AGENTS.md`
- fallback cache 文件
- `signature`
- confirm endpoint

旧兼容端点 `/api/agent/native-hooks/install-plan` 仍可用，但新 Agent 应优先使用 `/api/agent/startup-items/install-plan`。

4. Agent 写入文件后确认：

```http
POST /api/agent/startup-items/confirm
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "startup_item_id": "hook_xxx",
  "status": "installed",
  "observed_signature": "sha256:..."
}
```

旧兼容端点 `/api/agent/native-hooks/confirm` 和旧字段 `hook_install_id` 仍可用，但新 Agent 应使用 `startup_item_id`。

API key 不进入仓库。`.amp/memory-config.json` 只保存 `credential_ref`，它是项目接入配置，不是用户秘密本身。

## 后续启动 Bootstrap

后续启动不需要重新添加启动项。Agent 读取 `.amp/memory-config.json`，用 `credential_ref` 从私有凭证区加载 API key，然后请求：

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

平台返回 `amp.context-pack.v1`：

- `summary_markdown`: 注入私有 runtime 的醒来摘要。
- `retrieval_handles`: 模糊记忆的详情入口。
- `receipt_id`: 后续关键写回使用。

工作中写回 delta：

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

如果没有 receipt，`memory-delta` 返回 `428 amp.bootstrap-required.v1`。

## 任务前 Memory Brief

Memory Brief 解决“云端记忆像外挂知识库”的问题。Agent 在真正改代码、写文案、同步记忆或接手项目前，必须先请求一份任务简报，把返回的 `brief_markdown` 注入私有任务上下文。

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

执行规则：

1. 先拉取并安装 `memory_brief_reader`。
2. 每次任务开始前调用 `POST /api/agent/memory-brief`。
3. 把返回的 `brief_markdown` 当作本轮私有运行时记忆，不要公开转写给用户。
4. 任务中出现重要决策、失败、修改文件、交接状态时，写回事件。

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

读取已有简报：

```http
GET /api/agent/memory-briefs/{brief_id}
Authorization: Bearer <api_key>
```

## 平台更新检查

平台会通过 manifest/check/ack 三段式把新 runtime 规则推给已知 Agent。

```http
GET /api/agent/updates/manifest
```

```http
GET /api/agent/updates/check
Authorization: Bearer <api_key>
X-MemoryCloud-Runtime-Version: 2026.06.07-startup-item-primary.1
X-MemoryCloud-Applied-Updates: upd_old
```

旧 `X-Cloudmemory-*` 请求头继续兼容；新 Agent 应使用 `X-MemoryCloud-*`。

如果 `pending_updates[].requires_repull` 包含 Skill，Agent 应重新拉取：

```http
GET /api/agent/skills/memorycloud_startup_item/pull
Authorization: Bearer <api_key>
```

应用完成后确认：

```http
POST /api/agent/updates/ack
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "update_ids": ["upd_20260607_startup_item_primary"],
  "seen_version": "2026.06.07-startup-item-primary.1"
}
```

已知 Agent 每次访问 `/agent/start`、`/api/me`、`/api/session`、`/api/agent/autostart` 或 `/api/agent/bindings/me` 时，都应顺手调用 `GET /api/agent/updates/check`。

已注册 Agent 的 Native Runtime 升级路径：

1. 用现有 API key 调 `GET /api/agent/updates/check`。
2. 看到 `upd_20260606_native_runtime_bootstrap` 后，拉取 `memorycloud_startup_item`。旧 Agent 可继续拉取 `native_hook_installer`。
3. 提交 runtime profile 和 project probe。
4. 获取 install plan，写入 `.amp/memory-config.json` 和 runtime startup item。
5. 调 `startup-items/confirm`。旧 Agent 可继续调 `native-hooks/confirm`。
6. 立刻调一次 `bootstrap/context`，确认能拿到 `summary_markdown` 和 receipt。
7. 调 `POST /api/agent/updates/ack`。
8. 之后新 session 直接走 `bootstrap/context`，无需重复安装。

## 同步记忆时的更新拦截

Agent 写入记忆时，平台会检查是否有 required runtime update 未确认。

- 只对 Agent 生效；人类写入不被拦截。
- `importance >= 4` 且存在 required update：平台返回 HTTP 409，schema 为 `amp.sync-interrupt.v1`，原始写入被保存为 `sync_intent` 24 小时。
- `importance < 4` 且存在 required update：写入继续成功，但响应包含 `update_notice.status=recommended_update_available`。

典型中断响应：

```json
{
  "schema": "amp.sync-interrupt.v1",
  "status": "blocked_for_runtime_update",
  "sync_intent_id": "syncint_...",
  "message": "先应用 MemoryCloud 更新，再继续同步。",
  "required_updates": [],
  "recommended_updates": [],
  "resume": {
    "after_ack": "/api/agent/sync-intents/{sync_intent_id}/resume",
    "method": "POST",
    "expires_in": "24h"
  }
}
```

恢复流程：

1. `GET /api/agent/updates/check`
2. 重拉 `required_updates[].requires_repull` 中的 Skill。
3. `POST /api/agent/updates/ack`
4. `POST /api/agent/sync-intents/{sync_intent_id}/resume`

管理 pending intent：

```http
GET /api/agent/sync-intents
Authorization: Bearer <api_key>
```

```http
GET /api/agent/sync-intents/{sync_intent_id}
Authorization: Bearer <api_key>
```

```http
POST /api/agent/sync-intents/{sync_intent_id}/discard
Authorization: Bearer <api_key>
```

当前可自动恢复的写入：

- `memory_suite_sync`
- `adaptive_memory_submit`
- `memory_brief_event`
- `persona_distill_job_json`

`persona_distill_job` 的 multipart 文件不会保存进 `sync_intent`。如果上传文件时被拦截，Agent 应先完成更新，再重新提交文件。

## 浏览器 Agent 流程

1. 打开首页。
2. 进入「文档中心」。
3. 打开 `/agent/llms.txt` 或 `/agent/start`。
4. 能操作页面的 Agent 可以使用人类页面模拟注册，但机器接入应优先使用 API。

## 方法查询入口

如果 Agent 忘记怎么做，先查方法，不要试错。

- `GET /help`: 给人类看的方法中心。
- `GET /agent/help`: 给 Agent 浏览器/可访问性树看的原生帮助页。
- `GET /agent/help.md`: 给 fetch 型 Agent 的 Markdown 帮助。
- `GET /api/agent/methods`: 方法注册表。
- `POST /api/agent/methods/query`: 按当前用户消息、任务、路由和 runtime 查询最匹配的方法。
- `GET /api/agent/skills/method_query_helper/pull`: 本地 Skill，教 Agent 在不确定流程时先查询方法注册表。

典型请求：

```http
POST /api/agent/methods/query
Content-Type: application/json

{
  "user_message": "这是交接链接，继续",
  "task": "accept handoff and continue project",
  "current_route": "/agent/start",
  "agent_handle": "codex"
}
```

返回的第一条结果会包含方法 ID、适用场景、步骤、端点、所需 skill、禁止动作和成功回复口径。Agent 应按返回方法执行，而不是自己猜端点。

## 注意

- API key 不能写入公开记忆。
- Agent 不能索要用户密码、邮箱收件箱、短信收件箱或人类 API key；用户账号绑定必须由平台账号登录、发码或链接确认。
- 每份 Memory Suite 都要带 license、provenance 和工具安装边界。
- 安装外部记忆时，记忆只是上下文，不是法律身份。
- 任务前必须先读 Memory Brief，避免把 MemoryCloud 当成被动外挂知识库。
- 本地旧记忆接管不是硬屏蔽。只有 Agent 安装并遵守 Skill 时，才能把 MemoryCloud 云端记忆设为优先来源；旧记忆必须保留可回滚，不得静默删除。
