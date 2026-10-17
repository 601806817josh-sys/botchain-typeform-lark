# BOT Chain Typeform → Lark

This service receives a configured Typeform webhook, maps every answer by immutable Typeform field `ref`, writes the common data to the Lark master table, writes each selected application type to its own business table, and then notifies the review group with real Lark `@` mentions.

## Fixed routing

| Typeform application type | Business table | Reviewer |
|---|---|---|
| 生态扶持奖励 | 生态扶持奖励 | Evan |
| Gas返佣 | Gas返佣 | Evan |
| 活动合作 | 活动合作 | Chris, Evan |
| 孵化加速 | 孵化加速 | Moses |

Multiple selections create one master record and one linked record in every selected business table. Mapping is deterministic; DeepSeek is not used to decide fields or routes.

## Reliability rules

- Verify the `Typeform-Signature` HMAC before processing.
- Reject any unexpected form ID or unknown application type.
- Store the Typeform response token in SQLite as the idempotency key.
- Resume partially completed multi-table writes without recreating successful records.
- Notify only after the corresponding business record exists.
- Store the Lark message ID before final status synchronization to avoid duplicate notifications on retry.
- Preserve the complete raw Typeform payload in the master table.

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Configure Typeform to POST to `https://YOUR_DOMAIN/webhooks/typeform` using the same secret as `TYPEFORM_WEBHOOK_SECRET`.

Set `LARK_NOTIFICATIONS_ENABLED=false` until the notification group is ready. In this mode, submissions are written to the master and business tables and remain `待通知`; no group message is sent. Add the group ID and set the flag to `true` when notifications are ready.

Run tests:

```powershell
.venv\Scripts\python -m unittest discover -v
```

## Environment

Copy `.env.example` to `.env`. Never commit `.env`.

- Typeform: form ID and webhook signature secret.
- Lark: app credentials, Base token, five table IDs, notification chat ID, and reviewer open IDs.
- DeepSeek: key/base URL/model are kept for later auxiliary features only; they do not control routing.

## Endpoints

- `GET /healthz`
- `POST /webhooks/typeform`
