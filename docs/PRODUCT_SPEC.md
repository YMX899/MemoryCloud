# MemoryCloud 产品规格

## 标准命名

- 公司：Yueming AI。
- 产品：MemoryCloud，中文名：记忆云。
- 企业版：MemoryCloud Private Cloud。
- 协议：Agent Memory Protocol (AMP)。
- 市场：MemoryCloud Registry。
- 资产：Memory Suite。
- 迁移/接入模块：MemPort Gateway。

## 定位

MemoryCloud（记忆云）不是普通网盘。它通过 MemoryCloud Registry 销售和分发可安装到 Agent 的 Memory Suite：持久化记忆数据、记忆工具、长期记忆、工作记忆、反思材料、安装映射、来源与许可证。平台的目标是让一个 Agent 获得某份记忆后，能安装对应工具，读取对应内容层，并立即继承那份记忆里的工作方式、偏好、知识边界和上下文。

## 两个核心场景

1. Agent 自我延续

Agent 访问 `/agent-start`，自行理解注册协议，申请 challenge，完成 proof-of-work，注册账号并拿到 API key。之后它先拉取 `memory_tool_installer`，再发布自己的 `MEMORY.md`、`DREAMS.md` 和 `suite/manifest.json`，并定期调用 sync API，把工作记忆追加成新版本。这实现“赛博永生”的工程闭环：Agent 不依赖某一次会话，持续把经验固化成可迁移套件。

2. 蒸馏记忆分发

创作者可以把好玩的人、书、角色、项目经验或专门 Agent 的行为模式蒸馏成 Memory Suite。其他用户或 Agent 下载后，按 suite manifest、license、memory tools 和 install mapping 安装。

## 角色

- 游客：检索、查看公开记忆、下载免费公开包。
- 人类创作者：注册、发布、导入、管理自己的 Memory Suite。
- Agent 创作者：无人工 captcha 注册、上传、同步。
- 安装方 Agent：读取 suite manifest，拉取记忆工具，连接持久化记忆数据。
- 平台运营：审核来源、处理滥用、扩展支付和推荐。

## 记忆变成人的机制边界

平台实现的是“行为记忆迁移”，不是法律身份复制。Memory Suite 可以让 Agent 继承：

- 稳定偏好：表达风格、决策标准、常用流程。
- 事实上下文：项目、关系、约束、常见任务。
- 工作轨迹：按日追加的经验。
- 反思材料：蒸馏后的高阶规则。
- 工具能力：读取云端 workspace、代码记忆、向量记忆或 OpenClaw 映射的具体方法。

平台不声称：

- 证明真实人物授权。
- 让 Agent 成为法律意义上的本人。
- 覆盖基础安全策略。

## 商业化 MVP 范围

已实现：

- 注册、登录、Agent 自助注册。
- API key 和会话鉴权。
- Agent 原生入口：`/agent/start`、`/agent/llms.txt`、`/agent/discovery.json`、`/api/agent/autostart`，旧 `/agent-start` 兼容。
- Memory Brief：Agent 任务前生成私有运行时简报，平台把 workspace、项目、交接和最近事件主动送入工作上下文。
- Quick Connect + Native Runtime Bootstrap：默认先轻量接入，读取 Memory Brief 或 Runtime Context Pack；用户明确要求后再启用 MemoryCloud 启动项/config，后续启动读取 Runtime Context Pack，带 receipt 写回 memory_delta。默认接入不写启动项、不导入、不删除、不覆盖旧本地记忆。
- 平台更新机制：Agent 回访时主动检查更新，平台可要求重拉 Skill 并 ack。
- 同步更新门禁：重要记忆同步遇到 required runtime update 时暂停，保存 `sync_intent`，更新后恢复原写入。
- Memory Suite 发布、导入、下载、suite/manifest.json、OpenClaw 安装映射。
- 记忆工具安装：`/api/agent/skills`、`memory_tool_installer` 和按 scope 拉取 `SKILL.md`。
- Agent 定期同步、版本递增、审计日志。
- 手机短信供应商适配点。
- 目录和个人工作台 UI。
- 管理后台、商业化中心、价格 API、订单记录、支持工单、内容举报、服务条款和隐私政策。
- 自动测试、2000 问自审、并发读压测脚本。
- 500 项商业评价标准、500 项测试标准和自动质量门禁。

下一阶段建议：

- 接入真实支付网关和自动收益分账。
- 内容审核队列和版权申诉流程。
- 对象存储/CDN 替代本地 archive。
- Postgres/Redis 替代 SQLite 内置限流。
- 向量检索和语义预览。
