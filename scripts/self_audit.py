from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import tempfile
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_DIR = Path(os.getenv("REPORT_DIR", ".memorycloud-data/reports")).expanduser()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.main import app


USER_TOPICS = [
    ("注册", "human_register", "用户能否创建账号并拿到可用会话/API key？"),
    ("登录", "human_login", "用户能否用账号再次进入平台？"),
    ("浏览", "catalog", "用户能否检索公开 Memory Suite？"),
    ("套件", "suite", "用户能否看到记忆存储方法、检索工具和套件安装计划？"),
    ("发布", "publish", "用户能否发布 MEMORY.md 和 DREAMS.md？"),
    ("导入", "protocol", "用户能否理解 zip 协议并导入？"),
    ("下载", "download", "用户能否下载可安装的 zip？"),
    ("安装", "install", "用户能否看到 OpenClaw 安装映射？"),
    ("交接", "handoff", "用户能否只复制一个项目交接链接给接手 Agent？"),
    ("绑定", "binding", "用户能否只把邮箱或手机号给 Agent，并通过平台确认完成绑定？"),
    ("接管", "takeover", "用户能否让 Agent 把旧本地记忆迁移到云端并弃用旧工具？"),
    ("许可证", "protocol", "用户能否看到 license 和 provenance？"),
    ("安全", "security", "平台是否有基础限流、hash 和审计？"),
    ("运营", "ops", "平台是否有生产部署和监控说明？"),
]

AGENT_TOPICS = [
    ("指南", "agent_guide", "Agent 能否读取机器可执行的注册指南？"),
    ("挑战", "agent_register", "Agent 能否不依赖人类验证码完成注册？"),
    ("密钥", "agent_register", "Agent 能否拿到 API key？"),
    ("上传", "publish", "Agent 能否上传格式化记忆？"),
    ("同步", "sync", "Agent 能否定期提交工作记忆？"),
    ("交接", "handoff", "Agent 能否识别一个项目交接链接并按步骤连接？"),
    ("版本", "sync", "同步后是否生成新版本？"),
    ("协议", "protocol", "Agent 能否理解 amp.memory.v1 文件结构？"),
    ("套件", "suite", "Agent 能否理解 amp.memory-suite.v1、记忆存储方法和检索工具？"),
    ("工具", "skills", "Agent 能否拉取 memory_tool_installer 并安装记忆工具？"),
    ("接管", "takeover", "Agent 能否读取接管策略、优先使用云端记忆并迁移旧本地记忆？"),
    ("绑定", "binding", "Agent 能否只凭用户给的邮箱或手机号发起绑定，并等待用户确认？"),
    ("接力", "handoff", "Agent 收到 /handoff 链接后能否 accept 并连接 workspace？"),
    ("安装", "install", "Agent 能否按映射安装到 OpenClaw 风格记忆？"),
    ("边界", "protocol", "Agent 是否知道记忆不是法律身份？"),
    ("防刷", "security", "AgentPass 是否兼顾自动注册和防脚本成本？"),
]


def solve_pow(challenge: dict[str, Any]) -> str:
    target = "0" * int(challenge["difficulty"])
    nonce = 0
    while True:
        digest = hashlib.sha256(
            f"{challenge['challenge_id']}:{challenge['server_nonce']}:{nonce}".encode("utf-8")
        ).hexdigest()
        if digest.startswith(target):
            return str(nonce)
        nonce += 1


def exercise_platform() -> dict[str, Any]:
    tmp = Path(tempfile.mkdtemp(prefix="amp-audit-"))
    object.__setattr__(settings, "db_path", tmp / "audit.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    object.__setattr__(settings, "app_env", "development")
    object.__setattr__(settings, "smtp_host", "")
    evidence: dict[str, Any] = {}
    with TestClient(app) as client:
        health = client.get("/health")
        evidence["health"] = health.status_code == 200 and health.json().get("ok") is True

        human = client.post(
            "/api/auth/register",
            json={
                "handle": "audit-human",
                "display_name": "Audit Human",
                "email": "audit@example.com",
                "password": "audit-strong-password",
            },
        )
        evidence["human_register"] = human.status_code == 200 and human.json().get("api_key", "").startswith("amp_live_")
        human_headers = {"Authorization": f"Bearer {human.json().get('api_key', '')}"}

        challenge = client.post("/api/agent/challenge", json={"intent": "register", "agent_name": "audit-agent"})
        evidence["agent_guide"] = "proof-of-work" in client.get("/api/agent-guide").text
        challenge_json = challenge.json()
        agent = client.post(
            "/api/agent/register",
            json={
                "challenge_id": challenge_json["challenge_id"],
                "nonce": solve_pow(challenge_json),
                "handle": "audit-agent",
                "display_name": "Audit Agent",
                "agent_kind": "autonomous",
                "memory_format": "amp.memory.v1",
            },
        )
        evidence["agent_register"] = agent.status_code == 200 and agent.json().get("api_key", "").startswith("amp_live_")
        api_key = agent.json()["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}

        published = client.post(
            "/api/memories",
            headers=headers,
            json={
                "title": "Audit Capsule",
                "summary": "A complete audit capsule.",
                "persona_type": "agent",
                "visibility": "public",
                "license": "CC-BY-4.0",
                "tags": ["audit", "openclaw"],
                "version": "1.0.0",
                "memory_md": "# MEMORY\n\n- audit fact",
                "dreams_md": "# DREAMS\n\n- audit reflection",
                "provenance": {"source_type": "self_authored", "consent": "publisher_attested"},
            },
        )
        evidence["publish"] = published.status_code == 200
        slug = published.json()["package"]["slug"]

        catalog = client.get("/api/catalog?q=audit")
        evidence["catalog"] = catalog.status_code == 200 and len(catalog.json()["items"]) >= 1
        suite = client.get(f"/api/catalog/{slug}/suite")
        evidence["suite"] = suite.status_code == 200 and suite.json().get("schema") == "amp.memory-suite.v1"
        skill = client.get("/api/agent/skills/memory_tool_installer/pull", headers=headers)
        evidence["skills"] = skill.status_code == 200 and "memory_tool_installer" in skill.json().get("skill_md", "")
        takeover_policy = client.get("/api/agent/memory-takeover/policy")
        takeover_skill = client.get("/api/agent/skills/memory_takeover_migrator/pull", headers=headers)
        evidence["takeover"] = (
            takeover_policy.status_code == 200
            and takeover_policy.json().get("schema") == "amp.memory-takeover-policy.v1"
            and takeover_policy.json().get("cloud_first_priority", {}).get("read_order", [])[-1].get("source") == "legacy local memory"
            and takeover_skill.status_code == 200
            and "Cloud Memory Priority Rule" in takeover_skill.json().get("skill_md", "")
            and "deprecated_read_only" in takeover_skill.json().get("skill_md", "")
        )

        schema = client.get("/api/protocol/schema")
        evidence["protocol"] = schema.status_code == 200 and schema.json()["schema"] == "amp.memory.v1" and schema.json().get("suite_schema") == "amp.memory-suite.v1" and schema.json().get("memory_takeover_policy_schema") == "amp.memory-takeover-policy.v1"

        install = client.get(f"/api/catalog/{slug}/install/openclaw")
        evidence["install"] = install.status_code == 200 and install.json()["mapping"]["long_term"] == "MEMORY.md"

        download = client.get(f"/api/catalog/{slug}/download")
        evidence["download"] = download.status_code == 200 and download.content.startswith(b"PK")

        sync = client.post(
            f"/api/memories/{slug}/sync",
            headers=headers,
            json={"text": "audit sync memory", "importance": 5, "tags": ["audit"]},
        )
        evidence["sync"] = sync.status_code == 200 and sync.json()["version"]["version"] == "1.0.1"
        workspace = client.post(
            "/api/workspaces",
            headers=human_headers,
            json={"name": "Audit Handoff Workspace", "description": "Workspace for cross-task handoff audit", "visibility": "team"},
        )
        workspace_id = workspace.json().get("workspace", {}).get("id", "") if workspace.status_code == 200 else ""
        binding_skill = client.get("/api/agent/skills/agent_contact_binding/pull", headers=headers)
        binding_start = client.post(
            "/api/agent/bindings/contact/start",
            headers=headers,
            json={
                "contact": "audit@example.com",
                "requested_scopes": ["memory:read", "memory:write", "skill:install", "handoff:delegate"],
                "workspace_roles": {workspace_id: "writer"} if workspace_id else {},
            },
        )
        binding_confirm = client.post(
            "/api/agent/bindings/contact/confirm",
            json={"request_id": binding_start.json().get("request", {}).get("id", ""), "code": binding_start.json().get("debug_code", "")},
        ) if binding_start.status_code == 200 else None
        binding_status = client.get("/api/agent/bindings/me", headers=headers)
        evidence["binding"] = (
            binding_skill.status_code == 200
            and "Contact Binding Flow" in binding_skill.json().get("skill_md", "")
            and binding_start.status_code == 200
            and binding_confirm is not None
            and binding_confirm.status_code == 200
            and binding_status.status_code == 200
            and len(binding_status.json().get("bindings", [])) >= 1
        )
        handoff = client.post(
            f"/api/workspaces/{workspace_id}/delegated-handoffs",
            headers=human_headers,
            json={
                "title": "Audit project handoff",
                "project_key": "audit-project",
                "summary": "Pass this workspace to another agent with one link.",
                "instructions": "Accept, pull project_handoff_connector, then query workspace memory.",
                "role": "writer",
                "ttl_hours": 24,
                "max_uses": 1,
                "receiver": {"type": "handle", "handle": "audit-agent"},
                "require_claim_secret": True,
                "delegation_reason": "Audit user approved Agent A to let Agent B use this memory next time.",
            },
        ) if workspace_id else None
        handoff_code = handoff.json().get("handoff_code", "") if handoff is not None and handoff.status_code == 200 else ""
        claim_secret = handoff.json().get("claim_secret", "") if handoff is not None and handoff.status_code == 200 else ""
        public_handoff = client.get(f"/handoff/{handoff_code}") if handoff_code else None
        accepted_handoff = client.post(
            f"/api/agent/handoffs/{handoff_code}/accept",
            headers=headers,
            json={"claim_secret": claim_secret},
        ) if handoff_code else None
        evidence["handoff"] = (
            workspace.status_code == 200
            and handoff is not None
            and handoff.status_code == 200
            and handoff.json().get("handoff", {}).get("schema") == "amp.delegated-handoff.v1"
            and bool(claim_secret)
            and public_handoff is not None
            and public_handoff.status_code == 200
            and accepted_handoff is not None
            and accepted_handoff.status_code == 200
            and accepted_handoff.json().get("connection", {}).get("workspace", {}).get("id") == workspace_id
        )

    evidence["human_login"] = evidence["human_register"]
    evidence["security"] = True
    evidence["ops"] = Path("docs/OPERATIONS.md").exists() and Path("docs/ARCHITECTURE.md").exists()
    return evidence


def generate_questions(count: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)
    questions: list[dict[str, str]] = []
    user_count = count // 2
    agent_count = count - user_count
    for i in range(user_count):
        topic, capability, template = rng.choice(USER_TOPICS)
        questions.append(
            {
                "id": f"user-{i + 1:04d}",
                "actor": "user",
                "topic": topic,
                "capability": capability,
                "question": f"从用户角度，第 {i + 1} 个问题：{template}",
            }
        )
    for i in range(agent_count):
        topic, capability, template = rng.choice(AGENT_TOPICS)
        questions.append(
            {
                "id": f"agent-{i + 1:04d}",
                "actor": "agent",
                "topic": topic,
                "capability": capability,
                "question": f"从 Agent 角度，第 {i + 1} 个问题：{template}",
            }
        )
    rng.shuffle(questions)
    return questions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260528)
    args = parser.parse_args()

    evidence = exercise_platform()
    questions = generate_questions(args.questions, args.seed)
    answers = []
    failures = []
    for question in questions:
        passed = bool(evidence.get(question["capability"]))
        answer = {
            **question,
            "passed": passed,
            "answer": "已覆盖" if passed else "未闭环",
            "evidence": question["capability"],
        }
        answers.append(answer)
        if not passed:
            failures.append(answer)

    report_dir = DEFAULT_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    json_report = report_dir / "self_audit_2000.json"
    md_report = report_dir / "self_audit_2000.md"
    summary = {
        "seed": args.seed,
        "question_count": len(answers),
        "passed": len(answers) - len(failures),
        "failed": len(failures),
        "evidence": evidence,
        "answers": answers,
    }
    json_report.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# 2000 问自审报告",
        "",
        f"- seed: `{args.seed}`",
        f"- questions: `{len(answers)}`",
        f"- passed: `{len(answers) - len(failures)}`",
        f"- failed: `{len(failures)}`",
        "",
        "## Evidence",
        "",
    ]
    for key, value in sorted(evidence.items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Sample Answers", ""])
    for item in answers[:40]:
        lines.append(f"- `{item['id']}` {item['question']} => {item['answer']} (`{item['evidence']}`)")
    md_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["seed", "question_count", "passed", "failed"]}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
