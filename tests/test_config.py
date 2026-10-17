from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.config import Settings


class ConfigTests(unittest.TestCase):
    required_env = {
        "TYPEFORM_FORM_ID": "test-form-id",
        "TYPEFORM_WEBHOOK_SECRET": "test-webhook-secret",
        "LARK_APP_ID": "test-app-id",
        "LARK_APP_SECRET": "test-app-secret",
        "LARK_BASE_TOKEN": "test-base-token",
        "LARK_MASTER_TABLE_ID": "test-master-table",
        "LARK_ECOSYSTEM_TABLE_ID": "test-ecosystem-table",
        "LARK_GAS_TABLE_ID": "test-gas-table",
        "LARK_EVENT_TABLE_ID": "test-event-table",
        "LARK_INCUBATION_TABLE_ID": "test-incubation-table",
    }

    def test_group_and_chris_are_optional_when_notifications_are_disabled(self) -> None:
        env = {
            **self.required_env,
            "LARK_NOTIFICATIONS_ENABLED": "false",
            "LARK_NOTIFICATION_CHAT_ID": "",
            "LARK_OWNER_CHRIS_OPEN_ID": "",
        }
        with patch.dict(os.environ, env, clear=False):
            settings = Settings.from_env()
        self.assertFalse(settings.notifications_enabled)
        self.assertEqual(settings.notification_chat_id, "")
        self.assertEqual(settings.owner_open_ids["Chris"], "")

    def test_group_is_required_when_notifications_are_enabled(self) -> None:
        env = {
            **self.required_env,
            "LARK_NOTIFICATIONS_ENABLED": "true",
            "LARK_NOTIFICATION_CHAT_ID": "",
        }
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaisesRegex(RuntimeError, "LARK_NOTIFICATION_CHAT_ID"):
                Settings.from_env()
