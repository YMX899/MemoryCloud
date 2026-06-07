from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from .config import settings


def now_ts() -> int:
    return int(time.time())


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    rounds = 260_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return f"pbkdf2_sha256${rounds}${b64url(salt)}${b64url(digest)}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        algo, rounds_s, salt_s, digest_s = stored.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        rounds = int(rounds_s)
        salt = b64url_decode(salt_s)
        expected = b64url_decode(digest_s)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def sign_token(payload: dict[str, Any], ttl_seconds: int = 86_400) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    body = dict(payload)
    body["exp"] = now_ts() + ttl_seconds
    body["iat"] = now_ts()
    body.setdefault("jti", new_id("jti"))
    encoded_header = b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_body = b64url(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_body}".encode("ascii")
    sig = hmac.new(settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_body}.{b64url(sig)}"


def verify_token(token: str, expected_type: str | None = None) -> dict[str, Any] | None:
    try:
        encoded_header, encoded_body, encoded_sig = token.split(".", 2)
        signing_input = f"{encoded_header}.{encoded_body}".encode("ascii")
        expected_sig = hmac.new(settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(b64url_decode(encoded_sig), expected_sig):
            return None
        payload = json.loads(b64url_decode(encoded_body))
        if int(payload.get("exp", 0)) < now_ts():
            return None
        if expected_type and payload.get("type") != expected_type:
            return None
        return payload
    except Exception:
        return None


def create_api_key() -> tuple[str, str, str]:
    raw = "amp_live_" + secrets.token_urlsafe(32)
    prefix = raw[:18]
    return raw, prefix, hash_api_key(raw)


def hash_api_key(api_key: str) -> str:
    pepper = settings.secret_key.encode("utf-8")
    return hmac.new(pepper, api_key.encode("utf-8"), hashlib.sha256).hexdigest()


def proof_of_work_digest(challenge_id: str, server_nonce: str, nonce: str) -> str:
    return hashlib.sha256(f"{challenge_id}:{server_nonce}:{nonce}".encode("utf-8")).hexdigest()


def verify_proof_of_work(challenge_id: str, server_nonce: str, nonce: str, difficulty: int) -> bool:
    digest = proof_of_work_digest(challenge_id, server_nonce, nonce)
    return digest.startswith("0" * difficulty)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
