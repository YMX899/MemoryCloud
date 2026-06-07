from __future__ import annotations

import re
from typing import Any


INTEGRATION_SCHEMA = "amp.memory-integrations.v1"
RECOMMENDATION_SCHEMA = "amp.memory-integration-recommendation.v1"


TOP_MEMORY_INTEGRATIONS: list[dict[str, Any]] = [
    {
        "id": "mem0",
        "rank": 1,
        "name": "mem0",
        "project": "mem0ai/mem0",
        "repo_url": "https://github.com/mem0ai/mem0",
        "docs_url": "https://mem0.ai",
        "license_spdx": "Apache-2.0",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 57530,
        "github_forks_checked": 6576,
        "positioning": "通用 AI Agent 长期记忆层。",
        "best_for": ["生产级个性化助手", "长期用户画像", "客服与私域助理", "跨会话偏好记忆"],
        "memory_methods": ["profile_memory", "conversation_memory", "task_execution_memory", "vector_semantic_retrieval"],
        "storage_patterns": ["用户画像记忆", "会话事实记忆", "时间衰减召回", "向量检索加元数据过滤"],
        "integration_mode": "sdk_or_api_adapter",
        "capabilities": ["ingest", "search", "update", "delete", "user_session_agent_scope", "semantic_retrieval"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud 的 profile/conversation/task 记忆映射到 mem0 user_id、agent_id 和 session_id 维度。",
            "retrieve": "按 workspace、user、agent、query 和时间范围召回，返回 source、confidence、created_at。",
            "export": "导出为 amp.memory.v1 的 MEMORY.md、结构化 JSON 和 provenance。",
        },
        "keywords": ["用户", "偏好", "会话", "长期", "客服", "personalization", "profile", "session", "mem0"],
        "risk_flags": ["benchmark_fit_needs_validation"],
        "commercial_policy": "Apache-2.0；可作为本地记忆运行时部署，生产前验证任务指标和数据驻留要求。",
    },
    {
        "id": "graphiti",
        "rank": 2,
        "name": "Graphiti",
        "project": "getzep/graphiti",
        "repo_url": "https://github.com/getzep/graphiti",
        "docs_url": "https://help.getzep.com/graphiti",
        "license_spdx": "Apache-2.0",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 26946,
        "github_forks_checked": 2688,
        "positioning": "面向 Agent 的实时 temporal knowledge graph。",
        "best_for": ["事实会变化的长期记忆", "企业关系网络", "多跳实体推理", "带 provenance 的知识图谱"],
        "memory_methods": ["entity_memory", "project_memory", "collaboration_memory", "temporal_knowledge_graph"],
        "storage_patterns": ["实体节点", "关系边", "时间有效性", "来源追踪", "冲突事实保留"],
        "integration_mode": "temporal_graph_adapter",
        "capabilities": ["ingest", "search", "graph_query", "temporal_reasoning", "provenance"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud entity/project/collaboration 记忆拆成 entity、edge、episode 和 valid_time。",
            "retrieve": "按实体、关系、时间窗口和 task query 召回图谱路径。",
            "export": "导出 entities、relations、time_scope 和 provenance 到 MemoryCloud 结构化事件。",
        },
        "keywords": ["图", "关系", "实体", "时间", "变化", "知识图谱", "graph", "temporal", "provenance", "graphiti"],
        "risk_flags": ["graph_database_operations_complexity"],
        "commercial_policy": "Apache-2.0；适合作为图记忆后端，需配置图数据库和迁移策略。",
    },
    {
        "id": "openviking",
        "rank": 3,
        "name": "OpenViking",
        "project": "volcengine/OpenViking",
        "repo_url": "https://github.com/volcengine/OpenViking",
        "docs_url": "https://openviking.ai",
        "license_spdx": "AGPL-3.0",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 25074,
        "github_forks_checked": 1928,
        "positioning": "面向 Agent 的 context database，用文件系统范式统一 memories、resources 和 skills。",
        "best_for": ["OpenClaw 或类 OpenClaw 运行时", "上下文工程", "长期项目目录", "技能/资源/记忆一体管理"],
        "memory_methods": ["hierarchical_file_memory", "workspace_memory", "procedure_memory", "resource_skill_context"],
        "storage_patterns": ["分层目录上下文", "资源索引", "Skill 目录", "可演化上下文树"],
        "integration_mode": "context_database_adapter",
        "capabilities": ["ingest", "search", "filesystem_mapping", "skill_context_delivery", "hierarchical_context"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud MEMORY.md、DREAMS.md、memory/*.md 和 install/openclaw.json 投影到 OpenViking context tree。",
            "retrieve": "按 path、resource、skill 和 task query 返回最小相关上下文。",
            "export": "保持文件路径、sha256、suite_id、version 和 OpenClaw 映射。",
        },
        "keywords": ["openclaw", "文件系统", "技能", "资源", "context", "filesystem", "OpenViking", "opencode"],
        "risk_flags": ["agpl_license_review_required", "closed_source_distribution_risk"],
        "commercial_policy": "AGPL-3.0；闭源商业部署必须做 license review 或保持隔离服务边界。",
    },
    {
        "id": "supermemory",
        "rank": 4,
        "name": "supermemory",
        "project": "supermemoryai/supermemory",
        "repo_url": "https://github.com/supermemoryai/supermemory",
        "docs_url": "https://supermemory.ai/docs",
        "license_spdx": "MIT",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 24857,
        "github_forks_checked": 2190,
        "positioning": "Memory API、应用和插件生态，面向快速接入统一记忆。",
        "best_for": ["快速给产品加统一记忆", "RAG 与资料摄取", "多模态资料抽取", "本地 API 优先场景"],
        "memory_methods": ["vector_semantic_retrieval", "profile_memory", "conversation_memory", "connector_ingestion"],
        "storage_patterns": ["事实抽取", "用户画像", "资料摄取", "语义检索 API"],
        "integration_mode": "hosted_or_self_hosted_api_adapter",
        "capabilities": ["ingest", "search", "connector_sync", "fact_extraction", "multimodal_ingestion"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud workspace 或 suite 内容推送到 supermemory collection，并保存 MemoryCloud provenance。",
            "retrieve": "按 query、user/workspace scope 和 source filters 调 supermemory 检索。",
            "export": "把抽取事实转回 MemoryCloud profile/conversation/project 记忆。",
        },
        "keywords": ["api", "connector", "插件", "多模态", "rag", "hosted", "supermemory"],
        "risk_flags": ["hosted_data_control_review"],
        "commercial_policy": "MIT；可自建或托管接入，生产前确认数据控制、region 和 SLA。",
    },
    {
        "id": "letta",
        "rank": 5,
        "name": "Letta",
        "project": "letta-ai/letta",
        "repo_url": "https://github.com/letta-ai/letta",
        "docs_url": "https://docs.letta.com/",
        "license_spdx": "Apache-2.0",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 23116,
        "github_forks_checked": 2464,
        "positioning": "Stateful agents 平台，面向有持久状态和自改进能力的 Agent runtime。",
        "best_for": ["完整 stateful agent runtime", "长期人格/状态", "自学习 Agent", "需要运行时级记忆管理"],
        "memory_methods": ["stateful_agent_memory", "profile_memory", "procedure_memory", "conversation_memory"],
        "storage_patterns": ["核心记忆", "归档记忆", "对话状态", "工具调用状态"],
        "integration_mode": "runtime_bridge",
        "capabilities": ["ingest", "search", "runtime_state", "agent_identity_state", "tool_memory"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud profile/procedure/conversation 记忆写入 Letta agent state 或 archival memory。",
            "retrieve": "执行任务前从 Letta runtime 拉取核心状态和相关归档片段。",
            "export": "把 runtime 更新摘要回写到 MemoryCloud adaptive memory 或 self sync。",
        },
        "keywords": ["stateful", "runtime", "agent state", "自改进", "人格", "letta", "memgpt"],
        "risk_flags": ["architecture_intrusion_heavier_than_sdk"],
        "commercial_policy": "Apache-2.0；适合 runtime 级集成，已有产品只需要轻量 memory layer 时不应默认选它。",
    },
    {
        "id": "agentmemory",
        "rank": 6,
        "name": "agentmemory",
        "project": "rohitg00/agentmemory",
        "repo_url": "https://github.com/rohitg00/agentmemory",
        "docs_url": "https://agent-memory.dev",
        "license_spdx": "Apache-2.0",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 20855,
        "github_forks_checked": 1719,
        "positioning": "面向编程 Agent 的 persistent memory，覆盖主流 MCP client。",
        "best_for": ["Claude Code/Codex/Cursor 跨会话项目记忆", "repo 约定", "错误复盘", "SOP 与测试经验"],
        "memory_methods": ["code_memory", "failure_memory", "procedure_memory", "mcp_persistent_memory"],
        "storage_patterns": ["项目约定", "文件/符号上下文", "失败经验", "MCP 工具记忆"],
        "integration_mode": "mcp_bridge",
        "capabilities": ["ingest", "search", "mcp_tool", "code_context", "failure_learning"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud code/failure/procedure 记忆转成 MCP client 可检索的项目记忆。",
            "retrieve": "按 repo、file path、symbol、test command 和 bug keyword 查询。",
            "export": "把 coding agent 新学到的规则回写到 MemoryCloud code memory。",
        },
        "keywords": ["代码", "codex", "cursor", "claude", "mcp", "repo", "测试", "bug", "agentmemory"],
        "risk_flags": ["new_project_poc_required"],
        "commercial_policy": "Apache-2.0；建议先在真实 repo 跑 PoC，再开放团队默认安装。",
    },
    {
        "id": "cognee",
        "rank": 7,
        "name": "cognee",
        "project": "topoteretes/cognee",
        "repo_url": "https://github.com/topoteretes/cognee",
        "docs_url": "https://www.cognee.ai",
        "license_spdx": "Apache-2.0",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 17656,
        "github_forks_checked": 1865,
        "positioning": "Agent memory control plane，结合 embeddings、graph 和数据管道。",
        "best_for": ["Company Brain", "企业资料摄取", "跨 Agent 共享知识", "GraphRAG 工作流"],
        "memory_methods": ["graph_rag_memory", "vector_semantic_retrieval", "entity_memory", "decision_memory"],
        "storage_patterns": ["数据管道", "向量索引", "图索引", "共享知识控制面"],
        "integration_mode": "graph_rag_pipeline_adapter",
        "capabilities": ["ingest", "search", "graph_query", "pipeline", "shared_knowledge"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud suite/workspace 内容批量送入 cognee 数据管道，保留 workspace、source 和 consent 标签。",
            "retrieve": "用 query 触发向量召回和图路径召回，返回可解释片段。",
            "export": "把图谱事实和决策沉淀回 MemoryCloud entity/decision/project 记忆。",
        },
        "keywords": ["企业", "company brain", "graphrag", "数据管道", "embedding", "cognee", "共享知识"],
        "risk_flags": ["pipeline_operations_required"],
        "commercial_policy": "Apache-2.0；适合企业知识控制面，需配置 LLM、向量库、图数据库和数据治理。",
    },
    {
        "id": "memvid",
        "rank": 8,
        "name": "memvid",
        "project": "memvid/memvid",
        "repo_url": "https://github.com/memvid/memvid",
        "docs_url": "https://www.memvid.com",
        "license_spdx": "Apache-2.0",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 15608,
        "github_forks_checked": 1348,
        "positioning": "Serverless、单文件、可携带的 Agent memory layer。",
        "best_for": ["离线可分发记忆胶囊", "低运维 RAG", "单文件交付", "时间线回溯"],
        "memory_methods": ["portable_capsule_memory", "vector_semantic_retrieval", "append_only_timeline"],
        "storage_patterns": ["单文件索引", "append-only 时间线", "本地优先检索", "可携带资料库"],
        "integration_mode": "portable_capsule_adapter",
        "capabilities": ["ingest", "search", "portable_archive", "offline_retrieval", "timeline"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud suite 或 workspace 片段打包成 memvid 单文件，并写入 suite_id/version 元数据。",
            "retrieve": "本地优先按 query 检索，返回 source offsets 和 generated_at。",
            "export": "把 capsule 变更追加回 MemoryCloud work memory 或发布新版本。",
        },
        "keywords": ["离线", "单文件", "便携", "serverless", "capsule", "timeline", "memvid"],
        "risk_flags": ["large_scale_write_restore_migration_validation_required"],
        "commercial_policy": "Apache-2.0；适合离线分发，生产前验证大规模追加、恢复和迁移。",
    },
    {
        "id": "hindsight",
        "rank": 9,
        "name": "Hindsight",
        "project": "vectorize-io/hindsight",
        "repo_url": "https://github.com/vectorize-io/hindsight",
        "docs_url": "https://hindsight.vectorize.io/",
        "license_spdx": "MIT",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 15558,
        "github_forks_checked": 880,
        "positioning": "Agent Memory That Learns，强调从经验中学习而非只召回聊天记录。",
        "best_for": ["失败经验沉淀", "决策经验复用", "任务后反思", "行为策略学习"],
        "memory_methods": ["failure_memory", "decision_memory", "procedure_memory", "experience_learning_memory"],
        "storage_patterns": ["经验样本", "失败到修复映射", "决策结果", "可复用策略"],
        "integration_mode": "experience_learning_adapter",
        "capabilities": ["ingest", "search", "learn_from_experience", "failure_replay", "policy_hint"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud failure/decision/procedure 记忆映射为经验样本和结果标签。",
            "retrieve": "在相似任务开始前召回失败教训、成功策略和风险提示。",
            "export": "把 Hindsight 学到的经验压缩成 MemoryCloud failure/procedure 记忆。",
        },
        "keywords": ["经验", "失败", "反思", "决策", "learn", "hindsight", "policy"],
        "risk_flags": ["cloud_open_source_boundary_review", "benchmark_reproducibility_review"],
        "commercial_policy": "MIT；适合经验学习层，需核查云服务边界和 benchmark 可复现性。",
    },
    {
        "id": "memori",
        "rank": 10,
        "name": "Memori",
        "project": "MemoriLabs/Memori",
        "repo_url": "https://github.com/MemoriLabs/Memori",
        "docs_url": "https://memorilabs.ai",
        "license_spdx": "NOASSERTION",
        "github_checked_at": "2026-06-03",
        "github_stars_checked": 15168,
        "github_forks_checked": 2538,
        "positioning": "Agent-native memory infrastructure，LLM 和 datastore agnostic。",
        "best_for": ["现有产品快速嵌入后台记忆", "LLM 无关记忆层", "会话转结构化状态", "生产系统持久状态"],
        "memory_methods": ["conversation_memory", "profile_memory", "structured_event_memory", "agent_native_state"],
        "storage_patterns": ["会话状态", "结构化事实", "数据存储无关", "Agent 原生状态"],
        "integration_mode": "llm_agnostic_sdk_adapter",
        "capabilities": ["ingest", "search", "conversation_state", "datastore_agnostic", "llm_agnostic"],
        "adapter_contract": {
            "ingest": "把 MemoryCloud conversation/profile/task 记忆写入 Memori 的持久状态层。",
            "retrieve": "按用户、会话、agent 和业务对象检索结构化状态。",
            "export": "把状态快照回写为 MemoryCloud structured event memory。",
        },
        "keywords": ["会话", "llm agnostic", "datastore", "状态", "产品接入", "memori"],
        "risk_flags": ["license_not_declared_on_github_api", "cloud_data_hosting_review"],
        "commercial_policy": "GitHub API 未声明许可证；商业接入前必须确认许可、云服务和数据托管条款。",
    },
]


def integration_ids() -> list[str]:
    return [item["id"] for item in TOP_MEMORY_INTEGRATIONS]


def get_integration(integration_id: str) -> dict[str, Any] | None:
    normalized = integration_id.strip().lower()
    for item in TOP_MEMORY_INTEGRATIONS:
        if item["id"] == normalized or item["project"].lower() == normalized:
            return dict(item)
    return None


def public_integration(item: dict[str, Any], base_url: str | None = None) -> dict[str, Any]:
    payload = dict(item)
    payload["schema"] = "amp.memory-integration.v1"
    payload["status"] = "local_system_supported"
    payload["install_boundary"] = (
        "MemoryCloud provides a local-first runtime contract and route. The built-in local runtime is immediately usable; "
        "a real upstream project can replace it behind the same 127.0.0.1 route after dependency and license review."
    )
    if base_url:
        base = base_url.rstrip("/")
        payload["amp_endpoints"] = {
            "detail": f"{base}/api/memory/integrations/{item['id']}",
            "install_plan": f"{base}/api/memory/integrations/{item['id']}/install-plan",
            "local_deployment": f"{base}/api/memory/integrations/{item['id']}/local-deployment",
            "route_health": f"{base}/memory-routes/{item['id']}/health",
            "recommend": f"{base}/api/memory/integrations/recommend",
            "skill": f"{base}/api/agent/skills/memory_system_integrator/pull",
        }
    return payload


def list_integrations(
    *,
    q: str | None = None,
    capability: str | None = None,
    memory_method: str | None = None,
    base_url: str | None = None,
) -> list[dict[str, Any]]:
    terms = (q or "").strip().lower()
    capability = (capability or "").strip()
    memory_method = (memory_method or "").strip()
    items: list[dict[str, Any]] = []
    for item in TOP_MEMORY_INTEGRATIONS:
        haystack = " ".join(
            [
                item["id"],
                item["name"],
                item["project"],
                item["positioning"],
                " ".join(item["best_for"]),
                " ".join(item["memory_methods"]),
                " ".join(item["storage_patterns"]),
                " ".join(item["keywords"]),
            ]
        ).lower()
        if terms and terms not in haystack:
            continue
        if capability and capability not in item["capabilities"]:
            continue
        if memory_method and memory_method not in item["memory_methods"]:
            continue
        items.append(public_integration(item, base_url))
    return sorted(items, key=lambda value: int(value["rank"]))


def score_integration(item: dict[str, Any], text: str, requirements: dict[str, Any]) -> tuple[float, list[str]]:
    score = 100 - int(item["rank"])
    reasons: list[str] = []
    text = text.lower()
    for keyword in item["keywords"]:
        if keyword.lower() in text:
            score += 16
            reasons.append(f"命中关键词 {keyword}")
    for method in item["memory_methods"]:
        if method.lower() in text:
            score += 12
            reasons.append(f"匹配记忆方法 {method}")
    for capability in requirements.get("required_capabilities") or []:
        if capability in item["capabilities"]:
            score += 20
            reasons.append(f"满足能力 {capability}")
        else:
            score -= 18
    deployment = str(requirements.get("deployment") or "").lower()
    if deployment in {"closed_source", "commercial_closed_source"} and "agpl_license_review_required" in item["risk_flags"]:
        score -= 45
        reasons.append("闭源商业场景需要 AGPL license review")
    if requirements.get("offline") and "offline_retrieval" in item["capabilities"]:
        score += 36
        reasons.append("满足离线可携带检索")
    if requirements.get("graph") and ("graph_query" in item["capabilities"] or "temporal_reasoning" in item["capabilities"]):
        score += 34
        reasons.append("满足图谱/关系推理")
    if requirements.get("coding_agent") and "code_context" in item["capabilities"]:
        score += 40
        reasons.append("适配编程 Agent 项目记忆")
    if requirements.get("stateful_runtime") and "runtime_state" in item["capabilities"]:
        score += 40
        reasons.append("适配 stateful agent runtime")
    if not reasons:
        reasons.append("按 Top 10 排名和通用记忆能力兜底")
    return score, reasons[:6]


def infer_requirement_flags(text: str, environment: dict[str, Any]) -> dict[str, Any]:
    lower = text.lower()
    flags = dict(environment.get("integration_requirements") or {})
    flags.setdefault("graph", bool(re.search(r"图谱|关系|实体|多跳|graph|temporal|provenance", lower)))
    flags.setdefault("coding_agent", bool(re.search(r"代码|repo|文件|接口|测试|bug|codex|cursor|claude|mcp|github", lower)))
    flags.setdefault("offline", bool(re.search(r"离线|单文件|便携|serverless|offline|capsule|portable", lower)))
    flags.setdefault("stateful_runtime", bool(re.search(r"stateful|runtime|自改进|人格|agent state|memgpt|letta", lower)))
    flags.setdefault("deployment", environment.get("deployment") or environment.get("license_mode") or "")
    return flags


def recommend_integrations(
    *,
    task: str,
    what_i_remember: str = "",
    environment: dict[str, Any] | None = None,
    top_n: int = 3,
    preferred_ids: list[str] | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    environment = environment or {}
    text = " ".join([task, what_i_remember, str(environment)])
    requirements = infer_requirement_flags(text, environment)
    preferred = {item.strip().lower() for item in preferred_ids or environment.get("preferred_integrations") or [] if str(item).strip()}
    scored: list[dict[str, Any]] = []
    for item in TOP_MEMORY_INTEGRATIONS:
        score, reasons = score_integration(item, text, requirements)
        if item["id"] in preferred or item["project"].lower() in preferred:
            score += 50
            reasons.insert(0, "用户或环境显式偏好该系统")
        public = public_integration(item, base_url)
        public["score"] = round(score, 2)
        public["match_reasons"] = reasons
        scored.append(public)
    scored.sort(key=lambda value: (-float(value["score"]), int(value["rank"])))
    selected = scored[0]
    return {
        "schema": RECOMMENDATION_SCHEMA,
        "selected_integration_id": selected["id"],
        "selected": selected,
        "alternatives": scored[1 : max(1, top_n)],
        "requirements": requirements,
        "install_plan": build_install_plan(selected, base_url=base_url),
    }


def build_install_plan(integration: dict[str, Any], base_url: str | None = None) -> dict[str, Any]:
    base = (base_url or "").rstrip("/")
    amp_prefix = base or ""
    integration_id = integration["id"]
    return {
        "schema": "amp.memory-integration-install-plan.v1",
        "integration_id": integration_id,
        "name": integration["name"],
        "repo_url": integration["repo_url"],
        "license_spdx": integration["license_spdx"],
        "risk_flags": integration["risk_flags"],
        "required_amp_skill": "memory_system_integrator",
        "required_scopes": ["skill:install", "memory:read", "memory:write"],
        "phases": [
            {
                "phase": "review",
                "goal": "确认 upstream license、数据驻留、运行时依赖和商业边界。",
                "checks": ["license_spdx", "risk_flags", "repo_url", "docs_url", "deployment boundary"],
            },
            {
                "phase": "map_amp_memory",
                "goal": "把 MemoryCloud 记忆类型映射到目标系统的数据模型。",
                "memory_methods": integration["memory_methods"],
                "adapter_contract": integration["adapter_contract"],
            },
            {
                "phase": "provision_runtime",
                "goal": "本地启动目标系统或 MemoryCloud 内置本地运行时，不把第三方密钥写入公开记忆。",
                "mode": integration["integration_mode"],
                "notes": [
                    "默认使用 MemoryCloud 本地运行时，数据留在本机 SQLite 或本机依赖服务内。",
                    "真实上游项目替换时，仍然绑定 127.0.0.1 并通过 /memory-routes/{integration_id} 暴露。",
                    "AGPL 或未声明许可项目默认隔离为外部服务，不能直接混入闭源核心。",
                ],
            },
            {
                "phase": "connect_amp",
                "goal": "通过 MemoryCloud skill、本地路由和 API 完成写入、检索、导出。",
                "endpoints": [
                    f"{amp_prefix}/api/memory/integrations/{integration_id}" if amp_prefix else f"/api/memory/integrations/{integration_id}",
                    f"{amp_prefix}/api/memory/integrations/{integration_id}/install-plan" if amp_prefix else f"/api/memory/integrations/{integration_id}/install-plan",
                    f"{amp_prefix}/api/memory/integrations/{integration_id}/local-deployment" if amp_prefix else f"/api/memory/integrations/{integration_id}/local-deployment",
                    f"{amp_prefix}/memory-routes/{integration_id}/health" if amp_prefix else f"/memory-routes/{integration_id}/health",
                    f"{amp_prefix}/api/memory/router/select" if amp_prefix else "/api/memory/router/select",
                    f"{amp_prefix}/api/workspaces/{{workspace_id}}/memory/query" if amp_prefix else "/api/workspaces/{workspace_id}/memory/query",
                ],
            },
            {
                "phase": "verify",
                "goal": "写入一条测试记忆，按同一 topic 检索回来，核对 source、confidence、provenance。",
                "success_criteria": ["write ok", "query returns expected memory", "provenance preserved", "no secret in exported context"],
            },
        ],
        "agent_prompt": (
            f"Use {integration['name']} through the local MemoryCloud route after reviewing license and deployment boundary. "
            "Map MemoryCloud memory types to the route contract, keep credentials private, verify retrieval once, then write durable facts back through MemoryCloud."
        ),
    }
