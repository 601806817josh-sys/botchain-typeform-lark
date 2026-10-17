from __future__ import annotations

import json
import threading
import time
from typing import Any

import requests


API_BASE = "https://open.larksuite.com/open-apis"


class LarkError(RuntimeError):
    pass


class LarkClient:
    def __init__(self, app_id: str, app_secret: str, base_token: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_token = base_token
        self._token = ""
        self._token_expires_at = 0.0
        self._lock = threading.Lock()

    @staticmethod
    def _parse(response: requests.Response, action: str) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise LarkError(f"{action}: invalid JSON (HTTP {response.status_code})") from exc
        if response.status_code >= 400 or data.get("code") != 0:
            raise LarkError(f"{action} failed (HTTP {response.status_code}): {data}")
        return data

    def token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._token_expires_at:
                return self._token
            response = requests.post(
                f"{API_BASE}/auth/v3/tenant_access_token/internal",
                json={"app_id": self.app_id, "app_secret": self.app_secret},
                timeout=20,
            )
            data = self._parse(response, "get tenant token")
            self._token = str(data["tenant_access_token"])
            self._token_expires_at = time.time() + max(60, int(data.get("expire", 7200)) - 300)
            return self._token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"}

    def create_record(self, table_id: str, fields: dict[str, Any]) -> str:
        response = requests.post(
            f"{API_BASE}/bitable/v1/apps/{self.base_token}/tables/{table_id}/records",
            headers=self._headers(),
            json={"fields": fields},
            timeout=30,
        )
        data = self._parse(response, f"create record in {table_id}")
        record_id = str((((data.get("data") or {}).get("record") or {}).get("record_id") or ""))
        if not record_id:
            raise LarkError(f"create record in {table_id}: missing record_id")
        return record_id

    def update_record(self, table_id: str, record_id: str, fields: dict[str, Any]) -> None:
        response = requests.put(
            f"{API_BASE}/bitable/v1/apps/{self.base_token}/tables/{table_id}/records/{record_id}",
            headers=self._headers(),
            json={"fields": fields},
            timeout=30,
        )
        self._parse(response, f"update record {record_id}")

    def delete_record(self, table_id: str, record_id: str) -> None:
        response = requests.delete(
            f"{API_BASE}/bitable/v1/apps/{self.base_token}/tables/{table_id}/records/{record_id}",
            headers=self._headers(),
            timeout=30,
        )
        self._parse(response, f"delete record {record_id}")

    def send_group_text(self, chat_id: str, text: str) -> str:
        response = requests.post(
            f"{API_BASE}/im/v1/messages",
            params={"receive_id_type": "chat_id"},
            headers=self._headers(),
            json={"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": text}, ensure_ascii=False)},
            timeout=30,
        )
        data = self._parse(response, "send group notification")
        message_id = str((((data.get("data") or {}).get("message_id")) or ""))
        if not message_id:
            raise LarkError("send group notification: missing message_id")
        return message_id


def people_value(open_ids: list[str]) -> list[dict[str, str]]:
    return [{"id": value} for value in open_ids if value]


def group_value(chat_id: str) -> list[dict[str, str]]:
    return [{"id": chat_id}] if chat_id else []


def at_mentions(owners: tuple[str, ...], owner_open_ids: dict[str, str]) -> str:
    return " ".join(
        f'<at user_id="{owner_open_ids[name]}">{name}</at>'
        for name in owners
        if owner_open_ids.get(name)
    )
