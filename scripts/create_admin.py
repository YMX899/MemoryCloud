from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.db import db, init_db
from app.security import create_api_key, hash_api_key, hash_password, new_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle", default="admin")
    parser.add_argument("--email", default="admin@example.com")
    parser.add_argument("--display-name", default="Platform Admin")
    parser.add_argument("--password")
    parser.add_argument("--output", default=str(settings.data_root / "local_admin_credentials.txt"))
    args = parser.parse_args()

    password = args.password or "adm_" + secrets.token_urlsafe(18)
    init_db()
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE handle=? OR email=?", (args.handle, args.email)).fetchone()
        if row:
            user_id = row["id"]
            conn.execute(
                """
                UPDATE users
                SET display_name=?, email=?, password_hash=?, trust_level=10, disabled=0, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (args.display_name, args.email, hash_password(password), user_id),
            )
        else:
            user_id = new_id("usr")
            conn.execute(
                """
                INSERT INTO users(id, handle, display_name, email, password_hash, auth_type, trust_level)
                VALUES (?, ?, ?, ?, ?, 'human', 10)
                """,
                (user_id, args.handle, args.display_name, args.email, hash_password(password)),
            )
        raw_key, prefix, key_hash = create_api_key()
        conn.execute(
            "INSERT INTO api_keys(id, user_id, name, prefix, key_hash) VALUES (?, ?, 'admin automation', ?, ?)",
            (new_id("key"), user_id, prefix, key_hash),
        )

    output = Path(args.output).expanduser()
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                "记忆云管理员账号",
                f"handle={args.handle}",
                f"email={args.email}",
                f"password={password}",
                f"api_key={raw_key}",
                "",
                "登录后打开前端左侧「管理后台」。",
            ]
        ),
        encoding="utf-8",
    )
    output.chmod(0o600)
    print(f"admin ready: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
