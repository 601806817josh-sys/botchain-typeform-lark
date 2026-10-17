from __future__ import annotations

import unittest

from app.mapping import MappedSubmission, RouteRecord
from app.service import SubmissionService


class NotificationTextTests(unittest.TestCase):
    def test_notification_text_is_structured_and_actionable(self) -> None:
        mapped = MappedSubmission("response-1", "Demo Project", [], {}, [])
        route = RouteRecord("event", ("Chris", "Evan"), {})

        text = SubmissionService._notification_text(
            mapped,
            route,
            '<at user_id="chris">Chris</at> <at user_id="evan">Evan</at>',
            "https://example.com/record",
        )

        self.assertIn("【新申请待审核｜活动合作】", text)
        self.assertIn("项目名称：Demo Project", text)
        self.assertIn("审核负责人：Chris、Evan", text)
        self.assertIn("当前状态：待审核", text)
        self.assertIn("审核入口：https://example.com/record", text)
        self.assertIn("及时更新审核状态", text)
        self.assertNotIn("机器人接口", text)

    def test_notification_text_has_no_blank_first_line_without_mentions(self) -> None:
        mapped = MappedSubmission("response-1", "Demo Project", [], {}, [])
        route = RouteRecord("gas", ("Evan",), {})

        text = SubmissionService._notification_text(mapped, route, "", "https://example.com/record")

        self.assertTrue(text.startswith("【新申请待审核｜Gas 返佣】"))


if __name__ == "__main__":
    unittest.main()
