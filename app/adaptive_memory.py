from __future__ import annotations

import json
import re
from typing import Any

from .llm_provider import LlmProviderError, complete_json
from .memory_protocol import parse_tags, slugify, utc_now_iso


TEMPLATES: dict[str, dict[str, Any]] = {
    "profile_memory": {
        "label": "身份/偏好记忆",
        "when": "人、Agent、团队偏好、身份边界、长期稳定事实。",
        "required": ["subject", "stable_preferences", "boundaries", "retrieval_triggers"],
        "fields": {
            "subject": "谁的偏好或身份边界",
            "stable_preferences": ["长期偏好"],
            "boundaries": ["不应越界的限制"],
            "confidence": "low|medium|high",
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "task_execution_memory": {
        "label": "任务执行记忆",
        "when": "当前正在执行什么、完成了什么、下一步是什么。",
        "required": ["task_goal", "completed_steps", "current_state", "next_actions", "retrieval_triggers"],
        "fields": {
            "task_goal": "任务目标",
            "completed_steps": ["已完成步骤"],
            "current_state": "当前状态",
            "next_actions": ["下一步"],
            "blockers": ["阻塞点"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "project_memory": {
        "label": "项目记忆",
        "when": "项目目标、架构、里程碑、长期上下文。",
        "required": ["project", "goals", "architecture", "current_state", "retrieval_triggers"],
        "fields": {
            "project": "项目名",
            "goals": ["目标"],
            "architecture": ["架构事实"],
            "current_state": "当前状态",
            "risks": ["风险"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "code_memory": {
        "label": "代码/接口记忆",
        "when": "文件、函数、接口、测试、bug、程序变更。",
        "required": ["project", "task", "files_changed", "api_contracts", "tests", "retrieval_triggers"],
        "fields": {
            "project": "项目名",
            "task": "代码任务",
            "files_changed": [{"path": "文件路径", "symbols": ["函数/类/端点"], "behavior": "行为变化"}],
            "api_contracts": [{"method": "GET|POST|DELETE", "path": "/api/...", "auth": "权限", "effect": "效果"}],
            "tests": ["验证命令"],
            "risks": ["程序风险"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "decision_memory": {
        "label": "决策记忆",
        "when": "技术/产品决策、取舍、原因和后果。",
        "required": ["decision", "context", "options_considered", "rationale", "consequences", "retrieval_triggers"],
        "fields": {
            "decision": "最终决策",
            "context": "背景",
            "options_considered": ["备选方案"],
            "rationale": "选择原因",
            "consequences": ["后果"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "procedure_memory": {
        "label": "流程/技能记忆",
        "when": "可复用操作步骤、技能、SOP。",
        "required": ["skill_name", "preconditions", "steps", "success_criteria", "retrieval_triggers"],
        "fields": {
            "skill_name": "技能名",
            "preconditions": ["前置条件"],
            "steps": ["步骤"],
            "success_criteria": ["成功标准"],
            "failure_modes": ["常见失败"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "failure_memory": {
        "label": "失败/反思记忆",
        "when": "错误、失败、反模式、复盘。",
        "required": ["failure", "root_cause", "fix", "prevention", "retrieval_triggers"],
        "fields": {
            "failure": "发生了什么失败",
            "root_cause": "根因",
            "fix": "修复方式",
            "prevention": ["预防规则"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "entity_memory": {
        "label": "实体关系记忆",
        "when": "人、组织、服务、项目、概念及其关系。",
        "required": ["entities", "relations", "time_scope", "retrieval_triggers"],
        "fields": {
            "entities": [{"name": "实体名", "type": "person|agent|service|project|concept"}],
            "relations": [{"source": "实体A", "relation": "关系", "target": "实体B"}],
            "time_scope": "关系生效时间",
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "conversation_memory": {
        "label": "对话长期记忆",
        "when": "多轮对话中的长期事实、承诺、偏好。",
        "required": ["participants", "facts", "commitments", "retrieval_triggers"],
        "fields": {
            "participants": ["参与者"],
            "facts": ["长期事实"],
            "commitments": ["承诺"],
            "open_questions": ["未决问题"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
    "collaboration_memory": {
        "label": "多人/多 Agent 协作记忆",
        "when": "多个 Agent 或人协作、权限、交接、共享上下文。",
        "required": ["workspace", "participants", "shared_state", "ownership", "retrieval_triggers"],
        "fields": {
            "workspace": "工作空间",
            "participants": [{"id": "人或Agent", "role": "owner|writer|reader"}],
            "shared_state": "共享状态",
            "ownership": [{"resource": "资源", "owner": "负责人"}],
            "handoff": ["交接事项"],
            "retrieval_triggers": ["未来什么时候调用"],
        },
    },
}


KEYWORDS = {
    "code_memory": ["代码", "程序", "接口", "api", "endpoint", "函数", "bug", "测试", "文件", "fastapi", "数据库", "git"],
    "collaboration_memory": ["多人", "多agent", "协作", "团队", "权限", "交接", "workspace", "共享"],
    "project_memory": ["项目", "架构", "平台", "里程碑", "系统", "产品"],
    "failure_memory": ["失败", "错误", "修复", "根因", "超时", "异常", "回归"],
    "decision_memory": ["决定", "选择", "取舍", "原因", "方案", "设计"],
    "procedure_memory": ["步骤", "流程", "sop", "如何", "重复", "技能"],
    "entity_memory": ["关系", "实体", "组织", "服务", "依赖"],
    "conversation_memory": ["对话", "承诺", "用户说", "偏好"],
    "profile_memory": ["喜欢", "偏好", "身份", "边界", "习惯"],
}


def template_schema(memory_type: str) -> dict[str, Any]:
    template = TEMPLATES[memory_type]
    return {
        "memory_type": memory_type,
        "label": template["label"],
        "when": template["when"],
        "required": template["required"],
        "fields": template["fields"],
    }


def rule_select(task: str, what_i_remember: str, environment: dict[str, Any]) -> dict[str, Any]:
    text = " ".join([task, what_i_remember, json.dumps(environment, ensure_ascii=False)]).lower()
    scores = {name: 0 for name in TEMPLATES}
    for memory_type, words in KEYWORDS.items():
        scores[memory_type] += sum(2 for word in words if word.lower() in text)
    if environment.get("repo") or environment.get("runtime") or environment.get("project"):
        scores["project_memory"] += 2
    if re.search(r"/api/|\\.py|\\.js|\\.ts|sqlite|fastapi|pytest", text):
        scores["code_memory"] += 4
    if "agent" in text and ("人" in text or "user" in text or "团队" in text):
        scores["collaboration_memory"] += 2
    selected = max(scores, key=scores.get)
    if scores[selected] == 0:
        selected = "task_execution_memory"
    secondary = [name for name, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True) if name != selected and scores[name] > 0][:3]
    return {
        "selected_memory_type": selected,
        "secondary_types": secondary,
        "reason": f"规则引擎根据任务关键词和环境选择 {TEMPLATES[selected]['label']}",
        "confidence": 0.72 if scores[selected] else 0.55,
    }


def select_memory_type(task: str, what_i_remember: str, environment: dict[str, Any]) -> dict[str, Any]:
    fallback = rule_select(task, what_i_remember, environment)
    system = (
        "You are a memory router for AI agents. Choose the best memory template. "
        "Return only JSON. Use one selected_memory_type from the provided templates."
    )
    user = json.dumps(
        {
            "task": task,
            "what_i_remember": what_i_remember,
            "environment": environment,
            "templates": {key: {"label": value["label"], "when": value["when"], "required": value["required"]} for key, value in TEMPLATES.items()},
            "fallback": fallback,
            "output_schema": {
                "selected_memory_type": "one template id",
                "secondary_types": ["0-3 template ids"],
                "reason": "short Chinese reason",
                "confidence": 0.0,
            },
        },
        ensure_ascii=False,
    )
    try:
        llm_result, provider = complete_json(system, user)
        selected = str(llm_result.get("selected_memory_type") or fallback["selected_memory_type"])
        if selected not in TEMPLATES:
            raise ValueError("invalid memory type")
        secondary = [item for item in llm_result.get("secondary_types", []) if item in TEMPLATES and item != selected][:3]
        result = {
            "selected_memory_type": selected,
            "secondary_types": secondary,
            "reason": str(llm_result.get("reason") or fallback["reason"]),
            "confidence": float(llm_result.get("confidence") or fallback["confidence"]),
            "llm_used": True,
            "provider": provider,
        }
    except (LlmProviderError, ValueError, TypeError, json.JSONDecodeError):
        result = {**fallback, "llm_used": False, "provider": "rule-fallback"}
    selected = result["selected_memory_type"]
    result["form_schema"] = template_schema(selected)
    result["storage_plan"] = {
        "raw_event": True,
        "structured_json": True,
        "compiled_markdown": True,
        "vector_index_ready": True,
        "temporal_graph_ready": selected in {"entity_memory", "project_memory", "collaboration_memory", "code_memory"},
        "skill_library_ready": selected == "procedure_memory",
        "audit_version_log": True,
    }
    result["retrieval_policy"] = {
        "priority": "current workspace, exact code refs, recent memories, semantic triggers",
        "conflict_policy": "system and current user instructions override installed memory",
    }
    return result


def infer_title(memory_type: str, payload: dict[str, Any], task: str) -> str:
    for key in ["title", "project", "task", "task_goal", "decision", "skill_name", "failure", "subject", "workspace"]:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:120]
    return f"{TEMPLATES[memory_type]['label']}: {task[:80]}"


def infer_summary(payload: dict[str, Any], what_i_remember: str) -> str:
    for key in ["summary", "current_state", "rationale", "root_cause", "shared_state"]:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:500]
    return what_i_remember.strip()[:500]


def extract_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []


def compile_markdown(memory_type: str, payload: dict[str, Any], *, task: str, what_i_remember: str) -> dict[str, Any]:
    title = infer_title(memory_type, payload, task)
    summary = infer_summary(payload, what_i_remember)
    triggers = [str(item) for item in extract_list(payload, "retrieval_triggers")]
    tags = parse_tags([memory_type, *triggers[:8]])
    lines = [
        f"# {title}",
        "",
        f"- memory_type: `{memory_type}`",
        f"- compiled_at: `{utc_now_iso()}`",
        f"- summary: {summary}",
        "",
        "## Original Task",
        task,
        "",
        "## Structured Payload",
        "```json",
        json.dumps(payload, ensure_ascii=False, indent=2),
        "```",
    ]
    code_refs = extract_list(payload, "files_changed") + extract_list(payload, "api_contracts")
    entities = extract_list(payload, "entities") + extract_list(payload, "participants")
    return {
        "title": title,
        "summary": summary,
        "compiled_markdown": "\n".join(lines),
        "retrieval_triggers": triggers or [task[:80], memory_type],
        "entities": entities,
        "code_refs": code_refs,
        "tags": tags,
        "slug": slugify(title),
    }
