from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_env: str
    log_level: str
    sqlite_path: Path
    typeform_form_id: str
    typeform_webhook_secret: str
    lark_app_id: str
    lark_app_secret: str
    lark_base_token: str
    lark_master_table_id: str
    table_ids: dict[str, str]
    notifications_enabled: bool
    notification_chat_id: str
    owner_open_ids: dict[str, str]
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str

    @classmethod
    def from_env(cls, *, require_runtime_secrets: bool = True) -> "Settings":
        load_dotenv()
        get = lambda key, default="": os.getenv(key, default).strip()
        get_bool = lambda key, default="false": get(key, default).lower() in {"1", "true", "yes", "on"}
        settings = cls(
            app_env=get("APP_ENV", "development"),
            log_level=get("LOG_LEVEL", "INFO"),
            sqlite_path=Path(get("SQLITE_PATH", "data/typeform_lark.sqlite3")),
            typeform_form_id=get("TYPEFORM_FORM_ID"),
            typeform_webhook_secret=get("TYPEFORM_WEBHOOK_SECRET"),
            lark_app_id=get("LARK_APP_ID"),
            lark_app_secret=get("LARK_APP_SECRET"),
            lark_base_token=get("LARK_BASE_TOKEN"),
            lark_master_table_id=get("LARK_MASTER_TABLE_ID"),
            table_ids={
                "ecosystem": get("LARK_ECOSYSTEM_TABLE_ID"),
                "gas": get("LARK_GAS_TABLE_ID"),
                "event": get("LARK_EVENT_TABLE_ID"),
                "incubation": get("LARK_INCUBATION_TABLE_ID"),
            },
            notifications_enabled=get_bool("LARK_NOTIFICATIONS_ENABLED"),
            notification_chat_id=get("LARK_NOTIFICATION_CHAT_ID"),
            owner_open_ids={
                "Evan": get("LARK_OWNER_EVAN_OPEN_ID"),
                "Chris": get("LARK_OWNER_CHRIS_OPEN_ID"),
                "Moses": get("LARK_OWNER_MOSES_OPEN_ID"),
            },
            deepseek_api_key=get("DEEPSEEK_API_KEY"),
            deepseek_base_url=get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            deepseek_model=get("DEEPSEEK_MODEL", "deepseek-chat"),
        )
        if require_runtime_secrets:
            missing = []
            for key, value in {
                "TYPEFORM_FORM_ID": settings.typeform_form_id,
                "TYPEFORM_WEBHOOK_SECRET": settings.typeform_webhook_secret,
                "LARK_APP_ID": settings.lark_app_id,
                "LARK_APP_SECRET": settings.lark_app_secret,
                "LARK_BASE_TOKEN": settings.lark_base_token,
                "LARK_MASTER_TABLE_ID": settings.lark_master_table_id,
                "LARK_ECOSYSTEM_TABLE_ID": settings.table_ids["ecosystem"],
                "LARK_GAS_TABLE_ID": settings.table_ids["gas"],
                "LARK_EVENT_TABLE_ID": settings.table_ids["event"],
                "LARK_INCUBATION_TABLE_ID": settings.table_ids["incubation"],
            }.items():
                if not value:
                    missing.append(key)
            if settings.notifications_enabled and not settings.notification_chat_id:
                missing.append("LARK_NOTIFICATION_CHAT_ID")
            if missing:
                raise RuntimeError("Missing required environment variables: " + ", ".join(missing))
        return settings
