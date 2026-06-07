from __future__ import annotations

import argparse
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field


class MemoryEvent(BaseModel):
    workspace_id: str = ""
    user_id: str = ""
    agent_id: str = ""
    memory_type: str = "generic"
    title: str = ""
    content: str = Field(default="", max_length=500_000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    q: str = Field(default="", max_length=20_000)
    query: str = Field(default="", max_length=20_000)
    limit: int = Field(default=10, ge=1, le=100)
    filters: dict[str, Any] = Field(default_factory=dict)


def utc_stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def default_db_path(system_id: str) -> Path:
    configured = os.environ.get("AMP_LOCAL_MEMORY_DB", "").strip()
    if configured:
        return Path(configured).expanduser()
    data_dir = os.environ.get("AMP_LOCAL_MEMORY_DATA_DIR", ".memorycloud-data/local-memory").strip()
    return Path(data_dir).expanduser() / f"{system_id}.sqlite3"


class LocalMemoryStore:
    def __init__(self, system_id: str, db_path: Path) -> None:
        self.system_id = system_id
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    system_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL DEFAULT '',
                    user_id TEXT NOT NULL DEFAULT '',
                    agent_id TEXT NOT NULL DEFAULT '',
                    memory_type TEXT NOT NULL,
                    title TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    source_route TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_memories_scope
                    ON memories(system_id, workspace_id, user_id, agent_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_memories_type
                    ON memories(system_id, memory_type, created_at DESC);
                """
            )

    def count(self) -> int:
        with self.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) AS c FROM memories WHERE system_id=?", (self.system_id,)).fetchone()["c"])

    def write(self, event: MemoryEvent, source_route: str) -> dict[str, Any]:
        now = utc_stamp()
        item_id = f"{self.system_id}-{time.time_ns()}-{os.getpid()}"
        metadata = dict(event.metadata or {})
        metadata.setdefault("runtime", "amp_local_memory_runtime")
        metadata.setdefault("source_route", source_route)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO memories(
                    id, system_id, workspace_id, user_id, agent_id, memory_type, title,
                    content, metadata_json, source_route, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    self.system_id,
                    event.workspace_id,
                    event.user_id,
                    event.agent_id,
                    event.memory_type,
                    event.title,
                    event.content,
                    json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                    source_route,
                    now,
                    now,
                ),
            )
        return {
            "id": item_id,
            "system": self.system_id,
            "workspace_id": event.workspace_id,
            "user_id": event.user_id,
            "agent_id": event.agent_id,
            "memory_type": event.memory_type,
            "title": event.title,
            "content": event.content,
            "metadata": metadata,
            "created_at": now,
        }

    def search(self, query: str, limit: int, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        params: list[Any] = [self.system_id]
        clauses = ["system_id=?"]
        for key in ("workspace_id", "user_id", "agent_id", "memory_type"):
            value = str(filters.get(key) or "").strip()
            if value:
                clauses.append(f"{key}=?")
                params.append(value)
        needle = query.strip().lower()
        sql = f"""
            SELECT * FROM memories
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at DESC
            LIMIT 500
        """
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        items: list[dict[str, Any]] = []
        for row in rows:
            metadata = json.loads(row["metadata_json"] or "{}")
            metadata_text = " ".join(str(value) for value in metadata.values())
            haystack = f"{row['title']} {row['content']} {metadata_text}".lower()
            if needle and needle not in haystack:
                continue
            score = 1.0 if not needle else min(1.0, 0.55 + haystack.count(needle) * 0.15)
            items.append(
                {
                    "id": row["id"],
                    "system": row["system_id"],
                    "workspace_id": row["workspace_id"],
                    "user_id": row["user_id"],
                    "agent_id": row["agent_id"],
                    "memory_type": row["memory_type"],
                    "title": row["title"],
                    "content": row["content"],
                    "metadata": metadata,
                    "source_route": row["source_route"],
                    "created_at": row["created_at"],
                    "confidence": round(score, 3),
                    "provenance": {
                        "runtime": "amp_local_memory_runtime",
                        "db_path": str(self.db_path),
                        "source_route": row["source_route"],
                    },
                }
            )
            if len(items) >= limit:
                break
        return items

    def get(self, item_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM memories WHERE system_id=? AND id=?", (self.system_id, item_id)).fetchone()
        if not row:
            return None
        metadata = json.loads(row["metadata_json"] or "{}")
        return {
            "id": row["id"],
            "system": row["system_id"],
            "workspace_id": row["workspace_id"],
            "user_id": row["user_id"],
            "agent_id": row["agent_id"],
            "memory_type": row["memory_type"],
            "title": row["title"],
            "content": row["content"],
            "metadata": metadata,
            "source_route": row["source_route"],
            "created_at": row["created_at"],
            "confidence": 1.0,
            "provenance": {
                "runtime": "amp_local_memory_runtime",
                "db_path": str(self.db_path),
                "source_route": row["source_route"],
            },
        }

    def export(self) -> list[dict[str, Any]]:
        return self.search("", 100, {})


def text_from_payload(payload: dict[str, Any]) -> str:
    for key in ("content", "text", "memory", "message", "summary", "episode", "context", "experience", "state"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    for key in ("messages", "items", "documents", "data"):
        value = payload.get(key)
        if value:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def event_from_payload(payload: dict[str, Any], *, memory_type: str, route: str) -> MemoryEvent:
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    for key in ("filters", "source", "provenance", "entities", "relations", "tags"):
        if key in payload and key not in metadata:
            metadata[key] = payload[key]
    metadata["compat_route"] = route
    title = str(payload.get("title") or payload.get("name") or payload.get("id") or memory_type).strip()
    return MemoryEvent(
        workspace_id=str(payload.get("workspace_id") or metadata.get("workspace_id") or ""),
        user_id=str(payload.get("user_id") or metadata.get("user_id") or ""),
        agent_id=str(payload.get("agent_id") or metadata.get("agent_id") or ""),
        memory_type=str(payload.get("memory_type") or memory_type),
        title=title[:240],
        content=text_from_payload(payload),
        metadata=metadata,
    )


async def json_body(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        raw = await request.body()
        payload = {"content": raw.decode("utf-8", errors="replace")}
    if isinstance(payload, dict):
        return payload
    return {"data": payload}


def build_app(system_id: str, db_path: Path | None = None) -> FastAPI:
    store = LocalMemoryStore(system_id, db_path or default_db_path(system_id))
    started_at = time.time()
    app = FastAPI(title=f"AMP local memory runtime: {system_id}", version="1.0.0")

    def health_payload() -> dict[str, Any]:
        return {
            "ok": True,
            "system": system_id,
            "runtime": "amp_local_memory_runtime",
            "mode": "local_first_self_hosted",
            "network": "127.0.0.1 upstream behind AMP route",
            "db_path": str(store.db_path),
            "uptime_seconds": round(time.time() - started_at, 3),
            "stored_events": store.count(),
            "contract": ["ingest", "search", "export", "system_specific_aliases"],
        }

    @app.get("/health")
    def health() -> dict[str, Any]:
        return health_payload()

    @app.get("/v1/health")
    def v1_health() -> dict[str, Any]:
        return health_payload()

    @app.post("/ingest")
    async def ingest(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="generic", route="/ingest"), "/ingest")
        return {"ok": True, "system": system_id, "item": item}

    @app.post("/search")
    async def search(request: Request) -> dict[str, Any]:
        payload = SearchRequest(**(await json_body(request)))
        query = payload.q or payload.query
        items = store.search(query, payload.limit, payload.filters)
        return {"ok": True, "system": system_id, "query": query, "items": items, "count": len(items)}

    @app.post("/export")
    async def export() -> dict[str, Any]:
        items = store.export()
        return {"ok": True, "system": system_id, "items": items, "count": len(items)}

    @app.post("/memories")
    @app.post("/v1/memories")
    async def memories(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="conversation_memory", route=str(request.url.path)), str(request.url.path))
        return {"ok": True, "system": system_id, "memory": item}

    @app.post("/episodes")
    async def episodes(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="temporal_episode", route="/episodes"), "/episodes")
        return {"ok": True, "system": system_id, "episode": item}

    @app.post("/graph/query")
    async def graph_query(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        query = str(payload.get("q") or payload.get("query") or "")
        items = store.search(query, int(payload.get("limit") or 10), payload.get("filters") if isinstance(payload.get("filters"), dict) else {})
        nodes = [{"id": item["id"], "label": item["title"] or item["memory_type"], "type": item["memory_type"]} for item in items]
        edges = [{"source": items[index]["id"], "target": items[index + 1]["id"], "type": "related_by_query"} for index in range(max(0, len(items) - 1))]
        return {"ok": True, "system": system_id, "query": query, "nodes": nodes, "edges": edges, "items": items}

    @app.post("/contexts")
    async def contexts(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="hierarchical_context", route="/contexts"), "/contexts")
        return {"ok": True, "system": system_id, "context": item}

    @app.get("/contexts/{context_path:path}")
    async def get_context(context_path: str) -> dict[str, Any]:
        items = store.search(context_path, 20, {})
        return {"ok": True, "system": system_id, "path": context_path, "items": items, "count": len(items)}

    @app.post("/connectors/sync")
    async def connector_sync(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="connector_sync", route="/connectors/sync"), "/connectors/sync")
        return {"ok": True, "system": system_id, "synced": item}

    @app.post("/v1/agents")
    async def create_agent(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        agent_id = str(payload.get("agent_id") or payload.get("name") or f"{system_id}-agent")
        item = store.write(event_from_payload({**payload, "agent_id": agent_id}, memory_type="agent_state", route="/v1/agents"), "/v1/agents")
        return {"ok": True, "system": system_id, "agent": {"id": agent_id, "state_memory_id": item["id"]}}

    @app.post("/v1/agents/{agent_id}/memory")
    async def write_agent_memory(agent_id: str, request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload({**payload, "agent_id": agent_id}, memory_type="agent_state", route="/v1/agents/{id}/memory"), "/v1/agents/{id}/memory")
        return {"ok": True, "system": system_id, "memory": item}

    @app.get("/v1/agents/{agent_id}/memory")
    async def read_agent_memory(agent_id: str, q: str = "", limit: int = 10) -> dict[str, Any]:
        items = store.search(q, limit, {"agent_id": agent_id})
        return {"ok": True, "system": system_id, "agent_id": agent_id, "items": items, "count": len(items)}

    @app.post("/remember")
    async def remember(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="code_memory", route="/remember"), "/remember")
        return {"ok": True, "system": system_id, "remembered": item}

    @app.post("/recall")
    async def recall(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        query = str(payload.get("q") or payload.get("query") or payload.get("text") or "")
        items = store.search(query, int(payload.get("limit") or 10), payload.get("filters") if isinstance(payload.get("filters"), dict) else {})
        return {"ok": True, "system": system_id, "query": query, "items": items, "count": len(items)}

    @app.get("/mcp")
    async def mcp_manifest() -> dict[str, Any]:
        return {
            "ok": True,
            "system": system_id,
            "runtime": "amp_local_memory_runtime",
            "tools": [
                {"name": "remember", "method": "POST", "path": "/remember"},
                {"name": "recall", "method": "POST", "path": "/recall"},
            ],
        }

    @app.post("/datasets")
    async def datasets(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="dataset_memory", route="/datasets"), "/datasets")
        return {"ok": True, "system": system_id, "dataset": item}

    @app.post("/cognify")
    async def cognify(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="graph_rag_memory", route="/cognify"), "/cognify")
        return {"ok": True, "system": system_id, "result": {"memory_id": item["id"], "status": "indexed"}}

    @app.post("/capsules")
    async def capsules(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="portable_capsule_memory", route="/capsules"), "/capsules")
        return {"ok": True, "system": system_id, "capsule": item, "download": f"/capsules/{item['id']}/download"}

    @app.get("/capsules/{capsule_id}/download")
    async def capsule_download(capsule_id: str) -> JSONResponse:
        found = store.get(capsule_id)
        items = [found] if found else []
        return JSONResponse({"ok": True, "system": system_id, "capsule_id": capsule_id, "items": items})

    @app.post("/experiences")
    async def experiences(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="experience_learning_memory", route="/experiences"), "/experiences")
        return {"ok": True, "system": system_id, "experience": item}

    @app.post("/learn")
    async def learn(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="procedure_memory", route="/learn"), "/learn")
        return {"ok": True, "system": system_id, "lesson": item}

    @app.post("/state")
    async def state(request: Request) -> dict[str, Any]:
        payload = await json_body(request)
        item = store.write(event_from_payload(payload, memory_type="agent_native_state", route="/state"), "/state")
        return {"ok": True, "system": system_id, "state": item}

    @app.get("/robots.txt", response_class=PlainTextResponse)
    async def robots() -> str:
        return "User-agent: *\nDisallow:\n"

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--db", default="")
    args = parser.parse_args()
    db_path = Path(args.db) if args.db else default_db_path(args.system)
    uvicorn.run(build_app(args.system, db_path), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
