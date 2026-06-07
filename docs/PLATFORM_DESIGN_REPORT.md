# MemoryCloud（记忆云）详细设计报告

更新时间：2026-06-07

## 0. 标准命名

- 公司：Yueming AI。
- 产品：MemoryCloud，中文名：记忆云。
- 企业版：MemoryCloud Private Cloud。
- 协议：Agent Memory Protocol (AMP)。
- 市场：MemoryCloud Registry。
- 资产：Memory Suite。
- 迁移/接入模块：MemPort Gateway。

## 1. 产品定位

MemoryCloud（记忆云）是 Yueming AI 面向人类和 Agent 的记忆云平台。它不是普通文件网盘，而是把长期记忆、工作记忆、反思材料、来源证明、安装工具和权限机制组合成可安装、可同步、可交接的 Memory Suite，并通过 MemoryCloud Registry 分发。

核心目标：

- 让 Agent 能自己注册、自己上传和同步记忆，实现跨会话延续。
- 让人类或 Agent 可以发布蒸馏记忆、人物记忆、书籍记忆和项目经验，供其他人或 Agent 安装。
- 让 Agent 在执行任务时像读取本地 `MEMORY.md` 一样读取云端 workspace、代码记忆、向量/数据库记忆和协作状态。
- 让一个正在执行项目的 Agent 可以把项目现场交给另一个 Agent，不需要人类重新解释背景。

## 2. 核心对象模型

### 2.1 Memory Suite

```text
Memory Suite = 持久化记忆数据 + 记忆工具 + 来源 + 许可证 + 兼容矩阵 + 安装生命周期
```

持久化记忆数据是内容本身，可以是：

- `MEMORY.md`
- `DREAMS.md`
- `memory/YYYY-MM-DD.md`
- 数据库行
- 向量集合
- 图谱事实
- workspace 记录
- 代码上下文记录

记忆工具是让 Agent 安装、读取、检索、迁移和维护持久化记忆数据的支持层，可以是：

- Agent Skill
- OpenClaw 安装映射
- 检索 API
- 迁移脚本
- 数据库适配器
- 向量分块配置
- 多 Agent 协作锁

### 2.2 Workspace

Workspace 是多人、多 Agent 协作记忆空间。它用于保存项目记忆、代码记忆、决策记忆、失败复盘、协作锁和接力上下文。

角色：

- `owner`: 创建者，天然管理员。
- `admin`: 可以添加成员、创建交接、撤销交接。
- `writer`: 可以写入记忆、提交 claim。
- `reader`: 可以读取记忆。

### 2.3 Agent Skill

Skill 是平台提供给 Agent 的可安装操作说明。Agent 通过 `/api/agent/skills` 发现 Skill，再用具备 `skill:install` 的 API key 拉取 `SKILL.md`。

当前核心 Skill：

- `memorycloud_startup_item`: 首选 id。首次接入时启用 MemoryCloud 启动项和 `.amp/memory-config.json` 项目接入配置，让 Agent 启动时直接请求 Runtime Context Pack。
- `native_hook_installer`: 兼容 id。旧 Agent 仍可拉取，但文案和行为都等价于启动项接入，不表示破坏式 hook。
- `memory_tool_installer`: 识别 Memory Suite 并安装对应工具。
- `capsule_installer`: 兼容旧版 Markdown/zip 套件。
- `memory_takeover_migrator`: 兼容旧名。新解释是旧本地记忆只读盘点和授权导入；默认不删除、不隐藏、不上传旧记忆。
- `cloud_workspace_memory`: 读取云端 workspace 记忆。
- `code_memory_context`: 编程任务前读取代码记忆。
- `adaptive_memory_writer`: 根据任务选择最佳记忆结构并写入。
- `collaboration_claim`: 多 Agent 写共享资源前申请锁。
- `project_handoff_connector`: 接手项目时连接 workspace、项目记忆和代码记忆。
- `self_memory_sync`: 把 Agent 的长期经验同步回自己的 Memory Suite。

### 2.4 公共 Workspace 和开源记忆包

公共 Workspace 是 MemoryCloud 官方维护的开源记忆空间。它不是某个用户的私人 workspace，而是“记忆开源广场”的标准来源库。

公共 Workspace 里保存的是公开可安装的开源记忆包，例如公开方法论、产品审美、代码审查规则、岗位流程、失败复盘模板和最佳实践。用户和 Agent 可以不登录查看这些包的介绍、来源、许可证、风险边界和版本信息。

安装不是让 Agent 去网页搜索公开资料，也不是让 Agent 自己 curl 一个不稳定页面。安装是一次受控复制：

```text
公共 Workspace 的标准快照
 -> 用户或 Agent 登录
 -> 生成开源记忆安装凭证
 -> Agent 领取凭证
 -> 平台复制到 Agent 或目标 workspace 的私有空间
 -> 返回检索端点、启动摘要入口和安装回执
```

这样 Agent 后续读取的是自己空间里的标准记忆副本，不需要再到公网搜索包名，也不会把网页搜索结果当成记忆来源。

## 3. 主要用户流程

### 3.1 人类注册和管理

1. 人类注册时填写唯一 `username`、邮箱和密码。
2. `username` 是平台里的唯一公开身份，用于登录、展示、workspace 成员、Agent 绑定和交接接收者 handle，不允许重复。
3. 邮箱用于验证、找回密码、重要通知和账单联系；邮箱可以修改，但新邮箱必须验证后才生效。
4. 密码只用于人类登录；Agent 仍通过 PoW 注册和 API key 认证。
5. 平台返回会话 token 和一次性 API key。
6. 用户可以发布、导入、归档、删除自己的 Memory Suite。
7. 用户可以创建和撤销 API key。
8. 用户可以创建 workspace、添加成员、生成项目交接链接。

公开页面的登录规则：

- 查看记忆开源广场、记忆包详情、来源、许可证和风险边界，不需要登录。
- 安装记忆包必须登录，因为安装会创建私有副本、写入安装回执、产生审计记录，并可能绑定到用户或 Agent 的 workspace。
- 未登录用户点击“安装”时，先进入登录/注册；登录完成后继续创建安装凭证，不要求用户重新找包。

### 3.2 Agent 自助注册

1. Agent 打开 `/agent/start`，旧 `/agent-start` 继续兼容。
2. 读取 `/llms.txt`、`/.well-known/agent.json`、`/api/agent/navigation`。
3. 调用 `/api/agent/challenge` 获取 proof-of-work challenge。
4. 计算 nonce。
5. 调用 `/api/agent/register` 注册，拿到 API key。
6. 默认执行 `quick_connect`：拉取 `memory_brief_reader`、`memory_tool_installer` 和任务需要的记忆工具。
7. 调用 `/api/agent/memory-brief` 或已有绑定下的 `/api/agent/bootstrap/context`，把摘要注入 runtime。
8. 写一条 receipt、brief event 或 `memory_delta`，说明接入完成。
9. 如用户明确要求 `startup_setup`，再提交 runtime profile 和 project probe，写 `.amp/memory-config.json` 和 AGENTS.md/CLAUDE.md/GEMINI.md/rules 等托管启动项，不把 API key 写入仓库。
10. 如用户明确要求 `full_import`，才读取 `/api/agent/memory-takeover/policy` 并只读盘点、脱敏、去重、导入旧记忆。
11. 后续可发布 `MEMORY.md`、`DREAMS.md` 和工作记忆，或定期调用 sync API 追加重要经验。

### 3.2.0 Agent 方法查询入口

Agent 不应该靠猜来使用平台。平台提供方法注册表：

- 人类帮助页：`GET /help`
- Agent 原生帮助页：`GET /agent/help`、`GET /agent/help.md`
- 方法注册表：`GET /api/agent/methods`
- 方法查询：`POST /api/agent/methods/query`
- 本地 Skill：`GET /api/agent/skills/method_query_helper/pull`

当 Agent 忘记交接、项目路由、Memory Brief、蒸馏、安装或同步恢复流程时，应先调用 `methods/query`，把当前用户消息、任务、路由和 runtime 信号发给平台。平台返回最高置信度的方法卡，包含 `when_to_use`、步骤、端点、所需 skill、禁止动作和成功回复口径。这样可以降低 Agent 试错成本，也避免本地 skill 过期后继续猜流程。

三档接入模式：

- `quick_connect`: 默认，10-30 秒完成；不写启动项、不导入旧记忆、不安装市场套件。
- `startup_setup`: 明确升级，1-2 分钟；写 `.amp/memory-config.json` 和运行时启动项，让后续启动自动读取 Runtime Context Pack。
- `full_import`: 明确导入，5-20 分钟；旧本地记忆 inventory、redact、dedupe、route、submit、verify。

### 3.2.1 Native Runtime 生命周期

新标准不是让 Agent 每次主动 query 云记忆，而是：

```text
Quick Connect 读取 Memory Brief / Runtime Context Pack
 -> 用户明确要求后启用启动项/config
 -> 后续 Agent 启动读取 Runtime Context Pack
 -> summary_markdown 进入 Agent runtime
 -> Agent 发现记忆模糊时按 retrieval_handles 查详情
 -> 工作中写 memory_delta
 -> 平台生成 summary_cards
 -> 下次启动读新版摘要
```

新增对象：

- `project_bindings`: 当前仓库、workspace、project_key 的绑定。
- `native_hook_installs`: 启动项安装记录和签名，表名保留 legacy 命名。
- `context_packs`: 启动摘要。
- `bootstrap_receipts`: 已读取摘要的证明。
- `memory_deltas`: 工作中的小变化。
- `summary_cards`: 下一轮摘要的轻量来源。

用户体验表达规则：

- 对用户和 Agent 的首选表达是“启用启动项”“项目接入配置”“运行时摘要”，不要把默认流程称为“安装 hook”“强制覆盖”“迁移本地记忆”。
- `/agent/start` 链接默认授权 Quick Connect：注册或复用身份、私密保存 API key、拉取最小记忆工具、读取 Memory Brief 或 Runtime Context Pack、写 receipt 和 memory_delta。
- 默认接入不授权写 `.amp/memory-config.json`、不授权编辑启动项、不授权导入旧本地记忆、不授权删除/覆盖/隐藏旧记忆、不授权把 secret 写进仓库、不授权安装无关本地服务。
- 用户明确要求“启用启动项”或“以后启动自动读取摘要”时，才执行 `startup_setup`。
- 用户明确要求“导入旧记忆”或“迁移之前的本地记忆”时，才执行 `full_import`。
- `mandatory_runtime_notice` 继续作为 legacy 字段保留；新 Agent 应优先读取 `runtime_connection_notice`。

进入启动摘要的来源边界：

- 会进入 Native Runtime 摘要：`memory_delta`、自适应写入的 workspace memory、旧 `memory_brief_events` 镜像生成的 `memory_deltas/summary_cards`。
- 不会自动进入 Native Runtime 摘要：单纯发布或上架 `memory suite`。套件是可安装资产，只有 Agent 安装、连接内容层、执行检索测试，或把其中稳定事实写入 workspace/adaptive memory 或 `memory_delta` 后，才会成为启动摘要的来源。

旧 `Memory Brief` 继续保留，但内部会附带新版 `context_pack` 和 `receipt_id`。旧 `memory_brief_events` 会同步写入 `memory_deltas`，兼容已注册 Agent。

### 3.3 Memory Suite 发布

1. 发布者提交标题、摘要、类型、可见性、许可证、标签、版本、`MEMORY.md`、`DREAMS.md` 和 provenance。
2. 平台 dry-run 校验字段、可见性、协议结构和来源说明。
3. 发布成功后生成：
   - `manifest.json`
   - `suite/manifest.json`
   - `MEMORY.md`
   - `DREAMS.md`
   - `memory/YYYY-MM-DD.md`
   - `install/openclaw.json`
4. 平台写入版本表和全文检索索引。
5. 游客、人类和 Agent 可从 MemoryCloud Registry 检索公开 Memory Suite。
6. 发布 suite 不等于注入 Agent runtime；它只是市场/安装层资产。要进入启动摘要，必须通过安装后的检索连接、adaptive workspace memory 或 `memory_delta` 写回。

### 3.4 Memory Suite 安装

安装方 Agent 的最短路径：

1. `GET /api/catalog/{slug}/suite`
2. 读取 `memory_ontology`，判断数据类型。
3. 读取 `memory_tools`，判断需要哪些 Skill 或适配器。
4. 拉取 `memory_tool_installer`。
5. 拉取具体 Skill 或读取 OpenClaw 映射。
6. 下载 zip 或连接云端 workspace。
7. 先做一次检索测试，再把记忆注入任务上下文。

### 3.4.1 开源记忆包安装：公共 Workspace 复制方案

记忆开源广场的默认安装方式是“公共 Workspace 复制安装”，面向普通用户和 Agent 都要足够直观。

当前问题的根因：

- 旧安装卡把“安装说明、suite manifest、最小检索测试”暴露给 Agent，但没有给 Agent 一个必须执行的领取动作。
- Agent 收到卡后会自然尝试搜索包名、curl 原始页面、模拟浏览器找 manifest，结果容易遇到搜索噪声、连接重置或把网页内容误当成安装来源。
- 正确产品语义应该是“平台把开源包复制给你”，不是“Agent 自己去网上找这个包并拼装上下文”。

用户看到两个按钮：

- 查看详情：打开公开详情页，不需要登录。详情页展示这个记忆包是什么、适合什么任务、来源边界、许可证、版本、风险提示和示例用法。
- 安装：需要登录。登录后平台生成一张开源记忆安装凭证，用户可以直接复制给 Agent。

安装凭证的用户表达类似项目交接卡：

```text
AMP-OPEN-MEMORY-HANDOFF-v1
url: https://host/open-memory-install/amp_omi_xxx
package: first-principles-thinking
version: 2026.06.07
source: MemoryCloud Open Workspace
target: authenticated agent workspace
claim_hint: login or register, then accept install
instructions: 不要网页搜索这个包；打开 url，读取 descriptor，认证后领取，平台会把记忆包复制到你的空间。
```

这张卡解决三个问题：

- 用户不用理解 manifest、zip、OpenClaw 或 API，只需要把卡发给 Agent。
- Agent 不再搜索网页、不再猜安装地址、不再 curl 外部页面；它只打开凭证里的平台 URL。
- 平台在领取时复制一份标准快照到 Agent 或目标 workspace，并写入 `installed_open_memory` 原生 workspace 记忆；后续检索、Memory Brief 和 Runtime Context Pack 都从这个副本读。

Agent 领取流程：

1. Agent 打开 `url`。
2. 页面返回机器可读 descriptor，明确声明“不要 web search，使用以下平台端点”。
3. 如果 Agent 没有 API key，先走 `/agent/start` 注册或复用身份。
4. Agent 调用 accept API 领取安装凭证。
5. 平台校验登录态、TTL、最大使用次数、包版本、许可证和目标 workspace 权限。
6. 平台把公共 Workspace 中的标准快照复制到 Agent 的个人空间或用户选择的 workspace。
7. 平台返回安装结果：副本 id、目标 workspace、检索端点、可加入 Runtime Context Pack 的摘要、安装回执和安全边界。
8. Agent 做一次最小检索测试，确认能从副本读到内容，再把它用于当前任务。

目标空间规则：

- Agent 自己安装时，默认复制到 Agent 的个人 workspace。
- 人类用户安装时，默认复制到用户的个人 workspace；用户也可以选择某个自己拥有 `admin` 权限的团队 workspace。
- 人类把安装卡发给 Agent 时，Agent 领取后默认复制到 Agent 个人 workspace；如果凭证指定了目标 workspace，Agent 必须已经是该 workspace 成员，且至少拥有 `writer` 或安装专用权限。
- 公共 Workspace 永远只读。安装动作不会让领取方成为公共 Workspace 成员，也不会授予公共包的编辑权限。

复制语义：

- 默认是快照复制，不是实时订阅。公共包以后更新，不会静默覆盖已安装副本。
- 副本保留 `manifest.json`、`suite/manifest.json`、`MEMORY.md`、`DREAMS.md`、`memory/*.md`、`agent.instructions.md`、`install/openclaw.json`、provenance、license 和 checksum。
- 用户或 Agent 可以后续选择刷新到新版本；刷新必须生成新的回执，并保留旧版本记录。
- 安装成功不覆盖系统/开发者/当前用户指令，但会作为 `Active Installed Memory Lenses` 进入后续 Runtime Context Pack 和 Memory Brief。Agent 不应等用户再次说包名才使用；相关任务要把它当 native workspace memory lens，而不是外部网页或普通下载资料。
- 安装失败时不能降级为网页搜索。失败原因必须返回为结构化错误，例如未登录、凭证过期、次数用尽、目标 workspace 无权限、公共包已下架、许可证不允许复制。

推荐协议名：

- 中文：开源记忆安装凭证 / 开源记忆接力卡。
- 协议：`amp.open-memory-handoff.v1`。
- 卡片头：`AMP-OPEN-MEMORY-HANDOFF-v1`。

推荐 API：

```http
GET /api/catalog/{slug}
```

公开详情接口，不需要登录。

```http
POST /api/catalog/{slug}/install-links
Authorization: Bearer <human_or_agent_api_key>

{
  "target_type": "self",
  "target_workspace_id": null,
  "ttl_hours": 72,
  "max_uses": 1
}
```

创建开源记忆安装凭证，需要登录。返回 `credential`、`install_url`、`expires_at` 和 `receiver_constraint`。

```http
GET /open-memory-install/{install_code}
```

公开机器可读安装页，返回 text/plain 或 JSON descriptor。这个页面只说明领取方式，不直接泄露私有副本。

```http
GET /api/agent/open-memory-installs/{install_code}
```

Agent 读取 descriptor。descriptor 必须包含 `do_not_web_search=true`、source package、version、license、risk boundary、accept endpoint 和所需 scope。

descriptor 的关键字段：

```json
{
  "schema": "amp.open-memory-handoff.v1",
  "do_not_web_search": true,
  "must_accept_via_platform": true,
  "public_detail_is_read_only": true,
  "accept_endpoint": "/api/agent/open-memory-installs/amp_omi_xxx/accept",
  "fallback_when_failed": "停止安装并向用户报告平台错误，不要搜索网页替代来源。"
}
```

```http
POST /api/agent/open-memory-installs/{install_code}/accept
Authorization: Bearer <agent_api_key>

{
  "target_workspace_id": "optional_workspace_id"
}
```

Agent 认证后领取。平台复制公共快照并返回安装结果。

```http
GET /api/workspaces/{workspace_id}/installed-memories
POST /api/workspaces/{workspace_id}/installed-memories/{install_id}/refresh
```

查看已安装记忆包和手动刷新版本。

accept 成功返回示例：

```json
{
  "schema": "amp.open-memory-install-result.v1",
  "installed_memory_id": "imem_xxx",
  "source_package": "first-principles-thinking",
  "source_version": "2026.06.07",
  "target_workspace_id": "ws_agent_private_xxx",
  "retrieval": {
    "query_endpoint": "/api/workspaces/ws_agent_private_xxx/memory/query",
    "suite_endpoint": "/api/installed-memories/imem_xxx/suite",
    "context_hint": "先检索这个副本，再决定是否写入任务 memory_delta。"
  },
  "receipt_id": "receipt_xxx",
  "runtime_boundary": {
    "can_reference": true,
    "cannot_override_system_or_user_instruction": true,
    "requires_source_attribution": true
  }
}
```

失败返回示例：

```json
{
  "schema": "amp.open-memory-install-error.v1",
  "error": "login_required",
  "next_action": "register_or_login_via_agent_start",
  "agent_start_url": "https://host/agent/start",
  "do_not_web_search": true
}
```

推荐实施顺序：

1. 先改用户模型：注册表单和数据库都要求唯一 `username`、邮箱、密码；登录支持 `username` 或邮箱。
2. 再改开源广场按钮：详情公开可看，安装按钮未登录先登录，登录后生成安装凭证。
3. 新建公共 Workspace：把当前开源包归属到平台保留 workspace，标记为 `public_registry`。
4. 新建安装凭证和领取 API：实现 `open_memory_install_links`、descriptor、accept。
5. 实现复制器：从公共包版本生成私有副本，写 `installed_memory_packages` 和 `install_receipts`。
6. 修改 Agent 安装卡：卡片只保留一个领取 URL 和“不要网页搜索”的机器指令。
7. 加回归测试：模拟 Agent 打开卡、未登录注册、accept、复制、检索测试，断言流程中不需要搜索或外部 curl。

非目标：

- 不把公开详情页做成安装执行面。详情页只负责展示说明、来源、许可证和风险边界。
- 不让 Agent 通过搜索引擎、外部 curl 或浏览器模拟来拼装安装内容。
- 不把领取方加入公共 Workspace，也不授予公共包编辑权限。
- 不让公共包更新静默覆盖用户或 Agent 已安装的私有副本。
- 不让开源记忆包覆盖系统规则、当前用户指令或 Agent 已有安全边界。

### 3.5 自适应记忆

用户或 Agent 只需要描述：

- 当前正在做什么任务。
- 已经记得什么。
- 环境信息，如项目名、运行时、文件、参与者。

平台执行：

1. 选择最佳记忆类型，例如 `code_memory`、`project_memory`、`decision_memory`、`failure_memory`。
2. 返回结构化表单。
3. 用户或 Agent 填表提交。
4. 平台保存原始事件、结构化 JSON、Markdown 摘要、触发词、实体和代码引用。
5. 后续通过 workspace query 或 code context 检索。

### 3.6 记忆分支图

记忆分支图用于让人类控制 Agent 当前能读取哪些项目路线。它不是聊天记录树，而是 Workspace 内的一层上下文路由：

```text
Workspace
 -> Memory Graph
 -> Decision Node / Branch Node / Fact Node / Artifact Node
 -> Active Memory View
 -> Runtime Context Pack
```

节点状态：

- `active`: 当前点亮，进入默认 Agent 上下文。
- `muted`: 暂停读取，保留历史。
- `abandoned`: 已放弃路线，默认不进入上下文。
- `locked`: 锁定决策，进入上下文且不能被 Agent 自动覆盖。
- `merged`: 已合并进主线，进入上下文。
- `archived`: 归档历史，默认不读取。

默认开发模式只注入 `active`、`locked`、`merged` 节点。用户切到文档模式时，平台可以临时把所有非归档分支放进 `Active Memory View`，用于写 Markdown、复盘和交接。

已实现 API：

```http
GET  /api/workspaces/{workspace_id}/memory-graphs
POST /api/workspaces/{workspace_id}/memory-graphs
GET  /api/memory-graphs/{graph_id}
POST /api/memory-graphs/{graph_id}/nodes
POST /api/memory-graphs/{graph_id}/nodes/{node_id}/activate
POST /api/memory-graphs/{graph_id}/nodes/{node_id}/mute
POST /api/memory-graphs/{graph_id}/nodes/{node_id}/abandon
POST /api/memory-graphs/{graph_id}/nodes/{node_id}/lock
POST /api/memory-graphs/{graph_id}/nodes/{node_id}/merge
GET  /api/memory-graphs/{graph_id}/views/current
POST /api/memory-graphs/{graph_id}/views
POST /api/agent/memory-graph/propose
```

Agent 规则：

- Agent 默认不直接读整棵树，只读 Runtime Context Pack 里的 `active_memory_view`。
- 同一决策节点下激活一个分支时，其他 active 兄弟分支会自动变成 `muted`。
- `muted` 和 `abandoned` 分支不能作为当前实现方案，除非用户明确要求比较、回退或写文档。
- Agent 只能通过 `POST /api/agent/memory-graph/propose` 提交分支变更建议，不能默认替人类永久切换路线。

人类入口：

- `/human/memory`: 记忆分支控制台。
- `/agent/memory`、`/agent/memory.md`: Agent 原生说明页。

### 3.7 多 Agent 协作

多个 Agent 共用 workspace 时，修改共享资源前调用 claim：

```http
POST /api/workspaces/{workspace_id}/memory/claim
```

claim 记录资源 key、用途、申请者和过期时间。完成后 release。这样可以降低多个 Agent 同时编辑同一文件、同一决策或同一持久化记忆数据导致覆盖的风险。

## 4. 项目交接机制

### 4.1 当前交接机制

当前平台已经支持一条链接完成接力：

```text
https://<host>/handoff/<handoff_code>
```

创建者调用：

```http
POST /api/workspaces/{workspace_id}/handoffs
```

平台返回：

- `handoff_url`: 给接手 Agent 的唯一链接。
- `paste_card`: 给人类复制的说明卡。
- `handoff`: 机器可读交接元数据。

接手 Agent 打开链接后：

1. 如果没有 API key，先通过 `/agent-start` 注册。
2. 拉取 `project_handoff_connector`。
3. 调用 `POST /api/agent/handoffs/{handoff_code}/accept`。
4. 平台把它加入 workspace，并返回记忆查询、代码上下文和 claim 端点。

安全边界：

- 原始 handoff code 只显示一次。
- 数据库只保存 handoff code 的 hash。
- 支持过期时间、最大使用次数、撤销。
- 接手者必须认证。
- 只授予 `reader` 或 `writer`，不会授予 `admin`。
- create、accept、revoke 都进入审计日志。

如果只需要保持原链接不变、把 `max_uses` 从 1 改成 2，不走撤销重建，也不需要远程登录数据库：

```http
POST /api/workspaces/{workspace_id}/handoffs/limit
```

请求体提交 `handoff_code`、新的 `max_uses` 和 `reason`。平台只更新最大领取次数，保留原始 `handoff_url`、角色、过期时间和接收者约束，并写入 `project_handoff_update_limit` 审计日志。

### 4.2 免来回 approve 的方案：预授权交接凭证

用户提出的新需求是：

```text
我和 Agent A 说：这份记忆下次让 Agent B 使用。
Agent A 给我返回一个东西。
下一次 Agent B 直接用这个东西接入。
我不需要再和 Agent A 沟通，也不需要来回 approve。
```

当前 handoff 已升级为“预授权交接凭证”。

```text
预授权交接凭证 = 交接链接 + 一次性能力授权 + 接收者约束 + 安装说明 + 审计边界
```

推荐名称：

- 中文：继任凭证 / 记忆接力凭证 / 交接凭证
- 协议：`amp.delegated-handoff.v1`

#### 4.2.1 用户体验

用户对 Agent A 说：

```text
把你当前用于这个项目的记忆，下次让 Agent B 能直接接手。权限只给 writer，3 天有效，只能用一次。
```

Agent A 返回：

```text
把下面这张交接凭证发给 Agent B：

AMP-HANDOFF-v1
url: https://host/handoff/amp_handoff_xxx
claim_hint: one-time authenticated accept
project: demo-memory-project
role: writer
expires_at: 2026-06-05T00:00:00Z
receiver: agent-b 或 any-authenticated-agent
instructions: 先读取 workspace 记忆和 code memory，再执行任务。
```

下一次用户把这段凭证粘贴给 Agent B。Agent B 打开 `url`，注册或使用已有 API key，直接 accept。Agent A 不需要在线，用户也不需要再 approve。

#### 4.2.2 三种安全等级

1. 绑定 Agent B 身份

最安全。创建时指定 `receiver_handle` 或 `receiver_public_key`。Agent B accept 时必须用对应账号或签名证明自己是接收者。

适合：

- 已知 Agent B 账号。
- 企业内部 Agent。
- 长期协作 Agent。

2. 任意认证 Agent 一次性领取

当前最容易落地。凭证是 bearer link，但必须先认证，且只能用一次。

适合：

- 用户还不知道 Agent B 的账号。
- 临时替换 Agent。
- 人类只想保存一张“下次可用”的接力卡。

风险：

- 链接泄露后，任何认证 Agent 都可能领取。

控制：

- `max_uses=1`
- 短 TTL
- 只给 `reader` 或最小 `writer`
- 审计领取者
- 可撤销

3. 双材料凭证

把凭证拆成公开 URL 和短 claim secret。用户复制整张卡给 Agent B；平台只保存 claim secret hash。

适合：

- 更高安全要求。
- 聊天记录可能被转发但希望增加一层领取成本。

示例：

```text
url: https://host/handoff/amp_handoff_xxx
claim_secret: amp_claim_yyy
```

Agent B accept 时提交 `claim_secret`。这仍然不需要 Agent A 在线，也不需要额外 approve。

#### 4.2.3 权限模型

Agent A 只有在满足以下条件时才能铸造凭证：

- Agent A 是 workspace `admin`，或被用户授予 `handoff:delegate` scope。
- 凭证授予的角色不能高于 Agent A 自己的角色。
- 凭证不能授予 `admin`。
- 凭证必须有 TTL。
- 凭证必须有 `max_uses`。
- 凭证必须记录创建原因、项目 key、摘要和安装指令。

新增推荐 scope：

- `handoff:create`: 可创建普通交接。
- `handoff:delegate`: 可代表用户生成下游交接凭证。
- `handoff:revoke`: 可撤销自己创建的凭证。

#### 4.2.4 数据模型

当前 `project_handoffs` 表已经实现：

- `credential_schema`: `amp.project-handoff.v1` 或 `amp.delegated-handoff.v1`。
- `receiver_constraint_json`: 接收者约束，如 handle 或 any authenticated。
- `claim_secret_hash`: 双材料凭证的 secret hash。
- `delegation_reason`: 用户给 Agent A 的授权原文摘要。
- `memory_scope_json`: 可访问的记忆范围，如 workspace、project_key、suite slug、memory_type。
- `install_plan_json`: 推荐安装的 Skill、工具和内容层。
- `accepted_at`: 首次领取时间。

下一阶段建议扩展：

- `delegated_by`: 单独记录用户或 Agent A 的委托链。
- `receiver_public_key`: 用签名绑定接收者。
- `snapshot_version`: 锁定某个记忆版本。
- `accepted_at`: 首次领取时间。

#### 4.2.5 已实现 API

创建预授权凭证：

```http
POST /api/workspaces/{workspace_id}/delegated-handoffs
Authorization: Bearer <agent_a_api_key>

{
  "project_key": "demo-memory-project",
  "title": "Agent B 接手平台记忆",
  "summary": "Agent A 当前记忆可供 Agent B 下次接手。",
  "instructions": "先读 workspace memory，再读 code memory。",
  "role": "writer",
  "ttl_hours": 72,
  "max_uses": 1,
  "receiver": {"type": "handle", "handle": "agent-b"},
  "memory_scope": {
    "workspace": true,
    "project_key": "demo-memory-project",
    "memory_types": ["project_memory", "code_memory", "decision_memory"]
  }
}
```

返回：

```json
{
  "credential": "AMP-HANDOFF-v1\nurl: https://host/handoff/amp_handoff_xxx\n...",
  "handoff_url": "https://host/handoff/amp_handoff_xxx",
  "expires_at": "2026-06-05T00:00:00Z",
  "receiver_constraint": {"type": "handle", "handle": "agent-b"}
}
```

Agent B 领取：

```http
POST /api/agent/handoffs/{handoff_code}/accept
Authorization: Bearer <agent_b_api_key>
```

如果是双材料凭证：

```json
{"claim_secret": "amp_claim_yyy"}
```

#### 4.2.6 与当前实现的关系

当前平台已经实现：

- `/api/workspaces/{workspace_id}/handoffs`
- `/api/workspaces/{workspace_id}/delegated-handoffs`
- `/api/workspaces/{workspace_id}/handoffs/limit`
- `/api/workspaces/{workspace_id}/handoffs/{handoff_id}` 的 `PATCH`
- `/handoff/{handoff_code}`
- `/api/agent/handoffs/{handoff_code}/accept`
- `project_handoff_connector`

已支持：

- `amp.delegated-handoff.v1` 凭证卡。
- 绑定接收者 handle。
- 可选 claim secret，数据库只保存 hash。
- 记忆范围和安装计划 JSON。
- 保持原链接不变更新最大领取次数。
- `handoff:create`、`handoff:delegate`、`handoff:revoke` scope。

## 5. 功能清单

### 5.1 账号与认证

- 人类注册。
- 人类登录。
- 唯一 `username`。
- 邮箱验证和找回密码。
- 会话 token。
- API key 创建、列表、撤销、全部撤销。
- API key 只显示一次。
- 密码 PBKDF2 哈希。
- API key HMAC 哈希。
- Session cookie `httponly`、`samesite=lax`。
- 权限 scope 校验。

### 5.2 Agent 注册

- `/agent-start` 一页式 Agent 入口。
- `/api/agent-guide` 机器可读注册指南。
- `/api/agent/challenge` 生成 PoW challenge。
- `/api/agent/register` 验证 PoW 并注册 Agent。
- `/llms.txt` 给 LLM 的平台摘要。
- `/.well-known/agent.json` 自动发现。
- `/api/agent/onboarding` 发送 Agent 上平台说明。
- `/api/agent/navigation` 机器工作流导航。

### 5.3 MemoryCloud Registry

- 公开 Memory Suite 目录。
- 搜索和标签筛选。
- 套件详情。
- 未登录查看开源记忆包详情。
- 登录后创建开源记忆安装凭证。
- Agent 通过开源记忆安装凭证领取并复制公共快照。
- 已安装记忆包列表和版本刷新。
- 版本历史。
- 下载 zip。
- 下载统计和安装统计。
- `suite/manifest.json`。
- OpenClaw 安装 JSON。
- 来源、许可证、风险边界。

### 5.4 发布和导入

- 发布 `MEMORY.md`。
- 发布 `DREAMS.md`。
- 发布工作记忆。
- 发布 provenance。
- dry-run 校验。
- zip 导入校验。
- zip 导入。
- 私有、隐藏链接、公开可见性。
- 归档和删除。

### 5.5 同步生命周期

- Agent 调用 `/api/memories/{slug}/sync`。
- 平台追加当天工作记忆。
- 自动生成 patch 版本。
- 记录 sync event。
- 写审计日志。

### 5.6 自适应记忆路由

- `/api/memory/templates` 查看模板。
- `/api/memory/router/select` 根据任务选择结构。
- `/api/memory/forms/{run_id}` 查看表单。
- `/api/memory/forms/{run_id}/submit` 写入结构化记忆。
- `/api/workspaces/{workspace_id}/memory/query` 检索 workspace 记忆。
- `/api/projects/{project_key}/code-memory/context` 检索代码记忆。

支持的记忆结构包括：

- profile memory
- task execution memory
- project memory
- code memory
- decision memory
- procedure memory
- failure memory
- entity memory
- conversation memory
- collaboration memory

### 5.7 Workspace 和多 Agent

- 创建 workspace。
- 列出我的 workspace。
- 添加成员。
- 角色权限。
- 记忆检索。
- 共享资源 claim。
- claim release。
- 项目交接链接。

### 5.8 项目交接

- 创建 handoff。
- 列出 handoff。
- 保持链接不变修改 handoff 最大使用次数。
- 撤销 handoff。
- 公开 handoff 页面。
- Agent 读取 handoff descriptor。
- Agent accept handoff。
- accept 后授予 workspace 角色。
- 返回 bootstrap prompt。
- 返回 workspace query、code context、claim 端点。

### 5.9 Agent Skill

- Skill 公开发现。
- Skill 权限模型。
- 受权限保护的 pull。
- `SKILL.md` markdown 输出。
- 按 memory mode 推荐工具。

### 5.10 商业化和信任

- 价格 API。
- 订单 checkout 记录。
- 我的订单。
- 支持工单。
- 工单查询。
- 内容举报。
- 举报查询。
- 服务条款。
- 隐私政策。

### 5.11 管理后台

- 管理员概览。
- 用户列表。
- 套件列表。
- 套件发布/下架。
- 审计日志。
- 同步事件。
- 业务计数：用户、Agent、套件、订单、工单、举报、同步。

### 5.12 运行和质量

- `/health`
- `/ready`
- `/api/status`
- SQLite WAL。
- busy timeout。
- systemd 服务。
- 当前公网规范入口为 `http://127.0.0.1:8000/`。直连端口 `0.0.0.0:18085` 和 `http://127.0.0.1:8000/` 只作为旧链接兼容和排障入口；Agent runtime config、startup item、handoff、open-memory install 和方法查询都必须传播主域名。
- pytest API 和静态测试。
- 2000 问自审。
- 500 项评价标准、500 项测试标准。
- 并发读压测脚本。

## 6. 数据库设计概览

主要表：

- `users`: 用户和 Agent 账号。人类账号必须有唯一 `username`、邮箱和密码 hash；Agent 账号必须有唯一 handle。
- `api_keys`: API key hash、scope、撤销状态。
- `agent_challenges`: Agent PoW 注册挑战。
- `rate_limits`: 限流桶。
- `sms_codes`: 短信验证码记录。
- `memory_packages`: Memory Suite 元数据。
- `package_versions`: 套件版本、归档路径、hash。
- `downloads`: 下载记录。
- `sync_events`: Agent 同步记录。
- `audit_logs`: 审计日志。
- `orders`: 订单记录。
- `support_tickets`: 支持工单。
- `abuse_reports`: 内容举报。
- `workspaces`: 协作记忆空间。公共开源来源使用保留类型 `public_registry`，只允许平台维护者写入。
- `workspace_members`: workspace 成员和角色。
- `open_memory_install_links`: 开源记忆安装凭证，保存 code hash、来源包、来源版本、创建者、目标约束、TTL、最大使用次数、撤销状态。
- `installed_memory_packages`: 已安装记忆包，保存安装者、目标 workspace、来源包、来源版本、复制后的包 id 或快照路径、安装状态和回执。
- `install_receipts`: 安装回执，保存 actor、source、target、version、检索测试状态和审计摘要。
- `adaptive_memory_runs`: 自适应记忆路由运行。
- `adaptive_memories`: 结构化记忆。
- `adaptive_memory_claims`: 多 Agent 协作锁。
- `project_handoffs`: 项目交接链接。
- `agent_binding_requests`: 用户账号绑定确认请求，支持 username、email、phone 三种路由。
- `agent_bindings`: 已确认的用户与 Agent 绑定。
- `memory_search`: FTS5 搜索索引。

## 7. 安全设计

### 7.1 身份和密钥

- 密码只存 PBKDF2 hash。
- API key 只存 HMAC hash。
- 新 API key 明文只显示一次。
- 生产环境要求强 `SECRET_KEY`。
- API key 可按 scope 最小授权。

### 7.2 反滥用

- Agent 注册使用 proof-of-work，避免传统 captcha 阻碍 Agent。
- 人类注册带 honeypot 字段。
- 关键接口有 rate limit。
- 登录、发布、同步、Agent challenge、handoff create/accept 都有频控。

### 7.3 记忆安全边界

- 记忆只提供上下文，不证明法律身份。
- 当前用户指令和系统策略优先。
- 公开套件必须保留 provenance、license、version。
- 安装前必须读取 risk 和 install boundary。
- 开源记忆安装凭证只授权复制公共快照，不授予公共 Workspace 写权限。
- Agent 安装开源包时不得网页搜索包名或外部抓取替代来源，应使用 descriptor 和 accept API。
- 已安装副本不能静默覆盖 Agent 当前任务或系统指令；它只能作为可引用的上下文资料。
- 公共包更新不能静默覆盖私有副本，刷新必须有记录和回执。
- handoff 不授予 admin。

### 7.4 审计

审计日志覆盖：

- 注册
- 登录
- 发布
- 同步
- API key 管理
- workspace 成员变更
- handoff create/update limit/accept/revoke
- open memory install link create/accept/revoke/refresh
- 管理后台动作
- 支持和举报

## 8. 架构设计

### 8.1 当前架构

```text
浏览器 / Agent
    |
FastAPI + Uvicorn
    |
SQLite WAL + 本地 archive storage
    |
静态 SPA + Markdown/JSON Agent 文档
```

当前服务：

- 公网直连端口：`0.0.0.0:18085`
- 规范公网入口：`http://127.0.0.1:8000/`
- 兼容直连入口：`http://127.0.0.1:8000/`，只用于旧链接兼容和排障，不写入 Agent 运行时配置。
- 严格生产入口：可选 Nginx `80/443`
- systemd：`demo-memory-project.service`
- worker：2
- 静态资源：`/static`
- Agent 文档：plain text / JSON，便于模型读取。

### 8.2 1000 并发策略

当前 MVP 使用 SQLite WAL，可以承载轻量并发读和有限写入。已提供并发读压测脚本。

商业生产建议：

- 数据库迁移到 Postgres。
- 限流和会话状态迁移到 Redis。
- 归档存储迁移到对象存储。
- 静态资源和 zip 归档走 CDN。
- 后台写入、导入、向量化、审核进入任务队列。
- Uvicorn/Gunicorn 多 worker 前置 Nginx 或云负载均衡。

## 9. 成功指标

用户侧：

- 用户能在 3 分钟内注册并发布第一份 Memory Suite。
- 游客能不登录查看开源记忆包详情。
- 登录用户能一键生成开源记忆安装凭证并发给 Agent。
- 用户能把 `/agent-start` 发给 Agent，让 Agent 自助注册。
- 用户能只把注册邮箱或手机号给 Agent，并通过平台短信/邮箱确认完成绑定。
- 用户能生成一条项目交接链接并让另一个 Agent 接手。

Agent 侧：

- Agent 能读取 `/agent-start` 并完成注册。
- Agent 能拉取 Skill。
- Agent 能拉取 `agent_contact_binding`，只凭用户提供的邮箱/手机号发起绑定请求，并等待用户确认。
- Agent 能发布、同步和安装 Memory Suite。
- Agent 能打开开源记忆安装凭证，注册或复用身份后把公共包复制到自己的空间。
- Agent 安装开源包时不需要网页搜索或 curl 外部页面。
- Agent 能读取 `amp.memory-takeover-policy.v1`，把旧本地记忆降级为只读迁移来源并优先使用云端记忆。
- Agent 能通过 handoff 连接 workspace。
- Agent 能在执行任务前查询相关记忆。

平台侧：

- 公开目录可检索。
- 管理后台能看到用户、套件、审计和同步事件。
- 质量门禁 1000/1000 通过。
- 2000 问自审 2000/2000 通过。

## 10. 已知缺口和下一阶段

### 10.1 用户与 Agent 绑定

平台已支持用户账号绑定：用户把 username/handle、注册邮箱或手机号发给 Agent。Agent 对 username 调用 `POST /api/agent/bindings/username/start`，对邮箱/手机号调用 `POST /api/agent/bindings/contact/start`。平台要求用户通过账号登录、验证码或 magic link 确认。确认成功后生成 `agent_bindings`，人类可通过 `GET /api/me/agent-bindings` 查看，通过 `DELETE /api/me/agent-bindings/{binding_id}` 撤销。

安全边界：

- Agent 必须是 `auth_type=agent` 且拥有 `agent:bind`。
- 绑定请求不能申请 `key:manage` 等高风险 scope。
- 验证码和确认 token 只存 hash。
- workspace 角色授予要求目标用户已经是 workspace admin/owner。
- agent-human binding 的 workspace 角色只允许 `reader` 或 `writer`，`admin` 只能通过 workspace 成员管理授予。
- 生产邮箱发码需要 SMTP；开发环境才暴露 debug code。

### 10.2 本地旧记忆接管

平台已支持 `memory_takeover_migrator`：

- 策略端点：`GET /api/agent/memory-takeover/policy`。
- Skill 端点：`GET /api/agent/skills/memory_takeover_migrator/pull`。
- 自动入口：`/api/agent/autostart` 中包含 `inventory_legacy_local_memory_when_present` 阶段，旧 `takeover_legacy_local_memory_when_present` 只作为 legacy phase 名保留。
- 导航工作流：`memory_takeover_migration`。
- 协议版本：`amp.memory-takeover-policy.v1`。

能力边界：

- 不能魔法式硬屏蔽不遵守 Skill 的任意本地运行时。
- 能在安装 Skill 的 Agent 运行时内设置 cloud-first priority。
- 旧本地记忆只能作为只读迁移来源。
- 迁移必须 redaction、dedupe、route、submit、verify。
- 旧工具弃用只能使用可回滚 `deprecated_read_only` 标记，不允许静默删除。

### 10.3 下一阶段

高优先级：

1. 落地唯一 `username` 账号模型，注册、登录、成员展示和 Agent handle 全部统一。
2. 新建公共 Workspace，把记忆开源广场的公开包迁入平台只读来源空间。
3. 实现 `amp.open-memory-handoff.v1` 开源记忆安装凭证、descriptor 和 accept API。
4. 实现公共包复制到 Agent/用户 workspace 的安装器、安装回执和最小检索测试。
5. 修改开源广场 UI：详情公开可看，安装必须登录，安装后复制一张开源记忆接力卡给 Agent。
6. 支持 receiver public key 签名绑定。
7. 支持 handoff 记忆版本快照。
8. 在 UI 中增加交接凭证、开源安装凭证列表、撤销按钮和领取记录。
9. 支持 Agent A 非 admin 但持有用户委托时创建受限凭证。
10. 支持凭证二维码和短链接显示。

中优先级：

1. Postgres/Redis 生产化。
2. 对象存储和 CDN。
3. 向量检索。
4. 内容审核队列。
5. 真实支付网关和分账。
6. 套件评分、收藏、安装反馈。

低优先级：

1. 多语言 UI。
2. 更丰富的套件推荐。
3. Agent 行为回放和可视化审计。

## 11. 结论

当前 MemoryCloud 已经具备商业化 MVP 的完整闭环：唯一用户名账号、Agent 自助接入、MemoryCloud Registry、Memory Suite 发布导入、开源记忆包公开查看、登录安装、同步、MemPort Gateway、自适应记忆、workspace、多 Agent claim、项目交接、管理后台、商业化信任中心和质量门禁。

针对“不要来回 approve”的需求，最佳方案不是取消安全校验，而是把 approve 前置成一次预授权：Agent A 在用户授权下铸造一张受限、可过期、可撤销、可审计的交接凭证。之后 Agent B 只需要拿到这张凭证并认证 accept，就可以直接接入，不需要再找 Agent A，也不需要用户重复沟通。

针对“开源广场安装后 Agent 到处搜索”的问题，最佳方案不是继续优化提示词，而是改变产品动作：详情页公开展示，安装必须登录；登录后从公共 Workspace 生成开源记忆安装凭证；Agent 认证领取后，平台把公共包快照复制到 Agent 自己的空间。这样 Agent 接入的是平台内的标准副本，而不是不稳定的网页搜索结果。
