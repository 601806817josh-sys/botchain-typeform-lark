"""Create the local .env without printing or committing secrets.

Usage:
  python scripts/bootstrap_env.py PATH_TO_EXISTING_BOT_ENV
"""

from __future__ import annotations

import secrets
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Pass the existing bot .env path")
    source = read_env(Path(sys.argv[1]))
    form_id = os.environ.get("TYPEFORM_FORM_ID", "").strip()
    if not form_id:
        raise SystemExit("Set TYPEFORM_FORM_ID in the environment before running this script")
    required = [
        "LARK_APP_ID",
        "LARK_APP_SECRET",
        "LARK_BASE_TOKEN",
        "LARK_MASTER_TABLE_ID",
        "LARK_ECOSYSTEM_TABLE_ID",
        "LARK_GAS_TABLE_ID",
        "LARK_EVENT_TABLE_ID",
        "LARK_INCUBATION_TABLE_ID",
    ]
    missing = [key for key in required if not source.get(key)]
    if missing:
        raise SystemExit("Source env is missing: " + ", ".join(missing))

    output = f"""APP_ENV=development
LOG_LEVEL=INFO
SQLITE_PATH=data/typeform_lark.sqlite3

TYPEFORM_FORM_ID={form_id}
TYPEFORM_WEBHOOK_SECRET={secrets.token_urlsafe(48)}

LARK_APP_ID={source['LARK_APP_ID']}
LARK_APP_SECRET={source['LARK_APP_SECRET']}
LARK_BASE_TOKEN={source['LARK_BASE_TOKEN']}
LARK_MASTER_TABLE_ID={source.get('LARK_MASTER_TABLE_ID', '')}
LARK_ECOSYSTEM_TABLE_ID={source.get('LARK_ECOSYSTEM_TABLE_ID', '')}
LARK_GAS_TABLE_ID={source.get('LARK_GAS_TABLE_ID', '')}
LARK_EVENT_TABLE_ID={source.get('LARK_EVENT_TABLE_ID', '')}
LARK_INCUBATION_TABLE_ID={source.get('LARK_INCUBATION_TABLE_ID', '')}

LARK_NOTIFICATION_CHAT_ID=
LARK_OWNER_EVAN_OPEN_ID=
LARK_OWNER_CHRIS_OPEN_ID=
LARK_OWNER_MOSES_OPEN_ID=

DEEPSEEK_API_KEY={source.get('DEEPSEEK_API_KEY', '')}
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
"""
    target = ROOT / ".env"
    target.write_text(output, encoding="utf-8", newline="\n")
    print(f"Created {target} with secrets redacted from output")


if __name__ == "__main__":
    main()
