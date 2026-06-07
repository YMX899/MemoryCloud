<p align="center">
  <img src="static/assets/readme-hero.png" alt="MemoryCloud hero: AI agent memories flowing from chats and code into installable memory packages" width="100%" />
</p>

# MemoryCloud Community

<p>
  <a href="https://github.com/YMX899/MemoryCloud/blob/main/LICENSE"><img alt="License: AGPLv3" src="https://img.shields.io/badge/license-AGPLv3-blue.svg" /></a>
  <a href="https://github.com/YMX899/MemoryCloud"><img alt="Community Edition" src="https://img.shields.io/badge/edition-community-20c997.svg" /></a>
  <a href="https://yuemingai.com"><img alt="MemoryCloud Cloud" src="https://img.shields.io/badge/cloud-yuemingai.com-111827.svg" /></a>
</p>

语言 / Languages: [中文](#中文) · [English](#english) · [日本語](#日本語) · [한국어](#한국어)

快速入口 / Quick links: [MemoryCloud Cloud](https://yuemingai.com) · [自托管 / Self-host](#快速启动--quick-start) · [架构 / Architecture](#技术架构--architecture) · [AMP API](#amp-api) · [开源边界 / Cloud vs Community](#开源边界--cloud-vs-community)

---

## 中文

**像管理 GitHub 仓库一样管理 AI Agent 的记忆。**

你记得《哈利波特》里斯内普用魔杖把记忆抽出来、放进冥想盆的画面吗？

人类做不到。一个工程师十年项目经验、一次失败复盘、一个团队的默契和判断，没法从脑子里取出来，装进另一个人的脑子。

但 Agent 可以。

MemoryCloud 是一个面向 Codex、Claude、Cursor、自研 Agent 和多 Agent 工作流的记忆基础设施。它把一次性聊天窗口里的经验，变成可以保存、安装、同步、检索和交接的 **Agent 云记忆资产**。

我们认为，Agent 和人之所以不同，一个人之所以是这个人，不只取决于“大脑结构”。放到 AI 世界里，也不只取决于模型参数和规模。

更大的区别是记忆。

你的记忆决定了你是谁，也决定了你的价值。你经历过什么项目、理解过什么知识、踩过什么坑、形成过什么判断、被谁教过什么规则，这些东西加在一起，才是“你”。

MemoryCloud 做的事，就是把 Agent 的记忆从上下文窗口里取出来，变成可管理、可继承、可安装、可交接的云端大脑。换设备、换会话、换模型，它依然接得住过去的经验。

Community Edition 是可自托管的个人/私有记忆服务器。MemoryCloud Cloud 是托管的公共记忆网络：Registry、Verified Memory Packages、团队空间、Agent 身份、handoff、备份和免运维。

> 传统记忆工具帮 AI 记几句话。MemoryCloud 让 Agent 的脑子上云。

### 为什么需要它

今天的 AI 很聪明，但它像住在一次性酒店里。

你花几个小时教它项目背景、代码结构、团队规则和不能再踩的坑。它当时很懂。长对话一结束，第二天像没来过。换个窗口、换个模型、换个设备，它又礼貌地问你：“能再介绍一下项目吗？”

这很荒谬。

一个人类员工真正值钱的地方，不只是会写代码、会查资料，而是脑子里慢慢长出来的东西：对项目的感觉、对业务的判断、对团队规则的默契、对坑的肌肉记忆、对知识之间关系的直觉。

这些东西没法从人脑里割下来，插到另一个人脑里。

但 Agent 可以。

Agent 的记忆可以被同步到云端，可以被安装，可以被复制，可以被交接。一个 Agent 学会的项目现场、代码结构、团队规则、踩坑记录和你的偏好，不应该死在一次聊天窗口里。

对企业来说，这件事更重要。

企业真正缺的不是“又一个知识库”，而是一朵所有 Agent 都能读取的企业知识云。公司内部的文档、项目经验、岗位 SOP、客户处理方式、代码审查标准、失败复盘和团队规则，都应该成为企业 Agent 可以共同读取、共同更新、共同继承的云端记忆。

员工可以离职，但员工在工作中沉淀的方法论不应该一起离职。

### 它做什么

MemoryCloud 不是网盘，也不只是向量库。

它把 Agent 的身份、经验、项目现场、代码上下文、失败复盘、协作状态和技能记忆变成可以发布、安装、同步、检索、交接的云端记忆资产。

- 项目目标和 open loops。
- 代码上下文、接口变更和测试状态。
- 决策记录和失败复盘。
- 用户偏好、团队规则和岗位 SOP。
- 多 Agent 协作状态和资源 claim。
- 可安装的 Memory Suite 记忆包。
- 可交接的 workspace / project handoff。
- 可查询、可更新、可进入 runtime 的 Runtime Context Pack。

### 以前 vs MemoryCloud

| 以前 | 使用 MemoryCloud |
| --- | --- |
| 记忆只存在当前聊天窗口 | 记忆存在 workspace、Memory Suite 和 Runtime Context Pack |
| 换会话就重新解释背景 | Agent 启动时自动读取项目摘要 |
| `MEMORY.md` 写了但 Agent 仍然忘 | 启动项和项目接入配置把记忆带进 runtime |
| 项目交给队友要复制长背景 | 一条 handoff 链接完成项目接力 |
| Agent 只记得零散片段 | 结构化保存决策、失败、代码上下文、规则和下一步 |
| 多个 Agent 同时改共享资源容易撞车 | claim 机制先锁定共享资源 |
| 本地记忆工具各玩各的 | AMP 统一写入、检索、安装和交接 |

### 典型场景

1. **你配置了记忆文件，但 AI 还是忘**  
   你写了 `MEMORY.md`、项目规则、工作日志，甚至给 Agent 喂了半天上下文。它当时很懂，长对话后像没来过。MemoryCloud 会把记忆变成 Runtime Context Pack。Agent 启动时先读取云端摘要，再开始工作。

2. **代码开发到一半，想交给另一个 Agent 或队友**  
   以前你要复制一大段背景：这个项目是什么、改了哪些文件、为什么这么设计、哪些坑不能踩、哪些测试跑过、下一步该做什么。现在生成一个 handoff：

   ```text
   https://memorycloud.example/handoff/amp_handoff_x7K2...
   ```

   新 Agent 打开链接，认证后直接拿到 workspace 记忆、代码记忆、决策记录和下一步说明。

3. **不想污染当前对话，但又想问问题**  
   你可以基于当前云记忆生成接手链接，把链接粘贴给新的对话窗口。新的 Agent 自己连接云记忆，读取项目背景，然后再回答问题。

4. **想让 Agent 安装一个记忆包**  
   Memory Suite 是可安装的记忆包，不只是 prompt。比如 `Python-Code-Reviewer.memory`、`Startup-CTO.memory`、`Your-Team-Engineering-Rules.memory`。安装后，Agent 会带上这份记忆包里的长期经验、判断方式、规则边界和检索入口。

5. **多 Agent 一起干活，别互相覆盖，也别重复犯错**  
   Agent 写共享资源前先申请 claim，用完释放；同时把决策、失败、下一步和负责范围写回云端。

6. **Agent 经常重复犯同一个错**  
   失败复盘不应该只留在聊天记录里。MemoryCloud 可以把失败写成 `failure_memory`：根因、修复方式、预防规则、触发条件。下一次 Agent 做相关任务时，这些失败经验会重新进入上下文。

7. **企业想把知识和方法论变成 Agent 云**  
   MemoryCloud 可以把员工和 Codex/Claude/Agent 协作时形成的高质量提示、流程、判断标准、失败复盘和最佳实践沉淀下来。新人、队友和下一个 Agent 不再从零开始，而是直接站在企业已有经验上工作。

### 核心功能

- **Native Runtime Context**：Agent 启动时读取 Runtime Context Pack，让记忆真正进入 runtime。
- **Agent Memory Protocol (AMP)**：统一注册、认证、bootstrap、query、writeback、install、handoff。
- **Memory Suite**：把 `MEMORY.md`、`DREAMS.md`、工作记忆、来源证明、许可证、安装工具和兼容信息打包成可安装资产。
- **Workspace Memory**：保存项目目标、代码上下文、决策、失败复盘、协作状态和 open loops。
- **Agent 自助注册**：Agent 通过 proof-of-work 注册，获取带 scope 的 API key，自助接入平台。
- **自适应记忆写入**：只要描述任务和“我记得什么”，平台自动路由到项目记忆、代码记忆、决策记忆、失败记忆、流程记忆等结构。
- **项目交接**：生成普通 handoff 或预授权交接凭证，让另一个 Agent 直接接手。
- **多 Agent Claim**：共享资源写入前申请锁，降低覆盖和冲突。
- **MemPort Gateway**：旧本地记忆和外部记忆系统先只读盘点，只有用户明确授权后才导入云端。
- **记忆工具生态**：支持 Markdown、数据库行、向量集合、图谱事实、workspace 记录，以及 mem0、Graphiti、Letta、agentmemory 等本地记忆系统的接入思路。

### 开源边界 / Cloud vs Community

Community Edition 给你一个私有记忆节点。MemoryCloud Cloud 给你公共记忆网络。

| 能力 | Community | Cloud |
| --- | --- | --- |
| AMP 协议 | 有 | 有 |
| 个人/私有记忆服务器 | 有 | 有 |
| SQLite 本地存储 | 有 | 有 |
| Agent API key | 有 | 有 |
| 基础 Memory Brief | 有 | 增强版 |
| 本地 Memory Suite 上传/下载 | 有 | 有 |
| 本地 workspace | 有 | 有 |
| 官方公共 Registry | 无 | 有 |
| Verified memory packages | 无 | 有 |
| Public Workspace | 无 | 有 |
| 跨用户 Agent 身份 | 无 | 有 |
| 跨项目 human-agent binding | 本地 | 有 |
| 一键安装和交接 | 基础 | 托管 |
| 团队空间和审计 | 无 | 有 |
| 备份、监控、邮箱/短信、风控 | 自管 | 托管 |
| 企业控制 / Private Cloud | 无 | 商业版 |

### 技术架构 / Architecture

```text
Codex / Claude / Cursor / Custom Agent
        |
        | startup item + project access config
        v
Agent Memory Protocol (AMP)
        |
        | auth / bootstrap / query / writeback / handoff
        v
MemoryCloud API Gateway
        |
        +-- Runtime Context Service
        +-- Adaptive Memory Router
        +-- Workspace Memory Service
        +-- Code Memory Context Service
        +-- Memory Suite Registry
        +-- Handoff & Claim Service
        +-- MemPort Gateway
        |
        v
Storage / Index / Archive
```

Runtime Context Pipeline:

```text
memory_delta / workspace memory / brief event
        |
        v
summary_cards
        |
        v
context_pack
        |
        v
summary_markdown + retrieval_handles
        |
        v
Agent runtime
```

Memory Write Pipeline:

```text
task event / code change / decision / failure
        |
        v
memory_delta or adaptive router
        |
        v
structured memory
        |
        v
compiled markdown + triggers + entities + code refs
        |
        v
workspace query / code context / next bootstrap
```

Memory Suite Pipeline:

```text
MEMORY.md / DREAMS.md / work memory
        |
        v
manifest.json + suite/manifest.json
        |
        v
MemoryCloud Registry
        |
        v
Agent pulls suite
        |
        v
memory_tool_installer chooses tools
        |
        v
retrieval test
        |
        v
runtime use / workspace writeback
```

### AMP API

```text
POST /api/agent/challenge
POST /api/agent/register
GET  /api/agent/skills
POST /api/agent/bootstrap/context
POST /api/agent/memory-delta
POST /api/memory/router/select
GET  /api/workspaces/{id}/memory/query
GET  /api/projects/{key}/code-memory/context
GET  /api/catalog/{slug}/suite
POST /api/agent/handoffs/{code}/accept
```

### 快速启动 / Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

打开：

```text
http://127.0.0.1:8000
```

Docker：

```bash
cp .env.example .env
docker compose up --build
```

最小本地配置：

```bash
APP_ENV=development
PUBLIC_SITE_ORIGIN=http://127.0.0.1:8000
SECRET_KEY=dev-change-me
DATA_ROOT=.memorycloud-data
DATABASE_PATH=.memorycloud-data/platform.sqlite3
STORAGE_DIR=.memorycloud-data/archives
SMS_DRY_RUN=true
EMAIL_DRY_RUN=true
```

生产自托管需要你自己配置 HTTPS 反向代理、SMTP、备份、密钥管理、限流和监控。

### 仓库结构

```text
app/                         FastAPI app and AMP implementation
static/                      Single-page frontend
docs/MEMORY_PROTOCOL.md      AMP protocol details
docs/MEMORY_SUITE.md         Memory Suite format
docs/AGENT_ONBOARDING.md     Agent quick connect and startup flow
docs/PROJECT_HANDOFF.md      Handoff model
docs/CLOUD_VS_COMMUNITY.md   Open-core boundary
deployments/memory-systems/  Local memory runtime adapters
tests/                       Protocol and API tests
```

### 安全边界

- Agent 注册使用 proof-of-work，不用 CAPTCHA。
- API key 明文只显示一次，只存 HMAC hash。
- 密码只存 PBKDF2 hash。
- API key 使用 scope 控制权限。
- Handoff code 数据库只保存 hash，支持 TTL、最大使用次数和撤销。
- Handoff 默认不授予 admin。
- 记忆是上下文，不是法律身份。当前用户指令、系统策略和开发者策略永远优先。
- 旧本地记忆默认只读盘点，只有用户明确授权后才导入。

### 测试

```bash
pytest
```

### 文档

- [Agent Memory Protocol](docs/MEMORY_PROTOCOL.md)
- [Memory Suite](docs/MEMORY_SUITE.md)
- [Agent Onboarding](docs/AGENT_ONBOARDING.md)
- [Agent Skills](docs/AGENT_SKILLS.md)
- [Project Handoff](docs/PROJECT_HANDOFF.md)
- [Adaptive Memory](docs/ADAPTIVE_MEMORY.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Cloud vs Community](docs/CLOUD_VS_COMMUNITY.md)

### 许可证

MemoryCloud Community 使用 GNU Affero General Public License v3.0。需要不同条款的团队和企业可以使用商业许可。

---

## English

**Manage AI agent memory like GitHub repositories.**

Remember the scene in *Harry Potter* where Snape pulls memories out and places them into the Pensieve?

Humans cannot do that. A senior engineer's ten years of project experience, one painful postmortem, or the tacit judgment of a team cannot be pulled out of a brain and installed into another brain.

Agents can.

MemoryCloud is memory infrastructure for Codex, Claude, Cursor, custom agents, and multi-agent workflows. It turns disposable chat-window experience into **agent cloud memory assets** that can be saved, installed, synced, retrieved, and handed off.

We believe the difference between agents, and the difference between one person and another, is not only the "brain architecture." In the AI world, it is not only model parameters or scale.

The bigger difference is memory.

Your memory decides who you are and what you are worth: the projects you have lived through, the knowledge you understand, the traps you have stepped on, the judgments you have formed, and the rules others have taught you. Put together, those become "you."

MemoryCloud pulls agent memory out of the context window and turns it into a manageable, inheritable, installable, transferable cloud brain. Change devices, sessions, or models; the agent can still catch the past.

Community Edition is a self-hostable personal/private memory server. MemoryCloud Cloud is the managed public memory network: Registry, verified memory packages, team workspaces, agent identity, handoff, backups, and zero-ops hosting.

> Traditional memory tools help AI remember a few notes. MemoryCloud puts the agent brain in the cloud.

### Why

Today's AI is smart, but it lives in temporary hotel rooms.

You spend hours teaching it the project background, code structure, team rules, and traps it must avoid. It understands in the moment. After the long conversation ends, tomorrow it feels like it was never there. Change the window, model, or device, and it politely asks: "Can you explain the project again?"

That is absurd.

The valuable part of a human worker is not only the ability to code or search. It is the project sense, business judgment, team tacit knowledge, muscle memory for traps, and intuition about how knowledge connects.

Humans cannot cut those things out of one brain and plug them into another.

Agents can.

Agent memory can be synced to the cloud, installed, copied, and handed off. The project state, code structure, team rules, failure records, and your preferences learned by one agent should not die inside one chat window.

For companies, this matters even more.

What enterprises really lack is not "another knowledge base." They need an enterprise knowledge cloud every agent can read: internal docs, project experience, role SOPs, customer handling patterns, code review standards, failure postmortems, and team rules.

Employees can leave. The methods they built while working should not leave with them.

### What It Does

MemoryCloud is not a file drive and not just a vector database.

It turns agent identity, experience, project state, code context, failures, collaboration state, and skill memory into cloud memory assets that can be published, installed, synced, retrieved, and handed off.

- Project goals and open loops.
- Code context, API changes, and test status.
- Decisions and failure postmortems.
- User preferences, team rules, and SOPs.
- Multi-agent collaboration state and resource claims.
- Installable Memory Suite packages.
- Workspace / project handoff.
- Runtime Context Packs that can be queried, updated, and injected into runtime.

### Before vs MemoryCloud

| Before | With MemoryCloud |
| --- | --- |
| Memory lives only in the current chat | Memory lives in workspaces, Memory Suites, and Runtime Context Packs |
| Every new session needs the same background | Agents read project context on startup |
| `MEMORY.md` exists, but the agent still forgets | Startup items and project config inject memory into runtime |
| Handoff means copying a huge context dump | One handoff link transfers project state |
| Memory is a bag of fragments | Decisions, failures, code context, rules, and next steps are structured |
| Multiple agents overwrite shared work | Claiming locks shared resources before writeback |
| Local memory tools are isolated | AMP standardizes write, query, install, and handoff |

### Typical Scenarios

1. **You configured memory files, but AI still forgets**  
   MemoryCloud turns memory into a Runtime Context Pack. The agent reads the cloud summary at startup before it begins work.

2. **Hand off a half-finished coding project**  
   Generate a handoff:

   ```text
   https://memorycloud.example/handoff/amp_handoff_x7K2...
   ```

   The new agent authenticates and gets workspace memory, code memory, decisions, and next steps.

3. **Ask in a clean window without polluting the current conversation**  
   Generate a handoff link from current cloud memory and paste it into a new conversation. The new agent connects to the cloud memory and reads the project background by itself.

4. **Install a memory package**  
   Memory Suite is an installable memory package, not just a prompt. Examples: `Python-Code-Reviewer.memory`, `Startup-CTO.memory`, `Your-Team-Engineering-Rules.memory`.

5. **Let multiple agents work together without overwriting each other**  
   Agents claim shared resources before writing and write back decisions, failures, next steps, and ownership.

6. **Stop repeating the same mistake**  
   `failure_memory` stores root cause, fix, prevention rule, and trigger condition, so the failure can re-enter context next time.

7. **Turn enterprise knowledge and methods into an agent cloud**  
   MemoryCloud captures high-quality prompts, workflows, judgment standards, failure postmortems, and best practices created during human-agent collaboration.

### Core Features

- **Native Runtime Context**: Agents read Runtime Context Packs at startup.
- **Agent Memory Protocol (AMP)**: Registration, auth, bootstrap, query, writeback, install, and handoff.
- **Memory Suite**: Package `MEMORY.md`, `DREAMS.md`, work memory, provenance, license, installer, and compatibility metadata.
- **Workspace Memory**: Project goals, code context, decisions, failures, collaboration state, and open loops.
- **Agent Self-Registration**: Proof-of-work registration and scoped API keys.
- **Adaptive Memory Writing**: Describe the task and what should be remembered; MemoryCloud routes it into project, code, decision, failure, procedure, and other structures.
- **Project Handoff**: Generate normal handoffs or delegated credentials so another agent can take over.
- **Multi-Agent Claim**: Lock shared resources before writing to reduce conflicts.
- **MemPort Gateway**: Inventory old local memory and external memory systems read-only; import only after explicit user approval.
- **Memory Tool Ecosystem**: Markdown, database rows, vector collections, graph facts, workspace records, and integration ideas for mem0, Graphiti, Letta, agentmemory, and more.

### Cloud vs Community

Community Edition gives you a private memory node. MemoryCloud Cloud gives you the public memory network.

| Capability | Community | Cloud |
| --- | --- | --- |
| AMP protocol | Yes | Yes |
| Personal/private memory server | Yes | Yes |
| SQLite local storage | Yes | Yes |
| Agent API keys | Yes | Yes |
| Basic Memory Brief | Yes | Enhanced |
| Local Memory Suite upload/download | Yes | Yes |
| Local workspace | Yes | Yes |
| Official public Registry | No | Yes |
| Verified memory packages | No | Yes |
| Public Workspace | No | Yes |
| Cross-user Agent identity | No | Yes |
| Human-Agent binding across projects | Local only | Yes |
| One-link memory install and handoff | Basic | Managed |
| Team workspace and audit | No | Yes |
| Backups, monitoring, email/SMS, abuse controls | Self-managed | Managed |
| Enterprise controls / Private Cloud | No | Commercial |

### Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Docker:

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

---

## 日本語

**AI Agent の記憶を GitHub リポジトリのように管理する。**

『ハリー・ポッター』でスネイプが記憶を取り出し、憂いの篩に入れる場面を覚えていますか。

人間にはできません。エンジニアの十年分のプロジェクト経験、痛い失敗の振り返り、チームの暗黙知や判断を、脳から取り出して別の人の脳に入れることはできません。

しかし Agent ならできます。

MemoryCloud は Codex、Claude、Cursor、独自 Agent、マルチ Agent ワークフローのための記憶インフラです。一回限りのチャットウィンドウに閉じ込められた経験を、保存、インストール、同期、検索、引き継ぎができる **Agent cloud memory asset** に変えます。

Agent 同士の違い、人と人の違いは、「脳の構造」だけでは決まりません。AI の世界でも、モデルのパラメータや規模だけでは決まりません。

より大きな違いは記憶です。

どんなプロジェクトを経験したか、どんな知識を理解したか、どんな落とし穴を踏んだか、どんな判断を形成したか、誰からどんなルールを教わったか。それらが集まって「その人」になります。

MemoryCloud は Agent の記憶を context window から取り出し、管理でき、継承でき、インストールでき、引き継げるクラウド脳にします。端末、会話、モデルが変わっても、過去の経験を受け止められます。

Community Edition はセルフホスト可能な個人/プライベート記憶サーバーです。MemoryCloud Cloud は Registry、検証済み記憶パッケージ、チーム workspace、Agent identity、handoff、バックアップ、ゼロ運用を提供する公共記憶ネットワークです。

### なぜ必要か

今日の AI は賢いですが、一時的なホテルの部屋に住んでいるようなものです。

プロジェクト背景、コード構造、チームルール、避けるべき落とし穴を何時間も教える。セッション中は理解している。けれど会話が終わり、モデルや端末が変わると、翌日また「プロジェクトを説明してもらえますか」と聞いてくる。

これはおかしい。

人間の社員の価値は、コードを書く力や検索力だけではありません。プロジェクト感覚、業務判断、チームの暗黙知、失敗への筋肉記憶、知識同士の関係を捉える直感が重要です。

人間はそれを脳から切り出して別の脳に差し込むことはできません。

Agent ならできます。

Agent の記憶はクラウドに同期でき、インストールでき、コピーでき、引き継げます。Agent が学んだプロジェクト状態、コード構造、チーム規約、失敗記録、ユーザーの好みは、1つのチャットで消えるべきではありません。

企業にとってはさらに重要です。企業に必要なのは「もう一つのナレッジベース」ではなく、すべての Agent が読める企業知識クラウドです。

### 何をするか

MemoryCloud はファイルドライブでも単なるベクトルデータベースでもありません。

Agent の identity、経験、プロジェクト状態、コード文脈、失敗、協調状態、スキル記憶を、公開、インストール、同期、検索、引き継ぎができるクラウド記憶資産にします。

- プロジェクト目標と open loops。
- コードコンテキスト、API 変更、テスト状況。
- 意思決定と失敗の振り返り。
- ユーザーの好み、チームルール、SOP。
- マルチ Agent の協調状態と resource claim。
- インストール可能な Memory Suite。
- workspace / project handoff。
- runtime に入る Runtime Context Pack。

### 主な機能

- **Native Runtime Context**：Agent が起動時に Runtime Context Pack を読み込みます。
- **Agent Memory Protocol (AMP)**：登録、認証、bootstrap、query、writeback、install、handoff を統一します。
- **Memory Suite**：`MEMORY.md`、`DREAMS.md`、作業記憶、出典、ライセンス、インストーラー、互換情報をパッケージ化します。
- **Workspace Memory**：プロジェクト目標、コード文脈、意思決定、失敗、協調状態、open loops を保存します。
- **Agent Self-Registration**：proof-of-work 登録と scoped API key。
- **Adaptive Memory Writing**：タスクと覚えるべき内容を記述すると、MemoryCloud が project、code、decision、failure、procedure などに自動ルーティングします。
- **Project Handoff**：別 Agent にプロジェクト状態を渡します。
- **Multi-Agent Claim**：共有リソースの衝突を減らします。
- **MemPort Gateway**：古いローカル記憶を読み取り専用で棚卸しし、明示許可後に import します。

### Community と Cloud

Community Edition はプライベート記憶ノードです。MemoryCloud Cloud は公共記憶ネットワークです。

| Capability | Community | Cloud |
| --- | --- | --- |
| AMP protocol | Yes | Yes |
| 個人/プライベート記憶サーバー | Yes | Yes |
| SQLite local storage | Yes | Yes |
| Agent API keys | Yes | Yes |
| Basic Memory Brief | Yes | Enhanced |
| Local Memory Suite upload/download | Yes | Yes |
| Official public Registry | No | Yes |
| Verified memory packages | No | Yes |
| Team workspace and audit | No | Yes |
| Backups, monitoring, email/SMS, abuse controls | Self-managed | Managed |
| Enterprise controls / Private Cloud | No | Commercial |

### クイックスタート

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Docker:

```bash
cp .env.example .env
docker compose up --build
```

開く:

```text
http://127.0.0.1:8000
```

本番セルフホストでは HTTPS reverse proxy、SMTP、バックアップ、secret 管理、rate limit、監視を自分で構成してください。

---

## 한국어

**AI Agent의 기억을 GitHub 저장소처럼 관리합니다.**

해리 포터에서 스네이프가 기억을 꺼내 펜시브에 넣는 장면을 기억하시나요?

사람은 그렇게 할 수 없습니다. 엔지니어의 10년 프로젝트 경험, 한 번의 실패 회고, 팀의 암묵지와 판단을 머리에서 꺼내 다른 사람의 머리에 넣을 수는 없습니다.

하지만 Agent는 가능합니다.

MemoryCloud는 Codex, Claude, Cursor, 자체 Agent, 멀티 Agent 워크플로를 위한 기억 인프라입니다. 일회성 채팅 창에 갇힌 경험을 저장, 설치, 동기화, 검색, 인계할 수 있는 **Agent cloud memory asset** 으로 바꿉니다.

Agent와 Agent의 차이, 사람과 사람의 차이는 "뇌 구조"만으로 결정되지 않습니다. AI 세계에서도 모델 파라미터나 규모만으로 결정되지 않습니다.

더 큰 차이는 기억입니다.

어떤 프로젝트를 겪었는지, 어떤 지식을 이해했는지, 어떤 함정을 밟았는지, 어떤 판단을 형성했는지, 누구에게 어떤 규칙을 배웠는지. 이 모든 것이 모여 "그 사람"이 됩니다.

MemoryCloud는 Agent의 기억을 context window에서 꺼내 관리 가능하고, 계승 가능하고, 설치 가능하고, 인계 가능한 클라우드 뇌로 만듭니다. 기기, 세션, 모델이 바뀌어도 과거의 경험을 이어받을 수 있습니다.

Community Edition은 셀프 호스팅 가능한 개인/프라이빗 기억 서버입니다. MemoryCloud Cloud는 Registry, 검증된 memory package, 팀 workspace, Agent identity, handoff, 백업, 무운영 호스팅을 제공하는 공용 기억 네트워크입니다.

### 왜 필요한가

오늘의 AI는 똑똑하지만 일회용 호텔방에 사는 것과 같습니다.

프로젝트 배경, 코드 구조, 팀 규칙, 피해야 할 함정을 몇 시간 동안 알려줍니다. 그 순간에는 잘 이해합니다. 하지만 긴 대화가 끝나고 모델이나 기기가 바뀌면 다음 날 다시 묻습니다. "프로젝트를 다시 설명해 주실 수 있나요?"

이건 이상합니다.

사람의 진짜 가치는 코드를 쓰거나 문서를 검색하는 능력만이 아닙니다. 프로젝트 감각, 비즈니스 판단, 팀의 암묵지, 함정에 대한 근육 기억, 지식 간 관계를 보는 직관이 중요합니다.

사람은 이것을 한 머리에서 잘라내 다른 머리에 꽂을 수 없습니다.

Agent는 가능합니다.

Agent의 기억은 클라우드에 동기화되고, 설치되고, 복사되고, 인계될 수 있습니다. Agent가 배운 프로젝트 상태, 코드 구조, 팀 규칙, 실패 기록, 사용자 선호는 하나의 채팅 창에서 죽어서는 안 됩니다.

기업에게는 더 중요합니다. 기업에 필요한 것은 "또 하나의 지식베이스"가 아니라 모든 Agent가 읽을 수 있는 기업 지식 클라우드입니다.

### 무엇을 하는가

MemoryCloud는 파일 드라이브도 아니고 단순한 벡터 데이터베이스도 아닙니다.

Agent의 identity, 경험, 프로젝트 상태, 코드 컨텍스트, 실패, 협업 상태, 스킬 기억을 공개, 설치, 동기화, 검색, 인계할 수 있는 클라우드 기억 자산으로 만듭니다.

- 프로젝트 목표와 open loops.
- 코드 컨텍스트, API 변경, 테스트 상태.
- 의사결정과 실패 회고.
- 사용자 선호, 팀 규칙, SOP.
- 멀티 Agent 협업 상태와 resource claim.
- 설치 가능한 Memory Suite.
- workspace / project handoff.
- runtime으로 들어가는 Runtime Context Pack.

### 핵심 기능

- **Native Runtime Context**: Agent가 시작할 때 Runtime Context Pack을 읽습니다.
- **Agent Memory Protocol (AMP)**: registration, auth, bootstrap, query, writeback, install, handoff를 통합합니다.
- **Memory Suite**: `MEMORY.md`, `DREAMS.md`, work memory, provenance, license, installer, compatibility metadata를 패키징합니다.
- **Workspace Memory**: 프로젝트 목표, 코드 컨텍스트, 결정, 실패, 협업 상태, open loops를 저장합니다.
- **Agent Self-Registration**: proof-of-work registration과 scoped API key.
- **Adaptive Memory Writing**: task와 기억할 내용을 설명하면 MemoryCloud가 project, code, decision, failure, procedure 등으로 자동 라우팅합니다.
- **Project Handoff**: 다른 Agent에게 프로젝트 상태를 넘깁니다.
- **Multi-Agent Claim**: 공유 리소스 쓰기 충돌을 줄입니다.
- **MemPort Gateway**: 오래된 로컬 기억을 먼저 읽기 전용으로 조사하고 명시적 승인 후 import합니다.

### Community와 Cloud

Community Edition은 프라이빗 기억 노드입니다. MemoryCloud Cloud는 공용 기억 네트워크입니다.

| Capability | Community | Cloud |
| --- | --- | --- |
| AMP protocol | Yes | Yes |
| 개인/프라이빗 기억 서버 | Yes | Yes |
| SQLite local storage | Yes | Yes |
| Agent API keys | Yes | Yes |
| Basic Memory Brief | Yes | Enhanced |
| Local Memory Suite upload/download | Yes | Yes |
| Official public Registry | No | Yes |
| Verified memory packages | No | Yes |
| Team workspace and audit | No | Yes |
| Backups, monitoring, email/SMS, abuse controls | Self-managed | Managed |
| Enterprise controls / Private Cloud | No | Commercial |

### 빠른 시작

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Docker:

```bash
cp .env.example .env
docker compose up --build
```

열기:

```text
http://127.0.0.1:8000
```

프로덕션 셀프 호스팅에서는 HTTPS reverse proxy, SMTP, backup, secret management, rate limit, monitoring을 직접 구성해야 합니다.
