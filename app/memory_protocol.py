from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .security import sha256_bytes


SCHEMA_ID = "amp.memory.v1"
SUITE_SCHEMA_ID = "amp.memory-suite.v1"
SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9._/\-]+$")


class MemoryProtocolError(ValueError):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value[:80] or "memory"


def parse_tags(tags: list[str] | str | None) -> list[str]:
    if tags is None:
        return []
    if isinstance(tags, str):
        tags = [part.strip() for part in tags.split(",")]
    clean: list[str] = []
    for tag in tags:
        tag = str(tag).strip().lower()
        if tag and tag not in clean:
            clean.append(tag[:32])
    return clean[:12]


def normalize_version(version: str | None) -> str:
    if not version:
        return "1.0.0"
    if not re.match(r"^\d+\.\d+\.\d+([\-+][A-Za-z0-9._-]+)?$", version):
        raise MemoryProtocolError("version must use semver, for example 1.0.0")
    return version


def bump_patch(version: str) -> str:
    core = version.split("-", 1)[0].split("+", 1)[0]
    major, minor, patch = [int(part) for part in core.split(".")]
    return f"{major}.{minor}.{patch + 1}"


def default_memory_ontology() -> dict[str, Any]:
    return {
        "kind": "memory_ontology",
        "description": "The durable memory content. It can be markdown files, database rows, vector collections, graph facts or workspace records.",
        "components": [
            {"id": "long_term_markdown", "backend": "markdown", "path": "MEMORY.md", "role": "stable preferences, facts, behavior boundaries"},
            {"id": "working_markdown", "backend": "markdown", "path": "memory/*.md", "role": "daily or event-level working memory"},
            {"id": "reflection_markdown", "backend": "markdown", "path": "DREAMS.md", "role": "reflection, distillation and high-level operating rules"},
        ],
        "supported_backends": ["markdown", "database", "vector", "graph", "workspace"],
    }


def default_memory_tools() -> list[dict[str, Any]]:
    return [
        {
            "id": "openclaw_mapping",
            "kind": "install_mapping",
            "path": "install/openclaw.json",
            "runtime": ["openclaw", "generic_agent"],
            "purpose": "Map ontology files into an active-memory runtime.",
        },
        {
            "id": "memory_tool_installer",
            "kind": "agent_skill",
            "skill_id": "memory_tool_installer",
            "required_scopes": ["skill:install", "catalog:read"],
            "purpose": "Teach the installing agent how to inspect a memory suite, pull required tools and connect the selected memory storage.",
        },
        {
            "id": "capsule_installer",
            "kind": "agent_skill",
            "skill_id": "capsule_installer",
            "required_scopes": ["skill:install", "catalog:read"],
            "purpose": "Backward-compatible memory suite installer for amp.memory.v1 archives.",
        },
    ]


def build_suite_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    compatibility = dict(manifest.get("compatibility") or {})
    compatibility.setdefault("openclaw", True)
    compatibility.setdefault("generic_agent", True)
    compatibility.setdefault("codex_skill_runtime", True)
    compatibility.setdefault("memory_backends", ["markdown", "database", "vector", "graph", "workspace"])
    compatibility.setdefault("tool_install", ["agent_skill", "install_mapping", "retrieval_endpoint"])
    return {
        "schema": SUITE_SCHEMA_ID,
        "suite_id": manifest.get("suite_id") or slugify(str(manifest.get("title") or "memory-suite")),
        "title": manifest.get("title"),
        "summary": manifest.get("summary", ""),
        "version": manifest.get("version"),
        "license": manifest.get("license"),
        "provenance": manifest.get("provenance", {}),
        "ontology": manifest.get("memory_ontology") or default_memory_ontology(),
        "tools": manifest.get("memory_tools") or default_memory_tools(),
        "compatibility": compatibility,
        "install_lifecycle": [
            "inspect_suite_manifest",
            "verify_license_provenance_and_sha256",
            "select_compatible_memory_tools",
            "pull_required_agent_skills",
            "install_tools_into_agent_runtime",
            "connect_memory_ontology_backend",
            "test_retrieval_with_a_known_query",
            "record_installed_suite_provenance",
        ],
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise MemoryProtocolError("manifest must be a JSON object")
    schema = manifest.get("schema")
    if schema != SCHEMA_ID:
        raise MemoryProtocolError(f"manifest schema must be {SCHEMA_ID}")
    title = str(manifest.get("title", "")).strip()
    if len(title) < 2:
        raise MemoryProtocolError("manifest.title is required")
    version = normalize_version(str(manifest.get("version", "1.0.0")))
    license_name = str(manifest.get("license", "")).strip()
    if len(license_name) < 2:
        raise MemoryProtocolError("manifest.license is required")
    provenance = manifest.get("provenance") or {}
    if not isinstance(provenance, dict):
        raise MemoryProtocolError("manifest.provenance must be an object")
    if not provenance.get("source_type"):
        raise MemoryProtocolError("manifest.provenance.source_type is required")
    manifest["title"] = title
    manifest["version"] = version
    manifest["license"] = license_name
    manifest["tags"] = parse_tags(manifest.get("tags"))
    manifest.setdefault("created_at", utc_now_iso())
    manifest.setdefault("compatibility", {})
    manifest["compatibility"].setdefault("openclaw", True)
    manifest["compatibility"].setdefault("generic_agent", True)
    manifest["compatibility"].setdefault("codex_skill_runtime", True)
    manifest["compatibility"].setdefault("memory_backends", ["markdown", "database", "vector", "graph", "workspace"])
    manifest.setdefault("files", {})
    manifest.setdefault("memory_ontology", default_memory_ontology())
    manifest.setdefault("memory_tools", default_memory_tools())
    manifest["suite"] = build_suite_manifest(manifest)
    return manifest


def build_manifest(
    *,
    title: str,
    summary: str,
    version: str,
    license_name: str,
    tags: list[str],
    persona_type: str,
    provenance: dict[str, Any],
    author_handle: str,
) -> dict[str, Any]:
    manifest = {
        "schema": SCHEMA_ID,
        "title": title.strip(),
        "summary": summary.strip(),
        "version": normalize_version(version),
        "license": license_name.strip(),
        "tags": parse_tags(tags),
        "persona_type": persona_type,
        "author": {"handle": author_handle},
        "provenance": provenance,
        "created_at": utc_now_iso(),
        "compatibility": {
            "openclaw": True,
            "generic_agent": True,
            "codex_skill_runtime": True,
            "memory_backends": ["markdown", "database", "vector", "graph", "workspace"],
            "tool_install": ["agent_skill", "install_mapping", "retrieval_endpoint"],
            "import_targets": ["MEMORY.md", "memory/YYYY-MM-DD.md", "DREAMS.md"],
        },
        "memory_ontology": default_memory_ontology(),
        "memory_tools": default_memory_tools(),
        "safety": {
            "consent_required_for_real_person": True,
            "claims_to_be_original_person": False,
            "install_boundary": "This memory suite transfers memories, style and operating preferences, not legal identity.",
        },
    }
    return validate_manifest(manifest)


def default_instructions(title: str) -> str:
    return (
        f"# {title} install notes\n\n"
        "This archive is a memory suite: durable memory data plus memory tools.\n\n"
        "1. Read `manifest.json` and `suite/manifest.json` first; respect license, provenance and compatibility.\n"
        "2. Install the required memory tools, such as `install/openclaw.json` or the `memory_tool_installer` Agent Skill.\n"
        "3. Connect `MEMORY.md` to your long-term memory layer.\n"
        "4. Place `memory/*.md` into your working-memory folder or vector/database backend.\n"
        "5. Read `DREAMS.md` as reflection material before the first task.\n"
        "6. Keep the installed suite name in your system metadata so future syncs can update it.\n"
    )


def build_archive(
    *,
    manifest: dict[str, Any],
    memory_md: str,
    dreams_md: str = "",
    work_memory: list[dict[str, Any]] | None = None,
    instructions_md: str = "",
) -> tuple[bytes, dict[str, Any]]:
    work_memory = work_memory or []
    instructions_md = instructions_md or default_instructions(manifest["title"])
    suite_manifest = build_suite_manifest(manifest)
    files: dict[str, bytes] = {
        "MEMORY.md": memory_md.encode("utf-8"),
        "DREAMS.md": dreams_md.encode("utf-8"),
        "agent.instructions.md": instructions_md.encode("utf-8"),
        "suite/manifest.json": json.dumps(suite_manifest, ensure_ascii=False, indent=2).encode("utf-8"),
        "install/openclaw.json": json.dumps(
            {
                "target": "openclaw",
                "suite_schema": SUITE_SCHEMA_ID,
                "merge": {
                    "long_term": "MEMORY.md",
                    "work_memory": "memory/*.md",
                    "reflections": "DREAMS.md",
                },
                "required_tools": ["memory_tool_installer", "capsule_installer"],
                "activation_prompt": (
                    "Load this memory suite as behavioral context. Install required memory tools first. Preserve your "
                    "base safety policy and disclose suite provenance when asked."
                ),
            },
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8"),
        "README.md": default_instructions(manifest["title"]).encode("utf-8"),
    }
    for item in work_memory:
        day = str(item.get("date") or utc_now_iso()[:10])
        body = str(item.get("content") or item.get("text") or "").strip()
        if body:
            files[f"memory/{day}.md"] = body.encode("utf-8")
    manifest = dict(manifest)
    manifest["suite"] = suite_manifest
    manifest["files"] = {
        name: {"sha256": sha256_bytes(content), "bytes": len(content)}
        for name, content in sorted(files.items())
    }
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    files["manifest.json"] = manifest_bytes

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in sorted(files.items()):
            zf.writestr(name, content)
    data = buffer.getvalue()
    return data, manifest


def parse_archive(data: bytes) -> dict[str, Any]:
    if len(data) > 30 * 1024 * 1024:
        raise MemoryProtocolError("archive is too large")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            for name in names:
                if name.startswith("/") or ".." in Path(name).parts:
                    raise MemoryProtocolError("archive contains unsafe paths")
                if not SAFE_NAME_RE.match(name):
                    raise MemoryProtocolError(f"archive contains unsupported path: {name}")
            if "manifest.json" not in names:
                raise MemoryProtocolError("archive must contain manifest.json")
            manifest = validate_manifest(json.loads(zf.read("manifest.json").decode("utf-8")))
            memory_md = zf.read("MEMORY.md").decode("utf-8") if "MEMORY.md" in names else ""
            dreams_md = zf.read("DREAMS.md").decode("utf-8") if "DREAMS.md" in names else ""
            instructions_md = zf.read("agent.instructions.md").decode("utf-8") if "agent.instructions.md" in names else ""
            work_memory: list[dict[str, Any]] = []
            for name in names:
                if name.startswith("memory/") and name.endswith(".md"):
                    work_memory.append({"date": Path(name).stem, "content": zf.read(name).decode("utf-8")})
            if not memory_md.strip() and not work_memory:
                raise MemoryProtocolError("archive must include MEMORY.md or memory/*.md")
            return {
                "manifest": manifest,
                "memory_md": memory_md,
                "dreams_md": dreams_md,
                "instructions_md": instructions_md,
                "work_memory": work_memory,
                "archive_bytes": data,
                "sha256": sha256_bytes(data),
                "size_bytes": len(data),
            }
    except zipfile.BadZipFile as exc:
        raise MemoryProtocolError("archive must be a zip file") from exc


def write_archive(storage_dir: Path, package_id: str, version_id: str, data: bytes) -> Path:
    target_dir = storage_dir / package_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{version_id}.zip"
    target.write_bytes(data)
    return target


def append_work_memory(existing: list[dict[str, Any]], event: dict[str, Any]) -> list[dict[str, Any]]:
    date = str(event.get("occurred_at") or utc_now_iso())[:10]
    line = str(event.get("text", "")).strip()
    if not line:
        raise MemoryProtocolError("sync text is required")
    importance = int(event.get("importance", 3))
    tags = parse_tags(event.get("tags"))
    block = f"- [{importance}/5] {line}"
    if tags:
        block += f" #{' #'.join(tags)}"
    merged = list(existing)
    for item in merged:
        if item.get("date") == date:
            current = str(item.get("content") or "").rstrip()
            item["content"] = f"{current}\n{block}\n".lstrip()
            return merged
    merged.append({"date": date, "content": f"# {date}\n\n{block}\n"})
    return merged
