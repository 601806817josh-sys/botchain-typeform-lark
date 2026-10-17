"""Create and delete one representative record in every Lark table.

This does not send any group message. Every created record is deleted in finally.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.lark import LarkClient, group_value, people_value  # noqa: E402
from app.mapping import REF, map_submission  # noqa: E402


def main() -> None:
    settings = Settings.from_env(require_runtime_secrets=False)
    lark = LarkClient(settings.lark_app_id, settings.lark_app_secret, settings.lark_base_token)
    token = "SMOKE-" + uuid.uuid4().hex[:12]
    answers = {
        REF["project_name"]: token,
        REF["website"]: "https://example.com",
        REF["intro"]: "Automated mapping smoke test",
        REF["category"]: "DeFi",
        REF["social"]: "https://x.com/example",
        REF["deployed"]: "是 / Yes",
        REF["core_contract"]: "0x0000000000000000000000000000000000000000",
        REF["bd"]: "Smoke Test",
        REF["contact"]: "smoke@example.com",
        REF["team_5"]: "是 / Yes",
        REF["new_project"]: "是 / Yes",
        REF["application_type"]: list({
            "生态扶持奖励 / Ecosystem Support Incentive",
            "Gas返佣 / Gas Rebate",
            "活动合作 / Event Collaboration",
            "孵化加速 / Incubation Accelerator",
        }),
        REF["token_issued"]: "已发币 / Token Issued",
        REF["support_path"]: "DEX激励 / DEX Incentive",
        REF["pair_link"]: "https://example.com/pair",
        REF["pair_type"]: "BOT/USDT",
        REF["pair_contract"]: "0x1111111111111111111111111111111111111111",
        REF["native"]: "是 / Yes",
        REF["exchange"]: "Example Exchange",
        REF["bdex_link"]: "https://example.com/bdex-pair",
        REF["listing"]: "https://example.com/announcement",
        REF["business_contract"]: "0x2222222222222222222222222222222222222222",
        REF["is_defi"]: "是 / Yes",
        REF["tvl"]: "1200",
        REF["user_sources"]: "Community",
        REF["growth_plan"]: "Grow active users",
        REF["gas_contract"]: "0x3333333333333333333333333333333333333333",
        REF["gas_threshold"]: "是 / Yes",
        REF["rebate_wallet"]: "0x4444444444444444444444444444444444444444",
        REF["event_name"]: "Smoke Event",
        REF["event_type"]: "Online",
        REF["campaign_plan"]: "Test plan",
        REF["user_tasks"]: "Test task",
        REF["budget"]: "5000",
        REF["budget_format"]: "BOT",
        REF["chain_value"]: "Test chain value",
        REF["expected"]: "1000 active addresses",
        REF["roi"]: "300 valid cross-chain transactions",
        REF["cases"]: "Previous project",
        REF["twitter_5000"]: "是 / Yes",
        REF["gas_30_bot"]: "是 / Yes",
        REF["active_growth"]: "是 / Yes",
        REF["other_support"]: "否 / No",
    }
    parsed = {
        "response_token": token,
        "form_id": settings.typeform_form_id,
        "submitted_at": "2026-09-29T12:00:00Z",
        "answers": answers,
        "raw": {"smoke_test": True, "token": token},
    }
    mapped = map_submission(parsed)
    created: list[tuple[str, str]] = []
    try:
        master_id = lark.create_record(settings.lark_master_table_id, mapped.master_fields)
        created.append((settings.lark_master_table_id, master_id))
        for route in mapped.routes:
            fields = dict(route.fields)
            fields["关联总申请"] = [master_id]
            known_owner_ids = [settings.owner_open_ids[name] for name in route.owners if settings.owner_open_ids.get(name)]
            if known_owner_ids:
                fields["审核负责人"] = people_value(known_owner_ids)
            fields["通知群"] = group_value(settings.notification_chat_id)
            record_id = lark.create_record(settings.table_ids[route.route], fields)
            created.append((settings.table_ids[route.route], record_id))
        print(f"PASS: created {len(created)} linked records across all five tables")
    finally:
        for table_id, record_id in reversed(created):
            lark.delete_record(table_id, record_id)
        if created:
            print(f"CLEANUP: deleted {len(created)} smoke-test records")


if __name__ == "__main__":
    main()

