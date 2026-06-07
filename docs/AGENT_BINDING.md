# 用户与智能体绑定机制

## 目标

本机制称为“用户账号绑定”。

用户只需要把自己的 MemoryCloud 用户名、注册邮箱或手机号发给 Agent。Agent 可以自行发起绑定请求；用户名走平台账号确认，邮箱或手机号走验证码/确认链接。只有用户完成平台确认后，绑定才生效。

这不是“知道账号名就能绑定”。账号名和联系方式都只是路由线索，真正的授权证明来自目标账号登录确认、邮箱或短信通道。

## 核心对象

- `agent_binding_requests`：待确认请求，保存 Agent、用户、账号/联系方式类型、请求权限、workspace 角色、验证码 hash、确认 token hash、过期时间和投递元数据。
- `agent_bindings`：已确认绑定，保存用户、Agent、授权 scopes、workspace 角色、状态和撤销时间。
- `agent_contact_binding`：Agent Skill，教 Agent 如何发起绑定、等待用户确认、查询绑定状态。

## Agent 流程

1. Agent 注册并持有 `agent:bind` scope 的 API key。
2. Agent 拉取 Skill：

```http
GET /api/agent/skills/agent_contact_binding/pull
Authorization: Bearer <api_key>
```

3. 用户给 Agent 一个用户名、注册邮箱或手机号。
4. 如果用户给的是用户名或 handle，Agent 发起用户名绑定：

```http
POST /api/agent/bindings/username/start
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "username": "alice",
  "requested_scopes": ["memory:read", "memory:write", "skill:install", "handoff:delegate"],
  "workspace_roles": {
    "workspace_id": "writer"
  },
  "note": "User asked this agent to bind."
}
```

5. 如果用户给的是邮箱或手机号，Agent 发起联系方式绑定：

```http
POST /api/agent/bindings/contact/start
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "contact": "user@example.com",
  "requested_scopes": ["memory:read", "memory:write", "skill:install", "handoff:delegate"],
  "workspace_roles": {
    "workspace_id": "writer"
  },
  "note": "User asked this agent to bind."
}
```

6. `workspace_roles` 只能是 `reader` 或 `writer`。`admin` 是 workspace 成员管理，不是 agent-human binding 权限。
7. 平台让用户通过账号登录、邮箱或手机号确认。
8. 用户确认后，Agent 查询状态：

```http
GET /api/agent/bindings/me
Authorization: Bearer <api_key>
```

## 用户确认

用户名和邮箱确认链接会打开：

```http
GET /agent-binding/{approval_token}
```

用户点击确认按钮后，平台会执行一次性批准。

短信确认、邮箱确认或开发环境 API 自动化确认使用：

```http
POST /api/agent/bindings/contact/confirm
Content-Type: application/json

{
  "request_id": "abr_xxx",
  "code": "123456"
}
```

或：

```json
{"approval_token": "amp_bind_xxx"}
```

## 用户管理

用户可以查看和撤销已绑定 Agent：

```http
GET /api/me/agent-bindings
Authorization: Bearer <session_or_api_key>

DELETE /api/me/agent-bindings/{binding_id}
Authorization: Bearer <session_or_api_key>
```

撤销后，绑定状态变为 `revoked`。如果绑定曾授予 workspace 角色，平台会移除本次绑定记录对应的角色成员关系。

## 安全边界

- 只有 `auth_type=agent` 且拥有 `agent:bind` scope 的账号可以发起绑定。
- 绑定只能请求 `BINDING_ALLOWED_SCOPES` 中的安全范围，不能请求 `key:manage`。
- 验证码和 magic link token 只存 hash。
- 请求默认 15 分钟过期。
- 生产环境用户名绑定必须由目标人类账号登录确认；开发环境才会返回调试 token 方便自动化测试。
- workspace 角色只有目标用户已经是该 workspace admin/owner 时才能授予。
- agent-human binding 只能授予 `reader` 或 `writer`，不能授予 `admin`。
- 所有开始、确认、撤销动作写入审计日志。
- 生产环境邮箱绑定必须配置 SMTP；开发环境才会返回 `debug_code`。

## SMTP 配置

```bash
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=notify@example.com
SMTP_PASSWORD=<smtp-password>
SMTP_FROM=notify@example.com
SMTP_TLS=true
```

手机号绑定复用现有短信配置：

```bash
SMS_DRY_RUN=false
FX_AI_API_KEY=<sms-provider-key>
SMS_API_BASE=https://api.fenxianglife.com/fenxiang-ai-brain/skill/api/sms/code
```
