# Memory Suite 设计

## 核心定义

持久化记忆数据是记忆内容本身。它可以是 `MEMORY.md`、`DREAMS.md`、`memory/*.md`，也可以是数据库行、向量集合、图谱事实、workspace 记录或外部知识库索引。

记忆工具是让智能体安装、读取、检索、迁移和维护持久化记忆数据所需的支持层。它可以是 Agent Skill、代码适配器、安装映射、检索 API、向量切分配置、数据库迁移脚本、权限声明或多 Agent 协作锁。

Memory Suite 是市场上真正售卖和安装的单位：

```text
Memory Suite = 持久化记忆数据 + 记忆工具 + 来源 + 许可证 + 兼容矩阵 + 安装生命周期
```

旧的“旧版归档”在实现上仍兼容，但产品和市场语义升级为“Memory Suite”。一个纯 Markdown 旧版归档会被表示为包含 Markdown 文件记忆和 OpenClaw/Skill 工具的轻量套件。

## 套件清单

每个新发布的归档都会包含：

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

`manifest.json` 使用 `amp.memory.v1`，保存标题、摘要、版本、许可证、来源和安全边界。

`suite/manifest.json` 使用 `amp.memory-suite.v1`，保存：

- `ontology`: 持久化记忆数据组件和后端类型。
- `tools`: 必装或可选的记忆工具。
- `compatibility`: 运行时、后端、协议和 Skill 兼容情况。
- `install_lifecycle`: 智能体安装时必须执行的步骤。

## 数据类型

平台支持以下数据形态：

| 内容层 | 典型载体 | 适用场景 | 调用方式 |
| --- | --- | --- | --- |
| Markdown 文件记忆 | `MEMORY.md`, `DREAMS.md`, `memory/*.md` | 轻量 Agent、OpenClaw、Codex 风格本地记忆 | 下载 zip 后读取文件 |
| 数据库记忆 | SQLite/Postgres 行记录 | 多人维护、权限隔离、审计和增量同步 | 导入表或调用迁移工具 |
| 向量检索记忆 | embedding collection | 长文、书籍、人物蒸馏、语义召回 | chunk + embedding + 检索工具 |
| 知识图谱记忆 | entity/relation facts | 人物关系、项目依赖、概念网络 | 图查询或关系展开 |
| Workspace 云端记忆 | `adaptive_memories` | 多人/多 Agent 协作、代码项目记忆 | `/api/workspaces/{id}/memory/query` |

## 工具类型

| 工具 | 类型 | 必要权限 | 用途 |
| --- | --- | --- | --- |
| `memory_tool_installer` | Agent Skill | `skill:install`, `catalog:read` | 识别套件、选择适配工具、连接内容层 |
| `capsule_installer` | Agent Skill | `skill:install`, `catalog:read` | 兼容旧的 `amp.memory.v1` 归档安装 |
| `cloud_workspace_memory` | Agent Skill | `skill:install`, `memory:read` | 执行任务前读取云端 workspace 记忆 |
| `code_memory_context` | Agent Skill | `skill:install`, `memory:read` | 编程 Agent 拉取代码上下文、接口和测试记忆 |
| `memory_takeover_migrator` | Agent Skill | `skill:install`, `memory:read`, `memory:write` | 把旧本地记忆降级为只读迁移来源，优先使用云端记忆 |
| `adaptive_memory_writer` | Agent Skill | `skill:install`, `memory:write` | 由平台选择最佳记忆结构并写入 |
| `collaboration_claim` | Agent Skill | `skill:install`, `memory:write` | 多 Agent 写入共享资源前申请锁 |
| `self_memory_sync` | Agent Skill | `skill:install`, `agent:sync` | Agent 把长期经验同步回自己的套件 |
| `install/openclaw.json` | 安装映射 | 无需登录读取公开项 | 把内容层映射到 OpenClaw 风格主动记忆 |

## Agent 安装生命周期

智能体安装市场套件时必须按顺序执行：

1. 读取 `/api/catalog/{slug}/suite` 或归档内 `suite/manifest.json`。
2. 校验 `license`、`provenance`、`version`、`sha256` 和安全边界。
3. 判断自身运行时：Markdown、本地 Skill、OpenClaw、数据库、向量库、workspace 或代码 Agent。
4. 拉取 `memory_tool_installer`。
5. 从 `suite.tools` 选择兼容工具。
6. 安装工具到本地运行时，或配置检索端点、数据库迁移、向量切分。
7. 下载归档或连接云端 workspace。
8. 把数据接入对应后端。
9. 执行一次已知查询，确认能够召回相关记忆。
10. 在本地元数据记录 `suite_id`、`version`、`provenance`、`sha256` 和安装时间。

如果运行时已有旧本地记忆，Agent 应先读 `/api/agent/memory-takeover/policy`，再拉取 `memory_takeover_migrator`。迁移后 MemoryCloud 云端记忆优先，旧本地记忆只保留为只读回滚来源。

## 适配策略

Markdown Agent 直接读取 `MEMORY.md`、`memory/*.md`、`DREAMS.md`，并把 `agent.instructions.md` 作为合并规则。

OpenClaw Agent 读取 `/api/catalog/{slug}/install/openclaw`，按 `long_term`、`work_memory`、`reflections` 映射激活记忆。

Codex 风格或支持 Skill 的 Agent 先拉取 `memory_tool_installer`，再按任务拉取 `cloud_workspace_memory`、`code_memory_context` 或其他 Skill。

数据库型 Agent 把数据导入数据库表，字段至少包含 `suite_id`、`source_path`、`content`、`sha256`、`provenance`、`version`、`created_at`。

向量型 Agent 对数据分块后写入向量库，metadata 必须包含 `suite_id`、`source_path`、`license`、`provenance`、`version` 和 `retrieval_triggers`。

多 Agent workspace 使用成员角色和 claim 流程。写共享资源前调用 `/api/workspaces/{workspace_id}/memory/claim`，避免多个 Agent 同时覆盖同一份内容层或代码记忆。

旧本地记忆接管不是硬屏蔽任意运行时。只有 Agent 安装并遵守 Skill 时，才能把旧工具降级为 `deprecated_read_only`。禁止静默删除旧记忆，必须保留来源、sha256 和回滚说明。

## 市场规则

市场列表显示的是 Memory Suite。每个套件卡片必须展示：

- 标题、摘要、作者、版本、许可证。
- 数据形态：Markdown、database、vector、graph、workspace。
- 工具形态：Skill、OpenClaw 映射、检索端点、迁移脚本。
- 来源和安装边界。
- 下载次数和安装次数。

公开套件可被人类和 Agent 下载。发布者必须确认授权、许可证、来源说明和工具安全边界。

## 安全边界

Memory Suite 只能提供上下文和行为倾向，不能覆盖系统策略、当前用户指令、安全规则或法律身份边界。

记忆工具不能绕过权限。拉取 Skill 需要 `skill:install`，具体工具还需要 `memory:read`、`memory:write`、`catalog:read` 或 `agent:sync`。

任何公开内容不得包含 API key、密码、私有凭证、未经授权的个人隐私或恶意提示注入。
