from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_ROOT = Path(os.getenv("DATA_ROOT", str(BASE_DIR / ".memorycloud-data"))).expanduser()


@dataclass(frozen=True)
class Settings:
    app_name: str = "记忆云"
    app_env: str = os.getenv("APP_ENV", "development")
    public_site_origin: str = os.getenv("PUBLIC_SITE_ORIGIN", "http://127.0.0.1:8000")
    secret_key: str = os.getenv("SECRET_KEY", "dev-change-me-before-production")
    data_root: Path = DEFAULT_DATA_ROOT
    db_path: Path = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATA_ROOT / "platform.sqlite3"))).expanduser()
    storage_dir: Path = Path(os.getenv("STORAGE_DIR", str(DEFAULT_DATA_ROOT / "archives"))).expanduser()
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(15 * 1024 * 1024)))
    pow_difficulty: int = int(os.getenv("POW_DIFFICULTY", "4"))
    sms_api_base: str = os.getenv("SMS_API_BASE", "https://api.fenxianglife.com/fenxiang-ai-brain/skill/api/sms/code")
    sms_api_key: str = os.getenv("FX_AI_API_KEY", "")
    sms_dry_run: bool = os.getenv("SMS_DRY_RUN", "true").lower() == "true"
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
    smtp_ssl: bool = os.getenv("SMTP_SSL", "false").lower() == "true"
    smtp_tls: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    email_dry_run: bool = os.getenv("EMAIL_DRY_RUN", "false").lower() == "true"
    llm_provider_config: Path = Path(os.getenv("LLM_PROVIDER_CONFIG", str(DEFAULT_DATA_ROOT / "llm_provider.json"))).expanduser()
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))

    @property
    def production(self) -> bool:
        return self.app_env.lower() == "production"


settings = Settings()
