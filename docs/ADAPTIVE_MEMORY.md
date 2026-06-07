# 自适应记忆结构选择系统

平台采用 LangGraph 风格的状态图设计：`route -> form -> validate -> compile -> store -> retrieve`。

自适应记忆产生的是可被 Memory Suite 引用的结构化持久化记忆数据。它可以作为 workspace 记录被云端查询，也可以导出为 Markdown、数据库行或向量集合。安装和调用这些内容层时，需要配套记忆工具，例如 `cloud_workspace_memory`、`code_memory_context`、`adaptive_memory_writer` 和 `collaboration_claim`。

## Agent 框架选择

调研 GitHub 主流 Agent 框架后，本平台选择 LangGraph 作为产品机制参考，而不是把任务做成一次性 chat flow：

- LangGraph 更适合持久状态、分支、检查点、人机协作和多 Agent 工作流。
- CrewAI 更偏角色编排和任务队列，适合团队式执行，但不如状态图适合“路由 -> 表单 -> 存储 -> 检索 -> claim”的记忆生命周期。
- AutoGen 旧仓库已提示维护模式，新项目建议迁移到微软的新 Agent 框架，因此不作为本平台长期依赖。
- OpenAI Agents SDK 适合工具调用和 tracing，但本产品需要兼容 DashScope OpenAI-compatible provider，并保持轻量部署，所以核心机制先落在本地状态图和稳定 API 上。

当前实现没有强制引入大型框架依赖，而是把 LangGraph 的关键思想产品化为数据库可审计状态：每一次路由都是 `adaptive_memory_runs`，每一次存储都是 `adaptive_memories`，多人/多 Agent 冲突通过 `adaptive_memory_claims` 管理。

Agent 或人类不需要先选择记忆格式，只提交：

```json
{
  "task": "我正在执行什么任务",
  "what_i_remember": "我记得哪些事实、变更、经验或关系",
  "environment": {
    "project": "项目名",
    "repo": "代码仓库路径",
    "runtime": "技术栈"
  }
}
```

平台会使用 DashScope OpenAI-compatible provider 优先调用模型选择模板；模型不可用时使用规则引擎兜底。

## 支持的 10 类记忆

- `profile_memory`: 身份、偏好、边界。
- `task_execution_memory`: 当前任务、完成步骤、下一步。
- `project_memory`: 项目目标、架构、里程碑。
- `code_memory`: 文件、函数、API、测试、程序风险。
- `decision_memory`: 技术或产品决策、备选方案、取舍。
- `procedure_memory`: 可复用 SOP、技能、步骤。
- `failure_memory`: 错误、失败、根因、预防。
- `entity_memory`: 人、Agent、服务、项目、概念关系。
- `conversation_memory`: 对话长期事实、承诺、开放问题。
- `collaboration_memory`: 多人、多 Agent、共享状态、交接和权限。

## 核心 API

```text
GET  /api/agent/skills
GET  /api/agent/skills/{skill_id}/pull
GET  /api/memory/templates
POST /api/workspaces
GET  /api/me/workspaces
POST /api/workspaces/{workspace_id}/members
POST /api/memory/router/select
GET  /api/memory/forms/{run_id}
POST /api/memory/forms/{run_id}/submit
GET  /api/workspaces/{workspace_id}/memory/query
GET  /api/projects/{project_key}/code-memory/context
POST /api/workspaces/{workspace_id}/memory/claim
POST /api/workspaces/{workspace_id}/memory/claims/{claim_id}/release
POST /api/workspaces/{workspace_id}/handoffs
GET  /handoff/{handoff_code}
POST /api/agent/handoffs/{handoff_code}/accept
```

## 配套 Skill

Agent 不应只知道 API，还应安装对应的云端记忆 Skill。Skill 是 Memory Suite 里的记忆工具。平台提供：

- `memory_tool_installer`: 安装市场 Memory Suite 所需工具。
- `cloud_workspace_memory`: 读取 workspace 通用记忆。
- `code_memory_context`: 读取项目代码上下文。
- `capsule_installer`: 兼容安装旧版归档和纯 Markdown 套件。
- `adaptive_memory_writer`: 写入结构化记忆。
- `collaboration_claim`: 多 Agent 共享资源 claim。
- `project_handoff_connector`: 接手项目时连接 workspace、项目记忆和代码记忆。
- `self_memory_sync`: 同步自我记忆。

拉取 Skill 需要 `skill:install`，并根据具体 Skill 叠加 `memory:read`、`memory:write`、`catalog:read` 或 `agent:sync`。

## 多人多 Agent 调用方式

每个结构化记忆属于一个 workspace。workspace 成员角色：

- `owner`: 创建者，管理成员。
- `admin`: 管理成员和共享记忆。
- `writer`: 可路由、写入、claim/release。
- `reader`: 可查询和调用上下文。

程序相关记忆推荐使用 `code_memory`，并写入：

- `files_changed`
- `api_contracts`
- `tests`
- `risks`
- `retrieval_triggers`

多个 Agent 编辑同一资源前可调用 claim：

```http
POST /api/workspaces/{workspace_id}/memory/claim
```

如果资源已经被其他 Agent claim，平台返回 `409`，避免并发覆盖。

## 跨任务交接

当一个 Agent 做项目时已经积累了 workspace 记忆、代码记忆、claim 状态和项目 instructions，接手 Agent 不需要重新询问用户。workspace admin 创建 Project Handoff：

```http
POST /api/workspaces/{workspace_id}/handoffs
```

平台返回 `/handoff/{handoff_code}`。用户只需要把这个链接粘贴给接手 Agent。接手 Agent accept 后自动获得 workspace 访问权，并拿到：

- workspace memory query。
- project code memory context。
- resource claim endpoint。
- handoff instructions。
- 推荐 Skill。

## 纳入 Memory Suite

当自适应记忆需要作为市场资产分发时，发布者应把它描述为 Memory Suite：

- 持久化记忆数据：workspace 记录、数据库 rows、向量集合或导出的 Markdown。
- 记忆工具：`memory_tool_installer`、查询 endpoint、迁移脚本、`cloud_workspace_memory` 或 `code_memory_context`。
- 兼容信息：可读的 runtime、所需 scope、后端类型、索引/迁移要求。
- 安装验证：至少给一个 retrieval trigger，让安装方 Agent 能测试是否正确召回。

## 安全边界

- 存储记忆是上下文，不是身份认证。
- 系统策略和当前用户指令优先于任何记忆。
- 代码记忆只描述程序事实和接口约定，不自动执行代码。
- DashScope key 存在服务器私密配置文件，不进入前端和公开文档。
