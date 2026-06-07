from __future__ import annotations

import json
import urllib.error
import urllib.request

from .config import settings


class SmsError(RuntimeError):
    pass


def send_sms_code(mobile: str, code: str) -> dict[str, object]:
    if settings.sms_dry_run:
        return {"dry_run": True, "provider": "fenxianglife", "mobile": mobile, "debug_code": code}
    if not settings.sms_api_key:
        raise SmsError("FX_AI_API_KEY is required when SMS_DRY_RUN=false")
    payload = json.dumps({"mobile": mobile, "checkCode": code}).encode("utf-8")
    request = urllib.request.Request(
        settings.sms_api_base,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Fx-Ai-Api-Key": f"Bearer {settings.sms_api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"dry_run": False, "status": response.status, "body": body[:500]}
    except urllib.error.URLError as exc:
        raise SmsError(str(exc)) from exc
