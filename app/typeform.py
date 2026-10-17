from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any


class TypeformPayloadError(ValueError):
    pass


def verify_signature(raw_body: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
    expected = "sha256=" + base64.b64encode(digest).decode("ascii")
    return hmac.compare_digest(expected, signature)


def answer_value(answer: dict[str, Any]) -> Any:
    answer_type = answer.get("type")
    if answer_type in {"text", "email", "url", "date", "number", "boolean"}:
        return answer.get(answer_type)
    if answer_type == "choice":
        choice = answer.get("choice") or {}
        return choice.get("label") or choice.get("other")
    if answer_type == "choices":
        choices = answer.get("choices") or {}
        labels = list(choices.get("labels") or [])
        if choices.get("other"):
            labels.append(choices["other"])
        return labels
    if answer_type == "file_url":
        return answer.get("file_url")
    return answer.get(answer_type) if answer_type else None


def parse_webhook(payload: dict[str, Any], expected_form_id: str) -> dict[str, Any]:
    response = payload.get("form_response") or {}
    form_id = str((response.get("form_id") or "")).strip()
    if form_id != expected_form_id:
        raise TypeformPayloadError(f"Unexpected form_id: {form_id!r}")
    response_token = str(response.get("token") or "").strip()
    if not response_token:
        raise TypeformPayloadError("Missing form_response.token")

    answers: dict[str, Any] = {}
    for answer in response.get("answers") or []:
        ref = str(((answer.get("field") or {}).get("ref") or "")).strip()
        if ref:
            answers[ref] = answer_value(answer)

    return {
        "response_token": response_token,
        "form_id": form_id,
        "submitted_at": response.get("submitted_at"),
        "answers": answers,
        "raw": payload,
    }

