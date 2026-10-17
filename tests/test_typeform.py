from __future__ import annotations

import base64
import hashlib
import hmac
import unittest

from app.typeform import answer_value, verify_signature


class TypeformTests(unittest.TestCase):
    def test_signature_verification(self) -> None:
        body = b'{"hello":"world"}'
        secret = "secret"
        signature = "sha256=" + base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()
        self.assertTrue(verify_signature(body, signature, secret))
        self.assertFalse(verify_signature(body + b"x", signature, secret))

    def test_choices_are_preserved_in_order(self) -> None:
        self.assertEqual(answer_value({"type": "choices", "choices": {"labels": ["A", "B"]}}), ["A", "B"])
