# Security

## Secrets and production data

Do not commit credentials or production identifiers. Keep these values only in
the deployment environment or an approved secret manager:

- Typeform webhook secrets and production form IDs
- Lark app IDs, app secrets, Base tokens, table IDs, chat IDs, and user open IDs
- API keys, SSH keys, server addresses, passwords, and session files
- SQLite databases, webhook payloads, logs, exports, and deployment archives

Use `.env.example` only as a template. The real `.env` is intentionally ignored
by Git.

If a secret is committed, remove it from Git history and rotate it immediately.
Deleting it in a later commit is not sufficient.

## Reporting

Please report suspected credential exposure privately to the repository owner.
Do not open a public issue containing secrets or production data.
