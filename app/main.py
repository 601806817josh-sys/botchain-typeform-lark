from __future__ import annotations

import logging

from fastapi import FastAPI, Header, HTTPException, Request

from app.config import Settings
from app.lark import LarkClient
from app.service import SubmissionService
from app.store import EventStore
from app.typeform import TypeformPayloadError, verify_signature


settings = Settings.from_env()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s %(message)s")
store = EventStore(settings.sqlite_path)
lark = LarkClient(settings.lark_app_id, settings.lark_app_secret, settings.lark_base_token)
service = SubmissionService(settings, lark, store)
app = FastAPI(title="BOT Chain Typeform → Lark", version="1.0.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhooks/typeform")
async def typeform_webhook(request: Request, typeform_signature: str | None = Header(default=None)) -> dict[str, object]:
    raw = await request.body()
    if not verify_signature(raw, typeform_signature, settings.typeform_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid Typeform signature")
    try:
        payload = await request.json()
        return service.process_payload(payload)
    except TypeformPayloadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # Typeform retries non-2xx responses.
        logging.exception("Webhook processing failed")
        raise HTTPException(status_code=503, detail=str(exc)) from exc

