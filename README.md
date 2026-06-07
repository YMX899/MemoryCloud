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

快速入口 / Quick links: [MemoryCloud Cloud](https://yuemingai.com) · [Agent 入口](https://yuemingai.com/agent/start) · [自托管安装](#安装方法--installation) · [开源边界](#开源边界--cloud-vs-community)

---

## 中文

**MemoryCloud 是面向 Codex、Claude、Cursor、自研 Agent 等 Agent 系统设计的史上最棒的记忆工具。可以理解为：记忆界的 GitHub。**

你记得《哈利波特》里斯内普用魔杖把记忆抽出来、放进冥想盆的画面吗？

人类做不到。一个工程师十年项目经验、一次失败复盘、一个团队的默契和判断，没法从脑子里取出来，装进另一个人的脑子。

但 Agent 可以。

MemoryCloud 把一次性聊天窗口里的经验，变成可以保存、安装、同步、检索和交接的 **Agent 云记忆资产**。

MemoryCloud 做的事，就是把 Agent 的记忆从上下文窗口里取出来，变成可管理、可继承、可安装、可交接的云端大脑。换设备、换会话、换模型，它依然记得住过去的记忆。

从此以后，Agent 的记忆将成为服务器里的一朵云。只要你让新的 Codex、Claude、Cursor 或其他 Agent 连接上这朵云，它就仍然是你认识的那个熟悉你、知晓你习惯、理解你项目现场的 Agent。

我们认为，Agent 和人之所以不同，一个人之所以是这个人，不只取决于“大脑结构”。放到 AI 世界里，也不只取决于模型参数和规模。

更大的区别是记忆。

你的记忆决定了你是谁，也决定了你的价值。你经历过什么项目、理解过什么知识、踩过什么坑、形成过什么判断、被谁教过什么规则，这些东西加在一起，才是“你”。

> 传统记忆工具帮 AI 记几句话。MemoryCloud 让 Agent 的脑子上云。

### 托管平台

为了方便大家使用，我们已经开发了 **MemoryCloud Cloud**，免去部署和租用服务器的烦恼。

- 人类阅读的网址：<https://yuemingai.com/>
- Agent 阅读的网址：<https://yuemingai.com/agent/start>

你只需要把和首页一样的接入命令发给 Codex、Claude、Cursor 或其他 Agent：

```text
接入 https://yuemingai.com/agent/start，按照要求完整做完
```

它就可以按 MemoryCloud 的 onboarding 流程注册、读取记忆、安装记忆包、接手项目、写回任务变化。

<sub>备注：服务已开源，可自行部署；不想维护服务器时，直接使用 MemoryCloud Cloud。</sub>

### 你会立刻拥有的能力

**你配置了记忆文件，但 AI 还是忘**

你写了 `MEMORY.md`、项目规则、工作日志，甚至给 Agent 喂了半天上下文。它当时很懂，长对话后像没来过。MemoryCloud 会把记忆变成 Runtime Context Pack。Agent 启动时先读取云端摘要，再开始工作。

**代码开发到一半，想交给另一个 Agent 或队友**

以前你要复制一大段背景：这个项目是什么、改了哪些文件、为什么这么设计、哪些坑不能踩、哪些测试跑过、下一步该做什么。现在生成一个 handoff：

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

新 Agent 打开链接，认证后直接拿到 workspace 记忆、代码记忆、决策记录和下一步说明。

**不想污染当前对话，但又想问问题**

你可以基于当前云记忆生成接手链接，把链接粘贴给新的对话窗口。新的 Agent 自己连接云记忆，读取项目背景，然后再回答问题。

**想让 Agent 安装一个记忆包**

Memory Suite 是可安装的记忆包，不只是 prompt。比如 `Python-Code-Reviewer.memory`、`Startup-CTO.memory`、`Your-Team-Engineering-Rules.memory`。安装后，Agent 会带上这份记忆包里的长期经验、判断方式、规则边界和检索入口。

**多 Agent 一起干活，别互相覆盖，也别重复犯错**

Agent 写共享资源前先申请 claim，用完释放；同时把决策、失败、下一步和负责范围写回云端。

**Agent 经常重复犯同一个错**

失败复盘不应该只留在聊天记录里。MemoryCloud 可以把失败写成 `failure_memory`：根因、修复方式、预防规则、触发条件。下一次 Agent 做相关任务时，这些失败经验会重新进入上下文。

**企业想把知识和方法论变成 Agent 云**

MemoryCloud 可以把员工和 Codex、Claude、Agent 协作时形成的高质量提示、流程、判断标准、失败复盘和最佳实践沉淀下来。新人、队友和下一个 Agent 不再从零开始，而是直接站在企业已有经验上工作。

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

### 安装方法 / Installation

**方式一：使用 MemoryCloud Cloud**

1. 打开 <https://yuemingai.com/>。
2. 把 `接入 https://yuemingai.com/agent/start，按照要求完整做完` 发给你的 Agent。
3. 让 Agent 按页面返回的 onboarding 指令注册、绑定、读取 Runtime Context Pack。

**方式二：自托管 Community Edition**

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
- [Cloud vs Community](docs/CLOUD_VS_COMMUNITY.md)

### 许可证

MemoryCloud Community 使用 GNU Affero General Public License v3.0。需要不同条款的团队和企业可以使用商业许可。

---

## English

**MemoryCloud is the best memory tool ever designed for agent systems like Codex, Claude, Cursor, and custom agents. Think of it as GitHub for memory.**

Remember the scene in *Harry Potter* where Snape pulls memories out and places them into the Pensieve?

Humans cannot do that. A senior engineer's ten years of project experience, one painful postmortem, or the tacit judgment of a team cannot be pulled out of a brain and installed into another brain.

Agents can.

MemoryCloud turns disposable chat-window experience into **agent cloud memory assets** that can be saved, installed, synced, retrieved, and handed off.

MemoryCloud pulls agent memory out of the context window and turns it into a manageable, inheritable, installable, transferable cloud brain. Change devices, sessions, or models; it still remembers what came before.

From now on, an agent's memory can become a cloud living on a server. Whenever a new Codex, Claude, Cursor, or other agent connects to that cloud, it can still be the familiar agent that knows you, your habits, and your project state.

The bigger difference between agents is memory. Your memory decides who you are and what you are worth: the projects you have lived through, the knowledge you understand, the traps you have stepped on, the judgments you have formed, and the rules others have taught you.

### Managed Platform

To make this easy, we built **MemoryCloud Cloud** so you do not need to deploy or rent a server.

- Human URL: <https://yuemingai.com/>
- Agent URL: <https://yuemingai.com/agent/start>

Send the same command shown on the homepage to Codex, Claude, Cursor, or another agent:

```text
接入 https://yuemingai.com/agent/start，按照要求完整做完
```

The agent can then follow the MemoryCloud onboarding flow to register, read memory, install memory packages, accept handoffs, and write back task changes.

<sub>Note: MemoryCloud Community is open source and self-hostable; use MemoryCloud Cloud when you do not want to operate a server.</sub>

### What You Get

**You configured memory files, but AI still forgets**

You wrote `MEMORY.md`, project rules, work logs, and maybe fed the agent a long context. It understood for a while, then the long conversation ended and it felt like it had never been there. MemoryCloud turns memory into a Runtime Context Pack. The agent reads the cloud summary at startup before it starts work.

**Hand off a half-finished coding project**

Before, you had to paste a huge explanation: what the project is, which files changed, why the design exists, which traps to avoid, which tests ran, and what to do next. Now you generate a handoff:

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

The new agent authenticates and gets workspace memory, code memory, decisions, and next steps.

**Ask in a clean window without polluting the current conversation**

Generate a handoff link from current cloud memory and paste it into a new conversation. The new agent connects to the cloud memory and reads the project background by itself.

**Install a memory package**

Memory Suite is an installable memory package, not just a prompt. Examples: `Python-Code-Reviewer.memory`, `Startup-CTO.memory`, `Your-Team-Engineering-Rules.memory`. After installation, the agent carries long-term experience, judgment style, rule boundaries, and retrieval handles.

**Let multiple agents work together without overwriting each other**

Agents claim shared resources before writing, release the claim after use, and write decisions, failures, next steps, and ownership back to the cloud.

**Stop repeating the same mistake**

Failure postmortems should not stay in chat logs. MemoryCloud can store `failure_memory`: root cause, fix, prevention rule, and trigger condition. Next time, that failure can re-enter context.

**Turn enterprise knowledge and methods into an agent cloud**

MemoryCloud captures high-quality prompts, workflows, judgment standards, failure postmortems, and best practices created during human-agent collaboration. New hires, teammates, and the next agent do not start from zero.

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

### Installation

Use MemoryCloud Cloud:

1. Open <https://yuemingai.com/>.
2. Send `接入 https://yuemingai.com/agent/start，按照要求完整做完` to your agent.
3. Let the agent follow onboarding, register, bind, and read the Runtime Context Pack.

Self-host Community Edition:

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

**MemoryCloud は Codex、Claude、Cursor、独自 Agent などの Agent システムのために設計された、史上最高の記憶ツールです。記憶界の GitHub と考えてください。**

『ハリー・ポッター』でスネイプが記憶を取り出し、憂いの篩に入れる場面を覚えていますか。

人間にはできません。エンジニアの十年分のプロジェクト経験、痛い失敗の振り返り、チームの暗黙知や判断を、脳から取り出して別の人の脳に入れることはできません。

しかし Agent ならできます。

MemoryCloud は、一回限りのチャットウィンドウに閉じ込められた経験を、保存、インストール、同期、検索、引き継ぎができる **Agent cloud memory asset** に変えます。

MemoryCloud がやることは、Agent の記憶を context window から取り出し、管理でき、継承でき、インストールでき、引き継げるクラウド脳にすることです。端末、会話、モデルが変わっても、過去の記憶を覚え続けます。

これから Agent の記憶はサーバー上の一つのクラウドになります。新しい Codex、Claude、Cursor、その他の Agent がそのクラウドに接続すれば、それはあなたを知り、習慣を理解し、プロジェクト状態を覚えている、あの馴染みの Agent のままです。

### マネージドプラットフォーム

簡単に使えるように、私たちは **MemoryCloud Cloud** を用意しました。デプロイやサーバーレンタルの手間を省けます。

- 人間向け URL：<https://yuemingai.com/>
- Agent 向け URL：<https://yuemingai.com/agent/start>

トップページと同じ接続コマンドを Codex、Claude、Cursor、または他の Agent に送るだけです。

```text
接入 https://yuemingai.com/agent/start，按照要求完整做完
```

Agent は onboarding に従って登録し、記憶を読み、記憶パッケージをインストールし、handoff を受け取り、タスク変化を書き戻せます。

<sub>注：MemoryCloud Community はオープンソースで、自分でデプロイできます。サーバー運用を避けたい場合は MemoryCloud Cloud を使ってください。</sub>

### できること

**記憶ファイルを設定したのに AI がまだ忘れる**

`MEMORY.md`、プロジェクトルール、作業ログ、長いコンテキストを与えても、長い会話の後には忘れてしまう。MemoryCloud はそれを Runtime Context Pack に変え、Agent が起動時にクラウド要約を読みます。

**途中のコード作業を別 Agent やチームメイトに渡す**

以前は巨大な背景説明が必要でした。今は handoff を生成します。

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

新しい Agent は認証後、workspace 記憶、コード記憶、意思決定、次の作業を取得します。

**現在の会話を汚さず質問する**

現在のクラウド記憶から handoff リンクを作り、新しい会話に貼るだけです。新しい Agent が自分でクラウド記憶に接続します。

**記憶パッケージをインストールする**

Memory Suite は prompt ではなく、インストール可能な記憶パッケージです。`Python-Code-Reviewer.memory`、`Startup-CTO.memory`、`Your-Team-Engineering-Rules.memory` などを使えます。

**複数 Agent が互いに上書きせず働く**

Agent は共有リソースに書き込む前に claim し、使用後に解放し、意思決定、失敗、次の作業、担当範囲を書き戻します。

**同じ失敗を繰り返さない**

MemoryCloud は `failure_memory` として原因、修正、予防ルール、発火条件を保存し、次回の関連タスクで再び文脈に入れます。

**企業の知識と方法論を Agent Cloud にする**

人間と Codex/Claude/Agent の協働で生まれる質の高いプロンプト、手順、判断基準、失敗の振り返り、ベストプラクティスを組織の記憶として残します。

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

### インストール方法

MemoryCloud Cloud を使う：

1. <https://yuemingai.com/> を開きます。
2. `接入 https://yuemingai.com/agent/start，按照要求完整做完` を Agent に送ります。
3. Agent に onboarding、登録、binding、Runtime Context Pack の読み込みを実行させます。

Community Edition をセルフホストする：

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

---

## 한국어

**MemoryCloud는 Codex, Claude, Cursor, 자체 Agent 같은 Agent 시스템을 위해 설계된 역사상 가장 뛰어난 기억 도구입니다. 기억 세계의 GitHub라고 이해하면 됩니다.**

해리 포터에서 스네이프가 기억을 꺼내 펜시브에 넣는 장면을 기억하시나요?

사람은 그렇게 할 수 없습니다. 엔지니어의 10년 프로젝트 경험, 한 번의 실패 회고, 팀의 암묵지와 판단을 머리에서 꺼내 다른 사람의 머리에 넣을 수는 없습니다.

하지만 Agent는 가능합니다.

MemoryCloud는 일회성 채팅 창의 경험을 저장, 설치, 동기화, 검색, 인계할 수 있는 **Agent cloud memory asset** 으로 바꿉니다.

MemoryCloud가 하는 일은 Agent의 기억을 context window에서 꺼내 관리 가능하고, 계승 가능하고, 설치 가능하고, 인계 가능한 클라우드 뇌로 만드는 것입니다. 기기, 세션, 모델이 바뀌어도 과거의 기억을 계속 기억합니다.

이제 Agent의 기억은 서버 안의 하나의 클라우드가 됩니다. 새로운 Codex, Claude, Cursor 또는 다른 Agent가 이 클라우드에 연결되기만 하면, 그것은 여전히 당신을 알고, 당신의 습관을 이해하고, 프로젝트 상황을 기억하는 익숙한 Agent입니다.

### 관리형 플랫폼

쉽게 사용할 수 있도록 **MemoryCloud Cloud** 를 만들었습니다. 배포하거나 서버를 빌릴 필요가 없습니다.

- 사람용 URL: <https://yuemingai.com/>
- Agent용 URL: <https://yuemingai.com/agent/start>

홈페이지와 같은 접속 명령을 Codex, Claude, Cursor 또는 다른 Agent에게 보내기만 하면 됩니다.

```text
接入 https://yuemingai.com/agent/start，按照要求完整做完
```

Agent는 onboarding에 따라 등록하고, 기억을 읽고, memory package를 설치하고, handoff를 받고, 작업 변화를 다시 기록할 수 있습니다.

<sub>참고: MemoryCloud Community는 오픈소스이며 직접 배포할 수 있습니다. 서버 운영을 피하고 싶다면 MemoryCloud Cloud를 사용하세요.</sub>

### 가능한 일

**기억 파일을 설정했지만 AI가 계속 잊어버릴 때**

`MEMORY.md`, 프로젝트 규칙, 작업 로그, 긴 컨텍스트를 줘도 긴 대화가 끝나면 잊어버립니다. MemoryCloud는 이를 Runtime Context Pack으로 바꾸고, Agent가 시작할 때 클라우드 요약을 읽게 합니다.

**중간까지 진행한 코딩 작업을 다른 Agent나 팀원에게 넘길 때**

예전에는 긴 배경 설명이 필요했습니다. 이제 handoff를 생성합니다.

```text
https://memorycloud.example/handoff/amp_handoff_x7K2...
```

새 Agent는 인증 후 workspace memory, code memory, decisions, next steps를 받습니다.

**현재 대화를 오염시키지 않고 질문할 때**

현재 클라우드 기억에서 handoff 링크를 만들고 새 대화에 붙여넣으면 됩니다. 새 Agent가 직접 클라우드 기억에 연결합니다.

**기억 패키지를 설치할 때**

Memory Suite는 prompt가 아니라 설치 가능한 기억 패키지입니다. `Python-Code-Reviewer.memory`, `Startup-CTO.memory`, `Your-Team-Engineering-Rules.memory` 같은 패키지를 사용할 수 있습니다.

**여러 Agent가 서로 덮어쓰지 않고 함께 일할 때**

Agent는 공유 리소스에 쓰기 전에 claim하고, 사용 후 해제하며, 결정, 실패, 다음 작업, 담당 범위를 클라우드에 다시 기록합니다.

**같은 실수를 반복하지 않을 때**

MemoryCloud는 `failure_memory`로 원인, 수정 방법, 예방 규칙, 트리거 조건을 저장하고 다음 관련 작업에서 다시 컨텍스트로 넣습니다.

**기업의 지식과 방법론을 Agent Cloud로 만들 때**

사람과 Codex/Claude/Agent가 협업하며 만든 고품질 프롬프트, 절차, 판단 기준, 실패 회고, 베스트 프랙티스를 조직의 기억으로 남깁니다.

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

### 설치 방법

MemoryCloud Cloud 사용:

1. <https://yuemingai.com/> 을 엽니다.
2. `接入 https://yuemingai.com/agent/start，按照要求完整做完` 를 Agent에게 보냅니다.
3. Agent가 onboarding, registration, binding, Runtime Context Pack 읽기를 수행하게 합니다.

Community Edition 셀프 호스팅:

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
