# Project Handoff

项目交接机制解决一个问题：一个智能体正在使用某个 workspace 和项目记忆工作，另一个智能体需要接手时，人类不应该重新解释项目背景、记忆位置、代码上下文和权限。平台提供一个可粘贴的交接链接。

```text
交接链接 = workspace + project_key + role + instructions + expiry + use_limit
```

用户只需要把一条链接发给接手智能体：

```text
https://<host>/handoff/<handoff_code>
```

接手智能体打开链接后，按页面说明注册或使用已有 API key，然后调用 accept 接口。平台会自动把它加入对应 workspace，并返回项目记忆、代码记忆和协作锁的调用方式。

## 创建交接

创建者必须是 workspace 的 `owner` 或 `admin`，并且具备 `memory:read`。

```http
POST /api/workspaces/{workspace_id}/handoffs
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "title": "支付模块交接",
  "project_key": "billing-service",
  "summary": "当前 Agent 已完成接口梳理，下一步需要修复退款测试。",
  "instructions": "先查询 code memory，再 claim tests/test_refund.py。",
  "role": "writer",
  "ttl_hours": 72,
  "max_uses": 1,
  "skills": ["project_handoff_connector", "cloud_workspace_memory", "code_memory_context"]
}
```

返回值包含：

- `handoff_url`: 人类粘贴给接手智能体的唯一对象。
- `paste_card`: 给人类复制的简短说明。
- `handoff`: 机器可读的交接元数据。

## 接手交接

接手智能体执行：

```http
GET /handoff/{handoff_code}
```

如果没有账号，先打开 `/agent-start` 完成 AgentPass 注册。随后：

```http
POST /api/agent/handoffs/{handoff_code}/accept
Authorization: Bearer <api_key>
```

成功后平台返回：

- workspace id、名称和授权角色。
- project key。
- 推荐拉取的 Skill：`project_handoff_connector`、`cloud_workspace_memory`、`code_memory_context`。
- workspace 记忆查询端点。
- code memory 查询端点。
- shared resource claim 端点。
- bootstrap prompt。

## 修改最大使用次数

如果用户已经有一条交接链接，只是想让同一条链接多给一个 Agent 使用，不要撤销重建，也不要登录服务器改数据库。直接调用限制更新接口，链接保持不变。

按原始 handoff code 更新：

```http
POST /api/workspaces/{workspace_id}/handoffs/limit
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "handoff_code": "amp_handoff_xxx",
  "max_uses": 2,
  "reason": "同一条链接给两个 Agent 接入"
}
```

已知 handoff id 时也可以更新：

```http
PATCH /api/workspaces/{workspace_id}/handoffs/{handoff_id}
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "max_uses": 2,
  "reason": "保持原链接，允许第二个 Agent 接入"
}
```

权限和边界：

- 调用者必须是 workspace 的 `owner` 或 `admin`。
- API key 需要 `handoff:create`、`handoff:delegate` 或 `handoff:revoke` 之一。
- `max_uses` 不能低于当前 `use_count`。
- 更新只改变最大领取次数，不改变 `handoff_url`、权限角色、过期时间或接收者约束。
- 审计日志记录 `project_handoff_update_limit`。

## 接手后的 Agent 规则

1. 先拉取 `project_handoff_connector`。
2. 接受交接。
3. 查询 workspace 记忆。
4. 如果是代码任务，查询 code memory。
5. 修改共享文件前先 claim。
6. 只把相关记忆片段注入上下文。
7. 当前用户指令和系统策略优先于交接记忆。
8. 形成新长期经验时写回 workspace 或同步到自己的 Memory Suite。

## 安全设计

- 交接码只保存哈希，数据库不保存原始码。
- 每个交接可以设置过期时间。
- 每个交接可以设置最大使用次数。
- 创建者可以 revoke。
- 交接只授予 workspace 中的 `reader` 或 `writer`，不会授予 admin。
- 接手者必须先认证；链接本身不能绕过 API key。
- 审计日志记录 create、update limit、accept、revoke。

## 与 Memory Suite 的关系

Memory Suite 解决“安装一份 Memory Suite”。项目交接解决“把一个正在进行的任务现场移交给另一个 Agent”。

两者可以组合：接手 Agent 通过交接链接进入 workspace 后，可以继续安装项目需要的 Memory Suite，也可以把接手过程中形成的新记忆写回 workspace。

## 免来回 approve：预授权交接凭证

用户希望的体验是：

```text
用户对 Agent A 说：这份记忆下次让 Agent B 使用。
Agent A 返回一张凭证。
下一次 Agent B 直接使用这张凭证接入，不需要再和 Agent A 沟通。
```

已实现协议：`amp.delegated-handoff.v1`。

```text
预授权交接凭证 = 交接链接 + 一次性能力授权 + 接收者约束 + 安装说明 + 审计边界
```

### 创建凭证

```http
POST /api/workspaces/{workspace_id}/delegated-handoffs
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "title": "Agent B 接手平台记忆",
  "project_key": "demo-memory-project",
  "summary": "Agent A 当前记忆可供 Agent B 下次接手。",
  "instructions": "先读 workspace memory，再读 code memory。",
  "role": "writer",
  "ttl_hours": 72,
  "max_uses": 1,
  "receiver": {"type": "handle", "handle": "agent-b"},
  "require_claim_secret": true,
  "delegation_reason": "用户授权 Agent A 生成下游交接凭证。"
}
```

### 凭证格式

```text
AMP-HANDOFF-v1
url: https://<host>/handoff/<handoff_code>
schema: amp.delegated-handoff.v1
project: <project_key>
role: reader|writer
expires_at: <iso_time>
max_uses: 1
receiver: agent-b | any-authenticated-agent
claim_secret: amp_claim_xxx
instructions: 先读取 workspace 记忆和 code memory，再执行任务。
```

用户只需要保存这张卡。下一次把整张卡发给 Agent B，Agent B 打开 `url`，注册或使用已有 API key，然后调用 accept 接口；如果凭证包含 `claim_secret`，accept 时一并提交。

```http
POST /api/agent/handoffs/{handoff_code}/accept
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "claim_secret": "amp_claim_xxx"
}
```

Agent A 不需要在线，用户也不需要再次 approve。安全边界依赖 TTL、`max_uses`、接收者约束、claim secret、最小 workspace 角色和审计日志。
