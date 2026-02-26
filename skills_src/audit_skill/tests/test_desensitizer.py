"""
Desensitization and sanitization tests.
"""
import sys
from pathlib import Path

import pytest

_skills_src = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_skills_src))

from audit_skill.desensitizer import (
    SENSITIVE_FIELDS,
    desensitize_dict,
    hash_for_reference,
    mask_string,
    sanitize_for_llm,
)


class TestDesensitizer:
    def test_mask_string(self) -> None:
        assert mask_string("1234567890", 4) == "******7890"
        assert mask_string("short", 4) == "*hort"

    def test_hash_deterministic(self) -> None:
        h1 = hash_for_reference("secret")
        h2 = hash_for_reference("secret")
        assert h1 == h2
        assert h1 != "secret"

    def test_desensitize_sensitive_fields(self) -> None:
        data = {
            "bank_account": "6222021234567890",
            "amount": 1000,
            "id_number": "310101199001011234",
        }
        out = desensitize_dict(data)
        assert out["bank_account"] != "6222021234567890"
        assert out["amount"] == 1000  # numeric non-PII preserved

    def test_sanitize_control_chars(self) -> None:
        raw = "hello\x00world\x1b\x7f"
        out = sanitize_for_llm(raw)
        assert "\x00" not in out
        assert "\x1b" not in out
