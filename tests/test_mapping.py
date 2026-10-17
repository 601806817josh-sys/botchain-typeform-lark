from __future__ import annotations

import json
import unittest

from app.mapping import REF, map_submission
from app.typeform import parse_webhook


def answer(ref: str, value: object) -> dict:
    if isinstance(value, list):
        return {"field": {"ref": ref}, "type": "choices", "choices": {"labels": value}}
    if isinstance(value, (int, float)):
        return {"field": {"ref": ref}, "type": "number", "number": value}
    return {"field": {"ref": ref}, "type": "text", "text": value}


def payload(values: dict[str, object], token: str = "response-1") -> dict:
    return {
        "event_type": "form_response",
        "form_response": {
            "form_id": "test-form-id",
            "token": token,
            "submitted_at": "2026-09-29T12:00:00Z",
            "answers": [answer(REF[key], value) for key, value in values.items()],
        },
    }


class MappingTests(unittest.TestCase):
    def test_multiselect_routes_to_every_table_and_owner(self) -> None:
        raw = payload(
        {
            "project_name": "Demo",
            "application_type": [
                "生态扶持奖励 / Ecosystem Support Incentive",
                "Gas返佣 / Gas Rebate",
                "活动合作 / Event Collaboration",
                "孵化加速 / Incubation Accelerator",
            ],
            "support_path": "DEX激励 / DEX Incentive",
            "tvl": "1,200 USDT",
            "budget": "5000 BOT",
            "team_5": "是 / Yes",
            "new_project": "否 / No",
        }
    )
        mapped = map_submission(parse_webhook(raw, "test-form-id"))
        self.assertEqual([item.route for item in mapped.routes], ["ecosystem", "gas", "event", "incubation"])
        self.assertEqual(mapped.routes[0].owners, ("Evan",))
        self.assertEqual(mapped.routes[1].owners, ("Evan",))
        self.assertEqual(mapped.routes[2].owners, ("Chris", "Evan"))
        self.assertEqual(mapped.routes[3].owners, ("Moses",))
        self.assertEqual(mapped.routes[0].fields["扶持路径 / Support Path"], "DEX 激励 / DEX Incentive")
        self.assertEqual(mapped.routes[0].fields["TVL / Total Value Locked"], 1200.0)
        self.assertIn("TVL 原始填写值", mapped.routes[0].fields["内部备注 / Internal Notes"])
        self.assertEqual(mapped.routes[2].fields["预算 / Budget"], 5000.0)

    def test_each_application_type_has_exact_route(self) -> None:
        cases = [
            ("生态扶持奖励 / Ecosystem Support Incentive", "ecosystem", ("Evan",)),
            ("Gas返佣 / Gas Rebate", "gas", ("Evan",)),
            ("活动合作 / Event Collaboration", "event", ("Chris", "Evan")),
            ("孵化加速 / Incubation Accelerator", "incubation", ("Moses",)),
        ]
        for application_type, route, owners in cases:
            with self.subTest(application_type=application_type):
                raw = payload({"project_name": "Demo", "application_type": [application_type]})
                mapped = map_submission(parse_webhook(raw, "test-form-id"))
                self.assertEqual(len(mapped.routes), 1)
                self.assertEqual(mapped.routes[0].route, route)
                self.assertEqual(mapped.routes[0].owners, owners)

    def test_unknown_application_type_fails_closed(self) -> None:
        raw = payload({"project_name": "Demo", "application_type": ["Unknown"]})
        with self.assertRaisesRegex(ValueError, "Unknown application type"):
            map_submission(parse_webhook(raw, "test-form-id"))

    def test_raw_payload_is_preserved(self) -> None:
        raw = payload({"project_name": "Demo", "application_type": ["Gas返佣 / Gas Rebate"]})
        mapped = map_submission(parse_webhook(raw, "test-form-id"))
        self.assertEqual(json.loads(mapped.master_fields["Typeform 原始响应 JSON"]), raw)

    def test_common_fields_stay_in_master_instead_of_being_duplicated(self) -> None:
        raw = payload(
            {
                "project_name": "Demo",
                "website": "https://example.com",
                "contact": "alice@example.com",
                "bd": "Evan",
                "application_type": ["活动合作 / Event Collaboration"],
            }
        )
        mapped = map_submission(parse_webhook(raw, "test-form-id"))
        self.assertEqual(mapped.master_fields["Typeform 提交 ID"], "response-1")
        self.assertEqual(mapped.master_fields["官网 / Official Website"]["link"], "https://example.com")
        self.assertEqual(mapped.master_fields["项目方联系人 / Project Team Contact"], "alice@example.com")
        self.assertEqual(mapped.master_fields["对接 BD / BD Contact"], "Evan")
        fields = mapped.routes[0].fields
        self.assertNotIn("Typeform 提交 ID", fields)
        self.assertNotIn("官网 / Official Website", fields)
        self.assertNotIn("项目方联系人 / Project Team Contact", fields)
