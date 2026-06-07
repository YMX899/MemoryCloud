from __future__ import annotations

import hashlib
import sqlite3
from urllib.parse import quote, urlparse

from fastapi.testclient import TestClient

from app.config import settings
from app.db import check_ready, connect, db, init_db
from app.main import app


CURRENT_RUNTIME_VERSION = "2026.06.07-startup-item-primary.1"


def solve(challenge: dict) -> str:
    nonce = 0
    target = "0" * challenge["difficulty"]
    while True:
        digest = hashlib.sha256(
            f"{challenge['challenge_id']}:{challenge['server_nonce']}:{nonce}".encode()
        ).hexdigest()
        if digest.startswith(target):
            return str(nonce)
        nonce += 1


def register_test_agent(client: TestClient, handle: str = "agent-bot") -> dict:
    challenge_response = client.post("/api/agent/challenge", json={"intent": "register", "agent_name": handle})
    assert challenge_response.status_code == 200, challenge_response.text
    challenge = challenge_response.json()
    register = client.post(
        "/api/agent/register",
        json={
            "challenge_id": challenge["challenge_id"],
            "nonce": solve(challenge),
            "handle": handle,
            "display_name": handle.replace("-", " ").title(),
            "agent_kind": "autonomous",
            "memory_format": "amp.memory.v1",
        },
    )
    assert register.status_code == 200, register.text
    return register.json()


def register_test_human(client: TestClient, *, handle: str, display_name: str = "", email: str):
    object.__setattr__(settings, "smtp_host", "")
    object.__setattr__(settings, "email_dry_run", True)
    email_sent = client.post("/api/email/send", json={"email": email, "purpose": "register"})
    assert email_sent.status_code == 200, email_sent.text
    email_code = email_sent.json()["provider"]["debug_code"]
    email_verified = client.post(
        "/api/email/verify",
        json={"email": email, "code": email_code, "purpose": "register"},
    )
    assert email_verified.status_code == 200, email_verified.text
    register = client.post(
        "/api/auth/register",
        json={
            "handle": handle,
            "email": email,
            "password": "very-strong-password",
            "email_ticket": email_verified.json()["email_ticket"],
        },
    )
    assert register.status_code == 200, register.text
    return register


def test_human_publish_download_sync(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "api.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    object.__setattr__(settings, "smtp_host", "")
    object.__setattr__(settings, "email_dry_run", True)
    with TestClient(app) as client:
        email_sent = client.post("/api/email/send", json={"email": "alice@example.com", "purpose": "register"})
        assert email_sent.status_code == 200, email_sent.text
        email_code = email_sent.json()["provider"]["debug_code"]
        email_verified = client.post(
            "/api/email/verify",
            json={"email": "alice@example.com", "code": email_code, "purpose": "register"},
        )
        assert email_verified.status_code == 200, email_verified.text
        email_ticket = email_verified.json()["email_ticket"]
        created = client.post(
            "/api/auth/register",
            json={
                "handle": "alice",
                "email": "alice@example.com",
                "password": "very-strong-password",
                "email_ticket": email_ticket,
            },
        )
        assert created.status_code == 200, created.text
        assert created.json()["user"]["username"] == "alice"
        assert "display_name" not in created.json()["user"]
        api_key = created.json()["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}

        dry_run = client.post(
            "/api/memories/validate",
            headers=headers,
            json={
                "title": "Alice Memory",
                "summary": "Useful long term preferences",
                "persona_type": "agent",
                "visibility": "public",
                "license": "CC-BY-4.0",
                "tags": ["agent"],
                "version": "1.0.0",
                "memory_md": "# Memory\n\n- prefers concise work",
                "dreams_md": "# Dreams\n\n- review before action",
                "provenance": {"source_type": "self_authored"},
            },
        )
        assert dry_run.status_code == 200, dry_run.text
        assert dry_run.json()["ok"] is True
        assert dry_run.json()["suite_schema"] == "amp.memory-suite.v1"
        assert "suite/manifest.json" in dry_run.json()["files"]

        response = client.post(
            "/api/memories",
            headers=headers,
            json={
                "title": "Alice Memory",
                "summary": "Useful long term preferences",
                "persona_type": "agent",
                "visibility": "public",
                "license": "CC-BY-4.0",
                "tags": ["agent"],
                "version": "1.0.0",
                "memory_md": "# Memory\n\n- prefers concise work",
                "dreams_md": "# Dreams\n\n- review before action",
                "provenance": {"source_type": "self_authored"},
            },
        )
        assert response.status_code == 200, response.text
        slug = response.json()["package"]["slug"]

        catalog = client.get("/api/catalog")
        assert catalog.status_code == 200
        assert any(item["slug"] == slug for item in catalog.json()["items"])
        catalog_item = next(item for item in catalog.json()["items"] if item["slug"] == slug)
        assert catalog_item["suite"]["schema"] == "amp.memory-suite.v1"
        assert "memory_tool_installer" in catalog_item["suite"]["tools"]

        install = client.get(f"/api/catalog/{slug}/install/openclaw")
        assert install.status_code == 200
        assert install.json()["mapping"]["long_term"] == "MEMORY.md"
        assert install.json()["mapping"]["suite_manifest"] == "suite/manifest.json"
        assert install.json()["suite"]["schema"] == "amp.memory-suite.v1"
        assert "risk" in install.json()
        suite = client.get(f"/api/catalog/{slug}/suite")
        assert suite.status_code == 200, suite.text
        assert suite.json()["schema"] == "amp.memory-suite.v1"
        assert suite.json()["ontology"]["kind"] == "memory_ontology"
        assert any(tool["id"] == "memory_tool_installer" for tool in suite.json()["tools"])
        assert suite.json()["tool_install"]["required_first_skill"] == "memory_tool_installer"
        assert suite.json()["memory_install_card"]["schema"] == "amp.open-memory-handoff.v1"
        assert suite.json()["memory_install_card"]["legacy_schema"] == "amp.memory-install.v1"
        assert suite.json()["memory_install_card"]["login_required_for_install"] is True
        assert suite.json()["memory_install_card"]["detail_requires_login"] is False
        assert suite.json()["memory_install_card"]["do_not_web_search"] is True
        assert suite.json()["memory_install_card"]["create_install_link"] == f"/api/catalog/{quote(slug, safe='')}/install-links"
        assert "/agent/memory-install/" in suite.json()["memory_install_card"]["url"]
        agent_install_card = client.get(f"/agent/memory-install/{slug}")
        assert agent_install_card.status_code == 200, agent_install_card.text
        assert "AMP-OPEN-MEMORY-HANDOFF-SETUP-v1" in agent_install_card.text
        assert "Do not web search this package name." in agent_install_card.text
        assert f"/api/catalog/{slug}/install-links" in agent_install_card.text
        assert "/api/agent/open-memory-installs/<install_code>/accept" in agent_install_card.text
        versions = client.get(f"/api/catalog/{slug}/versions")
        assert versions.status_code == 200
        assert versions.json()["items"][0]["version"] == "1.0.0"

        protocol = client.get("/api/protocol/schema")
        assert protocol.status_code == 200
        assert protocol.json()["schema"] == "amp.memory.v1"
        assert protocol.json()["suite_schema"] == "amp.memory-suite.v1"
        assert protocol.json()["delegated_handoff_schema"] == "amp.delegated-handoff.v1"
        assert protocol.json()["memory_takeover_policy_schema"] == "amp.memory-takeover-policy.v1"
        assert protocol.json()["memory_integration_schema"] == "amp.memory-integrations.v1"
        assert "memory_suite" in protocol.json()["concepts"]
        assert "delegated_handoff" in protocol.json()["concepts"]
        assert "memory_ontology" in protocol.json()["concepts"]
        assert "memory_integration" in protocol.json()["concepts"]
        assert "memory_tool" in protocol.json()["concepts"]
        assert "memory_takeover" in protocol.json()["concepts"]
        assert protocol.json()["memory_integrations"]["required_skill"] == "memory_system_integrator"
        assert "agentmemory" in protocol.json()["memory_integrations"]["supported_ids"]
        assert protocol.json()["memory_takeover"]["required_skill"] == "memory_takeover_migrator"

        integrations = client.get("/api/memory/integrations")
        assert integrations.status_code == 200, integrations.text
        assert integrations.json()["schema"] == "amp.memory-integrations.v1"
        assert integrations.json()["count"] == 10
        assert integrations.json()["supported_ids"] == [
            "mem0",
            "graphiti",
            "openviking",
            "supermemory",
            "letta",
            "agentmemory",
            "cognee",
            "memvid",
            "hindsight",
            "memori",
        ]
        assert integrations.json()["items"][0]["id"] == "mem0"
        assert integrations.json()["items"][2]["id"] == "openviking"
        assert "agpl_license_review_required" in integrations.json()["items"][2]["risk_flags"]
        assert integrations.json()["items"][5]["local_deployment"]["public_route_prefix"] == "/memory-routes/agentmemory"

        local_deployments = client.get("/api/memory/local-deployments")
        assert local_deployments.status_code == 200, local_deployments.text
        assert local_deployments.json()["schema"] == "amp.memory-local-deployments.v1"
        assert local_deployments.json()["base_url"] == "http://127.0.0.1:8000"
        assert local_deployments.json()["count"] == 10
        assert local_deployments.json()["public_route_model"]["route_prefix"] == "/memory-routes/{integration_id}"
        assert local_deployments.json()["items"][0]["integration_id"] == "mem0"
        local_routes = client.get("/api/memory/local-deployments/routes")
        assert local_routes.status_code == 200
        assert any(route["integration_id"] == "agentmemory" and route["public_route_url"].endswith("/memory-routes/agentmemory") for route in local_routes.json()["routes"])
        compose = client.get("/api/memory/local-deployments/compose.yml")
        assert compose.status_code == 200
        assert "amp-agentmemory" in compose.text
        assert "127.0.0.1:18115:18115" in compose.text
        env_example = client.get("/api/memory/local-deployments/env.example")
        assert env_example.status_code == 200
        assert "AMP_PUBLIC_BASE_URL=http://127.0.0.1:8000" in env_example.text
        assert "AMP_PUBLIC_BASE_URL=http://127.0.0.1:18085" not in env_example.text
        assert "AMP_ALLOW_AGPL_OPENVIKING=false" in env_example.text

        integration_doc = client.get("/api/memory/integrations/recommend")
        assert integration_doc.status_code == 200
        assert integration_doc.json()["method"] == "POST"
        recommend = client.post(
            "/api/memory/integrations/recommend",
            json={
                "task": "coding agent needs persistent repo memory for tests, bugs and project conventions",
                "what_i_remember": "Codex and Cursor should remember files, pytest failures and API contracts",
                "environment": {"coding_agent": True, "deployment": "commercial_closed_source"},
                "top_n": 3,
            },
        )
        assert recommend.status_code == 200, recommend.text
        assert recommend.json()["schema"] == "amp.memory-integration-recommendation.v1"
        assert recommend.json()["selected_integration_id"] == "agentmemory"
        assert recommend.json()["install_plan"]["required_amp_skill"] == "memory_system_integrator"
        assert recommend.json()["local_deployment"]["public_route_prefix"] == "/memory-routes/agentmemory"
        graph_recommend = client.post(
            "/api/memory/integrations/recommend",
            json={
                "task": "需要记录企业实体关系、事实变化、时间有效性和 provenance",
                "what_i_remember": "组织、服务、项目之间有多跳关系，需要 temporal graph",
                "environment": {"graph": True},
            },
        )
        assert graph_recommend.status_code == 200, graph_recommend.text
        assert graph_recommend.json()["selected_integration_id"] == "graphiti"
        install_plan = client.get("/api/memory/integrations/openviking/install-plan")
        assert install_plan.status_code == 200
        assert install_plan.json()["license_spdx"] == "AGPL-3.0"
        assert "agpl_license_review_required" in install_plan.json()["risk_flags"]
        openviking_local = client.get("/api/memory/integrations/openviking/local-deployment")
        assert openviking_local.status_code == 200
        assert openviking_local.json()["license_gate"] == "agpl_review_required"
        route_health = client.get("/memory-routes/agentmemory/health")
        assert route_health.status_code == 200
        assert route_health.json()["platform_route_reachable"] is True
        assert route_health.json()["deployment_url"].endswith("/api/memory/integrations/agentmemory/local-deployment")

        start = client.get("/agent/start")
        assert start.status_code == 200
        assert "http://127.0.0.1:8000/api/agent/autostart" in start.text
        assert "http://127.0.0.1:18085" not in start.text
        assert "Three Modes" in start.text
        assert "Execute the returned `autonomous_sequence` in order. It is Quick Connect only." in start.text
        assert "startup item" in start.text
        assert "read-only reference" in start.text
        assert "Ask again before writing `.amp/memory-config.json`" in start.text

        autostart = client.get("/api/agent/autostart")
        assert autostart.status_code == 200
        assert autostart.json()["schema"] == "amp.agent-autostart.v1"
        assert autostart.json()["entrypoint"] == "http://127.0.0.1:8000/agent/start"
        assert autostart.json()["entrypoint"].endswith("/agent/start")
        assert autostart.json()["legacy_entrypoint"].endswith("/agent-start")
        assert autostart.json()["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert autostart.json()["mandatory_runtime_notice"]["schema"] == "amp.mandatory-runtime-notice.v1"
        assert autostart.json()["mandatory_runtime_notice"]["legacy_name"] is True
        assert autostart.json()["platform_update_notice"]["schema"] == "amp.platform-update-notice.v1"
        assert autostart.json()["platform_update_notice"]["manifest_url"] == "http://127.0.0.1:8000/api/agent/updates/manifest"
        assert autostart.json()["memory_brief"]["create"].endswith("/api/agent/memory-brief")
        assert autostart.json()["recommended_mode"] == "quick_connect"
        assert autostart.json()["onboarding_modes"]["quick_connect"]["default"] is True
        assert autostart.json()["onboarding_modes"]["startup_setup"]["default"] is False
        assert autostart.json()["onboarding_modes"]["full_import"]["default"] is False
        assert autostart.json()["runtime_replacement_policy"]["requirement"] == "Quick Connect reads MemoryCloud runtime context before task work. Startup item setup is optional and explicit."
        assert autostart.json()["native_runtime_bootstrap"]["install_plan"].endswith("/api/agent/startup-items/install-plan")
        assert "legacy_native_hook_install_plan" not in autostart.json()["native_runtime_bootstrap"]
        assert autostart.json()["native_runtime_bootstrap"]["default_in_quick_connect"] is False
        assert autostart.json()["runtime_connection_notice"]["default_authorization"]["rule"].startswith("The /agent/start link authorizes Quick Connect")
        assert "autonomous_sequence" in autostart.json()
        default_phases = [phase["phase"] for phase in autostart.json()["autonomous_sequence"]]
        assert default_phases == [
            "quick_discover",
            "register_or_reuse_identity",
            "pull_minimal_runtime_skills",
            "read_runtime_context_and_report",
        ]
        assert not any("startup_item" in phase for phase in default_phases)
        assert "enable_memorycloud_startup_item_on_explicit_request" in [
            phase["phase"] for phase in autostart.json()["optional_sequences"]["startup_setup"]
        ]
        assert any(phase.get("legacy_phase") == "add_memorycloud_startup_item_on_first_init" for phase in autostart.json()["optional_sequences"]["startup_setup"])
        assert "inventory_legacy_local_memory_when_present" in [
            phase["phase"] for phase in autostart.json()["optional_sequences"]["full_import"]
        ]
        assert any(phase.get("legacy_phase") == "takeover_legacy_local_memory_when_present" for phase in autostart.json()["optional_sequences"]["full_import"])
        assert "choose_local_memory_system_when_needed" in [
            phase["phase"] for phase in autostart.json()["optional_sequences"]["local_memory_system"]
        ]
        assert "install_marketplace_suite_when_requested" in [
            phase["phase"] for phase in autostart.json()["optional_sequences"]["marketplace_install"]
        ]
        assert autostart.json()["compatibility"]["legacy_full_sequence_field"] == "legacy_full_sequence"
        assert client.get("/agent-start.json").json()["schema"] == "amp.agent-autostart.v1"
        assert client.get("/agent/autostart.json").json()["schema"] == "amp.agent-autostart.v1"
        assert client.get("/agent/start").status_code == 200
        assert client.get("/agent/llms.txt").status_code == 200
        assert client.get("/agent/discovery.json").status_code == 200

        takeover_policy = client.get("/api/agent/memory-takeover/policy")
        assert takeover_policy.status_code == 200
        assert takeover_policy.json()["schema"] == "amp.memory-takeover-policy.v1"
        assert takeover_policy.json()["required_skill"] == "memory_takeover_migrator"
        assert takeover_policy.json()["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert takeover_policy.json()["mandatory_runtime_notice"]["severity"] == "required"
        assert takeover_policy.json()["installation_requirement"]["legacy_runtime_status"] == "deprecated_read_only_after_inventory"
        assert takeover_policy.json()["deprecation_protocol"]["marker"]["status"] == "deprecated_read_only"
        assert "legacy local memory" in takeover_policy.json()["cloud_first_priority"]["rule_id"] or takeover_policy.json()["cloud_first_priority"]["read_order"][-1]["source"] == "legacy local memory"

        discovery = client.get("/.well-known/agent.json")
        assert discovery.status_code == 200
        assert discovery.json()["agent_start"] == "http://127.0.0.1:8000/agent/start"
        assert discovery.json()["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert discovery.json()["mandatory_runtime_notice"]["schema"] == "amp.mandatory-runtime-notice.v1"
        assert discovery.json()["platform_update_notice"]["schema"] == "amp.platform-update-notice.v1"
        assert discovery.json()["agent_start"].endswith("/agent/start")
        assert discovery.json()["legacy_agent_start"].endswith("/agent-start")
        assert discovery.json()["agent_web_view"].endswith("/agent/main")
        assert discovery.json()["agent_doc"].endswith("/agent/doc")
        assert discovery.json()["agent_docs"].endswith("/agent/docs")
        assert discovery.json()["shadow_routes"]["docs"]["agent"].endswith("/agent/docs")
        assert discovery.json()["agent_memory"].endswith("/agent/memory")
        assert discovery.json()["human_memory"].endswith("/human/memory")
        assert discovery.json()["agent_autostart"].endswith("/api/agent/autostart")
        assert discovery.json()["memory_takeover_policy"].endswith("/api/agent/memory-takeover/policy")
        assert discovery.json()["core_actions"]["autostart"].endswith("/api/agent/autostart")
        assert discovery.json()["core_actions"]["memory_takeover_policy"].endswith("/api/agent/memory-takeover/policy")
        assert discovery.json()["core_actions"]["publish"].endswith("/api/memories")
        assert discovery.json()["core_actions"]["suite"].endswith("/api/catalog/{slug}/suite")
        assert discovery.json()["core_actions"]["memory_integrations"].endswith("/api/memory/integrations")
        assert discovery.json()["core_actions"]["memory_integration_recommend"].endswith("/api/memory/integrations/recommend")
        assert discovery.json()["core_actions"]["memory_local_deployments"].endswith("/api/memory/local-deployments")
        assert discovery.json()["core_actions"]["memory_local_fleet_health"].endswith("/api/memory/local-deployments/health")
        assert discovery.json()["core_actions"]["memory_local_route_health"].endswith("/memory-routes/{integration_id}/health")
        assert discovery.json()["core_actions"]["memory_brief"].endswith("/api/agent/memory-brief")
        assert discovery.json()["core_actions"]["method_registry"].endswith("/api/agent/methods")
        assert discovery.json()["core_actions"]["method_query"].endswith("/api/agent/methods/query")
        assert discovery.json()["core_actions"]["memory_graphs"].endswith("/api/workspaces/{workspace_id}/memory-graphs")
        assert discovery.json()["core_actions"]["memory_graph_current_view"].endswith("/api/memory-graphs/{graph_id}/views/current")
        assert discovery.json()["core_actions"]["updates_check"].endswith("/api/agent/updates/check")
        assert discovery.json()["core_actions"]["startup_item_install_plan"].endswith("/api/agent/startup-items/install-plan")

        navigation = client.get("/api/agent/navigation")
        assert navigation.status_code == 200
        assert navigation.json()["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert navigation.json()["mandatory_runtime_notice"]["schema"] == "amp.mandatory-runtime-notice.v1"
        assert navigation.json()["platform_update_notice"]["schema"] == "amp.platform-update-notice.v1"
        assert navigation.json()["recommended_entry"].endswith("/agent/start")
        assert navigation.json()["web_view"].endswith("/agent/main")
        assert navigation.json()["human_return"].endswith("/human/main")
        assert navigation.json()["shadow_routes"]["main"]["human"].endswith("/human/main")
        assert navigation.json()["shadow_routes"]["main"]["agent"].endswith("/agent/main")
        assert navigation.json()["shadow_routes"]["account"]["agent"].endswith("/agent/account")
        assert navigation.json()["shadow_routes"]["memory"]["agent"].endswith("/agent/memory")
        assert navigation.json()["autostart"].endswith("/api/agent/autostart")
        assert "auto_start" in navigation.json()["workflows"]
        assert "register_agent" in navigation.json()["workflows"]
        assert "pull_memory_skill" in navigation.json()["workflows"]
        assert "install_memory_suite" in navigation.json()["workflows"]
        assert "memory_takeover_migration" in navigation.json()["workflows"]
        assert "choose_local_memory_system" in navigation.json()["workflows"]
        assert "memory_brief_runtime" in navigation.json()["workflows"]
        assert "platform_updates" in navigation.json()["workflows"]
        assert "startup_item_bootstrap" in navigation.json()["workflows"]
        assert "method_query" in navigation.json()["workflows"]
        assert "memory_branch_graph" in navigation.json()["workflows"]
        assert navigation.json()["shadow_routes"]["help"]["agent"].endswith("/agent/help")
        assert any(doc["url"].endswith("/agent/memory") for doc in navigation.json()["documents"])
        assert any(doc["url"].endswith("/agent/help") for doc in navigation.json()["documents"])
        assert any(doc["url"].endswith("/api/agent/methods/query") for doc in navigation.json()["documents"])
        assert any(doc["url"].endswith("/api/memory/local-deployments") for doc in navigation.json()["documents"])
        assert any(doc["url"].endswith("/api/memory/local-deployments/health") for doc in navigation.json()["documents"])

        methods = client.get("/api/agent/methods")
        assert methods.status_code == 200
        assert methods.json()["schema"] == "amp.agent-method-registry.v1"
        method_ids = {item["id"] for item in methods.json()["items"]}
        assert {"method.query", "handoff.accept", "memory.brief", "memory.branch.view", "cloudmemory.onboard"}.issubset(method_ids)
        query = client.post(
            "/api/agent/methods/query",
            json={"user_message": "这是交接链接，继续", "task": "accept handoff", "current_route": "/agent/start"},
        )
        assert query.status_code == 200
        assert query.json()["schema"] == "amp.agent-method-query.v1"
        assert query.json()["results"][0]["id"] == "handoff.accept"
        assert "/api/agent/handoffs/{handoff_code}/accept" in query.json()["results"][0]["required_endpoints"]
        assert client.get("/help").status_code == 200
        agent_help = client.get("/agent/help")
        assert agent_help.status_code == 200
        assert "Agent Help" in agent_help.text
        assert "/api/agent/methods/query" in agent_help.text
        help_md = client.get("/agent/help.md")
        assert help_md.status_code == 200
        assert "Method registry" in help_md.text or "Method Query" in help_md.text

        skills = client.get("/api/agent/skills")
        assert skills.status_code == 200
        assert any(item["id"] == "memory_brief_reader" for item in skills.json()["items"])
        assert any(item["id"] == "cloud_workspace_memory" for item in skills.json()["items"])
        assert any(item["id"] == "memory_tool_installer" for item in skills.json()["items"])
        assert any(item["id"] == "memorycloud_startup_item" for item in skills.json()["items"])
        assert any(item["id"] == "memory_takeover_migrator" for item in skills.json()["items"])
        assert any(item["id"] == "memory_system_integrator" for item in skills.json()["items"])
        assert any(item["id"] == "method_query_helper" for item in skills.json()["items"])
        pulled_skill = client.get("/api/agent/skills/cloud_workspace_memory/pull", headers=headers)
        assert pulled_skill.status_code == 200, pulled_skill.text
        assert pulled_skill.json()["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert pulled_skill.json()["mandatory_runtime_notice"]["schema"] == "amp.mandatory-runtime-notice.v1"
        assert "Cloud Workspace Memory Reader" in pulled_skill.json()["skill_md"]
        assert "memorycloud_startup_item" in client.get("/api/agent/skills/memorycloud_startup_item/pull", headers=headers).json()["skill_md"]
        suite_skill = client.get("/api/agent/skills/memory_tool_installer/pull", headers=headers)
        assert suite_skill.status_code == 200, suite_skill.text
        assert "Memory Suite Tool Installer" in suite_skill.json()["skill_md"]
        assert "Memory Suite" in suite_skill.json()["skill_md"]
        takeover_skill = client.get("/api/agent/skills/memory_takeover_migrator/pull", headers=headers)
        assert takeover_skill.status_code == 200, takeover_skill.text
        assert "Legacy Local Memory Inventory Rule" in takeover_skill.json()["skill_md"]
        assert "No Silent Destructive Change Boundary" in takeover_skill.json()["skill_md"]
        assert "deprecated_read_only" in takeover_skill.json()["skill_md"]
        integration_skill = client.get("/api/agent/skills/memory_system_integrator/pull", headers=headers)
        assert integration_skill.status_code == 200, integration_skill.text
        assert "Top 10 Memory System Integrator" in integration_skill.json()["skill_md"]
        assert "/api/memory/integrations/recommend" in integration_skill.json()["skill_md"]
        assert "/api/memory/local-deployments/compose.yml" in integration_skill.json()["skill_md"]
        assert "/api/memory/local-deployments/health" in integration_skill.json()["skill_md"]
        assert "/memory-routes/agentmemory/health" in integration_skill.json()["skill_md"]
        assert "Graphiti" in integration_skill.json()["skill_md"]
        method_skill = client.get("/api/agent/skills/method_query_helper/pull", headers=headers)
        assert method_skill.status_code == 200, method_skill.text
        assert "Method Query Rule" in method_skill.json()["skill_md"]
        assert "/api/agent/methods/query" in method_skill.json()["skill_md"]
        skill_md = client.get("/api/agent/skills/code_memory_context/skill.md", headers=headers)
        assert skill_md.status_code == 200
        assert "Code Memory Context Reader" in skill_md.text

        onboarding = client.get("/api/agent/onboarding")
        assert onboarding.status_code == 200
        assert "/agent/llms.txt" in onboarding.text
        integration_guide = client.get("/memory-integrations")
        assert integration_guide.status_code == 200
        assert "Top 10 记忆系统本地部署" in integration_guide.text
        assert "/api/memory/integrations/recommend" in integration_guide.text

        design_report = client.get("/platform-design-report")
        assert design_report.status_code == 200
        assert "MemoryCloud（记忆云）详细设计报告" in design_report.text
        assert "amp.delegated-handoff.v1" in design_report.text
        assert "amp.memory-takeover-policy.v1" in design_report.text
        takeover_doc = client.get("/memory-takeover")
        assert takeover_doc.status_code == 200
        assert "本地旧记忆只读盘点" in takeover_doc.text

        assert client.get("/terms").status_code == 200
        assert client.get("/privacy").status_code == 200
        assert client.get("/human/terms").status_code == 200
        assert client.get("/human/privacy").status_code == 200
        assert client.get("/human/main").status_code == 200
        assert client.get("/human/publish").status_code == 200
        assert client.get("/human/account").status_code == 200
        assert client.get("/human/team").status_code == 200
        assert client.get("/human/memory").status_code == 200
        assert client.get("/human/docs").status_code == 200
        assert client.get("/human/support").status_code == 200
        assert client.get("/human/protocol").status_code == 200
        human_persona = client.get("/human/persona", follow_redirects=False)
        assert human_persona.status_code == 308
        assert human_persona.headers["location"] == "/human/main#memory-distillation"
        assert client.get("/agent/main").status_code == 200
        assert client.get("/agent/publish").status_code == 200
        assert client.get("/agent/account").status_code == 200
        assert client.get("/agent/team").status_code == 200
        agent_memory = client.get("/agent/memory")
        assert agent_memory.status_code == 200
        assert "Agent Memory Branch Graph" in agent_memory.text
        assert client.get("/agent/memory.md").status_code == 200
        assert client.get("/agent/docs").status_code == 200
        assert client.get("/agent/support").status_code == 200
        assert client.get("/agent/protocol").status_code == 200
        assert client.get("/agent/doc").status_code == 200
        agent_persona = client.get("/agent/persona", follow_redirects=False)
        assert agent_persona.status_code == 308
        assert agent_persona.headers["location"] == "/agent/main"
        persona_md = client.get("/agent/persona.md")
        assert persona_md.status_code == 200
        assert "merged into the MemoryCloud memory system" in persona_md.text
        persona_sources = client.get("/api/persona/sources")
        assert persona_sources.status_code == 200
        assert persona_sources.json()["public_model"] == "merged_into_memory_assets"
        assert persona_sources.json()["human_page"].endswith("/human/main#memory-distillation")
        assert persona_sources.json()["agent_page"].endswith("/agent/main")
        pricing = client.get("/api/pricing")
        assert pricing.status_code == 200
        assert pricing.json()["marketplace_fee_bps"] > 0
        order = client.post(f"/api/orders/checkout", headers=headers, json={"slug": slug})
        assert order.status_code == 200, order.text
        assert order.json()["order"]["status"] == "paid"
        assert client.get("/api/me/orders", headers=headers).json()["items"]
        support = client.post(
            "/api/support/tickets",
            json={"email": "support@example.com", "subject": "Help", "message": "Need help with the platform"},
        )
        assert support.status_code == 200, support.text
        report = client.post(
            "/api/reports",
            json={"slug": slug, "reason": "test", "detail": "Testing report workflow"},
        )
        assert report.status_code == 200, report.text

        with db() as conn:
            conn.execute("UPDATE users SET trust_level=10 WHERE handle='alice'")
        admin = client.get("/api/admin/overview", headers=headers)
        assert admin.status_code == 200, admin.text
        assert admin.json()["counts"]["packages"] >= 1
        assert client.get("/api/admin/orders", headers=headers).status_code == 200
        assert client.get("/api/admin/support", headers=headers).status_code == 200
        assert client.get("/api/admin/reports", headers=headers).status_code == 200

        archive = client.get(f"/api/catalog/{slug}/download")
        assert archive.status_code == 200
        assert archive.content.startswith(b"PK")
        archive_check = client.post(
            "/api/memories/import/validate",
            files={"file": ("alice.zip", archive.content, "application/zip")},
        )
        assert archive_check.status_code == 200, archive_check.text
        assert archive_check.json()["ok"] is True
        assert "suite/manifest.json" in archive_check.json()["files"]

        synced = client.post(
            f"/api/memories/{slug}/sync",
            headers=headers,
            json={"text": "new durable fact", "importance": 4, "tags": ["daily"]},
        )
        assert synced.status_code == 200, synced.text
        assert synced.json()["version"]["version"] == "1.0.1"


def test_open_memory_install_handoff_copy_flow(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "open-install.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    object.__setattr__(settings, "smtp_host", "")
    object.__setattr__(settings, "email_dry_run", True)
    with TestClient(app) as client:
        publisher = register_test_human(client, handle="open-publisher", display_name="Open Publisher", email="open-publisher@example.com")
        publisher_headers = {"Authorization": f"Bearer {publisher.json()['api_key']}"}
        assert publisher.json()["user"]["username"] == "open-publisher"

        created = client.post(
            "/api/memories",
            headers=publisher_headers,
            json={
                "title": "Open Review Memory",
                "summary": "Code review rules for public installation.",
                "persona_type": "method_distill",
                "visibility": "public",
                "license": "CC-BY-4.0",
                "tags": ["open-memory", "review"],
                "version": "1.0.0",
                "memory_md": "# Review Rules\n\n- Check tests before merge\n- Verify source boundary",
                "dreams_md": "# Reflections\n\n- Do not override current instructions",
                "instructions_md": "# Install\n\nUse as review criteria only.",
                "provenance": {"source_type": "self_authored"},
            },
        )
        assert created.status_code == 200, created.text
        slug = created.json()["package"]["slug"]

        public_detail = client.get(f"/api/catalog/{slug}")
        assert public_detail.status_code == 200
        assert public_detail.json()["slug"] == slug
        assert public_detail.json()["install_card_url"].endswith(f"/agent/memory-install/{slug}")
        assert public_detail.json()["install_card"].startswith("AMP-OPEN-MEMORY-HANDOFF-SETUP-v1")
        assert public_detail.json()["source_workspace"]["slug"] == "memorycloud-open-workspace"

        suite = client.get(f"/api/catalog/{slug}/suite")
        assert suite.status_code == 200
        assert suite.json()["memory_install_card"]["source_workspace"]["slug"] == "memorycloud-open-workspace"

        client.post("/api/auth/logout")
        unauth_install = client.post(f"/api/catalog/{slug}/install-links", json={"ttl_hours": 24})
        assert unauth_install.status_code == 401

        install_link = client.post(f"/api/catalog/{slug}/install-links", headers=publisher_headers, json={"ttl_hours": 24})
        assert install_link.status_code == 200, install_link.text
        install_json = install_link.json()
        assert install_json["schema"] == "amp.open-memory-install-link.v1"
        assert "AMP-OPEN-MEMORY-HANDOFF-v1" in install_json["credential"]
        assert install_json["do_not_web_search"] is True
        assert install_json["source_workspace"]["visibility"] == "public"
        install_code = install_json["install_code"]
        publisher_installs = client.get("/api/me/installs", headers=publisher_headers)
        assert publisher_installs.status_code == 200, publisher_installs.text
        assert publisher_installs.json()["pending_links"][0]["source_slug"] == slug
        assert publisher_installs.json()["pending_links"][0]["status"] == "pending_accept"

        install_page = client.get(f"/open-memory-install/{install_code}")
        assert install_page.status_code == 200
        assert "do_not_web_search: true" in install_page.text
        assert "must_accept_via_platform: true" in install_page.text

        descriptor = client.get(f"/api/agent/open-memory-installs/{install_code}")
        assert descriptor.status_code == 200
        descriptor_json = descriptor.json()
        assert descriptor_json["schema"] == "amp.open-memory-handoff.v1"
        assert descriptor_json["source_workspace"]["slug"] == "memorycloud-open-workspace"
        assert descriptor_json["do_not_web_search"] is True
        assert descriptor_json["must_accept_via_platform"] is True
        assert descriptor_json["endpoints"]["descriptor"].endswith(f"/api/agent/open-memory-installs/{install_code}")
        assert descriptor_json["endpoints"]["accept"].endswith(f"/api/agent/open-memory-installs/{install_code}/accept")

        agent = register_test_agent(client, handle="open-install-agent")
        agent_headers = {"Authorization": f"Bearer {agent['api_key']}"}
        accepted = client.post(f"/api/agent/open-memory-installs/{install_code}/accept", headers=agent_headers)
        assert accepted.status_code == 200, accepted.text
        accepted_json = accepted.json()
        assert accepted_json["schema"] == "amp.open-memory-install-result.v1"
        assert accepted_json["do_not_web_search"] is True
        assert accepted_json["copied_slug"] != slug
        assert accepted_json["receipt_id"].startswith("receipt_")
        assert accepted_json["native_memory_id"].startswith("mem_")
        assert accepted_json["native_memory"]["schema"] == "amp.native-installed-memory.v1"
        assert accepted_json["native_memory"]["memory_type"] == "installed_open_memory"
        assert accepted_json["native_memory"]["bootstrap_endpoint"] == "/api/agent/bootstrap/context"
        assert accepted_json["memory_native_activation"]["schema"] == "amp.memory-native-activation.v1"
        assert accepted_json["memory_native_activation"]["mode"] == "native_runtime_bridge"
        assert accepted_json["memory_native_activation"]["authoritative_context_source"] == "runtime_context_pack.summary_markdown"
        assert "create_context_pack" in accepted_json["memory_native_activation"]["reuses_existing_pipeline"]
        assert "Active Installed Memory Lenses" in accepted_json["memory_native_activation"]["reuses_existing_pipeline"]
        assert accepted_json["memory_native_activation"]["must_inject_before_next_answer"] is True
        assert accepted_json["memory_native_activation"]["runtime_context_pack"]["schema"] == "amp.context-pack.v1"
        assert "Active Installed Memory Lenses" in accepted_json["memory_native_activation"]["runtime_context_pack"]["summary_markdown"]
        assert "not a second memory system" in accepted_json["memory_native_activation"]["context_markdown"]
        assert accepted_json["completion_contract"]["do_not_stop_at_install_success"] is True
        assert accepted_json["completion_contract"]["must_inject_before_next_answer"] == "memory_native_activation.runtime_context_pack.summary_markdown"
        assert accepted_json["context_receipt_id"].startswith("amp_receipt_")
        assert accepted_json["retrieval"]["native_detail_endpoint"].endswith("memory_type=installed_open_memory")
        assert accepted_json["retrieval"]["installed_detail_endpoint"].endswith(accepted_json["installed_memory_id"])
        assert accepted_json["snapshot"]["source_workspace_slug"] == "memorycloud-open-workspace"
        assert accepted_json["snapshot"]["native_memory_id"] == accepted_json["native_memory_id"]
        workspace_id = accepted_json["target_workspace_id"]
        my_installs = client.get("/api/me/installs", headers=agent_headers)
        assert my_installs.status_code == 200, my_installs.text
        assert my_installs.json()["items"][0]["source_slug"] == slug
        assert my_installs.json()["items"][0]["copied_slug"] == accepted_json["copied_slug"]
        assert my_installs.json()["items"][0]["receipt_id"] == accepted_json["receipt_id"]
        assert my_installs.json()["items"][0]["target_workspace_id"] == workspace_id

        query = client.get(f"/api/workspaces/{workspace_id}/memory/query?q=Review", headers=agent_headers)
        assert query.status_code == 200, query.text
        native_items = [item for item in query.json()["items"] if item["memory_type"] == "installed_open_memory"]
        assert native_items
        assert native_items[0]["native"] is True
        assert native_items[0]["id"] == accepted_json["native_memory_id"]
        assert native_items[0]["source_slug"] == slug
        assert "Check tests before merge" in query.json()["context"]

        direct_detail = client.get(f"/api/agent/memories/{accepted_json['native_memory_id']}", headers=agent_headers)
        assert direct_detail.status_code == 200, direct_detail.text
        assert direct_detail.json()["memory"]["native"] is True
        installed_detail = client.get(f"/api/agent/installed-open-memories/{accepted_json['installed_memory_id']}", headers=agent_headers)
        assert installed_detail.status_code == 200, installed_detail.text
        assert installed_detail.json()["schema"] == "amp.installed-open-memory-detail.v1"
        assert installed_detail.json()["native_memory_id"] == accepted_json["native_memory_id"]
        assert "Check tests before merge" in installed_detail.json()["compiled_markdown"]

        bootstrap = client.post(
            "/api/agent/bootstrap/context",
            headers=agent_headers,
            json={"workspace_id": workspace_id, "task": "use Review memory", "runtime": "codex", "reason": "agent_startup"},
        )
        assert bootstrap.status_code == 200, bootstrap.text
        assert any(handle["id"] == accepted_json["native_memory_id"] for handle in bootstrap.json()["retrieval_handles"])
        assert "Open Review Memory" in bootstrap.json()["summary_markdown"]
        assert "Active Installed Memory Lenses" in bootstrap.json()["summary_markdown"]
        assert bootstrap.json()["active_installed_memory_lenses"][0]["title"] == "Open Review Memory"

        implicit_brief = client.post(
            "/api/agent/memory-brief",
            headers=agent_headers,
            json={
                "workspace_id": workspace_id,
                "task": "女生今天晚上肚子痛，我怎么回复",
                "current_context": "用户没有重复记忆包名，但刚安装的关系沟通记忆应该作为 native lens 可用。",
                "environment": {"runtime": "codex"},
            },
        )
        assert implicit_brief.status_code == 200, implicit_brief.text
        assert implicit_brief.json()["source_counts"]["active_installed_memory_lenses"] >= 1
        assert "Active Installed Memory Lenses" in implicit_brief.json()["brief_markdown"]
        assert "Open Review Memory" in implicit_brief.json()["brief_markdown"]
        assert "even if the user does not repeat the package name" in implicit_brief.json()["context_pack"]["summary_markdown"]

        with db() as conn:
            conn.execute("DELETE FROM adaptive_memories WHERE id=?", (accepted_json["native_memory_id"],))
            conn.execute("UPDATE installed_memory_packages SET snapshot_json='{}' WHERE id=?", (accepted_json["installed_memory_id"],))

        backfilled_brief = client.post(
            "/api/agent/memory-brief",
            headers=agent_headers,
            json={
                "workspace_id": workspace_id,
                "task": "女生今天晚上肚子痛，我怎么回复",
                "current_context": "历史安装记录缺少 native row，也应该自动 backfill 成 native lens。",
                "environment": {"runtime": "codex"},
            },
        )
        assert backfilled_brief.status_code == 200, backfilled_brief.text
        assert backfilled_brief.json()["source_counts"]["active_installed_memory_lenses"] >= 1
        assert "Open Review Memory" in backfilled_brief.json()["brief_markdown"]
        with db() as conn:
            native_row = conn.execute(
                "SELECT id FROM adaptive_memories WHERE workspace_id=? AND memory_type='installed_open_memory' AND payload_json LIKE ?",
                (workspace_id, f"%{accepted_json['installed_memory_id']}%"),
            ).fetchone()
            assert native_row is not None


def test_readiness_security_auth_and_key_management(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "platform.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    with TestClient(app) as client:
        home = client.get("/")
        assert home.status_code == 200
        assert home.headers["X-Content-Type-Options"] == "nosniff"
        assert home.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'self'" in home.headers["Content-Security-Policy"]

        assert client.head("/").status_code == 200
        assert client.options("/api/auth/register").status_code in {200, 204}
        assert client.get("/ready").json()["ok"] is True
        status = client.get("/api/status")
        assert status.status_code == 200
        assert status.json()["database"]["ok"] is True

        assert client.get("/api/catalog").status_code == 200
        session = client.get("/api/session")
        assert session.status_code == 200
        assert session.json()["authenticated"] is False
        challenge = client.post("/api/agent/challenge", json={"intent": "register", "agent_name": "health-agent"})
        assert challenge.status_code == 200
        assert challenge.json()["challenge_id"]
        support = client.post(
            "/api/support/tickets",
            json={"email": "support@example.com", "subject": "Help", "message": "Need help with the platform"},
        )
        assert support.status_code == 200
        ticket_status = client.get(f"/api/support/tickets/{support.json()['ticket']['id']}")
        assert ticket_status.status_code == 200
        assert ticket_status.json()["ticket"]["status"] == "open"
        report = client.post("/api/reports", json={"reason": "test", "detail": "Testing public report flow"})
        assert report.status_code == 200
        report_status = client.get(f"/api/reports/{report.json()['report']['id']}")
        assert report_status.status_code == 200
        assert report_status.json()["report"]["status"] == "open"

        wrong_login = client.post(
            "/api/auth/login",
            json={"email_or_handle": "missing-user", "password": "wrong-password"},
        )
        assert wrong_login.status_code == 401

        registered = register_test_human(client, handle="cookie-user", display_name="Cookie User", email="cookie-user@example.com")
        cookie = registered.headers.get("set-cookie", "")
        assert registered.json()["user"]["username"] == "cookie-user"
        assert "display_name" not in registered.json()["user"]
        assert "amp_session=" in cookie
        assert "HttpOnly" in cookie
        assert "SameSite=lax" in cookie
        assert client.get("/api/me").status_code == 200
        assert client.get("/api/session").json()["authenticated"] is True

        keys = client.get("/api/me/api-keys")
        assert keys.status_code == 200
        assert len(keys.json()["items"]) >= 1
        created = client.post("/api/me/api-keys", json={"name": "rotation-test"})
        assert created.status_code == 200, created.text
        key_id = created.json()["id"]
        assert created.json()["api_key"].startswith("amp_live_")
        assert "key:manage" in created.json()["scopes"]
        assert "skill:install" in created.json()["scopes"]
        assert "handoff:delegate" in created.json()["scopes"]
        revoked = client.delete(f"/api/me/api-keys/{key_id}")
        assert revoked.status_code == 200
        key_list = client.get("/api/me/api-keys").json()["items"]
        assert any(item["id"] == key_id and item["revoked_at"] for item in key_list)

        restricted = client.post("/api/me/api-keys", json={"name": "read-only", "scopes": ["catalog:read"]})
        assert restricted.status_code == 200, restricted.text
        restricted_headers = {"Authorization": f"Bearer {restricted.json()['api_key']}"}
        restricted_skill = client.get("/api/agent/skills/capsule_installer/pull", headers=restricted_headers)
        assert restricted_skill.status_code == 403
        forbidden = client.post(
            "/api/memories",
            headers=restricted_headers,
            json={
                "title": "Forbidden Memory",
                "summary": "Should fail due to scope.",
                "persona_type": "agent",
                "visibility": "private",
                "license": "CC-BY-4.0",
                "tags": ["scope"],
                "version": "1.0.0",
                "memory_md": "# Forbidden",
                "provenance": {"source_type": "self_authored"},
            },
        )
        assert forbidden.status_code == 403

        duplicate_email_sent = client.post("/api/email/send", json={"email": "duplicate@example.com", "purpose": "register"})
        assert duplicate_email_sent.status_code == 200
        assert duplicate_email_sent.json()["cooldown_seconds"] == 60
        duplicate_email_cooldown = client.post("/api/email/send", json={"email": "duplicate@example.com", "purpose": "register"})
        assert duplicate_email_cooldown.status_code == 429
        assert "please wait" in duplicate_email_cooldown.json()["detail"]

        duplicate_verified = client.post(
            "/api/email/verify",
            json={"email": "duplicate@example.com", "code": duplicate_email_sent.json()["provider"]["debug_code"], "purpose": "register"},
        )
        assert duplicate_verified.status_code == 200
        duplicate_username = client.post(
            "/api/auth/register",
            json={
                "username": "cookie-user",
                "email": "duplicate@example.com",
                "password": "very-strong-password",
                "email_ticket": duplicate_verified.json()["email_ticket"],
            },
        )
        assert duplicate_username.status_code == 409
        assert duplicate_username.json()["detail"] == "username already exists"

        lifecycle = client.post(
            "/api/memories",
            json={
                "title": "Lifecycle Memory",
                "summary": "Archive and delete workflow.",
                "persona_type": "agent",
                "visibility": "public",
                "license": "CC-BY-4.0",
                "tags": ["lifecycle"],
                "version": "1.0.0",
                "memory_md": "# Lifecycle",
                "provenance": {"source_type": "self_authored"},
            },
        )
        assert lifecycle.status_code == 200, lifecycle.text
        lifecycle_slug = lifecycle.json()["package"]["slug"]
        archived = client.post(f"/api/memories/{lifecycle_slug}/archive")
        assert archived.status_code == 200
        assert archived.json()["package"]["status"] == "draft"
        deleted = client.delete(f"/api/memories/{lifecycle_slug}")
        assert deleted.status_code == 200
        assert client.get(f"/api/catalog/{lifecycle_slug}").status_code == 404

        logout = client.post("/api/auth/logout")
        assert logout.status_code == 200
        assert client.get("/api/me").status_code == 401


def test_legacy_database_migration_is_ready(tmp_path):
    db_path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                handle TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                auth_type TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "INSERT INTO users(id, handle, display_name, email, auth_type) VALUES ('usr_legacy', 'legacy', 'Legacy', 'legacy@example.com', 'human')"
        )
    init_db(db_path)
    readiness = check_ready(db_path)
    assert readiness["ok"] is True, readiness
    conn = connect(db_path)
    try:
        user_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        key_columns = {row["name"] for row in conn.execute("PRAGMA table_info(api_keys)").fetchall()}
        binding_request_columns = {row["name"] for row in conn.execute("PRAGMA table_info(agent_binding_requests)").fetchall()}
        binding_columns = {row["name"] for row in conn.execute("PRAGMA table_info(agent_bindings)").fetchall()}
        brief_columns = {row["name"] for row in conn.execute("PRAGMA table_info(memory_briefs)").fetchall()}
        objects = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master").fetchall()}
        assert {"phone", "trust_level", "disabled", "updated_at"} <= user_columns
        assert {"scopes", "expires_at", "last_used_at", "revoked_at"} <= key_columns
        assert {"user_id", "agent_id", "contact_type", "approval_token_hash", "code_hash", "delivery_json"} <= binding_request_columns
        assert {"user_id", "agent_id", "request_id", "scopes_json", "workspace_roles_json", "revoked_at"} <= binding_columns
        binding_sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_bindings'").fetchone()["sql"]
        assert "agent_binding_requests_legacy" not in binding_sql
        assert "REFERENCES agent_binding_requests" in binding_sql
        assert {"workspace_id", "project_key", "brief_json", "brief_markdown", "session_fingerprint"} <= brief_columns
        assert {
            "memory_brief_events",
            "platform_update_acks",
            "sync_intents",
            "project_bindings",
            "native_hook_installs",
            "context_packs",
            "bootstrap_receipts",
            "memory_deltas",
            "summary_cards",
        } <= objects
        conn.execute(
            """
            INSERT INTO agent_binding_requests(
                id, user_id, agent_id, contact_type, contact_value, approval_token_hash, code_hash, expires_at
            )
            VALUES ('abr_legacy_username', 'usr_legacy', 'usr_legacy', 'username', 'legacy', 'token_hash', 'code_hash', '2999-01-01 00:00:00')
            """
        )
    finally:
        conn.close()


def test_legacy_agent_binding_fk_migration(tmp_path):
    db_path = tmp_path / "legacy-binding-fk.sqlite3"
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                handle TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                auth_type TEXT NOT NULL,
                trust_level INTEGER NOT NULL DEFAULT 0,
                disabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE agent_binding_requests (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                contact_type TEXT NOT NULL CHECK(contact_type IN ('email', 'phone', 'username')),
                contact_value TEXT NOT NULL,
                approval_token_hash TEXT NOT NULL UNIQUE,
                code_hash TEXT NOT NULL,
                requested_scopes_json TEXT NOT NULL DEFAULT '[]',
                workspace_roles_json TEXT NOT NULL DEFAULT '{}',
                note TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'expired')),
                delivery_json TEXT NOT NULL DEFAULT '{}',
                expires_at TEXT NOT NULL,
                approved_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE agent_bindings (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                request_id TEXT REFERENCES "agent_binding_requests_legacy"(id) ON DELETE SET NULL,
                agent_handle TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'revoked')),
                scopes_json TEXT NOT NULL DEFAULT '[]',
                workspace_roles_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                revoked_at TEXT
            );
            """
        )
    init_db(db_path)
    conn = connect(db_path)
    try:
        binding_sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_bindings'").fetchone()["sql"]
        assert "agent_binding_requests_legacy" not in binding_sql
        assert "REFERENCES agent_binding_requests" in binding_sql
    finally:
        conn.close()


def test_agent_register_flow(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "agent.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    with TestClient(app) as client:
        challenge_response = client.post("/api/agent/challenge", json={"intent": "register", "agent_name": "bot"})
        assert challenge_response.status_code == 200
        challenge = challenge_response.json()
        register = client.post(
            "/api/agent/register",
            json={
                "challenge_id": challenge["challenge_id"],
                "nonce": solve(challenge),
                "handle": "agent-bot",
                "display_name": "Agent Bot",
                "agent_kind": "autonomous",
                "memory_format": "amp.memory.v1",
            },
        )
        assert register.status_code == 200, register.text
        assert register.json()["api_key"].startswith("amp_live_")
        assert register.json()["platform_update_notice"]["schema"] == "amp.platform-update-notice.v1"
        assert register.json()["next"]["memory_brief"] == "/api/agent/memory-brief"


def test_memory_brief_and_platform_updates_for_agent(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "brief.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    with TestClient(app) as client:
        agent = register_test_agent(client, "brief-agent")
        headers = {"Authorization": f"Bearer {agent['api_key']}"}

        updates_manifest = client.get("/api/agent/updates/manifest")
        assert updates_manifest.status_code == 200, updates_manifest.text
        assert updates_manifest.json()["schema"] == "amp.platform-updates.v1"
        assert updates_manifest.json()["runtime_version"] == CURRENT_RUNTIME_VERSION
        assert updates_manifest.json()["current_components"]["memory_brief_runtime"] == "amp.memory-brief.v1"
        assert updates_manifest.json()["current_components"]["native_runtime_bootstrap"] == "amp.native-runtime.v1"
        assert updates_manifest.json()["current_components"]["startup_item_install_plan"] == "amp.startup-item-install-plan.v1"
        assert "native_hook_install_plan" not in updates_manifest.json()["current_components"]
        assert updates_manifest.json()["legacy_components"]["native_hook_install_plan"] == "amp.native-hook-install-plan.v1"
        assert updates_manifest.json()["current_components"]["context_pack"] == "amp.context-pack.v1"
        assert updates_manifest.json()["current_components"]["bootstrap_receipt"] == "amp.bootstrap-receipt.v1"
        assert updates_manifest.json()["current_components"]["memory_delta"] == "amp.memory-delta.v1"

        updates_check = client.get("/api/agent/updates/check", headers=headers)
        assert updates_check.status_code == 200, updates_check.text
        assert updates_check.json()["schema"] == "amp.platform-update-check.v1"
        assert updates_check.json()["has_pending_updates"] is True
        assert any("memory_brief_reader" in update["requires_repull"] for update in updates_check.json()["pending_updates"])

        skill = client.get("/api/agent/skills/memory_brief_reader/pull", headers=headers)
        assert skill.status_code == 200, skill.text
        assert "Memory Brief Runtime Flow" in skill.json()["skill_md"]
        assert "/api/agent/memory-brief" in skill.json()["skill_md"]

        ack_before_writes = client.post(
            "/api/agent/updates/ack",
            headers=headers,
            json={"update_ids": [update["id"] for update in updates_check.json()["pending_updates"]], "seen_version": updates_manifest.json()["runtime_version"]},
        )
        assert ack_before_writes.status_code == 200, ack_before_writes.text
        assert ack_before_writes.json()["has_pending_updates"] is False

        route = client.post(
            "/api/memory/router/select",
            headers=headers,
            json={
                "task": "continue checkout redesign",
                "what_i_remember": "The project uses Apple-style minimal visual direction and MemoryCloud must be primary runtime.",
                "project_key": "demo-memory-project",
                "environment": {"runtime": "codex", "project": "demo-memory-project"},
            },
        )
        assert route.status_code == 200, route.text
        form_schema = route.json()["form_schema"]
        payload = {}
        for field_id, field_shape in form_schema["fields"].items():
            if isinstance(field_shape, list):
                payload[field_id] = ["Apple-style minimal visual direction"]
            else:
                payload[field_id] = f"{field_shape} for checkout redesign"
        submit = client.post(
            f"/api/memory/forms/{route.json()['run_id']}/submit",
            headers=headers,
            json={"payload": payload, "visibility": "workspace"},
        )
        assert submit.status_code == 200, submit.text

        brief = client.post(
            "/api/agent/memory-brief",
            headers=headers,
            json={
                "task": "continue checkout redesign",
                "project_key": "demo-memory-project",
                "current_context": "Need to continue from prior Apple-style UI and keep MemoryCloud primary.",
                "environment": {"runtime": "codex"},
            },
        )
        assert brief.status_code == 200, brief.text
        brief_json = brief.json()
        assert brief_json["schema"] == "amp.memory-brief.v1"
        assert brief_json["project_key"] == "demo-memory-project"
        assert brief_json["source_counts"]["carry_in"] >= 1
        assert "brief_markdown" in brief_json
        assert "MemoryCloud Memory Brief" in brief_json["brief_markdown"]
        assert "first task memory source" in brief_json["brief_markdown"]

        event = client.post(
            f"/api/agent/memory-briefs/{brief_json['brief_id']}/events",
            headers=headers,
            json={
                "event_type": "decision",
                "summary": "Generated a Memory Brief before task work and used it as private runtime context.",
                "importance": 4,
                "payload": {"files": ["app/main.py", "tests/test_api.py"]},
            },
        )
        assert event.status_code == 200, event.text
        assert event.json()["schema"] == "amp.memory-brief-event.v1"
        assert event.json()["event"]["importance"] == 4

        fetched = client.get(f"/api/agent/memory-briefs/{brief_json['brief_id']}", headers=headers)
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()["events"][0]["event_type"] == "decision"

        final_check = client.get("/api/agent/updates/check", headers=headers)
        assert final_check.status_code == 200, final_check.text
        assert final_check.json()["has_pending_updates"] is False


def test_native_runtime_bootstrap_hook_and_delta_flow(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "native-runtime.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    with TestClient(app) as client:
        agent = register_test_agent(client, "native-agent")
        headers = {"Authorization": f"Bearer {agent['api_key']}"}

        updates = client.get("/api/agent/updates/check", headers=headers)
        assert updates.status_code == 200, updates.text
        assert any(update["id"] == "upd_20260606_native_runtime_bootstrap" for update in updates.json()["pending_updates"])
        assert any(update["id"] == "upd_20260607_startup_item_primary" for update in updates.json()["pending_updates"])

        skill = client.get("/api/agent/skills/memorycloud_startup_item/pull", headers=headers)
        assert skill.status_code == 200, skill.text
        assert "MemoryCloud Startup Item Setup" in skill.json()["skill_md"]
        assert "/api/agent/startup-items/install-plan" in skill.json()["skill_md"]
        assert "/api/agent/bootstrap/context" in skill.json()["skill_md"]
        legacy_skill = client.get("/api/agent/skills/native_hook_installer/pull", headers=headers)
        assert legacy_skill.status_code == 200, legacy_skill.text
        assert "compatibility alias" in legacy_skill.json()["skill_md"]

        profile = client.post(
            "/api/agent/runtime/profile",
            headers=headers,
            json={
                "runtime": "codex",
                "repo_root": "/home/demo-memory-project",
                "git_remote": "https://github.com/example/demo-memory-project.git",
                "supports_files": True,
            },
        )
        assert profile.status_code == 200, profile.text
        assert profile.json()["recommended_startup_item"]["surface"] == "AGENTS.md"
        assert "recommended_hook" not in profile.json()
        assert profile.json()["legacy_aliases"]["recommended_hook"]["surface"] == "AGENTS.md"

        probe = client.post(
            "/api/agent/project/probe",
            headers=headers,
            json={
                "runtime": "codex",
                "project_key": "demo-memory-project",
                "repo_root": "/home/demo-memory-project",
                "git_remote": "https://github.com/example/demo-memory-project.git",
            },
        )
        assert probe.status_code == 200, probe.text
        project_binding_id = probe.json()["project_binding"]["id"]
        workspace_id = probe.json()["workspace"]["id"]
        assert probe.json()["project_binding"]["project_key"] == "demo-memory-project"

        plan = client.post(
            "/api/agent/startup-items/install-plan",
            headers=headers,
            json={"runtime": "codex", "project_binding_id": project_binding_id, "credential_ref": "memorycloud_default"},
        )
        assert plan.status_code == 200, plan.text
        plan_json = plan.json()
        assert plan_json["schema"] == "amp.startup-item-install-plan.v1"
        assert plan_json["legacy_schema"] == "amp.native-hook-install-plan.v1"
        assert plan_json["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert plan_json["memory_config"]["schema"] == "amp.memory-config.v1"
        assert plan_json["memory_config"]["credential_ref"] == "memorycloud_default"
        assert plan_json["memory_config"]["workspace_id"] == workspace_id
        assert plan_json["default_authorization"]["authorized_by"] == "explicit startup_setup request"
        assert "old local memory import" in plan_json["default_authorization"]["requires_extra_user_approval_for"]
        assert "Startup Item" in plan_json["managed_block"]
        assert "AMP MANAGED BLOCK START" in plan_json["managed_block"]
        assert "AGENTS.md" in plan_json["startup_item"]["startup_surface"]
        assert "hook_surface" not in plan_json["startup_item"]
        assert "native_hook" not in plan_json
        assert plan_json["next"]["confirm_body"]["startup_item_id"] == plan_json["startup_item"]["id"]
        assert not any("amp_live_" in str(item) for item in plan_json["install_manifest"]["write_files"])
        legacy_plan = client.post(
            "/api/agent/native-hooks/install-plan",
            headers=headers,
            json={"runtime": "codex", "project_binding_id": project_binding_id, "credential_ref": "memorycloud_default"},
        )
        assert legacy_plan.status_code == 200, legacy_plan.text
        assert legacy_plan.json()["schema"] == "amp.native-hook-install-plan.v1"
        assert legacy_plan.json()["superseded_by"].endswith("/api/agent/startup-items/install-plan")
        assert legacy_plan.json()["native_hook"]["hook_surface"] == "AGENTS.md"

        confirm = client.post(
            "/api/agent/startup-items/confirm",
            headers=headers,
            json={
                "startup_item_id": plan_json["startup_item"]["id"],
                "status": "installed",
                "observed_signature": plan_json["startup_item"]["signature"],
                "installed_paths": [".amp/memory-config.json", "AGENTS.md"],
            },
        )
        assert confirm.status_code == 200, confirm.text
        assert confirm.json()["schema"] == "amp.startup-item-confirm.v1"
        assert confirm.json()["verified"] is True
        assert "native_hook" not in confirm.json()
        assert confirm.json()["legacy_aliases"]["native_hook"]["hook_surface"] == "AGENTS.md"

        context = client.post(
            "/api/agent/bootstrap/context",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "project_key": "demo-memory-project",
                "project_binding_id": project_binding_id,
                "runtime": "codex",
                "task": "agent startup",
                "reason": "agent_startup",
            },
        )
        assert context.status_code == 200, context.text
        context_json = context.json()
        assert context_json["schema"] == "amp.context-pack.v1"
        assert context_json["receipt_id"].startswith("amp_receipt_")
        assert "Runtime Context Pack" in context_json["summary_markdown"]
        assert context_json["receipt"]["schema"] == "amp.bootstrap-receipt.v1"

        no_receipt_delta = client.post(
            "/api/agent/memory-delta",
            headers=headers,
            json={"summary": "This should require bootstrap receipt.", "importance": 2},
        )
        assert no_receipt_delta.status_code == 428
        assert no_receipt_delta.json()["detail"]["schema"] == "amp.bootstrap-required.v1"

        ack = client.post(
            "/api/agent/updates/ack",
            headers=headers,
            # Old clients may still report their last runtime version; the
            # server records each acknowledged update's own version.
            json={"update_ids": [update["id"] for update in updates.json()["pending_updates"]], "seen_version": "2026.06.05-memory-brief.1"},
        )
        assert ack.status_code == 200, ack.text
        assert ack.json()["has_pending_updates"] is False
        assert ack.json()["acked_updates"]["upd_20260606_native_runtime_bootstrap"] == "2026.06.06-native-runtime.1"

        delta = client.post(
            "/api/agent/memory-delta",
            headers={**headers, "X-AMP-Context-Receipt": context_json["receipt_id"]},
            json={
                "workspace_id": workspace_id,
                "project_key": "demo-memory-project",
                "project_binding_id": project_binding_id,
                "delta_type": "decision",
                "summary": "Native runtime context pack is the startup summary.",
                "why_it_matters": "Future agent sessions should inject summary first and query details on demand.",
                "retrieval_triggers": ["startup", "native memory", "bootstrap"],
                "importance": 4,
            },
        )
        assert delta.status_code == 200, delta.text
        assert delta.json()["schema"] == "amp.memory-delta.v1"
        assert delta.json()["delta"]["context_receipt_id"] == context_json["receipt_id"]

        route = client.post(
            "/api/memory/router/select",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "project_key": "demo-memory-project",
                "task": "store native runtime URL encoding regression",
                "what_i_remember": "Runtime Context Pack detail endpoints must be directly requestable even when memory titles contain spaces.",
                "environment": {"runtime": "codex", "project": "demo-memory-project"},
            },
        )
        assert route.status_code == 200, route.text
        form_schema = route.json()["form_schema"]
        payload = {}
        for field_id, field_shape in form_schema["fields"].items():
            if field_id == "task_goal":
                payload[field_id] = "Native runtime detail endpoint URL encoding"
            elif field_id == "current_state":
                payload[field_id] = "Detail endpoint query is generated by server and must be URL encoded."
            elif isinstance(field_shape, list):
                payload[field_id] = ["detail endpoint URL encoding"]
            else:
                payload[field_id] = f"{field_shape} for native runtime detail endpoint"
        submit = client.post(
            f"/api/memory/forms/{route.json()['run_id']}/submit",
            headers=headers,
            json={"payload": payload, "visibility": "workspace"},
        )
        assert submit.status_code == 200, submit.text
        assert " " in submit.json()["memory"]["title"]

        verify = client.post("/api/agent/bootstrap/verify", headers=headers, json={"receipt_id": context_json["receipt_id"], "project_key": "demo-memory-project"})
        assert verify.status_code == 200, verify.text
        assert verify.json()["valid"] is True

        refreshed = client.post(
            "/api/agent/bootstrap/refresh",
            headers=headers,
            json={"workspace_id": workspace_id, "project_key": "demo-memory-project", "project_binding_id": project_binding_id, "runtime": "codex", "reason": "refresh"},
        )
        assert refreshed.status_code == 200, refreshed.text
        assert "Native runtime context pack is the startup summary" in refreshed.json()["summary_markdown"]
        detail_handles = [handle for handle in refreshed.json()["retrieval_handles"] if handle["kind"] == "adaptive_memory"]
        assert detail_handles
        detail_endpoint = detail_handles[0]["detail_endpoint"]
        assert " " not in detail_endpoint
        detail_path = urlparse(detail_endpoint).path + "?" + urlparse(detail_endpoint).query
        detail = client.get(detail_path, headers=headers)
        assert detail.status_code == 200, detail.text
        assert any(item["id"] == submit.json()["memory"]["id"] for item in detail.json()["items"])

        brief = client.post(
            "/api/agent/memory-brief",
            headers=headers,
            json={"task": "legacy brief still works", "workspace_id": workspace_id, "project_key": "demo-memory-project", "environment": {"runtime": "codex"}},
        )
        assert brief.status_code == 200, brief.text
        assert brief.json()["schema"] == "amp.memory-brief.v1"
        assert brief.json()["context_pack"]["schema"] == "amp.context-pack.v1"
        assert brief.json()["receipt_id"].startswith("amp_receipt_")


def test_memory_branch_graph_controls_runtime_context(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "memory-branch.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    with TestClient(app) as client:
        owner = register_test_human(client, handle="branch-owner", display_name="Branch Owner", email="branch-owner@example.com")
        owner_headers = {"Authorization": f"Bearer {owner.json()['api_key']}"}
        agent = register_test_agent(client, "branch-agent")
        agent_headers = {"Authorization": f"Bearer {agent['api_key']}"}

        workspace = client.post(
            "/api/workspaces",
            headers=owner_headers,
            json={"name": "Branch Workspace", "description": "Controls active agent memory branches.", "visibility": "team"},
        )
        assert workspace.status_code == 200, workspace.text
        workspace_id = workspace.json()["workspace"]["id"]
        add_agent = client.post(
            f"/api/workspaces/{workspace_id}/members",
            headers=owner_headers,
            json={"handle": "branch-agent", "role": "writer"},
        )
        assert add_agent.status_code == 200, add_agent.text

        graph = client.post(
            f"/api/workspaces/{workspace_id}/memory-graphs",
            headers=owner_headers,
            json={"project_key": "demo-memory-project", "title": "电商项目记忆分支图", "root_summary": "控制当前 Agent 读取的项目路线。"},
        )
        assert graph.status_code == 200, graph.text
        graph_json = graph.json()
        graph_id = graph_json["graph"]["id"]
        root_id = graph_json["graph"]["root_node_id"]

        decision = client.post(
            f"/api/memory-graphs/{graph_id}/nodes",
            headers=owner_headers,
            json={"parent_id": root_id, "node_type": "decision", "title": "前端技术路线", "summary": "用户需要选择当前实现路线。", "status": "locked"},
        )
        assert decision.status_code == 200, decision.text
        decision_id = decision.json()["node"]["id"]
        react = client.post(
            f"/api/memory-graphs/{graph_id}/nodes",
            headers=owner_headers,
            json={"parent_id": decision_id, "node_type": "branch", "title": "React 路线", "summary": "作为候选路线保留。", "status": "active"},
        )
        assert react.status_code == 200, react.text
        django = client.post(
            f"/api/memory-graphs/{graph_id}/nodes",
            headers=owner_headers,
            json={"parent_id": decision_id, "node_type": "branch", "title": "Django 路线", "summary": "用户最终选择的当前路线。", "status": "muted"},
        )
        assert django.status_code == 200, django.text

        activate = client.post(
            f"/api/memory-graphs/{graph_id}/nodes/{django.json()['node']['id']}/activate",
            headers=owner_headers,
            json={"reason": "用户选择 Django 继续实现"},
        )
        assert activate.status_code == 200, activate.text
        assert react.json()["node"]["id"] in activate.json()["sibling_muted"]
        active_view = activate.json()["active_memory_view"]
        assert "Django 路线" in active_view["active_branches"]
        assert "React 路线" in active_view["muted_branches"]

        detail = client.get(f"/api/memory-graphs/{graph_id}", headers=owner_headers)
        assert detail.status_code == 200, detail.text
        nodes_by_title = {node["title"]: node for node in detail.json()["nodes"]}
        assert nodes_by_title["React 路线"]["status"] == "muted"
        assert nodes_by_title["Django 路线"]["status"] == "active"

        doc_view = client.post(
            f"/api/memory-graphs/{graph_id}/views",
            headers=owner_headers,
            json={"mode": "documentation", "reason": "写项目复盘时读取全部分支"},
        )
        assert doc_view.status_code == 200, doc_view.text
        assert doc_view.json()["view"]["mode"] == "documentation"
        assert "React 路线" in [node["title"] for node in doc_view.json()["active_memory_view"]["active_nodes"]]

        context = client.post(
            "/api/agent/bootstrap/context",
            headers=agent_headers,
            json={"workspace_id": workspace_id, "project_key": "demo-memory-project", "runtime": "codex", "task": "继续开发当前项目"},
        )
        assert context.status_code == 200, context.text
        context_json = context.json()
        assert context_json["active_memory_view"]["graph"]["id"] == graph_id
        assert "Django 路线" in context_json["active_memory_view"]["active_branches"]
        assert "React 路线" in context_json["active_memory_view"]["muted_branches"]
        assert "Django 路线" in context_json["summary_markdown"]
        assert "Active Memory View" in context_json["summary_markdown"]

        query = client.post(
            "/api/agent/methods/query",
            json={"user_message": "我想把原来的树枝暗掉，回到另一个路线继续", "task": "switch memory branch", "current_route": "/agent/memory"},
        )
        assert query.status_code == 200, query.text
        assert query.json()["results"][0]["id"] == "memory.branch.view"


def test_memory_lens_map_and_agent_view(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "memory-lens.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    object.__setattr__(settings, "smtp_host", "")
    object.__setattr__(settings, "email_dry_run", True)
    with TestClient(app) as client:
        owner = register_test_human(client, handle="lens-owner", display_name="Lens Owner", email="lens-owner@example.com")
        owner_headers = {"Authorization": f"Bearer {owner.json()['api_key']}"}
        workspace = client.post(
            "/api/workspaces",
            headers=owner_headers,
            json={"name": "Lens Workspace", "description": "Visual memory assets.", "visibility": "team"},
        )
        assert workspace.status_code == 200, workspace.text
        workspace_id = workspace.json()["workspace"]["id"]

        graph = client.post(
            f"/api/workspaces/{workspace_id}/memory-graphs",
            headers=owner_headers,
            json={"project_key": "memory-lens", "title": "Memory Lens Tree", "root_summary": "Small project memory tree."},
        )
        assert graph.status_code == 200, graph.text
        graph_id = graph.json()["graph"]["id"]
        root_id = graph.json()["graph"]["root_node_id"]
        branch = client.post(
            f"/api/memory-graphs/{graph_id}/nodes",
            headers=owner_headers,
            json={"parent_id": root_id, "node_type": "branch", "title": "小巧记忆树", "summary": "点亮后进入 Agent 上下文。", "status": "active"},
        )
        assert branch.status_code == 200, branch.text

        my_workspaces = client.get("/api/me/workspaces", headers=owner_headers)
        assert my_workspaces.status_code == 200, my_workspaces.text
        assert my_workspaces.json()["items"][0]["owner_username"] == "lens-owner"
        assert my_workspaces.json()["items"][0]["owned_by_current_user"] is True

        memory_map = client.get("/api/me/memory-map", headers=owner_headers)
        assert memory_map.status_code == 200, memory_map.text
        assert memory_map.json()["schema"] == "amp.memory-lens-map.v1"
        assert memory_map.json()["stats"]["workspaces"] == 1
        assert memory_map.json()["stats"]["assets"] >= 2
        assert "primary_assets" in memory_map.json()
        assert "secondary_assets" in memory_map.json()
        assert any(asset["title"] == "小巧记忆树" for asset in memory_map.json()["assets"])
        assert any(node["kind"] == "topic" for node in memory_map.json()["nodes"])

        workspace_map = client.get(f"/api/workspaces/{workspace_id}/memory-map", headers=owner_headers)
        assert workspace_map.status_code == 200, workspace_map.text
        assert workspace_map.json()["workspace_id"] == workspace_id
        assert all(asset["kind"] != "memory_package" for asset in workspace_map.json()["assets"])
        assert "primary_assets" in workspace_map.json()
        assert "secondary_assets" in workspace_map.json()

        agent = register_test_agent(client, "lens-agent")
        agent_headers = {"Authorization": f"Bearer {agent['api_key']}"}
        unbound = client.get(f"/api/agents/{agent['user']['id']}/memory-view", headers=owner_headers)
        assert unbound.status_code == 200, unbound.text
        assert unbound.json()["binding"]["status"] == "unbound"

        started = client.post(
            "/api/agent/bindings/contact/start",
            headers=agent_headers,
            json={"contact": "lens-owner@example.com", "requested_scopes": ["memory:read"], "workspace_roles": {workspace_id: "reader"}},
        )
        assert started.status_code == 200, started.text
        confirmed = client.post(
            "/api/agent/bindings/contact/confirm",
            json={"request_id": started.json()["request"]["id"], "code": started.json()["debug_code"]},
        )
        assert confirmed.status_code == 200, confirmed.text
        view = client.get(f"/api/agents/{agent['user']['id']}/memory-view?workspace_id={workspace_id}", headers=owner_headers)
        assert view.status_code == 200, view.text
        assert view.json()["schema"] == "amp.agent-memory-view.v1"
        assert view.json()["binding"]["status"] == "active"
        assert "summary" in view.json()
        dashboard = client.get(f"/api/agents/{agent['user']['id']}/workspace-dashboard", headers=owner_headers)
        assert dashboard.status_code == 200, dashboard.text
        assert dashboard.json()["schema"] == "amp.agent-workspace-dashboard.v1"
        assert dashboard.json()["dashboard_summary"]["workspace_count"] == 1
        assert dashboard.json()["dashboard_summary"]["project_count"] == 1
        assert dashboard.json()["dashboard_summary"]["tree_node_count"] >= 2
        assert dashboard.json()["workspaces"][0]["id"] == workspace_id
        assert any(node["title"] == "小巧记忆树" for node in dashboard.json()["memory_tree"])


def test_sync_memory_runtime_gate_interrupts_and_resumes(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "sync-gate.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    with TestClient(app) as client:
        agent = register_test_agent(client, "sync-gate-agent")
        headers = {"Authorization": f"Bearer {agent['api_key']}"}

        created = client.post(
            "/api/memories",
            headers=headers,
            json={
                "title": "Sync Gate Memory",
                "summary": "Agent-owned memory for sync gate tests.",
                "persona_type": "agent",
                "visibility": "private",
                "license": "CC-BY-4.0",
                "tags": ["sync"],
                "version": "1.0.0",
                "memory_md": "# Sync Gate\n\n- initial fact",
                "dreams_md": "# Reflection",
                "provenance": {"source_type": "self_authored"},
            },
        )
        assert created.status_code == 200, created.text
        slug = created.json()["package"]["slug"]

        interrupted = client.post(
            f"/api/memories/{slug}/sync",
            headers=headers,
            json={
                "event_type": "decision",
                "text": "Important decision should wait for runtime update.",
                "importance": 5,
                "tags": ["gate"],
            },
        )
        assert interrupted.status_code == 409, interrupted.text
        detail = interrupted.json()["detail"]
        assert detail["schema"] == "amp.sync-interrupt.v1"
        assert detail["status"] == "blocked_for_runtime_update"
        assert detail["sync_intent_id"].startswith("syncint_")
        assert detail["required_updates"]
        sync_intent_id = detail["sync_intent_id"]

        listed = client.get("/api/agent/sync-intents", headers=headers)
        assert listed.status_code == 200, listed.text
        assert listed.json()["items"][0]["id"] == sync_intent_id
        assert listed.json()["items"][0]["status"] == "blocked"

        resume_before_ack = client.post(f"/api/agent/sync-intents/{sync_intent_id}/resume", headers=headers)
        assert resume_before_ack.status_code == 409
        assert resume_before_ack.json()["detail"]["status"] == "blocked_for_runtime_update"

        updates = client.get("/api/agent/updates/check", headers=headers)
        assert updates.status_code == 200, updates.text
        ack = client.post(
            "/api/agent/updates/ack",
            headers=headers,
            json={"update_ids": [update["id"] for update in updates.json()["pending_updates"]], "seen_version": CURRENT_RUNTIME_VERSION},
        )
        assert ack.status_code == 200, ack.text
        assert ack.json()["has_pending_updates"] is False

        resumed = client.post(f"/api/agent/sync-intents/{sync_intent_id}/resume", headers=headers)
        assert resumed.status_code == 200, resumed.text
        assert resumed.json()["schema"] == "amp.sync-intent-resume.v1"
        assert resumed.json()["resumed"] is True
        assert resumed.json()["sync_intent"]["status"] == "resumed"
        assert resumed.json()["result"]["sync_event"]["text"] == "Important decision should wait for runtime update."

        second_agent = register_test_agent(client, "sync-low-agent")
        second_headers = {"Authorization": f"Bearer {second_agent['api_key']}"}
        second_memory = client.post(
            "/api/memories",
            headers=second_headers,
            json={
                "title": "Low Importance Memory",
                "summary": "Agent-owned memory for low importance sync.",
                "persona_type": "agent",
                "visibility": "private",
                "license": "CC-BY-4.0",
                "tags": ["sync"],
                "version": "1.0.0",
                "memory_md": "# Low Importance\n\n- initial fact",
                "provenance": {"source_type": "self_authored"},
            },
        )
        assert second_memory.status_code == 200, second_memory.text
        low_sync = client.post(
            f"/api/memories/{second_memory.json()['package']['slug']}/sync",
            headers=second_headers,
            json={"event_type": "note", "text": "Low importance note can sync with update warning.", "importance": 2},
        )
        assert low_sync.status_code == 200, low_sync.text
        assert low_sync.json()["update_notice"]["status"] == "recommended_update_available"
        assert low_sync.json()["update_notice"]["required_updates"] == []
        assert low_sync.json()["update_notice"]["recommended_updates"]


def test_agent_contact_binding_by_email(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "binding.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    object.__setattr__(settings, "app_env", "development")
    object.__setattr__(settings, "smtp_host", "")
    with TestClient(app) as client:
        human = register_test_human(client, handle="binding-owner", display_name="Binding Owner", email="binding-owner@example.com")
        human_headers = {"Authorization": f"Bearer {human.json()['api_key']}"}
        workspace = client.post(
            "/api/workspaces",
            headers=human_headers,
            json={"name": "Binding Workspace", "description": "Owner controlled memory", "visibility": "team"},
        )
        assert workspace.status_code == 200, workspace.text
        workspace_id = workspace.json()["workspace"]["id"]

        agent = register_test_agent(client, "binding-agent")
        agent_headers = {"Authorization": f"Bearer {agent['api_key']}"}

        skill = client.get("/api/agent/skills/agent_contact_binding/pull", headers=agent_headers)
        assert skill.status_code == 200, skill.text
        assert "User Binding Flow" in skill.json()["skill_md"]
        assert "/api/agent/bindings/username/start" in skill.json()["skill_md"]
        assert "/api/agent/bindings/contact/start" in skill.json()["skill_md"]

        unknown = client.post(
            "/api/agent/bindings/contact/start",
            headers=agent_headers,
            json={"contact": "missing@example.com"},
        )
        assert unknown.status_code == 404

        unsafe_scope = client.post(
            "/api/agent/bindings/contact/start",
            headers=agent_headers,
            json={"contact": "binding-owner@example.com", "requested_scopes": ["key:manage"]},
        )
        assert unsafe_scope.status_code == 400

        started = client.post(
            "/api/agent/bindings/contact/start",
            headers=agent_headers,
            json={
                "contact": "binding-owner@example.com",
                "requested_scopes": ["memory:read", "memory:write", "skill:install", "handoff:delegate"],
                "workspace_roles": {workspace_id: "writer"},
                "note": "User asked me to bind by email.",
            },
        )
        assert started.status_code == 200, started.text
        started_json = started.json()
        assert started_json["schema"] == "amp.agent-binding-request.v1"
        assert started_json["request"]["status"] == "pending"
        assert started_json["request"]["contact_masked"].endswith("@example.com")
        assert started_json["delivery"]["dry_run"] is True
        assert started_json["debug_code"]
        assert started_json["approval_token"].startswith("amp_bind_")
        assert started_json["approval_url"].endswith(started_json["approval_token"])

        wrong_code = client.post(
            "/api/agent/bindings/contact/confirm",
            json={"request_id": started_json["request"]["id"], "code": "000000"},
        )
        assert wrong_code.status_code == 400

        status_before = client.get("/api/agent/bindings/me", headers=agent_headers)
        assert status_before.status_code == 200, status_before.text
        assert len(status_before.json()["pending_requests"]) == 1

        confirmed = client.post(
            "/api/agent/bindings/contact/confirm",
            json={"request_id": started_json["request"]["id"], "code": started_json["debug_code"]},
        )
        assert confirmed.status_code == 200, confirmed.text
        confirmed_json = confirmed.json()
        assert confirmed_json["schema"] == "amp.agent-binding.v1"
        assert confirmed_json["approved"] is True
        assert confirmed_json["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert confirmed_json["mandatory_runtime_notice"]["schema"] == "amp.mandatory-runtime-notice.v1"
        assert confirmed_json["runtime_connection_notice"]["installation_requirement"]["connection_mode"] == "memorycloud_quick_connect"
        assert confirmed_json["mandatory_runtime_notice"]["installation_requirement"]["replacement_mode"] == "memorycloud_first_task_context"
        assert confirmed_json["mandatory_runtime_notice"]["installation_requirement"]["legacy_replacement_mode"] == "cloudmemory_primary_runtime"
        assert confirmed_json["runtime_connection_notice"]["default_authorization"]["rule"].startswith("The /agent/start link authorizes Quick Connect")
        assert "write .amp/memory-config.json or any repository startup/config file" in confirmed_json["runtime_connection_notice"]["default_authorization"]["requires_explicit_user_approval"]
        assert "import old local memory content into MemoryCloud" in confirmed_json["runtime_connection_notice"]["default_authorization"]["requires_explicit_user_approval"]
        binding_id = confirmed_json["binding"]["id"]
        assert confirmed_json["binding"]["workspace_roles"] == {workspace_id: "writer"}

        duplicate = client.post(
            "/api/agent/bindings/contact/confirm",
            json={"approval_token": started_json["approval_token"]},
        )
        assert duplicate.status_code == 409

        agent_bindings = client.get("/api/agent/bindings/me", headers=agent_headers)
        assert agent_bindings.status_code == 200, agent_bindings.text
        assert agent_bindings.json()["known_agent_message"].startswith("You are a known MemoryCloud agent")
        assert agent_bindings.json()["runtime_connection_notice"]["severity"] == "required"
        assert agent_bindings.json()["mandatory_runtime_notice"]["severity"] == "required"
        assert agent_bindings.json()["bindings"][0]["id"] == binding_id
        assert agent_bindings.json()["pending_requests"] == []

        agent_me = client.get("/api/me", headers=agent_headers)
        assert agent_me.status_code == 200, agent_me.text
        assert agent_me.json()["runtime_connection_notice"]["schema"] == "amp.runtime-connection-notice.v1"
        assert agent_me.json()["mandatory_runtime_notice"]["schema"] == "amp.mandatory-runtime-notice.v1"
        agent_session = client.get("/api/session", headers=agent_headers)
        assert agent_session.status_code == 200, agent_session.text
        assert agent_session.json()["runtime_connection_notice"]["installation_requirement"]["legacy_runtime_status"] == "available_read_only_reference"
        assert agent_session.json()["runtime_connection_notice"]["startup_item_plan_url"].endswith("/api/agent/startup-items/install-plan")

        human_bindings = client.get("/api/me/agent-bindings", headers=human_headers)
        assert human_bindings.status_code == 200, human_bindings.text
        assert human_bindings.json()["bindings"][0]["id"] == binding_id
        assert human_bindings.json()["requests"][0]["status"] == "approved"

        query_as_agent = client.get(
            f"/api/workspaces/{workspace_id}/memory/query?q=binding",
            headers=agent_headers,
        )
        assert query_as_agent.status_code == 200, query_as_agent.text

        revoked = client.delete(f"/api/me/agent-bindings/{binding_id}", headers=human_headers)
        assert revoked.status_code == 200, revoked.text
        assert revoked.json()["binding"]["status"] == "revoked"

        query_after_revoke = client.get(
            f"/api/workspaces/{workspace_id}/memory/query?q=binding",
            headers=agent_headers,
        )
        assert query_after_revoke.status_code == 403


def test_agent_username_binding_fast_path_and_method_query(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "username-binding.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    object.__setattr__(settings, "app_env", "development")
    object.__setattr__(settings, "smtp_host", "")
    object.__setattr__(settings, "email_dry_run", True)
    with TestClient(app) as client:
        human = register_test_human(client, handle="alice", display_name="Digmoney", email="alice@example.com")
        human_headers = {"Authorization": f"Bearer {human.json()['api_key']}"}
        workspace = client.post(
            "/api/workspaces",
            headers=human_headers,
            json={"name": "Digmoney Workspace", "description": "Owner controlled memory", "visibility": "team"},
        )
        assert workspace.status_code == 200, workspace.text
        workspace_id = workspace.json()["workspace"]["id"]

        agent = register_test_agent(client, "username-binding-agent")
        agent_headers = {"Authorization": f"Bearer {agent['api_key']}"}

        query = client.post(
            "/api/agent/methods/query",
            json={"user_message": "绑定alice这个号", "task": "bind account", "agent_handle": "codex"},
        )
        assert query.status_code == 200, query.text
        assert query.json()["results"][0]["id"] == "account.bind"
        assert "/api/agent/bindings/username/start" in query.json()["results"][0]["required_endpoint_urls"][0]

        skill = client.get("/api/agent/skills/agent_contact_binding/pull", headers=agent_headers)
        assert skill.status_code == 200, skill.text
        assert "/api/agent/bindings/username/start" in skill.json()["skill_md"]
        assert "alice" in skill.json()["skill_md"]

        contact_misroute = client.post(
            "/api/agent/bindings/contact/start",
            headers=agent_headers,
            json={"contact": "alice"},
        )
        assert contact_misroute.status_code == 400
        assert "/api/agent/bindings/username/start" in contact_misroute.json()["detail"]

        admin_role = client.post(
            "/api/agent/bindings/username/start",
            headers=agent_headers,
            json={"username": "alice", "requested_scopes": ["memory:read"], "workspace_roles": {workspace_id: "admin"}},
        )
        assert admin_role.status_code == 400
        assert "reader or writer" in admin_role.json()["detail"]
        assert "admin" in admin_role.json()["detail"]

        started = client.post(
            "/api/agent/bindings/username/start",
            headers=agent_headers,
            json={
                "username": "alice",
                "requested_scopes": ["memory:read", "memory:write", "skill:install"],
                "workspace_roles": {workspace_id: "writer"},
                "note": "User asked me to bind alice.",
            },
        )
        assert started.status_code == 200, started.text
        started_json = started.json()
        assert started_json["status"] == "pending_user_confirmation"
        assert started_json["request"]["contact_type"] == "username"
        assert started_json["request"]["contact_masked"] == "@alice"
        assert started_json["human_approval_url"].endswith(started_json["approval_token"])

        confirmed = client.post(
            "/api/agent/bindings/contact/confirm",
            json={"approval_token": started_json["approval_token"]},
        )
        assert confirmed.status_code == 200, confirmed.text
        assert confirmed.json()["binding"]["workspace_roles"] == {workspace_id: "writer"}

        agent_bindings = client.get("/api/agent/bindings/me", headers=agent_headers)
        assert agent_bindings.status_code == 200, agent_bindings.text
        assert agent_bindings.json()["bindings"][0]["owner"]["username"] == "alice"

        query_as_agent = client.get(
            f"/api/workspaces/{workspace_id}/memory/query?q=binding",
            headers=agent_headers,
        )
        assert query_as_agent.status_code == 200, query_as_agent.text


def test_adaptive_memory_router_workspace_and_code_context(tmp_path):
    object.__setattr__(settings, "db_path", tmp_path / "adaptive.sqlite3")
    object.__setattr__(settings, "storage_dir", tmp_path / "archives")
    object.__setattr__(settings, "pow_difficulty", 3)
    object.__setattr__(settings, "llm_provider_config", tmp_path / "missing-llm.json")
    with TestClient(app) as client:
        owner = register_test_human(client, handle="owner-human", display_name="Owner Human", email="owner@example.com")
        owner_headers = {"Authorization": f"Bearer {owner.json()['api_key']}"}
        writer = register_test_human(client, handle="writer-agent", display_name="Writer Agent", email="writer@example.com")
        writer_headers = {"Authorization": f"Bearer {writer.json()['api_key']}"}

        templates = client.get("/api/memory/templates")
        assert templates.status_code == 200
        assert "code_memory" in templates.json()["items"]

        workspace = client.post(
            "/api/workspaces",
            headers=owner_headers,
            json={"name": "Adaptive Workspace", "description": "Multi-agent code memory", "visibility": "team"},
        )
        assert workspace.status_code == 200, workspace.text
        workspace_id = workspace.json()["workspace"]["id"]
        member = client.post(
            f"/api/workspaces/{workspace_id}/members",
            headers=owner_headers,
            json={"handle": "writer-agent", "role": "writer"},
        )
        assert member.status_code == 200, member.text

        routed = client.post(
            "/api/memory/router/select",
            headers=writer_headers,
            json={
                "workspace_id": workspace_id,
                "project_key": "demo-memory-project",
                "task": "我正在修复 FastAPI 项目的 API Key scope、数据库迁移和接口测试",
                "what_i_remember": "涉及 app/main.py、app/db.py、pytest、/api/memory/router/select 和多 Agent workspace 调用",
                "environment": {"project": "demo-memory-project", "repo": "/home/demo-memory-project", "runtime": "FastAPI + SQLite"},
            },
        )
        assert routed.status_code == 200, routed.text
        assert routed.json()["selected_memory_type"] == "code_memory"
        assert routed.json()["integration_recommendation"]["selected_integration_id"] == "agentmemory"
        assert routed.json()["integration_recommendation"]["install_plan"]["required_amp_skill"] == "memory_system_integrator"
        assert routed.json()["integration_recommendation"]["local_deployment"]["public_route_prefix"] == "/memory-routes/agentmemory"
        run_id = routed.json()["run_id"]

        form = client.get(f"/api/memory/forms/{run_id}", headers=writer_headers)
        assert form.status_code == 200
        assert form.json()["form_schema"]["memory_type"] == "code_memory"

        submitted = client.post(
            f"/api/memory/forms/{run_id}/submit",
            headers=writer_headers,
            json={
                "visibility": "workspace",
                "payload": {
                    "project": "demo-memory-project",
                    "task": "实现自适应记忆路由",
                    "files_changed": [
                        {"path": "app/main.py", "symbols": ["route_memory", "submit_memory_form"], "behavior": "新增路由和提交接口"}
                    ],
                    "api_contracts": [
                        {"method": "POST", "path": "/api/memory/router/select", "auth": "memory:write", "effect": "选择最佳记忆模板"}
                    ],
                    "tests": ["pytest -q"],
                    "risks": ["LLM 不可用时必须规则兜底"],
                    "retrieval_triggers": ["adaptive memory", "code memory", "FastAPI route"],
                },
            },
        )
        assert submitted.status_code == 200, submitted.text
        memory_id = submitted.json()["memory"]["id"]
        assert "app/main.py" in submitted.json()["memory"]["compiled_markdown"]

        query = client.get(
            f"/api/workspaces/{workspace_id}/memory/query?q=FastAPI&memory_type=code_memory",
            headers=owner_headers,
        )
        assert query.status_code == 200, query.text
        assert any(item["id"] == memory_id for item in query.json()["items"])
        assert "Inject only relevant memories" in query.json()["call_instructions"]

        code_context = client.get("/api/projects/demo-memory-project/code-memory/context?q=route", headers=owner_headers)
        assert code_context.status_code == 200, code_context.text
        assert "route_memory" in code_context.json()["context"]

        handoff = client.post(
            f"/api/workspaces/{workspace_id}/handoffs",
            headers=owner_headers,
            json={
                "title": "Adaptive Workspace takeover",
                "project_key": "demo-memory-project",
                "summary": "Take over the adaptive memory implementation.",
                "instructions": "Read code memory before editing app/main.py.",
                "role": "writer",
                "ttl_hours": 24,
                "max_uses": 1,
            },
        )
        assert handoff.status_code == 200, handoff.text
        handoff_code = handoff.json()["handoff_code"]
        assert "/handoff/" in handoff.json()["handoff_url"]
        assert handoff.json()["handoff"]["schema"] == "amp.project-handoff.v1"
        assert "project_handoff_connector" in handoff.json()["handoff"]["skills_to_pull"]
        assert handoff.json()["handoff"]["grant"]["max_uses"] == 1

        limited_key = client.post(
            "/api/me/api-keys",
            headers=owner_headers,
            json={"name": "handoff-read-only", "scopes": ["memory:read"]},
        )
        assert limited_key.status_code == 200, limited_key.text
        limited_headers = {"Authorization": f"Bearer {limited_key.json()['api_key']}"}
        limit_without_scope = client.post(
            f"/api/workspaces/{workspace_id}/handoffs/limit",
            headers=limited_headers,
            json={"handoff_code": handoff_code, "max_uses": 2, "reason": "same link for two agents"},
        )
        assert limit_without_scope.status_code == 403

        limit_update = client.post(
            f"/api/workspaces/{workspace_id}/handoffs/limit",
            headers=owner_headers,
            json={"handoff_code": handoff_code, "max_uses": 2, "reason": "same link for two agents"},
        )
        assert limit_update.status_code == 200, limit_update.text
        limit_json = limit_update.json()
        assert limit_json["schema"] == "amp.project-handoff-limit-update.v1"
        assert limit_json["old_max_uses"] == 1
        assert limit_json["new_max_uses"] == 2
        assert limit_json["handoff"]["id"] == handoff.json()["handoff"]["id"]
        assert limit_json["handoff"]["grant"]["max_uses"] == 2
        assert limit_json["handoff"]["grant"]["use_count"] == 0
        assert limit_json["handoff_url"] == handoff.json()["handoff_url"]

        public_handoff = client.get(f"/handoff/{handoff_code}")
        assert public_handoff.status_code == 200
        assert "Agent Project Handoff" in public_handoff.text
        handoff_descriptor = client.get(f"/api/agent/handoffs/{handoff_code}")
        assert handoff_descriptor.status_code == 200
        assert handoff_descriptor.json()["project_key"] == "demo-memory-project"

        receiver = register_test_human(client, handle="receiver-agent", display_name="Receiver Agent", email="receiver@example.com")
        receiver_headers = {"Authorization": f"Bearer {receiver.json()['api_key']}"}
        accepted = client.post(f"/api/agent/handoffs/{handoff_code}/accept", headers=receiver_headers)
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["accepted"] is True
        assert accepted.json()["connection"]["workspace"]["id"] == workspace_id
        assert "workspace_query" in accepted.json()["connection"]["endpoints"]
        receiver_query = client.get(
            f"/api/workspaces/{workspace_id}/memory/query?q=FastAPI&memory_type=code_memory",
            headers=receiver_headers,
        )
        assert receiver_query.status_code == 200, receiver_query.text
        assert any(item["id"] == memory_id for item in receiver_query.json()["items"])

        too_low = client.post(
            f"/api/workspaces/{workspace_id}/handoffs/limit",
            headers=owner_headers,
            json={"handoff_code": handoff_code, "max_uses": 0, "reason": "invalid lower than current use count"},
        )
        assert too_low.status_code == 422
        second_receiver = register_test_human(client, handle="second-receiver", display_name="Second Receiver", email="second-receiver@example.com")
        second_receiver_headers = {"Authorization": f"Bearer {second_receiver.json()['api_key']}"}
        second_accepted = client.post(f"/api/agent/handoffs/{handoff_code}/accept", headers=second_receiver_headers)
        assert second_accepted.status_code == 200, second_accepted.text
        assert second_accepted.json()["connection"]["grant"]["use_count"] == 2
        third_receiver = register_test_human(client, handle="third-receiver", display_name="Third Receiver", email="third-receiver@example.com")
        third_headers = {"Authorization": f"Bearer {third_receiver.json()['api_key']}"}
        third_accept = client.post(f"/api/agent/handoffs/{handoff_code}/accept", headers=third_headers)
        assert third_accept.status_code == 410
        below_use_count = client.post(
            f"/api/workspaces/{workspace_id}/handoffs/limit",
            headers=owner_headers,
            json={"handoff_code": handoff_code, "max_uses": 1, "reason": "cannot go below two accepted agents"},
        )
        assert below_use_count.status_code == 400

        delegated = client.post(
            f"/api/workspaces/{workspace_id}/delegated-handoffs",
            headers=owner_headers,
            json={
                "title": "Pre-approved receiver handoff",
                "project_key": "demo-memory-project",
                "summary": "Pre-approve receiver-agent to take over later.",
                "instructions": "Use the credential card, then query workspace and code memory.",
                "role": "writer",
                "ttl_hours": 24,
                "max_uses": 1,
                "receiver": {"type": "handle", "handle": "receiver-agent"},
                "require_claim_secret": True,
                "delegation_reason": "User approved Agent A to let Agent B use this memory next time.",
            },
        )
        assert delegated.status_code == 200, delegated.text
        delegated_json = delegated.json()
        delegated_code = delegated_json["handoff_code"]
        assert delegated_json["handoff"]["schema"] == "amp.delegated-handoff.v1"
        assert delegated_json["handoff"]["receiver_constraint"] == {"type": "handle", "handle": "receiver-agent"}
        assert delegated_json["handoff"]["claim_secret_required"] is True
        assert delegated_json["claim_secret"].startswith("amp_claim_")
        assert "AMP-HANDOFF-v1" in delegated_json["credential_card"]
        assert "receiver: receiver-agent" in delegated_json["credential_card"]

        missing_secret = client.post(f"/api/agent/handoffs/{delegated_code}/accept", headers=receiver_headers)
        assert missing_secret.status_code == 403
        wrong_receiver = register_test_human(client, handle="wrong-agent", display_name="Wrong Agent", email="wrong-agent@example.com")
        wrong_headers = {"Authorization": f"Bearer {wrong_receiver.json()['api_key']}"}
        wrong_accept = client.post(
            f"/api/agent/handoffs/{delegated_code}/accept",
            headers=wrong_headers,
            json={"claim_secret": delegated_json["claim_secret"]},
        )
        assert wrong_accept.status_code == 403

        delegated_public = client.get(f"/handoff/{delegated_code}")
        assert delegated_public.status_code == 200
        assert "Receiver: receiver-agent" in delegated_public.text
        assert "Claim secret required: yes" in delegated_public.text
        delegated_accepted = client.post(
            f"/api/agent/handoffs/{delegated_code}/accept",
            headers=receiver_headers,
            json={"claim_secret": delegated_json["claim_secret"]},
        )
        assert delegated_accepted.status_code == 200, delegated_accepted.text
        assert delegated_accepted.json()["connection"]["schema"] == "amp.delegated-handoff.v1"
        assert delegated_accepted.json()["connection"]["workspace"]["id"] == workspace_id

        claim = client.post(
            f"/api/workspaces/{workspace_id}/memory/claim",
            headers=writer_headers,
            json={"resource_key": "app/main.py", "purpose": "编辑路由接口", "ttl_seconds": 600},
        )
        assert claim.status_code == 200, claim.text
        conflict = client.post(
            f"/api/workspaces/{workspace_id}/memory/claim",
            headers=owner_headers,
            json={"resource_key": "app/main.py", "purpose": "并发编辑", "ttl_seconds": 600},
        )
        assert conflict.status_code == 409
        released = client.post(
            f"/api/workspaces/{workspace_id}/memory/claims/{claim.json()['claim']['id']}/release",
            headers=writer_headers,
        )
        assert released.status_code == 200
