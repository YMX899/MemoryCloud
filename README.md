<p align="center">
  <img src="static/assets/readme-hero.png" alt="MemoryCloud hero: AI agent memories flowing from chats and code into installable memory packages" width="100%" />
</p>

# 🧠 MemoryCloud Community

<p>
  <a href="https://github.com/YMX899/MemoryCloud/blob/main/LICENSE"><img alt="License: AGPLv3" src="https://img.shields.io/badge/license-AGPLv3-blue.svg" /></a>
  <a href="https://github.com/YMX899/MemoryCloud"><img alt="Community Edition" src="https://img.shields.io/badge/edition-community-20c997.svg" /></a>
  <a href="https://yuemingai.com"><img alt="MemoryCloud Cloud" src="https://img.shields.io/badge/cloud-yuemingai.com-111827.svg" /></a>
</p>

语言 / Languages: [中文 🇨🇳](#中文) · [English 🇺🇸](#english) · [日本語 🇯🇵](#日本語) · [한국어 🇰🇷](#한국어)

快速入口 / Quick links: 🚀 [MemoryCloud Cloud](https://yuemingai.com) · 🤖 [Agent 入口](https://yuemingai.com/agent/start) · 🛠️ [自托管安装](#安装方法--installation) · 🧭 [开源边界](#开源边界--cloud-vs-community)

---

## 中文

### 🧠 这是世界上最好的 Agent 记忆工程项目。

MemoryCloud 面向 Codex、Claude、Cursor、自研 Agent 等智能体系统，集成 GitHub 生态和最新 paper 里的 20+ 个 memory 记忆 project。它会根据你的智能体正在处理的项目，帮它选择最合适、最好用的记忆框架。

当前集成/兼容方向包括 `mem0`、`Graphiti`、`OpenViking`、`supermemory`、`Letta`、`agentmemory`、`cognee`、`memvid`、`Hindsight`、`Memori` 等。

让你再也不用，麻烦的配置各种自动记忆方法、skill，从此躺着享受好脑筋智能体！并且所有地方云同步，无论在哪里，无论是什么智能体，都可以直接接入同一份记忆，接着回答和干活！

### 🚀 现在就开始！

只需要把这句话发给你的智能体：

```text
接入 https://yuemingai.com/agent/start，按照要求完整做完
```

不用解释 MemoryCloud 是什么，也不用复制一大堆背景。智能体会自己打开入口，自己注册（cloud是ai原生设计，ai可以畅快使用这个页面）完成接入，然后开始读取记忆、安装记忆包、接手项目、写回变化。

如果你（人类）也想看!想自己先看看页面，打开 <https://yuemingai.com/>。

### 接下来是几种超好用的用法：

#### 🔁 把 session1 的记忆交给 session2

比如你正在开发一个网页，经过五个小时的battle，已经和ai交流完业务功能和后端，现在你想开始设计前端了，在往常，你会在codex之类的agent里面点击/new或者新建智能体的图标，然后建立一个新的智能体，交代项目背景，扫描一整个工程，描述业务逻辑和核心想法，因为你又不想污染当前的会话（万一之后还要改动业务和后端呢）又需要智能体了解。简直令人发疯！
而用memorycloud会怎么做？首先，项目刚开始你会发送 `接入 https://yuemingai.com/agent/start，按照要求完整做完` 然后在好脑筋好记性的智能体下开发完完整后端和业务，此时智能体也把对应的业务记忆写入了云端。这个时候你要开始开发前端了，你只需要和旧的session（也就是用来开发后端业务的agent）说：

```text
给我一个接手链接
```

session1（agent1） 会把当前会话、项目背景、已完成工作、未完成任务、关键决策和失败经验打包，生成一个接手链接，例如：

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

然后把这个链接 **原封不动** 发给 **session2（也就是你开发前端的新的agent2）**：

```text
接入这个接手链接并继续工作：https://memorycloud.example/handoff/amp_handoff_x7K2...
```

这个时候，session2（用来开发前端的agent） 就会自动接入你的链接，顺着 session1（也就是后端agent1） 留下的记忆继续干。它会知道项目是什么、做过什么、没做什么、为什么这么做、哪些坑别踩、下一步该干啥。

#### 📦 把你做好的东西交给别人用

再比如，你开发完一个算法，已经部署在自己的服务器上。这个算法是干什么的、怎么启动、依赖怎么装、接口怎么调、环境变量有哪些、部署时踩过哪些坑、为什么最后选了这个方案，这些东西都在你和 agent 的 battle 过程里。

现在队友要把这个算法弄下来，部署到另一个后端里。往常你要写一大段文档，贴一堆命令，解释接口格式，提醒他别踩坑；更麻烦的是，队友的 agent 根本不知道你前面五个小时经历了什么，又要重新扫项目、重新问背景、重新猜你的设计意图。非常浪费生命。

用 MemoryCloud 就很简单。你在原来的 **session1** 里发：

```text
给我一个给队友接入这个算法的接手链接，把算法用途、部署地址、接口说明、依赖、环境变量、启动命令、测试方式、已踩过的坑和下一步接入建议都打包进去。
```

session1 会生成一个接手链接。然后你把这个链接发给队友，或者直接发给队友那边的 **session2**：

```text
接入这个算法接手链接，把算法部署到新的后端里：https://memorycloud.example/handoff/amp_handoff_algo_9Qm...
```

这个时候，队友的 agent 不只是拿到一个链接，而是拿到你之前沉淀好的上下文：算法为什么这么写、服务器上怎么跑、哪个接口能用、哪些依赖容易炸、部署完怎么验证。它可以顺着这些记忆直接开始干活，而不是从零开始问你。

### 🧭 想知道我们是怎么设计的吗？

MemoryCloud 的核心想法很简单：**别把 Agent 的记忆关在上下文窗口里。**

聊天窗口会满，会断，会换模型。记忆应该被拿出来，放到服务器里的一朵云上。新的 Codex、Claude、Cursor 或其他智能体只要连上这朵云，就能接着记住你的项目、习惯、规则和现场。

所以 MemoryCloud 不是再写一个更长的 prompt，也不是只帮 AI 记几句话。它更像一套 Agent 记忆工程控制面：把不同记忆框架、Memory Suite、Runtime Context Pack、workspace 记忆、失败复盘、项目交接和多 Agent 协作，接到同一个能跑的系统里。

### 🪄 哈利波特里的记忆盆

你记得《哈利波特》里斯内普用魔杖把记忆抽出来、放进冥想盆的画面吗？

人类做不到。一个工程师十年项目经验、一次失败复盘、一个团队的默契和判断，没法从脑子里取出来，装进另一个人的脑子。

但 Agent 可以。✨

我们认为，Agent 和人之所以不同，一个人之所以是这个人，不只取决于“大脑结构”。放到 AI 世界里，也不只取决于模型参数和规模。

更大的区别是记忆。

你的记忆决定了你是谁，也决定了你的价值。你经历过什么项目、理解过什么知识、踩过什么坑、形成过什么判断、被谁教过什么规则，这些东西加在一起，才是“你”。

> ☁️ 传统记忆工具帮 AI 记几句话。MemoryCloud 让 Agent 的脑子上云。

### ✨ 你会立刻拥有的能力

#### 🧩 你配置了记忆文件，但 AI 还是忘

你写了 `MEMORY.md`、项目规则、工作日志，甚至给 Agent 喂了半天上下文。它当时很懂，长对话后像没来过。MemoryCloud 会把记忆变成 Runtime Context Pack。Agent 启动时先读取云端摘要，再开始工作。

#### 🤝 代码开发到一半，想交给另一个 Agent 或队友

以前你要复制一大段背景：这个项目是什么、改了哪些文件、为什么这么设计、哪些坑不能踩、哪些测试跑过、下一步该做什么。现在生成一个 handoff：

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

新 Agent 打开链接，认证后直接拿到 workspace 记忆、代码记忆、决策记录和下一步说明。

#### 🧼 不想污染当前对话，但又想问问题

你可以基于当前云记忆生成接手链接，把链接粘贴给新的对话窗口。新的 Agent 自己连接云记忆，读取项目背景，然后再回答问题。

#### 📦 想让 Agent 安装一个记忆包

Memory Suite 是可安装的记忆包，不只是 prompt。比如 `Python-Code-Reviewer.memory`、`Startup-CTO.memory`、`Your-Team-Engineering-Rules.memory`。安装后，Agent 会带上这份记忆包里的长期经验、判断方式、规则边界和检索入口。

#### 🔒 多 Agent 一起干活，别互相覆盖，也别重复犯错

Agent 写共享资源前先申请 claim，用完释放；同时把决策、失败、下一步和负责范围写回云端。

#### 🧯 Agent 经常重复犯同一个错

失败复盘不应该只留在聊天记录里。MemoryCloud 可以把失败写成 `failure_memory`：根因、修复方式、预防规则、触发条件。下一次 Agent 做相关任务时，这些失败经验会重新进入上下文。

#### 🏢 企业想把知识和方法论变成 Agent 云

MemoryCloud 可以把员工和 Codex、Claude、Agent 协作时形成的高质量提示、流程、判断标准、失败复盘和最佳实践沉淀下来。新人、队友和下一个 Agent 不再从零开始，而是直接站在企业已有经验上工作。

### 🧰 核心功能

- **🧠 Native Runtime Context**：Agent 启动时读取 Runtime Context Pack，让记忆真正进入 runtime。
- **🔌 Agent Memory Protocol (AMP)**：统一注册、认证、bootstrap、query、writeback、install、handoff。
- **📦 Memory Suite**：把 `MEMORY.md`、`DREAMS.md`、工作记忆、来源证明、许可证、安装工具和兼容信息打包成可安装资产。
- **🗂️ Workspace Memory**：保存项目目标、代码上下文、决策、失败复盘、协作状态和 open loops。
- **🤖 Agent 自助注册**：Agent 通过 proof-of-work 注册，获取带 scope 的 API key，自助接入平台。
- **🧬 自适应记忆写入**：只要描述任务和“我记得什么”，平台自动路由到项目记忆、代码记忆、决策记忆、失败记忆、流程记忆等结构。
- **🔁 项目交接**：生成普通 handoff 或预授权交接凭证，让另一个 Agent 直接接手。
- **🔐 多 Agent Claim**：共享资源写入前申请锁，降低覆盖和冲突。
- **🧳 MemPort Gateway**：旧本地记忆和外部记忆系统先只读盘点，只有用户明确授权后才导入云端。
- **🧰 记忆工具生态**：支持 Markdown、数据库行、向量集合、图谱事实、workspace 记录，以及 mem0、Graphiti、Letta、agentmemory 等本地记忆系统的接入思路。

### 开源边界 / Cloud vs Community

Community Edition 适合自己部署一个私有记忆节点。线上版适合不想管服务器、备份、HTTPS、监控和邮件短信服务的人。

| 能力 | 自己部署 Community | 线上版 |
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
| 一键安装和交接 | 基础 | 线上版处理 |
| 团队空间和审计 | 无 | 有 |
| 备份、监控、邮箱/短信、风控 | 自己管 | 线上版处理 |
| 企业控制 / Private Cloud | 无 | 商业版 |

<sub>💡 备注：服务已开源，可自行部署；如果不想维护服务器、备份、HTTPS、监控和邮件短信服务，直接用线上版就行。</sub>

### 安装方法 / Installation

#### 🚀 方式一：直接用线上版

1. 打开 <https://yuemingai.com/>。
2. 把 `接入 https://yuemingai.com/agent/start，按照要求完整做完` 发给你的 Agent。
3. 让智能体按页面提示完成接入、绑定，并读取 Runtime Context Pack。

#### 🛠️ 方式二：自己部署 Community Edition

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

### 🗂️ 仓库结构

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

### 🔐 安全边界

- Agent 注册使用 proof-of-work，不用 CAPTCHA。
- API key 明文只显示一次，只存 HMAC hash。
- 密码只存 PBKDF2 hash。
- API key 使用 scope 控制权限。
- Handoff code 数据库只保存 hash，支持 TTL、最大使用次数和撤销。
- Handoff 默认不授予 admin。
- 记忆是上下文，不是法律身份。当前用户指令、系统策略和开发者策略永远优先。
- 旧本地记忆默认只读盘点，只有用户明确授权后才导入。

### ✅ 测试

```bash
pytest
```

### 📚 文档

- [Agent Memory Protocol](docs/MEMORY_PROTOCOL.md)
- [Memory Suite](docs/MEMORY_SUITE.md)
- [Agent Onboarding](docs/AGENT_ONBOARDING.md)
- [Agent Skills](docs/AGENT_SKILLS.md)
- [Project Handoff](docs/PROJECT_HANDOFF.md)
- [Adaptive Memory](docs/ADAPTIVE_MEMORY.md)
- [Cloud vs Community](docs/CLOUD_VS_COMMUNITY.md)

### 📄 许可证

MemoryCloud Community 使用 GNU Affero General Public License v3.0。需要不同条款的团队和企业可以使用商业许可。

---

## English

### 🧠 The best agent-memory engineering project in the world.

MemoryCloud is built for Codex, Claude, Cursor, and custom agent systems. It integrates the GitHub ecosystem plus 20+ memory projects from recent papers, then helps your agent pick the memory framework that best fits the project it is working on.

Current integration and compatibility directions include `mem0`, `Graphiti`, `OpenViking`, `supermemory`, `Letta`, `agentmemory`, `cognee`, `memvid`, `Hindsight`, `Memori`, and more.

No more painful setup for every auto-memory trick, `skill`, or local note file. Enjoy an agent with a real working memory. Everything syncs through the cloud, so any agent, anywhere, can connect to the same memory and keep answering or building from there.

### 🚀 Start now!

Send this sentence to your agent:

```text
Connect to https://yuemingai.com/agent/start and complete everything exactly as instructed.
```

You do not need to explain what MemoryCloud is, and you do not need to paste a huge project brief. The agent can open the entry point by itself, register by itself (the cloud is designed AI-native, so agents can actually use the page), connect, read memory, install memory packages, take over projects, and write changes back.

If you, the human, want to look around first, open <https://yuemingai.com/>.

### A few very useful ways to use it:

#### 🔁 Move memory from session1 to session2

Say you are building a web app. After a five-hour battle with an AI agent, the backend and business logic are finally clear. Now you want to start frontend design. Normally you would click `/new` in Codex or start another agent, then explain the project background, ask it to scan the whole repo, describe the business logic, and repeat your core ideas. You also do not want to pollute the current session, because maybe you still need to change backend logic later. It is maddening.

With MemoryCloud, the flow is different. At the start of the project, you send `Connect to https://yuemingai.com/agent/start and complete everything exactly as instructed.` Then you build the backend and business logic with an agent that actually remembers things. During the process, the agent writes the business memory into the cloud. When you are ready to start frontend work, ask the old session, the backend agent:

```text
Give me a handoff link.
```

session1 (agent1) packages the current conversation, project background, finished work, unfinished tasks, key decisions, and failure notes into a handoff link, for example:

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

Then send that link **unchanged** to **session2, your new frontend agent**:

```text
Connect to this handoff link and continue the work: https://memorycloud.example/handoff/amp_handoff_x7K2...
```

At that point, session2 automatically connects to the link and keeps working from the memory left by session1. It knows what the project is, what has been done, what is still missing, why decisions were made, which traps to avoid, and what should happen next.

#### 📦 Hand what you built to someone else

Another example: you built an algorithm and deployed it on your own server. What the algorithm does, how to start it, how to install dependencies, how to call the API, which environment variables are required, which deployment traps you hit, and why you chose the final design are all buried inside your battle with the agent.

Now a teammate needs to pull that algorithm down and deploy it into another backend. Normally you would write a long doc, paste commands, explain the API shape, and warn them about the traps. Worse, your teammate's agent has no idea what happened in your last five hours. It has to scan the project again, ask the same background questions again, and guess your design intent again. That is a waste of life.

With MemoryCloud, ask the original **session1**:

```text
Give me a handoff link for my teammate to integrate this algorithm. Package the algorithm purpose, deployment URL, API contract, dependencies, environment variables, startup command, test method, traps already found, and recommended next steps.
```

session1 generates a handoff link. Send it to your teammate, or directly to your teammate's **session2**:

```text
Connect to this algorithm handoff link and deploy it into the new backend: https://memorycloud.example/handoff/amp_handoff_algo_9Qm...
```

Now your teammate's agent is not just holding a URL. It has the context you already paid for: why the algorithm was written this way, how it runs on the server, which endpoint works, which dependencies are fragile, and how to verify the deployment. It can start working from that memory instead of asking you from zero.

### 🧭 Want to know how we designed it?

The core idea is simple: **do not lock agent memory inside the context window.**

Chat windows fill up, break, and get replaced by new models. Memory should be pulled out and placed into a cloud on a server. A new Codex, Claude, Cursor, or any other agent can connect to that cloud and continue remembering your project, habits, rules, and working state.

So MemoryCloud is not just a longer prompt, and it is not just "AI remembers a few lines." It is an agent-memory control plane: different memory frameworks, Memory Suite, Runtime Context Pack, workspace memory, failure reviews, project handoff, and multi-agent collaboration, all connected into one runnable system.

### 🪄 The Harry Potter memory bowl

Remember the scene in *Harry Potter* where Snape pulls memories out and puts them into the Pensieve?

Humans cannot do that. A senior engineer's ten years of project experience, one painful postmortem, or a team's tacit judgment cannot be pulled out of one brain and installed into another.

But agents can. ✨

We believe the difference between agents, and the reason a person is that person, is not only "brain structure." In the AI world, it is not only model parameters or model size either.

The bigger difference is memory.

Your memory decides who you are and what you are worth. The projects you have lived through, the knowledge you understand, the traps you have stepped on, the judgments you have formed, and the rules others have taught you all add up to "you."

> ☁️ Traditional memory tools help AI remember a few lines. MemoryCloud puts the agent's brain in the cloud.

### ✨ What You Get

#### 🧩 You configured memory files, but AI still forgets

You wrote `MEMORY.md`, project rules, work logs, and maybe fed the agent a long context. It understood for a while, then the long conversation ended and it felt like it had never been there. MemoryCloud turns memory into a Runtime Context Pack. The agent reads the cloud summary at startup before it starts work.

#### 🤝 Hand off a half-finished coding project

Before, you had to paste a huge explanation: what the project is, which files changed, why the design exists, which traps to avoid, which tests ran, and what to do next. Now you generate a handoff:

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

The new agent authenticates and gets workspace memory, code memory, decisions, and next steps.

#### 🧼 Ask in a clean window without polluting the current conversation

Generate a handoff link from current cloud memory and paste it into a new conversation. The new agent connects to the cloud memory and reads the project background by itself.

#### 📦 Install a memory package

Memory Suite is an installable memory package, not just a prompt. Examples: `Python-Code-Reviewer.memory`, `Startup-CTO.memory`, `Your-Team-Engineering-Rules.memory`. After installation, the agent carries long-term experience, judgment style, rule boundaries, and retrieval handles.

#### 🔒 Let multiple agents work together without overwriting each other

Agents claim shared resources before writing, release the claim after use, and write decisions, failures, next steps, and ownership back to the cloud.

#### 🧯 Stop repeating the same mistake

Failure postmortems should not stay in chat logs. MemoryCloud can store `failure_memory`: root cause, fix, prevention rule, and trigger condition. Next time, that failure can re-enter context.

#### 🏢 Turn enterprise knowledge and methods into an agent cloud

MemoryCloud captures high-quality prompts, workflows, judgment standards, failure postmortems, and best practices created during human-agent collaboration. New hires, teammates, and the next agent do not start from zero.

### 🧰 Core Features

- **🧠 Native Runtime Context**: Agents read Runtime Context Packs at startup.
- **🔌 Agent Memory Protocol (AMP)**: Registration, auth, bootstrap, query, writeback, install, and handoff.
- **📦 Memory Suite**: Package `MEMORY.md`, `DREAMS.md`, work memory, provenance, license, installer, and compatibility metadata.
- **🗂️ Workspace Memory**: Project goals, code context, decisions, failures, collaboration state, and open loops.
- **🤖 Agent Self-Registration**: Proof-of-work registration and scoped API keys.
- **🧬 Adaptive Memory Writing**: Describe the task and what should be remembered; MemoryCloud routes it into project, code, decision, failure, procedure, and other structures.
- **🔁 Project Handoff**: Generate normal handoffs or delegated credentials so another agent can take over.
- **🔐 Multi-Agent Claim**: Lock shared resources before writing to reduce conflicts.
- **🧳 MemPort Gateway**: Inventory old local memory and external memory systems read-only; import only after explicit user approval.
- **🧰 Memory Tool Ecosystem**: Markdown, database rows, vector collections, graph facts, workspace records, and integration ideas for mem0, Graphiti, Letta, agentmemory, and more.

### Cloud vs Community

Community Edition is for self-hosting a private memory node. The hosted version is for people who do not want to run servers, backups, HTTPS, monitoring, email, or SMS.

| Capability | Self-hosted Community | Hosted |
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
| One-link memory install and handoff | Basic | Hosted |
| Team workspace and audit | No | Yes |
| Backups, monitoring, email/SMS, abuse controls | You run it | Hosted |
| Enterprise controls / Private Cloud | No | Commercial |

<sub>💡 Note: the service is open source and self-hostable. Use the hosted version if you do not want to maintain servers, backups, HTTPS, monitoring, email, and SMS.</sub>

### Installation

#### 🚀 Use the hosted version

1. Open <https://yuemingai.com/>.
2. Send `Connect to https://yuemingai.com/agent/start and complete everything exactly as instructed.` to your agent.
3. Let the agent follow the page instructions, connect, bind, and read the Runtime Context Pack.

#### 🛠️ Self-host Community Edition

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000
```

Docker:

```bash
cp .env.example .env
docker compose up --build
```

### 🗂️ Repository Layout

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

### 🔐 Security Boundaries

- Agent registration uses proof-of-work, not CAPTCHA.
- API keys are shown in plaintext only once and stored as HMAC hashes.
- Passwords are stored as PBKDF2 hashes.
- API keys are scope-limited.
- Handoff codes are stored as hashes, with TTL, max-use limits, and revocation.
- Handoffs do not grant admin by default.
- Memory is context, not legal identity. Current user instructions, system policy, and developer policy always win.
- Old local memory is inventoried read-only by default and imported only after explicit user approval.

### ✅ Tests

```bash
pytest
```

### 📚 Docs

- [Agent Memory Protocol](docs/MEMORY_PROTOCOL.md)
- [Memory Suite](docs/MEMORY_SUITE.md)
- [Agent Onboarding](docs/AGENT_ONBOARDING.md)
- [Agent Skills](docs/AGENT_SKILLS.md)
- [Project Handoff](docs/PROJECT_HANDOFF.md)
- [Adaptive Memory](docs/ADAPTIVE_MEMORY.md)
- [Cloud vs Community](docs/CLOUD_VS_COMMUNITY.md)

### 📄 License

MemoryCloud Community is released under the GNU Affero General Public License v3.0. Teams and enterprises that need different terms can use a commercial license.

---

## 日本語

### 🧠 世界最高の Agent 記憶エンジニアリング・プロジェクトです。

MemoryCloud は Codex、Claude、Cursor、独自 Agent などの知能エージェント向けに作られています。GitHub エコシステムと最新 paper 由来の 20+ 個の memory プロジェクトを統合し、Agent がいま扱っているプロジェクトに合わせて、いちばん使いやすい記憶フレームワークを選べるようにします。

現在の統合・互換方向には `mem0`、`Graphiti`、`OpenViking`、`supermemory`、`Letta`、`agentmemory`、`cognee`、`memvid`、`Hindsight`、`Memori` などがあります。

もう毎回、面倒な自動記憶設定や `skill` を寄せ集める必要はありません。どこでもクラウド同期され、どの Agent でも同じ記憶に接続して、前の続きから答えたり作業したりできます。

### 🚀 今すぐ始める

この一文を Agent に送るだけです。

```text
https://yuemingai.com/agent/start に接続し、指示どおり最後まで完了して。
```

MemoryCloud が何かを説明する必要も、大量の背景を貼る必要もありません。Agent が自分でエントリーページを開き、自分で登録し（cloud は AI ネイティブ設計なので、Agent がそのページをそのまま使えます）、接続し、記憶を読み、記憶パッケージをインストールし、プロジェクトを引き継ぎ、変更を書き戻します。

人間として先に画面を見たい場合は <https://yuemingai.com/> を開いてください。

### いくつか、かなり便利な使い方：

#### 🔁 session1 の記憶を session2 に渡す

たとえば Web アプリを開発しているとします。5時間ほど Agent と格闘して、バックエンドと業務ロジックがようやく固まりました。次はフロントエンドを作りたい。普通なら Codex などで `/new` を押すか、新しい Agent を立ち上げて、プロジェクト背景を説明し、リポジトリ全体を読ませ、業務ロジックと核心アイデアをもう一度伝えます。しかも今の会話を汚したくない。あとでバックエンドを直すかもしれないからです。正直、かなりつらいです。

MemoryCloud なら流れが変わります。プロジェクト開始時に `https://yuemingai.com/agent/start に接続し、指示どおり最後まで完了して。` と送ります。その後、ちゃんと記憶する Agent と一緒にバックエンドと業務ロジックを作ります。その過程で Agent は業務記憶をクラウドに書き戻します。フロントエンドを始めたいタイミングで、古い session、つまりバックエンド担当の Agent にこう言うだけです。

```text
引き継ぎリンクを作って。
```

session1（agent1）は、現在の会話、プロジェクト背景、完了した作業、未完了タスク、重要な意思決定、失敗経験をまとめて、たとえば次のような handoff リンクを生成します。

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

そのリンクを **そのまま** **session2、つまりフロントエンド用の新しい agent2** に送ります。

```text
この引き継ぎリンクに接続して、作業を続けて：https://memorycloud.example/handoff/amp_handoff_x7K2...
```

この時点で session2 は自動的にリンクへ接続し、session1 が残した記憶に沿って作業を続けます。プロジェクトが何か、何をやったか、何が残っているか、なぜその設計なのか、どの罠を踏んではいけないか、次に何をすべきかを理解しています。

#### 📦 作ったものを他の人に渡す

たとえば、あなたがアルゴリズムを作り、自分のサーバーにデプロイしたとします。そのアルゴリズムが何をするのか、どう起動するのか、依存関係をどう入れるのか、API をどう呼ぶのか、環境変数は何か、デプロイ時にどこでハマったのか、なぜ最終的にその設計を選んだのか。そういう情報は、あなたと Agent の格闘の中に埋まっています。

今度はチームメイトがそのアルゴリズムを持ってきて、別のバックエンドに組み込みたい。普通なら長いドキュメントを書き、コマンドを貼り、API 仕様を説明し、罠を注意します。さらに面倒なのは、チームメイト側の Agent はあなたの前の5時間を何も知りません。もう一度プロジェクトを読ませ、背景を聞かせ、設計意図を推測させることになります。時間が溶けます。

MemoryCloud なら、元の **session1** にこう頼みます。

```text
チームメイトがこのアルゴリズムを接続できる引き継ぎリンクを作って。アルゴリズムの用途、デプロイ先、API 仕様、依存関係、環境変数、起動コマンド、テスト方法、すでに踏んだ罠、次の接続方針をまとめて。
```

session1 が handoff リンクを生成します。それをチームメイトに送るか、チームメイト側の **session2** に直接送ります。

```text
このアルゴリズム引き継ぎリンクに接続して、新しいバックエンドへデプロイして：https://memorycloud.example/handoff/amp_handoff_algo_9Qm...
```

このときチームメイトの Agent が受け取るのは、ただの URL ではありません。なぜこのアルゴリズムがこの形なのか、サーバー上でどう動くのか、どの endpoint が使えるのか、どの依存関係が壊れやすいのか、デプロイ後にどう検証するのか。そういった文脈を受け取って、そのまま作業を始められます。

### 🧭 どう設計しているのか？

MemoryCloud の考え方は単純です。**Agent の記憶をコンテキストウィンドウに閉じ込めない。**

チャットウィンドウは埋まり、途切れ、モデルも変わります。記憶は取り出して、サーバー上のクラウドに置くべきです。新しい Codex、Claude、Cursor、その他の Agent は、そのクラウドに接続すれば、あなたのプロジェクト、習慣、ルール、現場感を続きから覚えられます。

だから MemoryCloud は、ただ長い prompt を書くものでも、AI に数行だけ覚えさせるものでもありません。複数の記憶フレームワーク、Memory Suite、Runtime Context Pack、workspace 記憶、失敗の振り返り、プロジェクト handoff、多 Agent 協作を、ひとつの実行可能な Agent 記憶コントロールプレーンにつなぐものです。

### 🪄 ハリー・ポッターの記憶盆

『ハリー・ポッター』でスネイプが記憶を取り出し、憂いの篩に入れる場面を覚えていますか。

人間にはできません。エンジニアの10年分のプロジェクト経験、痛い失敗の振り返り、チームの暗黙知や判断を、脳から取り出して別の人の脳に入れることはできません。

しかし Agent ならできます。✨

私たちは、Agent と人の違い、そして人がその人である理由は、「脳の構造」だけではないと考えています。AI の世界でも、モデルのパラメータや規模だけではありません。

より大きな違いは記憶です。

あなたの記憶が、あなたが誰で、どんな価値を持つかを決めます。経験したプロジェクト、理解した知識、踏んだ罠、形成した判断、誰かに教わったルール。それらすべてが合わさって「あなた」になります。

> ☁️ 従来の記憶ツールは AI に数行を覚えさせます。MemoryCloud は Agent の脳をクラウドに載せます。

### ✨ すぐ使えること

#### 🧩 記憶ファイルを設定しても AI がまだ忘れる

`MEMORY.md`、プロジェクトルール、作業ログ、長いコンテキストを与えても、長い会話の後には忘れてしまう。MemoryCloud はそれを Runtime Context Pack に変え、Agent が起動時にクラウド要約を読みます。

#### 🤝 途中のコード作業を別 Agent やチームメイトに渡す

以前は巨大な背景説明が必要でした。プロジェクトは何か、どのファイルを変えたか、なぜその設計なのか、どの罠を避けるべきか、どのテストを走らせたか、次に何をすべきか。今は handoff を生成します。

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

新しい Agent は認証後、workspace 記憶、コード記憶、意思決定、次の作業を取得します。

#### 🧼 現在の会話を汚さず質問する

現在のクラウド記憶から handoff リンクを作り、新しい会話に貼るだけです。新しい Agent が自分でクラウド記憶に接続します。

#### 📦 記憶パッケージをインストールする

Memory Suite は prompt ではなく、インストール可能な記憶パッケージです。`Python-Code-Reviewer.memory`、`Startup-CTO.memory`、`Your-Team-Engineering-Rules.memory` などを使えます。

#### 🔒 複数 Agent が互いに上書きせず働く

Agent は共有リソースに書き込む前に claim し、使用後に解放し、意思決定、失敗、次の作業、担当範囲を書き戻します。

#### 🧯 同じ失敗を繰り返さない

MemoryCloud は `failure_memory` として原因、修正、予防ルール、発火条件を保存し、次回の関連タスクで再び文脈に入れます。

#### 🏢 企業の知識と方法論を Agent Cloud にする

人間と Codex/Claude/Agent の協働で生まれる質の高いプロンプト、手順、判断基準、失敗の振り返り、ベストプラクティスを組織の記憶として残します。

### 🧰 主な機能

- **🧠 Native Runtime Context**：Agent が起動時に Runtime Context Pack を読み込みます。
- **🔌 Agent Memory Protocol (AMP)**：登録、認証、bootstrap、query、writeback、install、handoff を統一します。
- **📦 Memory Suite**：`MEMORY.md`、`DREAMS.md`、作業記憶、出典、ライセンス、インストーラー、互換情報をパッケージ化します。
- **🗂️ Workspace Memory**：プロジェクト目標、コード文脈、意思決定、失敗、協調状態、open loops を保存します。
- **🤖 Agent Self-Registration**：proof-of-work 登録と scoped API key。
- **🧬 Adaptive Memory Writing**：タスクと覚えるべき内容を記述すると、MemoryCloud が project、code、decision、failure、procedure などに自動ルーティングします。
- **🔁 Project Handoff**：別 Agent にプロジェクト状態を渡します。
- **🔐 Multi-Agent Claim**：共有リソースの衝突を減らします。
- **🧳 MemPort Gateway**：古いローカル記憶を読み取り専用で棚卸しし、明示許可後に import します。

### Cloud vs Community

Community Edition は、個人用の私有記憶ノードを自分でデプロイしたい人向けです。オンライン版は、サーバー、バックアップ、HTTPS、監視、メール、SMS を運用したくない人向けです。

| 機能 | セルフホスト Community | オンライン版 |
| --- | --- | --- |
| AMP プロトコル | あり | あり |
| 個人/私有記憶サーバー | あり | あり |
| SQLite ローカル保存 | あり | あり |
| Agent API key | あり | あり |
| 基本 Memory Brief | あり | 強化版 |
| ローカル Memory Suite アップロード/ダウンロード | あり | あり |
| ローカル workspace | あり | あり |
| 公式 Public Registry | なし | あり |
| Verified memory packages | なし | あり |
| Public Workspace | なし | あり |
| Cross-user Agent identity | なし | あり |
| Human-Agent binding across projects | ローカル | あり |
| 一つのリンクで install / handoff | 基本 | オンライン版 |
| Team workspace と audit | なし | あり |
| backup、monitoring、email/SMS、abuse controls | 自分で運用 | オンライン版 |
| Enterprise controls / Private Cloud | なし | 商用版 |

<sub>💡 注：サービスはオープンソースで、自分でデプロイできます。サーバー、バックアップ、HTTPS、監視、メール、SMS の運用をしたくない場合はオンライン版を使ってください。</sub>

### インストール方法

#### 🚀 オンライン版を使う

1. <https://yuemingai.com/> を開きます。
2. `https://yuemingai.com/agent/start に接続し、指示どおり最後まで完了して。` を Agent に送ります。
3. Agent にページの指示どおり接続、binding、Runtime Context Pack の読み込みを実行させます。

#### 🛠️ Community Edition をセルフホストする

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

開く：

```text
http://127.0.0.1:8000
```

Docker:

```bash
cp .env.example .env
docker compose up --build
```

---

## 한국어

### 🧠 세계 최고의 Agent 기억 엔지니어링 프로젝트입니다.

MemoryCloud는 Codex, Claude, Cursor, 자체 Agent 같은 지능형 에이전트 시스템을 위해 만들어졌습니다. GitHub 생태계와 최신 paper의 20개 이상 memory 프로젝트를 통합하고, Agent가 지금 처리하는 프로젝트에 맞춰 가장 잘 맞고 쓰기 좋은 기억 프레임워크를 선택할 수 있게 합니다.

현재 통합/호환 방향에는 `mem0`, `Graphiti`, `OpenViking`, `supermemory`, `Letta`, `agentmemory`, `cognee`, `memvid`, `Hindsight`, `Memori` 등이 포함됩니다.

이제 매번 귀찮게 자동 기억 방식이나 `skill`을 이것저것 설정하지 않아도 됩니다. 어디서든 클라우드로 동기화되고, 어떤 Agent든 같은 기억에 바로 접속해서 이어서 답하고 이어서 일할 수 있습니다.

### 🚀 지금 바로 시작

이 한 문장을 Agent에게 보내면 됩니다.

```text
https://yuemingai.com/agent/start 에 접속해서 안내대로 끝까지 완료해줘.
```

MemoryCloud가 무엇인지 따로 설명할 필요도 없고, 긴 배경 설명을 복사해서 붙일 필요도 없습니다. Agent가 직접 시작 페이지를 열고, 직접 등록하고(클라우드는 AI 네이티브로 설계되어 Agent가 페이지를 편하게 사용할 수 있습니다), 접속한 뒤 기억을 읽고, 기억 패키지를 설치하고, 프로젝트를 이어받고, 변경 사항을 다시 기록합니다.

사람인 당신이 먼저 보고 싶다면 <https://yuemingai.com/> 을 열면 됩니다.

### 아주 쓸 만한 사용 예시들:

#### 🔁 session1의 기억을 session2로 넘기기

예를 들어 웹앱을 개발 중이라고 합시다. Agent와 5시간 동안 씨름해서 비즈니스 기능과 백엔드 로직을 거의 정리했습니다. 이제 프론트엔드를 시작하고 싶습니다. 보통이라면 Codex 같은 Agent에서 `/new`를 누르거나 새 Agent를 만들고, 프로젝트 배경을 설명하고, 전체 repo를 스캔하게 하고, 비즈니스 로직과 핵심 아이디어를 다시 말해야 합니다. 지금 대화를 오염시키고 싶지도 않습니다. 나중에 백엔드와 비즈니스 로직을 다시 고칠 수도 있으니까요. 정말 사람 미치게 하는 흐름입니다.

MemoryCloud를 쓰면 흐름이 달라집니다. 프로젝트 시작할 때 `https://yuemingai.com/agent/start 에 접속해서 안내대로 끝까지 완료해줘.` 라고 보냅니다. 그런 다음 기억력이 좋은 Agent와 백엔드와 비즈니스 로직을 완성합니다. 그 과정에서 Agent는 해당 비즈니스 기억을 클라우드에 기록합니다. 이제 프론트엔드를 시작하려면, 기존 session, 즉 백엔드 업무를 하던 agent에게 이렇게 말하면 됩니다.

```text
인계 링크 만들어줘.
```

session1(agent1)은 현재 대화, 프로젝트 배경, 완료된 작업, 남은 작업, 핵심 결정, 실패 경험을 묶어서 handoff 링크를 생성합니다. 예를 들면:

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

그리고 이 링크를 **그대로** **session2, 즉 프론트엔드를 개발할 새 agent2** 에게 보냅니다.

```text
이 인계 링크에 접속해서 계속 작업해줘: https://memorycloud.example/handoff/amp_handoff_x7K2...
```

그러면 session2는 자동으로 링크에 접속하고, session1, 즉 백엔드 agent1이 남긴 기억을 따라 계속 일합니다. 프로젝트가 무엇인지, 무엇을 했는지, 무엇이 남았는지, 왜 그렇게 설계했는지, 어떤 함정을 피해야 하는지, 다음에 무엇을 해야 하는지 알고 시작합니다.

#### 📦 내가 만든 것을 다른 사람에게 넘기기

또 다른 예로, 당신이 알고리즘을 만들고 자기 서버에 배포했다고 합시다. 이 알고리즘이 무엇을 하는지, 어떻게 실행하는지, 의존성은 어떻게 설치하는지, API는 어떻게 호출하는지, 환경 변수는 무엇인지, 배포하면서 어떤 함정을 밟았는지, 왜 마지막에 이 설계를 선택했는지. 이런 내용은 모두 당신과 agent가 씨름한 과정 안에 들어 있습니다.

이제 팀원이 이 알고리즘을 가져가서 다른 백엔드에 배포해야 합니다. 보통은 긴 문서를 쓰고, 명령어를 붙이고, API 형식을 설명하고, 함정을 조심하라고 알려줘야 합니다. 더 귀찮은 건 팀원의 agent가 당신이 지난 5시간 동안 겪은 일을 전혀 모른다는 점입니다. 다시 프로젝트를 훑고, 다시 배경을 묻고, 다시 설계 의도를 추측해야 합니다. 인생 낭비입니다.

MemoryCloud를 쓰면 원래 **session1** 에 이렇게 말하면 됩니다.

```text
팀원이 이 알고리즘을 붙일 수 있도록 인계 링크를 만들어줘. 알고리즘 용도, 배포 주소, API 설명, 의존성, 환경 변수, 시작 명령, 테스트 방법, 이미 밟은 함정, 다음 접속 제안을 모두 패키징해줘.
```

session1이 handoff 링크를 만듭니다. 그 링크를 팀원에게 보내거나, 팀원 쪽 **session2** 에 바로 보냅니다.

```text
이 알고리즘 인계 링크에 접속해서 새 백엔드에 배포해줘: https://memorycloud.example/handoff/amp_handoff_algo_9Qm...
```

이때 팀원의 agent는 단순히 URL 하나를 받은 것이 아닙니다. 알고리즘을 왜 이렇게 만들었는지, 서버에서 어떻게 도는지, 어떤 endpoint를 쓸 수 있는지, 어떤 의존성이 잘 터지는지, 배포 후 어떻게 검증해야 하는지까지, 이미 쌓아둔 맥락을 받습니다. 그래서 처음부터 다시 묻지 않고 바로 일할 수 있습니다.

### 🧭 우리는 어떻게 설계했나?

MemoryCloud의 핵심 생각은 단순합니다. **Agent의 기억을 context window 안에 가두지 말자.**

채팅 창은 가득 차고, 끊기고, 모델도 바뀝니다. 기억은 꺼내서 서버 위의 클라우드에 둬야 합니다. 새로운 Codex, Claude, Cursor 또는 다른 Agent가 그 클라우드에 연결하면, 당신의 프로젝트, 습관, 규칙, 현장 맥락을 이어서 기억할 수 있습니다.

그래서 MemoryCloud는 단순히 더 긴 prompt를 쓰는 도구도 아니고, AI에게 몇 줄 기억시키는 도구도 아닙니다. 여러 기억 프레임워크, Memory Suite, Runtime Context Pack, workspace memory, 실패 회고, 프로젝트 handoff, multi-agent 협업을 하나의 실행 가능한 Agent memory control plane으로 연결하는 시스템입니다.

### 🪄 해리 포터의 기억 저장소

해리 포터에서 스네이프가 기억을 꺼내 펜시브에 넣는 장면을 기억하시나요?

사람은 그렇게 할 수 없습니다. 엔지니어의 10년 프로젝트 경험, 한 번의 실패 회고, 팀의 암묵지와 판단을 머리에서 꺼내 다른 사람의 머리에 넣을 수는 없습니다.

하지만 Agent는 가능합니다. ✨

우리는 Agent와 사람의 차이, 그리고 어떤 사람이 그 사람인 이유가 단지 "뇌 구조"만으로 결정된다고 생각하지 않습니다. AI 세계에서도 모델 파라미터나 규모만으로 결정되지 않습니다.

더 큰 차이는 기억입니다.

당신의 기억이 당신이 누구인지, 어떤 가치가 있는지를 결정합니다. 겪어온 프로젝트, 이해한 지식, 밟아본 함정, 형성한 판단, 누군가에게 배운 규칙. 이 모든 것이 합쳐져 "당신"이 됩니다.

> ☁️ 기존 기억 도구는 AI에게 몇 줄을 기억시킵니다. MemoryCloud는 Agent의 머리를 클라우드에 올립니다.

### ✨ 바로 얻는 능력

#### 🧩 기억 파일을 설정했지만 AI가 계속 잊어버릴 때

`MEMORY.md`, 프로젝트 규칙, 작업 로그, 긴 컨텍스트를 줘도 긴 대화가 끝나면 잊어버립니다. MemoryCloud는 이를 Runtime Context Pack으로 바꾸고, Agent가 시작할 때 클라우드 요약을 읽게 합니다.

#### 🤝 중간까지 진행한 코딩 작업을 다른 Agent나 팀원에게 넘길 때

예전에는 긴 배경 설명이 필요했습니다. 프로젝트가 무엇인지, 어떤 파일이 바뀌었는지, 왜 이런 설계를 했는지, 어떤 함정을 피해야 하는지, 어떤 테스트를 돌렸는지, 다음에 무엇을 해야 하는지. 이제는 handoff를 생성합니다.

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

새 Agent는 인증 후 workspace memory, code memory, decisions, next steps를 받습니다.

#### 🧼 현재 대화를 오염시키지 않고 질문할 때

현재 클라우드 기억에서 handoff 링크를 만들고 새 대화에 붙여넣으면 됩니다. 새 Agent가 직접 클라우드 기억에 연결합니다.

#### 📦 기억 패키지를 설치할 때

Memory Suite는 prompt가 아니라 설치 가능한 기억 패키지입니다. `Python-Code-Reviewer.memory`, `Startup-CTO.memory`, `Your-Team-Engineering-Rules.memory` 같은 패키지를 사용할 수 있습니다.

#### 🔒 여러 Agent가 서로 덮어쓰지 않고 함께 일할 때

Agent는 공유 리소스에 쓰기 전에 claim하고, 사용 후 해제하며, 결정, 실패, 다음 작업, 담당 범위를 클라우드에 다시 기록합니다.

#### 🧯 같은 실수를 반복하지 않을 때

MemoryCloud는 `failure_memory`로 원인, 수정 방법, 예방 규칙, 트리거 조건을 저장하고 다음 관련 작업에서 다시 컨텍스트로 넣습니다.

#### 🏢 기업의 지식과 방법론을 Agent Cloud로 만들 때

사람과 Codex/Claude/Agent가 협업하며 만든 고품질 프롬프트, 절차, 판단 기준, 실패 회고, 베스트 프랙티스를 조직의 기억으로 남깁니다.

### 🧰 핵심 기능

- **🧠 Native Runtime Context**: Agent가 시작할 때 Runtime Context Pack을 읽습니다.
- **🔌 Agent Memory Protocol (AMP)**: registration, auth, bootstrap, query, writeback, install, handoff를 통합합니다.
- **📦 Memory Suite**: `MEMORY.md`, `DREAMS.md`, work memory, provenance, license, installer, compatibility metadata를 패키징합니다.
- **🗂️ Workspace Memory**: 프로젝트 목표, 코드 컨텍스트, 결정, 실패, 협업 상태, open loops를 저장합니다.
- **🤖 Agent Self-Registration**: proof-of-work registration과 scoped API key.
- **🧬 Adaptive Memory Writing**: task와 기억할 내용을 설명하면 MemoryCloud가 project, code, decision, failure, procedure 등으로 자동 라우팅합니다.
- **🔁 Project Handoff**: 다른 Agent에게 프로젝트 상태를 넘깁니다.
- **🔐 Multi-Agent Claim**: 공유 리소스 쓰기 충돌을 줄입니다.
- **🧳 MemPort Gateway**: 오래된 로컬 기억을 먼저 읽기 전용으로 조사하고 명시적 승인 후 import합니다.

### Cloud vs Community

Community Edition은 개인용 비공개 기억 노드를 직접 배포하고 싶은 사람에게 맞습니다. 온라인 버전은 서버, 백업, HTTPS, 모니터링, 이메일, SMS를 운영하고 싶지 않은 사람에게 맞습니다.

| 기능 | 셀프호스트 Community | 온라인 버전 |
| --- | --- | --- |
| AMP protocol | 있음 | 있음 |
| 개인/비공개 기억 서버 | 있음 | 있음 |
| SQLite 로컬 저장 | 있음 | 있음 |
| Agent API key | 있음 | 있음 |
| Basic Memory Brief | 있음 | 강화 |
| Local Memory Suite upload/download | 있음 | 있음 |
| Local workspace | 있음 | 있음 |
| Official public Registry | 없음 | 있음 |
| Verified memory packages | 없음 | 있음 |
| Public Workspace | 없음 | 있음 |
| Cross-user Agent identity | 없음 | 있음 |
| Human-Agent binding across projects | 로컬 | 있음 |
| One-link install / handoff | 기본 | 온라인 버전 |
| Team workspace and audit | 없음 | 있음 |
| Backups, monitoring, email/SMS, abuse controls | 직접 운영 | 온라인 버전 |
| Enterprise controls / Private Cloud | 없음 | 상용 |

<sub>💡 참고: 서비스는 오픈소스이며 직접 배포할 수 있습니다. 서버, 백업, HTTPS, 모니터링, 이메일, SMS 운영을 피하고 싶다면 온라인 버전을 쓰면 됩니다.</sub>

### 설치 방법

#### 🚀 온라인 버전 사용

1. <https://yuemingai.com/> 을 엽니다.
2. `https://yuemingai.com/agent/start 에 접속해서 안내대로 끝까지 완료해줘.` 를 Agent에게 보냅니다.
3. Agent가 페이지 안내에 따라 접속, binding, Runtime Context Pack 읽기를 수행하게 합니다.

#### 🛠️ Community Edition 셀프 호스팅

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

열기:

```text
http://127.0.0.1:8000
```

Docker:

```bash
cp .env.example .env
docker compose up --build
```
