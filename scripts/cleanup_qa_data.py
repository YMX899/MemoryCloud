from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_ROOT = Path(os.getenv("DATA_ROOT", ".memorycloud-data")).expanduser()
DEFAULT_DB = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATA_ROOT / "platform.sqlite3"))).expanduser()
DEFAULT_ARCHIVES = Path(os.getenv("STORAGE_DIR", str(DEFAULT_DATA_ROOT / "archives"))).expanduser()
USER_PREFIXES = ("codex-", "cookie-", "logout-r2-", "e2e-human-", "e2e-agent-")
PACKAGE_PREFIXES = ("codex-", "e2e-", "quality-capsule")


def placeholders(values: list[str]) -> str:
    return ",".join(["?"] * len(values))


def prefixed_where(column: str, prefixes: tuple[str, ...]) -> tuple[str, list[str]]:
    return " OR ".join([f"{column} LIKE ?" for _ in prefixes]), [f"{prefix}%" for prefix in prefixes]


def collect(conn: sqlite3.Connection) -> dict[str, list[str]]:
    user_where, user_params = prefixed_where("handle", USER_PREFIXES)
    package_where, package_params = prefixed_where("slug", PACKAGE_PREFIXES)
    users = [row[0] for row in conn.execute(f"SELECT id FROM users WHERE {user_where}", user_params).fetchall()]
    packages = [
        row[0]
        for row in conn.execute(
            f"""
            SELECT id FROM memory_packages
            WHERE {package_where}
               OR owner_id IN ({placeholders(users) if users else "NULL"})
            """,
            (*package_params, *users),
        ).fetchall()
    ]
    workspaces = [
        row[0]
        for row in conn.execute(
            f"""
            SELECT id FROM workspaces
            WHERE name LIKE 'Codex%' OR slug LIKE 'codex-%'
               OR owner_id IN ({placeholders(users) if users else "NULL"})
            """,
            users,
        ).fetchall()
    ]
    adaptive_runs = [
        row[0]
        for row in conn.execute(
            f"""
            SELECT id FROM adaptive_memory_runs
            WHERE workspace_id IN ({placeholders(workspaces) if workspaces else "NULL"})
               OR user_id IN ({placeholders(users) if users else "NULL"})
            """,
            (*workspaces, *users),
        ).fetchall()
    ]
    adaptive_memories = [
        row[0]
        for row in conn.execute(
            f"""
            SELECT id FROM adaptive_memories
            WHERE workspace_id IN ({placeholders(workspaces) if workspaces else "NULL"})
               OR user_id IN ({placeholders(users) if users else "NULL"})
            """,
            (*workspaces, *users),
        ).fetchall()
    ]
    support = [
        row[0]
        for row in conn.execute(
            """
            SELECT id FROM support_tickets
            WHERE subject LIKE 'Smoke%' OR subject LIKE 'Quality%' OR message LIKE '%e2e%' OR message LIKE '%Smoke test%'
            """
        ).fetchall()
    ]
    reports = [
        row[0]
        for row in conn.execute(
            """
            SELECT id FROM abuse_reports
            WHERE reason IN ('smoke', 'quality', 'test') OR detail LIKE '%e2e%' OR detail LIKE '%Smoke test%'
            """
        ).fetchall()
    ]
    return {
        "users": users,
        "packages": packages,
        "workspaces": workspaces,
        "adaptive_memory_runs": adaptive_runs,
        "adaptive_memories": adaptive_memories,
        "support_tickets": support,
        "abuse_reports": reports,
    }


def delete_by_ids(conn: sqlite3.Connection, table: str, ids: list[str]) -> int:
    if not ids:
        return 0
    return conn.execute(f"DELETE FROM {table} WHERE id IN ({placeholders(ids)})", ids).rowcount


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean QA/deep-test data from the memory platform database.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--archives", type=Path, default=DEFAULT_ARCHIVES)
    parser.add_argument("--apply", action="store_true", help="Actually delete records. Default is dry-run.")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        found = collect(conn)
        print({key: len(value) for key, value in found.items()})
        if not args.apply:
            return 0
        backup = args.db.with_suffix(args.db.suffix + f".bak-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(args.db, backup)
        package_ids = list(found["packages"])
        removed = {
            "support_tickets": delete_by_ids(conn, "support_tickets", found["support_tickets"]),
            "abuse_reports": delete_by_ids(conn, "abuse_reports", found["abuse_reports"]),
            "adaptive_memories": delete_by_ids(conn, "adaptive_memories", found["adaptive_memories"]),
            "adaptive_memory_runs": delete_by_ids(conn, "adaptive_memory_runs", found["adaptive_memory_runs"]),
            "workspaces": delete_by_ids(conn, "workspaces", found["workspaces"]),
            "packages": delete_by_ids(conn, "memory_packages", found["packages"]),
            "users": delete_by_ids(conn, "users", found["users"]),
            "backup": str(backup),
        }
        for package_id in package_ids:
            archive_dir = args.archives / package_id
            if archive_dir.exists():
                shutil.rmtree(archive_dir, ignore_errors=True)
        conn.commit()
        print(removed)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
