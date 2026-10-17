from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any


REF = {
    "project_name": "2cd80287-b393-49ad-a16f-7aa6603b7530",
    "website": "1b45ecb6-a880-47c6-89ca-a78d8967f57f",
    "intro": "ff846ed7-4d94-4fb7-ae60-e7c8f3724e38",
    "category": "6d6c7c12-2a0f-4dad-9d3f-8fff94a1d27f",
    "social": "b3a217ac-aec6-4178-b6e9-f2332032fb70",
    "deployed": "a53d7437-ceb2-4961-8bc8-4e6757fd2e5f",
    "core_contract": "042d367c-168d-46c9-9409-dbced0a32a2b",
    "bd": "a89a608c-0e18-431a-a271-f9f763af09c4",
    "contact": "187249bc-d5a8-45ce-a5f1-def33655430e",
    "team_5": "a11f7e90-4183-45bb-8c87-ef22de6f37c4",
    "new_project": "b33db1bf-b700-471b-a692-80705f0ec349",
    "application_type": "976ad150-fe39-4a2f-ad5e-56e4a7f0e86b",
    "token_issued": "a5dab5a8-fc56-45b1-afd6-cf27802c8a0e",
    "support_path": "f1dab07c-4a23-4204-b298-5e2ccf1a09a5",
    "pair_link": "5c50b73a-b89b-4215-94d6-84332097a562",
    "pair_type": "480156bd-d093-4c2e-9c2d-25f1aef91af5",
    "pair_contract": "bc4bd648-f63e-4bc9-b177-58d189c9dd34",
    "native": "ef7c576d-ea50-4bf7-ac24-efd3087f010e",
    "exchange": "66c13656-cf57-40b3-ae15-a6ccb4f66a54",
    "bdex_link": "15b27c5a-88d1-40e1-b606-32462319ff29",
    "listing": "983c9ae4-cbf5-4baf-b230-3e9b6bd11f44",
    "business_contract": "dbbe26e1-d568-432f-af8d-919a7701a624",
    "is_defi": "df0ec4d8-4666-4875-ab4b-643b57ad9de4",
    "tvl": "f45d8000-6e5d-4325-82eb-abf402aa22ec",
    "user_sources": "76bda543-9e7e-4de8-bd95-ac9c971db1e9",
    "growth_plan": "60b8405a-1786-447a-b0ac-a98885c605c4",
    "gas_contract": "364f0ab7-2040-4fa0-8be4-5acdd7fcb1b4",
    "gas_threshold": "c62e07a3-58ce-4590-8804-0f8cf5188aa3",
    "rebate_wallet": "33eeeb97-051b-4479-bc23-533ad7f57290",
    "event_name": "a0102ec8-4a39-4266-9adc-8580273a6b4d",
    "event_type": "c7103ff3-e99a-41e5-a18f-bdc52df1500e",
    "campaign_plan": "66ab47c6-3fe5-4ba0-b25f-a850c9a3c4b5",
    "user_tasks": "fd42b82b-4665-45ef-bb41-29e9f9a3ea31",
    "budget": "7d37ff09-3da3-4fe9-b2fd-40b8ee54677a",
    "budget_format": "cb67d919-06e7-49fb-b6da-d5689ba99d93",
    "chain_value": "97c302bf-75a6-4180-8b89-86a925c89353",
    "expected": "556b3a8a-64bd-41ec-8771-059320e4f586",
    "roi": "bed70112-d956-44fe-8056-76efc216ef04",
    "cases": "1bcb299a-69a3-4e92-8495-390a2beecba8",
    "twitter_5000": "a0c9e352-5fda-43d7-9fd4-5ba629974f60",
    "gas_30_bot": "b37372b1-2b9d-4507-b762-637facbe47e6",
    "active_growth": "e518aacd-924e-4bef-b726-c0521f2381de",
    "other_support": "5f1b5ca1-9331-462c-8ca7-b63112795416",
    "other_support_detail": "bd6e1a25-c0e3-4e16-be3b-a1a8c3c1e680",
}

ROUTES = {
    "生态扶持奖励 / Ecosystem Support Incentive": ("ecosystem", ("Evan",)),
    "Gas返佣 / Gas Rebate": ("gas", ("Evan",)),
    "活动合作 / Event Collaboration": ("event", ("Chris", "Evan")),
    "孵化加速 / Incubation Accelerator": ("incubation", ("Moses",)),
}


@dataclass(frozen=True)
class RouteRecord:
    route: str
    owners: tuple[str, ...]
    fields: dict[str, Any]


…11306 tokens truncated…ent(settings.lark_app_id, settings.lark_app_secret, settings.lark_base_token)
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

