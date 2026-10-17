import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ENV_PATH = Path(os.environ.get("BOTCHAIN_ENV_PATH", Path(__file__).resolve().parent / ".env"))
SCHEMAS = {
    "总申请表": "master-fields.json",
    "生态扶持奖励": "ecosystem-fields.json",
    "Gas返佣": "gas-fields.json",
    "活动合作": "event-fields.json",
    "孵化加速": "incubation-fields.json",
}


def request(method, url, token=None, body=None):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    if result.get("code") != 0:
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    return result


def get_env_value(key):
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"{key} not found")


def get_token():
    result = request(
        "POST",
        "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal",
        body={"app_id": get_env_value("LARK_APP_ID"), "app_secret": get_env_value("LARK_APP_SECRET")},
    )
    return result["tenant_access_token"]


def api_path(table_id, suffix=""):
    root = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{get_env_value('LARK_BASE_TOKEN')}/tables/{table_id}"
    return root + suffix


def to_openapi_field(field):
    kind = field["type"]
    payload = {"field_name": field["name"], "type": 1}
    if kind == "select":
        payload["type"] = 4 if field.get("multiple") else 3
        payload["property"] = {"options": [{"name": item["name"]} for item in field.get("options", [])]}
    elif kind == "datetime":
        payload["type"] = 5
        payload["property"] = {"date_formatter": "yyyy-MM-dd HH:mm"}
    elif kind == "created_at":
        payload["type"] = 1001
        payload["property"] = {"date_formatter": "yyyy-MM-dd HH:mm"}
    elif kind == "updated_at":
        payload["type"] = 1002
        payload["property"] = {"date_formatter": "yyyy-MM-dd HH:mm"}
    # Reviewer, group, auto-number and link-like values stay text at this stage.
    # This keeps the webhook mapping stable before user/chat IDs and numbering rules
    # are finalized during the automation implementation step.
    return payload


def list_all(token, url):
    items = []
    page_token = None
    while True:
        joiner = "&" if "?" in url else "?"
        page_url = f"{url}{joiner}page_size=100"
        if page_token:
            page_url += "&page_token=" + urllib.parse.quote(page_token)
        data = request("GET", page_url, token=token)["data"]
        items.extend(data.get("items", []))
        if not data.get("has_more"):
            return items
        page_token = data["page_token"]


def main():
    token = get_token()
    tables = list_all(
        token,
        f"https://open.larksuite.com/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables",
    )
    by_name = {table["name"]: table["table_id"] for table in tables}
    missing = [name for name in SCHEMAS if name not in by_name]
    if missing:
        raise RuntimeError(f"Missing tables: {missing}")

    report = {}
    for table_name, schema_file in SCHEMAS.items():
        table_id = by_name[table_name]
        desired = json.loads((Path("schemas") / schema_file).read_text(encoding="utf-8"))
        current = list_all(token, api_path(table_id, "/fields"))

        if len(current) == 1 and current[0]["field_name"] == "文本":
            first = to_openapi_field(desired[0])
            request("PUT", api_path(table_id, f"/fields/{current[0]['field_id']}"), token, first)
            current[0]["field_name"] = first["field_name"]

        existing = {field["field_name"] for field in current}
        created = []
        for field in desired:
            if field["name"] in existing:
                continue
            payload = to_openapi_field(field)
            request("POST", api_path(table_id, "/fields"), token, payload)
            created.append(field["name"])
            existing.add(field["name"])

        final_fields = list_all(token, api_path(table_id, "/fields"))
        report[table_name] = {
            "table_id": table_id,
            "created": len(created),
            "field_count": len(final_fields),
            "fields": [field["field_name"] for field in final_fields],
        }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
