from __future__ import annotations

import os
from pathlib import Path
from typing import Any


LOCAL_DEPLOYMENT_SCHEMA = "amp.memory-local-deployments.v1"
LOCAL_ROUTE_SCHEMA = "amp.memory-local-route.v1"
LOCAL_FLEET_HEALTH_SCHEMA = "amp.memory-local-fleet-health.v1"
LOCAL_RUNTIME_NAME = "amp_local_memory_runtime"
LOCAL_RUNTIME_FILE = "deployments/memory-systems/adapters/amp_local_memory_runtime.py"
LOCAL_RUNTIME_DB_ROOT = str(Path(os.getenv("AMP_LOCAL_MEMORY_DATA_DIR", ".memorycloud-data/local-memory")).expanduser())
LOCAL_RUNTIME_CONTRACT = [
    "GET /health",
    "GET /v1/health",
    "POST /ingest",
    "POST /search",
    "POST /export",
    "system-specific route aliases",
]


LOCAL_DEPLOYMENT_SPECS: dict[str, dict[str, Any]] = {
    "mem0": {
        "service": "amp-mem0",
        "port": 18110,
        "health_path": "/health",
        "kind": "sdk_http_adapter",
        "runtime": "Python SDK adapter + local vector/database backend",
        "dependencies": ["qdrant", "postgres"],
        "persistent_volumes": ["mem0-data", "qdrant-data", "postgres-data"],
        "license_gate": "allow",
        "startup_order": 10,
        "native_commands": [
            "pip install mem0ai fastapi uvicorn qdrant-client psycopg[binary]",
            "uvicorn amp_mem0_adapter:app --host 0.0.0.0 --port 18110",
        ],
        "env": ["OPENAI_API_KEY optional", "MEM0_VECTOR_URL=http://qdrant:6333", "MEM0_DATABASE_URL=postgresql://amp:amp@postgres:5432/amp_memory"],
        "route_contract": ["GET /health", "POST /ingest", "POST /search", "POST /export"],
    },
    "graphiti": {
        "service": "amp-graphiti",
        "port": 18111,
        "health_path": "/health",
        "kind": "temporal_graph_service",
        "runtime": "Graphiti service with Neo4j-compatible graph database",
        "dependencies": ["neo4j"],
        "persistent_volumes": ["graphiti-data", "neo4j-data"],
        "license_gate": "allow",
        "startup_order": 20,
        "native_commands": [
            "pip install graphiti-core fastapi uvicorn neo4j",
            "uvicorn amp_graphiti_adapter:app --host 0.0.0.0 --port 18111",
        ],
        "env": ["NEO4J_URI=bolt://neo4j:7687", "NEO4J_USER=neo4j", "NEO4J_PASSWORD=change-me"],
        "route_contract": ["GET /health", "POST /episodes", "POST /search", "POST /graph/query"],
    },
    "openviking": {
        "service": "amp-openviking",
        "port": 18112,
        "health_path": "/health",
        "kind": "context_database_service",
        "runtime": "OpenViking context database isolated behind MemoryCloud route",
        "dependencies": ["postgres"],
        "persistent_volumes": ["openviking-data", "postgres-data"],
        "license_gate": "agpl_review_required",
        "startup_order": 30,
        "native_commands": [
            "git clone https://github.com/volcengine/OpenViking.git",
            "run upstream OpenViking service after AGPL review",
        ],
        "env": ["OPENVIKING_DATA_DIR=/data/openviking", "AMP_LICENSE_GATE=agpl_review_required"],
        "route_contract": ["GET /health", "POST /contexts", "POST /search", "GET /contexts/{path}"],
    },
    "supermemory": {
        "service": "amp-supermemory",
        "port": 18113,
        "health_path": "/health",
        "kind": "self_hosted_api_service",
        "runtime": "supermemory self-hosted API/app behind MemoryCloud route",
        "dependencies": ["postgres"],
        "persistent_volumes": ["supermemory-data", "postgres-data"],
        "license_gate": "allow",
        "startup_order": 40,
        "native_commands": [
            "git clone https://github.com/supermemoryai/supermemory.git",
            "configure local Postgres and run the API service on port 18113",
        ],
        "env": ["DATABASE_URL=postgresql://amp:amp@postgres:5432/amp_memory", "SUPERMEMORY_LOCAL_ONLY=true"],
        "route_contract": ["GET /health", "POST /memories", "POST /search", "POST /connectors/sync"],
    },
    "letta": {
        "service": "amp-letta",
        "port": 18114,
        "health_path": "/v1/health",
        "kind": "stateful_agent_runtime",
        "runtime": "Letta server isolated as local stateful agent runtime",
        "dependencies": ["postgres"],
        "persistent_volumes": ["letta-data", "postgres-data"],
        "license_gate": "allow",
        "startup_order": 50,
        "native_commands": [
            "pip install letta",
            "letta server --host 0.0.0.0 --port 18114",
        ],
        "env": ["LETTA_PG_URI=postgresql://amp:amp@postgres:5432/amp_memory"],
        "route_contract": ["GET /v1/health", "POST /v1/agents", "POST /v1/agents/{id}/memory", "GET /v1/agents/{id}/memory"],
    },
    "agentmemory": {
        "service": "amp-agentmemory",
        "port": 18115,
        "health_path": "/health",
        "kind": "mcp_http_gateway",
        "runtime": "agentmemory MCP gateway for coding agents",
        "dependencies": ["postgres"],
        "persistent_volumes": ["agentmemory-data", "postgres-data"],
        "license_gate": "allow",
        "startup_order": 60,
        "native_commands": [
            "git clone https://github.com/rohitg00/agentmemory.git",
            "run MCP gateway or HTTP bridge on port 18115",
        ],
        "env": ["AGENTMEMORY_PROJECT_ROOT=/workspaces", "DATABASE_URL=postgresql://amp:amp@postgres:5432/amp_memory"],
        "route_contract": ["GET /health", "POST /remember", "POST /recall", "GET /mcp"],
    },
    "cognee": {
        "service": "amp-cognee",
        "port": 18116,
        "health_path": "/health",
        "kind": "graph_rag_pipeline",
        "runtime": "cognee GraphRAG pipeline with graph/vector dependencies",
        "dependencies": ["qdrant", "neo4j", "postgres"],
        "persistent_volumes": ["cognee-data", "qdrant-data", "neo4j-data", "postgres-data"],
        "license_gate": "allow",
        "startup_order": 70,
        "native_commands": [
            "pip install cognee fastapi uvicorn",
            "uvicorn amp_cognee_adapter:app --host 0.0.0.0 --port 18116",
        ],
        "env": ["COGNEE_VECTOR_URL=http://qdrant:6333", "COGNEE_GRAPH_URI=bolt://neo4j:7687"],
        "route_contract": ["GET /health", "POST /datasets", "POST /cognify", "POST /search"],
    },
    "memvid": {
        "service": "amp-memvid",
        "port": 18117,
        "health_path": "/health",
        "kind": "portable_capsule_service",
        "runtime": "memvid single-file memory capsule service",
        "dependencies": [],
        "persistent_volumes": ["memvid-capsules"],
        "license_gate": "allow",
        "startup_order": 80,
        "native_commands": [
            "install memvid runtime",
            "run local capsule API on port 18117",
        ],
        "env": ["MEMVID_CAPSULE_DIR=/data/memvid"],
        "route_contract": ["GET /health", "POST /capsules", "POST /search", "GET /capsules/{id}/download"],
    },
    "hindsight": {
        "service": "amp-hindsight",
        "port": 18118,
        "health_path": "/health",
        "kind": "experience_learning_service",
        "runtime": "Hindsight experience-learning memory service",
        "dependencies": ["postgres", "qdrant"],
        "persistent_volumes": ["hindsight-data", "postgres-data", "qdrant-data"],
        "license_gate": "allow",
        "startup_order": 90,
        "native_commands": [
            "git clone https://github.com/vectorize-io/hindsight.git",
            "run local Hindsight API or MemoryCloud adapter on port 18118",
        ],
        "env": ["HINDSIGHT_LOCAL_ONLY=true", "DATABASE_URL=postgresql://amp:amp@postgres:5432/amp_memory"],
        "route_contract": ["GET /health", "POST /experiences", "POST /search", "POST /learn"],
    },
    "memori": {
        "service": "amp-memori",
        "port": 18119,
        "health_path": "/health",
        "kind": "agent_native_state_service",
        "runtime": "Memori local state service with license gate",
        "dependencies": ["postgres"],
        "persistent_volumes": ["memori-data", "postgres-data"],
        "license_gate": "license_review_required",
        "startup_order": 100,
        "native_commands": [
            "git clone https://github.com/MemoriLabs/Memori.git",
            "run local Memori API after license review",
        ],
        "env": ["MEMORI_LOCAL_ONLY=true", "AMP_LICENSE_GATE=license_review_required"],
        "route_contract": ["GET /health", "POST /state", "POST /search", "POST /export"],
    },
}


SHARED_DEPENDENCIES = {
    "postgres": {
        "image": "postgres:16-alpine",
        "port": 18130,
        "env": ["POSTGRES_USER=amp", "POSTGRES_PASSWORD=amp", "POSTGRES_DB=amp_memory"],
        "volume": "postgres-data:/var/lib/postgresql/data",
        "healthcheck": "pg_isready -U amp -d amp_memory",
    },
    "qdrant": {
        "image": "qdrant/qdrant:latest",
        "port": 18131,
        "volume": "qdrant-data:/qdrant/storage",
        "healthcheck": "wget -qO- http://127.0.0.1:6333/healthz || exit 1",
    },
    "neo4j": {
        "image": "neo4j:5-community",
        "port": 18132,
        "bolt_port": 18133,
        "env": ["NEO4J_AUTH=neo4j/change-me"],
        "volume": "neo4j-data:/data",
        "healthcheck": "wget -qO- http://127.0.0.1:7474 || exit 1",
    },
}


def deployment_ids() -> list[str]:
    return list(LOCAL_DEPLOYMENT_SPECS)


def get_local_deployment(integration_id: str, *, base_url: str | None = None) -> dict[str, Any] | None:
    spec = LOCAL_DEPLOYMENT_SPECS.get(integration_id.strip().lower())
    if not spec:
        return None
    payload = dict(spec)
    payload["schema"] = "amp.memory-local-deployment.v1"
    payload["integration_id"] = integration_id.strip().lower()
    payload["bind"] = "127.0.0.1"
    payload["upstream_base_url"] = f"http://127.0.0.1:{payload['port']}"
    payload["upstream_health_url"] = f"http://127.0.0.1:{payload['port']}{payload['health_path']}"
    payload["public_route_prefix"] = f"/memory-routes/{payload['integration_id']}"
    payload["public_health_route"] = f"/memory-routes/{payload['integration_id']}/health"
    payload["public_proxy_route"] = f"/memory-routes/{payload['integration_id']}/{{path}}"
    payload["deployment_model"] = "local_first_self_hosted"
    payload["current_runtime"] = {
        "name": LOCAL_RUNTIME_NAME,
        "implementation": LOCAL_RUNTIME_FILE,
        "status": "configured",
        "persistence": f"SQLite WAL files under {LOCAL_RUNTIME_DB_ROOT}/{payload['integration_id']}.sqlite3",
        "data_residency": "local machine only",
        "network": "binds to 127.0.0.1 and is only exposed through MemoryCloud public routes",
        "contract": LOCAL_RUNTIME_CONTRACT,
    }
    payload["upstream_replacement"] = {
        "allowed": True,
        "rule": "Replace the local runtime behind the same 127.0.0.1 port and keep the MemoryCloud route contract stable.",
        "real_upstream_commands": payload.get("native_commands", []),
        "license_gate": payload["license_gate"],
    }
    payload["runtime_env"] = {
        "native": [
            f"AMP_MEMORY_SYSTEM={payload['integration_id']}",
            "AMP_MEMORY_RUNTIME_MODE=amp_local_memory_runtime",
            f"AMP_LOCAL_MEMORY_DB={LOCAL_RUNTIME_DB_ROOT}/{payload['integration_id']}.sqlite3",
        ],
        "container": [
            f"AMP_MEMORY_SYSTEM={payload['integration_id']}",
            "AMP_MEMORY_RUNTIME_MODE=amp_local_memory_runtime",
            f"AMP_LOCAL_MEMORY_DB=/data/{payload['integration_id']}.sqlite3",
        ],
    }
    if base_url:
        base = base_url.rstrip("/")
        payload["public_route_url"] = f"{base}{payload['public_route_prefix']}"
        payload["public_health_url"] = f"{base}{payload['public_health_route']}"
        payload["local_deployment_url"] = f"{base}/api/memory/integrations/{payload['integration_id']}/local-deployment"
        payload["route_health_url"] = f"{base}/api/memory/integrations/{payload['integration_id']}/route-health"
    payload["route_reachability"] = {
        "platform_route": "always reachable when MemoryCloud platform is running",
        "local_runtime_route": "reachable after the local service container or native process is started",
        "public_port_requirement": "only MemoryCloud public port is required; local memory runtimes bind to 127.0.0.1 and are reached through MemoryCloud routes",
    }
    payload["commercial_runtime_boundary"] = {
        "no_hosted_dependency_required": True,
        "secrets_policy": "Do not write API keys or private credentials into memory records, public packages or logs.",
        "license_policy": "Systems with license gates run only after review or remain behind isolated service boundaries.",
    }
    return payload


def list_local_deployments(base_url: str | None = None) -> list[dict[str, Any]]:
    items = [get_local_deployment(integration_id, base_url=base_url) for integration_id in deployment_ids()]
    return sorted([item for item in items if item], key=lambda item: int(item["startup_order"]))


def render_env_example() -> str:
    lines = [
        "# MemoryCloud local memory systems",
        f"AMP_PUBLIC_BASE_URL={os.getenv('PUBLIC_SITE_ORIGIN', 'http://127.0.0.1:8000')}",
        "AMP_LOCAL_BIND=127.0.0.1",
        "AMP_MEMORY_RUNTIME_MODE=amp_local_memory_runtime",
        "AMP_LOCAL_MEMORY_DATA_DIR=.memorycloud-data/local-memory",
        "POSTGRES_PASSWORD=amp",
        "NEO4J_PASSWORD=change-me",
        "OPENAI_API_KEY=",
        "DASHSCOPE_API_KEY=",
        "AMP_ALLOW_AGPL_OPENVIKING=false",
        "AMP_ALLOW_MEMORI_NOASSERTION=false",
        "",
    ]
    return "\n".join(lines)


def render_compose() -> str:
    lines: list[str] = [
        "name: amp-memory-local-systems",
        "services:",
        "  postgres:",
        "    image: postgres:16-alpine",
        "    restart: unless-stopped",
        "    environment:",
        "      POSTGRES_USER: amp",
        "      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-amp}",
        "      POSTGRES_DB: amp_memory",
        "    ports:",
        "      - \"127.0.0.1:18130:5432\"",
        "    volumes:",
        "      - postgres-data:/var/lib/postgresql/data",
        "  qdrant:",
        "    image: qdrant/qdrant:latest",
        "    restart: unless-stopped",
        "    ports:",
        "      - \"127.0.0.1:18131:6333\"",
        "    volumes:",
        "      - qdrant-data:/qdrant/storage",
        "  neo4j:",
        "    image: neo4j:5-community",
        "    restart: unless-stopped",
        "    environment:",
        "      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD:-change-me}",
        "    ports:",
        "      - \"127.0.0.1:18132:7474\"",
        "      - \"127.0.0.1:18133:7687\"",
        "    volumes:",
        "      - neo4j-data:/data",
    ]
    for integration_id, spec in sorted(LOCAL_DEPLOYMENT_SPECS.items(), key=lambda item: item[1]["startup_order"]):
        lines.extend(
            [
                f"  {spec['service']}:",
                "    image: python:3.11-slim",
                "    restart: unless-stopped",
                f"    profiles: [\"{integration_id}\", \"all\"]",
                "    working_dir: /srv/adapter",
                "    command: >",
                "      sh -lc \"python -m pip install --no-cache-dir fastapi uvicorn &&",
                f"      python /srv/adapter/amp_local_memory_runtime.py --system {integration_id} --host 0.0.0.0 --port {spec['port']} --db /data/{integration_id}.sqlite3\"",
                "    ports:",
                f"      - \"127.0.0.1:{spec['port']}:{spec['port']}\"",
                "    volumes:",
                "      - ./adapters:/srv/adapter:ro",
                f"      - {integration_id}-data:/data",
            ]
        )
        if spec["dependencies"]:
            lines.append("    depends_on:")
            for dependency in spec["dependencies"]:
                lines.append(f"      - {dependency}")
        lines.append("    environment:")
        lines.append(f"      AMP_MEMORY_SYSTEM: {integration_id}")
        lines.append("      AMP_MEMORY_RUNTIME_MODE: amp_local_memory_runtime")
        lines.append(f"      AMP_LOCAL_MEMORY_DB: /data/{integration_id}.sqlite3")
        lines.append(f"      AMP_LICENSE_GATE: {spec['license_gate']}")
    volumes = {"postgres-data", "qdrant-data", "neo4j-data"}
    for spec in LOCAL_DEPLOYMENT_SPECS.values():
        volumes.update(spec["persistent_volumes"])
    lines.append("volumes:")
    for volume in sorted(volumes):
        lines.append(f"  {volume}:")
    lines.append("")
    return "\n".join(lines)
