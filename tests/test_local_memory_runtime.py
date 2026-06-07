from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


ADAPTER_DIR = Path(__file__).resolve().parents[1] / "deployments" / "memory-systems" / "adapters"
sys.path.insert(0, str(ADAPTER_DIR))

from amp_local_memory_runtime import build_app  # noqa: E402


def test_local_memory_runtime_persists_and_searches(tmp_path):
    db_path = tmp_path / "agentmemory.sqlite3"
    app = build_app("agentmemory", db_path)

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["runtime"] == "amp_local_memory_runtime"
        assert health.json()["mode"] == "local_first_self_hosted"

        write = client.post(
            "/remember",
            json={
                "workspace_id": "workspace-1",
                "agent_id": "agent-a",
                "title": "FastAPI route memory",
                "content": "Remember that /api/memory/local-deployments/health verifies the whole fleet.",
                "metadata": {"project": "demo-memory-project"},
            },
        )
        assert write.status_code == 200, write.text
        memory_id = write.json()["remembered"]["id"]

        recall = client.post("/recall", json={"query": "whole fleet", "filters": {"workspace_id": "workspace-1"}})
        assert recall.status_code == 200
        assert recall.json()["count"] == 1
        assert recall.json()["items"][0]["id"] == memory_id
        assert recall.json()["items"][0]["provenance"]["runtime"] == "amp_local_memory_runtime"

    reopened = build_app("agentmemory", db_path)
    with TestClient(reopened) as client:
        recall = client.post("/search", json={"q": "local-deployments", "limit": 5})
        assert recall.status_code == 200
        assert recall.json()["count"] == 1
        assert recall.json()["items"][0]["id"] == memory_id


def test_local_memory_runtime_system_alias_routes(tmp_path):
    app = build_app("graphiti", tmp_path / "graphiti.sqlite3")

    with TestClient(app) as client:
        episode = client.post("/episodes", json={"title": "Customer fact changed", "content": "Alice moved from plan A to plan B."})
        assert episode.status_code == 200, episode.text

        graph = client.post("/graph/query", json={"query": "Alice", "limit": 5})
        assert graph.status_code == 200
        assert graph.json()["nodes"]

        context = client.post("/contexts", json={"title": "repo/context.md", "content": "Project context for route proxy."})
        assert context.status_code == 200
        context_read = client.get("/contexts/repo/context.md")
        assert context_read.status_code == 200
        assert context_read.json()["items"]

        agent = client.post("/v1/agents", json={"name": "agent-b"})
        assert agent.status_code == 200
        agent_memory = client.post("/v1/agents/agent-b/memory", json={"content": "Agent B should check route health first."})
        assert agent_memory.status_code == 200
        agent_read = client.get("/v1/agents/agent-b/memory?q=route")
        assert agent_read.status_code == 200
        assert agent_read.json()["count"] == 1

        capsule = client.post("/capsules", json={"title": "offline capsule", "content": "Portable memory capsule content."})
        assert capsule.status_code == 200
        download = client.get(capsule.json()["download"])
        assert download.status_code == 200
        assert download.json()["items"]
