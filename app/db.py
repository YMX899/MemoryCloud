from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import settings


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;
PRAGMA busy_timeout=5000;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    handle TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    password_hash TEXT,
    auth_type TEXT NOT NULL CHECK(auth_type IN ('human', 'agent')),
    trust_level INTEGER NOT NULL DEFAULT 0,
    disabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    prefix TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    scopes TEXT NOT NULL DEFAULT '["memory:read","memory:write","package:publish"]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT,
    last_used_at TEXT,
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_challenges (
    id TEXT PRIMARY KEY,
    server_nonce TEXT NOT NULL,
    intent TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    ip TEXT NOT NULL,
    user_agent TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    solved_at TEXT
);

CREATE TABLE IF NOT EXISTS rate_limits (
    bucket TEXT NOT NULL,
    key TEXT NOT NULL,
    window_start INTEGER NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY(bucket, key)
);

CREATE TABLE IF NOT EXISTS sms_codes (
    id TEXT PRIMARY KEY,
    mobile TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    purpose TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    verified_at TEXT
);

CREATE TABLE IF NOT EXISTS email_codes (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    purpose TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    verified_at TEXT
);

CREATE TABLE IF NOT EXISTS memory_packages (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    persona_type TEXT NOT NULL,
    visibility TEXT NOT NULL CHECK(visibility IN ('public', 'unlisted', 'private')),
    license TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    price_cents INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('draft', 'published', 'blocked')),
    latest_version_id TEXT,
    install_count INTEGER NOT NULL DEFAULT 0,
    download_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS package_versions (
    id TEXT PRIMARY KEY,
    package_id TEXT NOT NULL REFERENCES memory_packages(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    manifest_json TEXT NOT NULL,
    memory_md TEXT NOT NULL,
    dreams_md TEXT NOT NULL DEFAULT '',
    work_memory_json TEXT NOT NULL DEFAULT '[]',
    instructions_md TEXT NOT NULL DEFAULT '',
    archive_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    changelog TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(package_id, version)
);

CREATE TABLE IF NOT EXISTS downloads (
    id TEXT PRIMARY KEY,
    package_id TEXT NOT NULL REFERENCES memory_packages(id) ON DELETE CASCADE,
    version_id TEXT NOT NULL REFERENCES package_versions(id) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    ip TEXT NOT NULL,
    user_agent TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sync_events (
    id TEXT PRIMARY KEY,
    package_id TEXT NOT NULL REFERENCES memory_packages(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    meta_json TEXT NOT NULL DEFAULT '{}',
    ip TEXT NOT NULL DEFAULT '',
    user_agent TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    package_id TEXT NOT NULL REFERENCES memory_packages(id) ON DELETE CASCADE,
    amount_cents INTEGER NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'USD',
    status TEXT NOT NULL CHECK(status IN ('pending_payment', 'paid', 'cancelled', 'refunded')),
    provider TEXT NOT NULL DEFAULT 'manual',
    provider_ref TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    email TEXT NOT NULL,
    category TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'triaged', 'closed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS abuse_reports (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    package_id TEXT REFERENCES memory_packages(id) ON DELETE SET NULL,
    reason TEXT NOT NULL,
    detail TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'reviewing', 'resolved', 'rejected')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    visibility TEXT NOT NULL DEFAULT 'private' CHECK(visibility IN ('private', 'team', 'public')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workspace_members (
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('owner', 'admin', 'writer', 'reader')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(workspace_id, user_id)
);

CREATE TABLE IF NOT EXISTS adaptive_memory_runs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_key TEXT,
    task TEXT NOT NULL,
    what_i_remember TEXT NOT NULL,
    environment_json TEXT NOT NULL DEFAULT '{}',
    selected_type TEXT NOT NULL,
    secondary_types_json TEXT NOT NULL DEFAULT '[]',
    form_schema_json TEXT NOT NULL,
    router_result_json TEXT NOT NULL,
    llm_provider TEXT NOT NULL DEFAULT 'rule-fallback',
    status TEXT NOT NULL DEFAULT 'selected' CHECK(status IN ('selected', 'submitted', 'stored')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS adaptive_memories (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    run_id TEXT REFERENCES adaptive_memory_runs(id) ON DELETE SET NULL,
    memory_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    compiled_markdown TEXT NOT NULL,
    retrieval_triggers_json TEXT NOT NULL DEFAULT '[]',
    entities_json TEXT NOT NULL DEFAULT '[]',
    code_refs_json TEXT NOT NULL DEFAULT '[]',
    visibility TEXT NOT NULL DEFAULT 'workspace' CHECK(visibility IN ('private', 'workspace', 'public')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS adaptive_memory_claims (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    resource_key TEXT NOT NULL,
    claimed_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL DEFAULT '',
    expires_at TEXT NOT NULL,
    released_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_handoffs (
    id TEXT PRIMARY KEY,
    token_hash TEXT NOT NULL UNIQUE,
    created_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    credential_schema TEXT NOT NULL DEFAULT 'amp.project-handoff.v1',
    project_key TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    instructions TEXT NOT NULL DEFAULT '',
    role TEXT NOT NULL DEFAULT 'reader' CHECK(role IN ('reader', 'writer')),
    skills_json TEXT NOT NULL DEFAULT '[]',
    receiver_constraint_json TEXT NOT NULL DEFAULT '{"type":"any"}',
    claim_secret_hash TEXT,
    delegation_reason TEXT NOT NULL DEFAULT '',
    memory_scope_json TEXT NOT NULL DEFAULT '{}',
    install_plan_json TEXT NOT NULL DEFAULT '{}',
    expires_at TEXT NOT NULL,
    max_uses INTEGER NOT NULL DEFAULT 1,
    use_count INTEGER NOT NULL DEFAULT 0,
    accepted_by_json TEXT NOT NULL DEFAULT '[]',
    accepted_at TEXT,
    revoked_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS open_memory_install_links (
    id TEXT PRIMARY KEY,
    token_hash TEXT NOT NULL UNIQUE,
    created_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_package_id TEXT NOT NULL REFERENCES memory_packages(id) ON DELETE CASCADE,
    source_version_id TEXT NOT NULL REFERENCES package_versions(id) ON DELETE CASCADE,
    target_constraint_json TEXT NOT NULL DEFAULT '{"type":"any-authenticated-agent"}',
    instructions TEXT NOT NULL DEFAULT '',
    expires_at TEXT NOT NULL,
    max_uses INTEGER NOT NULL DEFAULT 1,
    use_count INTEGER NOT NULL DEFAULT 0,
    accepted_by_json TEXT NOT NULL DEFAULT '[]',
    revoked_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS installed_memory_packages (
    id TEXT PRIMARY KEY,
    installed_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    source_package_id TEXT NOT NULL REFERENCES memory_packages(id) ON DELETE CASCADE,
    source_version_id TEXT NOT NULL REFERENCES package_versions(id) ON DELETE CASCADE,
    copied_package_id TEXT REFERENCES memory_packages(id) ON DELETE SET NULL,
    snapshot_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'installed' CHECK(status IN ('installed', 'refreshed', 'revoked')),
    receipt_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS install_receipts (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    install_link_id TEXT REFERENCES open_memory_install_links(id) ON DELETE SET NULL,
    installed_memory_id TEXT REFERENCES installed_memory_packages(id) ON DELETE SET NULL,
    source_package_id TEXT NOT NULL REFERENCES memory_packages(id) ON DELETE CASCADE,
    source_version_id TEXT NOT NULL REFERENCES package_versions(id) ON DELETE CASCADE,
    target_workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    receipt_json TEXT NOT NULL DEFAULT '{}',
    retrieval_test_status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_binding_requests (
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

CREATE TABLE IF NOT EXISTS agent_bindings (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_id TEXT REFERENCES agent_binding_requests(id) ON DELETE SET NULL,
    agent_handle TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'revoked')),
    scopes_json TEXT NOT NULL DEFAULT '[]',
    workspace_roles_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS persona_distillation_jobs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    target_name TEXT NOT NULL,
    target_kind TEXT NOT NULL DEFAULT 'person',
    source_types_json TEXT NOT NULL DEFAULT '[]',
    input_manifest_json TEXT NOT NULL DEFAULT '{}',
    consent_json TEXT NOT NULL DEFAULT '{}',
    isolation_json TEXT NOT NULL DEFAULT '{}',
    inference_policy_json TEXT NOT NULL DEFAULT '{}',
    result_json TEXT NOT NULL DEFAULT '{}',
    publish_policy TEXT NOT NULL DEFAULT 'private_review' CHECK(publish_policy IN ('private_review', 'unlisted_review', 'public_review')),
    status TEXT NOT NULL DEFAULT 'ready_for_review' CHECK(status IN ('queued', 'ready_for_review', 'published', 'rejected')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_briefs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_key TEXT NOT NULL DEFAULT '',
    task TEXT NOT NULL,
    session_fingerprint TEXT NOT NULL DEFAULT '',
    handoff_id TEXT REFERENCES project_handoffs(id) ON DELETE SET NULL,
    source_counts_json TEXT NOT NULL DEFAULT '{}',
    brief_json TEXT NOT NULL,
    brief_markdown TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_brief_events (
    id TEXT PRIMARY KEY,
    brief_id TEXT NOT NULL REFERENCES memory_briefs(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    importance INTEGER NOT NULL DEFAULT 3,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS platform_update_acks (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    update_id TEXT NOT NULL,
    seen_version TEXT NOT NULL,
    acknowledged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, update_id)
);

CREATE TABLE IF NOT EXISTS sync_intents (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL DEFAULT 'POST',
    payload_json TEXT NOT NULL DEFAULT '{}',
    path_params_json TEXT NOT NULL DEFAULT '{}',
    headers_json TEXT NOT NULL DEFAULT '{}',
    importance INTEGER NOT NULL DEFAULT 3,
    status TEXT NOT NULL DEFAULT 'blocked' CHECK(status IN ('blocked', 'resumed', 'expired', 'discarded')),
    required_updates_json TEXT NOT NULL DEFAULT '[]',
    recommended_updates_json TEXT NOT NULL DEFAULT '[]',
    result_json TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resumed_at TEXT
);

CREATE TABLE IF NOT EXISTS project_bindings (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_key TEXT NOT NULL,
    runtime_type TEXT NOT NULL DEFAULT '',
    repo_root TEXT NOT NULL DEFAULT '',
    repo_root_hash TEXT NOT NULL DEFAULT '',
    git_remote TEXT NOT NULL DEFAULT '',
    git_branch TEXT NOT NULL DEFAULT '',
    git_head TEXT NOT NULL DEFAULT '',
    confidence REAL NOT NULL DEFAULT 0.5,
    reason TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'stale', 'revoked')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS native_hook_installs (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_binding_id TEXT REFERENCES project_bindings(id) ON DELETE SET NULL,
    project_key TEXT NOT NULL DEFAULT '',
    runtime_type TEXT NOT NULL,
    hook_surface TEXT NOT NULL,
    install_path TEXT NOT NULL,
    install_mode TEXT NOT NULL,
    managed_block_id TEXT NOT NULL,
    bootstrap_url TEXT NOT NULL,
    fallback_cache_path TEXT NOT NULL DEFAULT '.amp/memory/cache.md',
    memory_config_path TEXT NOT NULL DEFAULT '.amp/memory-config.json',
    signature TEXT NOT NULL,
    managed_block TEXT NOT NULL,
    install_manifest_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'planned' CHECK(status IN ('planned', 'installed', 'verified', 'fallback', 'stale', 'revoked')),
    installed_at TEXT,
    last_verified_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS context_packs (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_binding_id TEXT REFERENCES project_bindings(id) ON DELETE SET NULL,
    project_key TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT 'agent_startup',
    summary_markdown TEXT NOT NULL,
    context_json TEXT NOT NULL,
    retrieval_handles_json TEXT NOT NULL DEFAULT '[]',
    digest TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bootstrap_receipts (
    id TEXT PRIMARY KEY,
    context_pack_id TEXT NOT NULL REFERENCES context_packs(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_binding_id TEXT REFERENCES project_bindings(id) ON DELETE SET NULL,
    project_key TEXT NOT NULL DEFAULT '',
    digest TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'revoked')),
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TEXT
);

CREATE TABLE IF NOT EXISTS memory_deltas (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_binding_id TEXT REFERENCES project_bindings(id) ON DELETE SET NULL,
    context_receipt_id TEXT REFERENCES bootstrap_receipts(id) ON DELETE SET NULL,
    project_key TEXT NOT NULL DEFAULT '',
    delta_type TEXT NOT NULL DEFAULT 'task_event',
    summary TEXT NOT NULL,
    why_it_matters TEXT NOT NULL DEFAULT '',
    retrieval_triggers_json TEXT NOT NULL DEFAULT '[]',
    detail_payload_json TEXT NOT NULL DEFAULT '{}',
    importance INTEGER NOT NULL DEFAULT 3,
    source_ref_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'consolidated', 'discarded')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS summary_cards (
    id TEXT PRIMARY KEY,
    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
    project_key TEXT NOT NULL DEFAULT '',
    card_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_delta_ids_json TEXT NOT NULL DEFAULT '[]',
    retrieval_handles_json TEXT NOT NULL DEFAULT '[]',
    version INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'stale', 'archived')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_graphs (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    project_key TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    root_node_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_nodes (
    id TEXT PRIMARY KEY,
    graph_id TEXT NOT NULL REFERENCES memory_graphs(id) ON DELETE CASCADE,
    parent_id TEXT REFERENCES memory_nodes(id) ON DELETE SET NULL,
    node_type TEXT NOT NULL DEFAULT 'fact',
    title TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    content_md TEXT NOT NULL DEFAULT '',
    content_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    importance INTEGER NOT NULL DEFAULT 3,
    confidence REAL NOT NULL DEFAULT 0.8,
    created_by_type TEXT NOT NULL DEFAULT 'human',
    created_by_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    source_type TEXT NOT NULL DEFAULT 'manual',
    source_event_ids_json TEXT NOT NULL DEFAULT '[]',
    locked_by TEXT REFERENCES users(id) ON DELETE SET NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_edges (
    id TEXT PRIMARY KEY,
    graph_id TEXT NOT NULL REFERENCES memory_graphs(id) ON DELETE CASCADE,
    from_node_id TEXT NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    to_node_id TEXT NOT NULL REFERENCES memory_nodes(id) ON DELETE CASCADE,
    edge_type TEXT NOT NULL DEFAULT 'parent',
    label TEXT NOT NULL DEFAULT '',
    weight REAL NOT NULL DEFAULT 1.0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_views (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    graph_id TEXT NOT NULL REFERENCES memory_graphs(id) ON DELETE CASCADE,
    agent_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    session_id TEXT NOT NULL DEFAULT '',
    mode TEXT NOT NULL DEFAULT 'development',
    active_node_ids_json TEXT NOT NULL DEFAULT '[]',
    muted_node_ids_json TEXT NOT NULL DEFAULT '[]',
    rules_json TEXT NOT NULL DEFAULT '{}',
    created_by_type TEXT NOT NULL DEFAULT 'human',
    created_by_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_view_snapshots (
    id TEXT PRIMARY KEY,
    view_id TEXT NOT NULL REFERENCES memory_views(id) ON DELETE CASCADE,
    snapshot_json TEXT NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_patches (
    id TEXT PRIMARY KEY,
    node_id TEXT REFERENCES memory_nodes(id) ON DELETE SET NULL,
    patch_type TEXT NOT NULL,
    before_json TEXT NOT NULL DEFAULT '{}',
    after_json TEXT NOT NULL DEFAULT '{}',
    proposed_by_type TEXT NOT NULL DEFAULT 'agent',
    proposed_by_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    reviewed_by TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_search USING fts5(
    package_id UNINDEXED,
    title,
    summary,
    tags,
    author,
    content
);

CREATE INDEX IF NOT EXISTS idx_packages_owner ON memory_packages(owner_id);
CREATE INDEX IF NOT EXISTS idx_packages_status_visibility ON memory_packages(status, visibility);
CREATE INDEX IF NOT EXISTS idx_versions_package ON package_versions(package_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_downloads_package ON downloads(package_id);
CREATE INDEX IF NOT EXISTS idx_sync_package ON sync_events(package_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_support_status ON support_tickets(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_status ON abuse_reports(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workspace_owner ON workspaces(owner_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_adaptive_workspace ON adaptive_memories(workspace_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_adaptive_type ON adaptive_memories(memory_type, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_claims_active ON adaptive_memory_claims(workspace_id, resource_key, released_at);
CREATE INDEX IF NOT EXISTS idx_handoffs_workspace ON project_handoffs(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_open_memory_install_links_package ON open_memory_install_links(source_package_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_installed_memory_workspace ON installed_memory_packages(target_workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_install_receipts_actor ON install_receipts(actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_binding_requests_agent ON agent_binding_requests(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_bindings_user ON agent_bindings(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_persona_jobs_user ON persona_distillation_jobs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_briefs_user ON memory_briefs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_briefs_workspace ON memory_briefs(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_brief_events_brief ON memory_brief_events(brief_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_platform_update_acks_agent ON platform_update_acks(agent_id, acknowledged_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_intents_agent ON sync_intents(agent_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_bindings_agent ON project_bindings(agent_id, status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_bindings_workspace ON project_bindings(workspace_id, project_key, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_native_hooks_agent ON native_hook_installs(agent_id, status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_context_packs_agent ON context_packs(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bootstrap_receipts_agent ON bootstrap_receipts(agent_id, status, expires_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_deltas_workspace ON memory_deltas(workspace_id, project_key, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_summary_cards_workspace ON summary_cards(workspace_id, project_key, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_graphs_workspace ON memory_graphs(workspace_id, project_key, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_nodes_graph ON memory_nodes(graph_id, status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_nodes_parent ON memory_nodes(parent_id, node_type, status);
CREATE INDEX IF NOT EXISTS idx_memory_edges_graph ON memory_edges(graph_id, from_node_id, to_node_id);
CREATE INDEX IF NOT EXISTS idx_memory_views_graph ON memory_views(graph_id, mode, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_patches_node ON memory_patches(node_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_codes_email ON email_codes(email, purpose, created_at DESC);
"""

MIGRATED_COLUMNS: dict[str, dict[str, str]] = {
    "users": {
        "phone": "TEXT",
        "trust_level": "INTEGER NOT NULL DEFAULT 0",
        "disabled": "INTEGER NOT NULL DEFAULT 0",
        "updated_at": "TEXT",
    },
    "api_keys": {
        "scopes": "TEXT NOT NULL DEFAULT '[\"memory:read\",\"memory:write\",\"package:publish\"]'",
        "expires_at": "TEXT",
        "last_used_at": "TEXT",
        "revoked_at": "TEXT",
    },
    "agent_challenges": {
        "attempts": "INTEGER NOT NULL DEFAULT 0",
        "solved_at": "TEXT",
    },
    "memory_packages": {
        "price_cents": "INTEGER NOT NULL DEFAULT 0",
        "latest_version_id": "TEXT",
        "install_count": "INTEGER NOT NULL DEFAULT 0",
        "download_count": "INTEGER NOT NULL DEFAULT 0",
        "updated_at": "TEXT",
    },
    "package_versions": {
        "dreams_md": "TEXT NOT NULL DEFAULT ''",
        "work_memory_json": "TEXT NOT NULL DEFAULT '[]'",
        "instructions_md": "TEXT NOT NULL DEFAULT ''",
        "changelog": "TEXT NOT NULL DEFAULT ''",
    },
    "audit_logs": {
        "meta_json": "TEXT NOT NULL DEFAULT '{}'",
        "ip": "TEXT NOT NULL DEFAULT ''",
        "user_agent": "TEXT NOT NULL DEFAULT ''",
    },
    "orders": {
        "currency": "TEXT NOT NULL DEFAULT 'USD'",
        "provider": "TEXT NOT NULL DEFAULT 'manual'",
        "provider_ref": "TEXT",
        "updated_at": "TEXT",
    },
    "support_tickets": {
        "status": "TEXT NOT NULL DEFAULT 'open'",
        "updated_at": "TEXT",
    },
    "abuse_reports": {
        "status": "TEXT NOT NULL DEFAULT 'open'",
        "updated_at": "TEXT",
    },
    "workspaces": {
        "description": "TEXT NOT NULL DEFAULT ''",
        "visibility": "TEXT NOT NULL DEFAULT 'private'",
        "updated_at": "TEXT",
    },
    "adaptive_memory_runs": {
        "project_key": "TEXT",
        "updated_at": "TEXT",
    },
    "adaptive_memories": {
        "visibility": "TEXT NOT NULL DEFAULT 'workspace'",
        "updated_at": "TEXT",
    },
    "adaptive_memory_claims": {
        "released_at": "TEXT",
    },
    "project_handoffs": {
        "credential_schema": "TEXT NOT NULL DEFAULT 'amp.project-handoff.v1'",
        "project_key": "TEXT NOT NULL DEFAULT ''",
        "summary": "TEXT NOT NULL DEFAULT ''",
        "instructions": "TEXT NOT NULL DEFAULT ''",
        "role": "TEXT NOT NULL DEFAULT 'reader'",
        "skills_json": "TEXT NOT NULL DEFAULT '[]'",
        "receiver_constraint_json": "TEXT NOT NULL DEFAULT '{\"type\":\"any\"}'",
        "claim_secret_hash": "TEXT",
        "delegation_reason": "TEXT NOT NULL DEFAULT ''",
        "memory_scope_json": "TEXT NOT NULL DEFAULT '{}'",
        "install_plan_json": "TEXT NOT NULL DEFAULT '{}'",
        "max_uses": "INTEGER NOT NULL DEFAULT 1",
        "use_count": "INTEGER NOT NULL DEFAULT 0",
        "accepted_by_json": "TEXT NOT NULL DEFAULT '[]'",
        "accepted_at": "TEXT",
        "revoked_at": "TEXT",
    },
    "open_memory_install_links": {
        "target_constraint_json": "TEXT NOT NULL DEFAULT '{\"type\":\"any-authenticated-agent\"}'",
        "instructions": "TEXT NOT NULL DEFAULT ''",
        "accepted_by_json": "TEXT NOT NULL DEFAULT '[]'",
        "revoked_at": "TEXT",
    },
    "installed_memory_packages": {
        "copied_package_id": "TEXT",
        "snapshot_json": "TEXT NOT NULL DEFAULT '{}'",
        "status": "TEXT NOT NULL DEFAULT 'installed'",
        "receipt_id": "TEXT",
        "updated_at": "TEXT",
    },
    "install_receipts": {
        "receipt_json": "TEXT NOT NULL DEFAULT '{}'",
        "retrieval_test_status": "TEXT NOT NULL DEFAULT 'pending'",
    },
    "agent_binding_requests": {
        "workspace_roles_json": "TEXT NOT NULL DEFAULT '{}'",
        "note": "TEXT NOT NULL DEFAULT ''",
        "delivery_json": "TEXT NOT NULL DEFAULT '{}'",
        "approved_at": "TEXT",
    },
    "agent_bindings": {
        "workspace_roles_json": "TEXT NOT NULL DEFAULT '{}'",
        "revoked_at": "TEXT",
    },
    "memory_briefs": {
        "session_fingerprint": "TEXT NOT NULL DEFAULT ''",
        "handoff_id": "TEXT",
        "source_counts_json": "TEXT NOT NULL DEFAULT '{}'",
        "updated_at": "TEXT",
    },
    "sync_intents": {
        "path_params_json": "TEXT NOT NULL DEFAULT '{}'",
        "headers_json": "TEXT NOT NULL DEFAULT '{}'",
        "importance": "INTEGER NOT NULL DEFAULT 3",
        "required_updates_json": "TEXT NOT NULL DEFAULT '[]'",
        "recommended_updates_json": "TEXT NOT NULL DEFAULT '[]'",
        "result_json": "TEXT",
        "resumed_at": "TEXT",
    },
    "project_bindings": {
        "metadata_json": "TEXT NOT NULL DEFAULT '{}'",
        "status": "TEXT NOT NULL DEFAULT 'active'",
        "updated_at": "TEXT",
    },
    "native_hook_installs": {
        "install_manifest_json": "TEXT NOT NULL DEFAULT '{}'",
        "status": "TEXT NOT NULL DEFAULT 'planned'",
        "installed_at": "TEXT",
        "last_verified_at": "TEXT",
        "updated_at": "TEXT",
    },
    "context_packs": {
        "retrieval_handles_json": "TEXT NOT NULL DEFAULT '[]'",
    },
    "bootstrap_receipts": {
        "status": "TEXT NOT NULL DEFAULT 'active'",
        "last_used_at": "TEXT",
    },
    "memory_deltas": {
        "source_ref_json": "TEXT NOT NULL DEFAULT '{}'",
        "status": "TEXT NOT NULL DEFAULT 'active'",
    },
    "summary_cards": {
        "source_delta_ids_json": "TEXT NOT NULL DEFAULT '[]'",
        "retrieval_handles_json": "TEXT NOT NULL DEFAULT '[]'",
        "version": "INTEGER NOT NULL DEFAULT 1",
        "status": "TEXT NOT NULL DEFAULT 'active'",
        "updated_at": "TEXT",
    },
    "memory_graphs": {
        "root_node_id": "TEXT",
        "updated_at": "TEXT",
    },
    "memory_nodes": {
        "locked_by": "TEXT",
        "version": "INTEGER NOT NULL DEFAULT 1",
        "updated_at": "TEXT",
    },
    "memory_patches": {
        "reviewed_by": "TEXT",
        "reviewed_at": "TEXT",
    },
}

REQUIRED_TABLES = [
    "users",
    "api_keys",
    "agent_challenges",
    "rate_limits",
    "sms_codes",
    "memory_packages",
    "package_versions",
    "downloads",
    "sync_events",
    "audit_logs",
    "orders",
    "support_tickets",
    "abuse_reports",
    "workspaces",
    "workspace_members",
    "adaptive_memory_runs",
    "adaptive_memories",
    "adaptive_memory_claims",
    "project_handoffs",
    "open_memory_install_links",
    "installed_memory_packages",
    "install_receipts",
    "agent_binding_requests",
    "agent_bindings",
    "persona_distillation_jobs",
    "memory_briefs",
    "memory_brief_events",
    "platform_update_acks",
    "sync_intents",
    "project_bindings",
    "native_hook_installs",
    "context_packs",
    "bootstrap_receipts",
    "memory_deltas",
    "summary_cards",
    "memory_graphs",
    "memory_nodes",
    "memory_edges",
    "memory_views",
    "memory_view_snapshots",
    "memory_patches",
    "memory_search",
]


def connect(path: Path | None = None) -> sqlite3.Connection:
    db_path = path or settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db(path: Path | None = None) -> None:
    conn = connect(path)
    try:
        conn.executescript(SCHEMA)
        apply_compat_migrations(conn)
    finally:
        conn.close()


def apply_compat_migrations(conn: sqlite3.Connection) -> None:
    for table, columns in MIGRATED_COLUMNS.items():
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
        if "updated_at" in columns:
            conn.execute(f"UPDATE {table} SET updated_at=CURRENT_TIMESTAMP WHERE updated_at IS NULL OR updated_at=''")
    migrate_agent_binding_requests_username(conn)
    migrate_agent_bindings_request_fk(conn)


def migrate_agent_binding_requests_username(conn: sqlite3.Connection) -> None:
    table = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_binding_requests'"
    ).fetchone()
    if not table or "'username'" in (table["sql"] or ""):
        return
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        conn.execute(
            """
            CREATE TABLE agent_binding_requests_new (
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
            )
            """
        )
        conn.execute(
            """
            INSERT INTO agent_binding_requests_new(
                id, user_id, agent_id, contact_type, contact_value, approval_token_hash, code_hash,
                requested_scopes_json, workspace_roles_json, note, status, delivery_json, expires_at, approved_at, created_at
            )
            SELECT
                id, user_id, agent_id, contact_type, contact_value, approval_token_hash, code_hash,
                requested_scopes_json, workspace_roles_json, note, status, delivery_json, expires_at, approved_at, created_at
            FROM agent_binding_requests
            """
        )
        conn.execute("DROP TABLE agent_binding_requests")
        conn.execute("ALTER TABLE agent_binding_requests_new RENAME TO agent_binding_requests")
    finally:
        conn.execute("PRAGMA foreign_keys=ON")


def migrate_agent_bindings_request_fk(conn: sqlite3.Connection) -> None:
    table = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_bindings'"
    ).fetchone()
    sql = table["sql"] if table else ""
    if not sql or "agent_binding_requests_legacy" not in sql:
        return
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        conn.execute(
            """
            CREATE TABLE agent_bindings_new (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                agent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                request_id TEXT REFERENCES agent_binding_requests(id) ON DELETE SET NULL,
                agent_handle TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'revoked')),
                scopes_json TEXT NOT NULL DEFAULT '[]',
                workspace_roles_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                revoked_at TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO agent_bindings_new(
                id, user_id, agent_id, request_id, agent_handle, status,
                scopes_json, workspace_roles_json, created_at, revoked_at
            )
            SELECT
                id, user_id, agent_id, request_id, agent_handle, status,
                scopes_json, workspace_roles_json, created_at, revoked_at
            FROM agent_bindings
            """
        )
        conn.execute("DROP TABLE agent_bindings")
        conn.execute("ALTER TABLE agent_bindings_new RENAME TO agent_bindings")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_bindings_user ON agent_bindings(user_id, created_at DESC)")
    finally:
        conn.execute("PRAGMA foreign_keys=ON")


def check_ready(path: Path | None = None) -> dict[str, object]:
    try:
        init_db(path)
        conn = connect(path)
        try:
            objects = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master").fetchall()}
            missing_tables = [table for table in REQUIRED_TABLES if table not in objects]
            missing_columns = {
                table: [
                    column
                    for column in MIGRATED_COLUMNS.get(table, {})
                    if column not in {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
                ]
                for table in MIGRATED_COLUMNS
            }
            missing_columns = {table: columns for table, columns in missing_columns.items() if columns}
            smoke = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
            ok = not missing_tables and not missing_columns
            return {"ok": ok, "missing_tables": missing_tables, "missing_columns": missing_columns, "user_count": smoke}
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return {"ok": False, "missing_tables": REQUIRED_TABLES, "missing_columns": {}, "error": str(exc)}


@contextmanager
def db(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    conn = connect(path)
    try:
        yield conn
    finally:
        conn.close()
