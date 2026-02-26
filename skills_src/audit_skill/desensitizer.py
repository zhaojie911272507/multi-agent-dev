"""
Data desensitization — MUST run before any AI logic.
PII and sensitive fields are masked before entering LLM context.
"""
import hashlib
import re
from typing import Any


def mask_string(value: str, keep_tail: int = 4) -> str:
    """Mask string, keep last N chars for reference."""
    if len(value) <= keep_tail:
        return "*" * len(value)
    return "*" * (len(value) - keep_tail) + value[-keep_tail:]


def hash_for_reference(value: str) -> str:
    """One-way hash for traceability without exposing raw data."""
    return hashlib.sha256(value.encode()).hexdigest()[:12]


# Fields to desensitize (configurable)
SENSITIVE_FIELDS = {
    "bank_account",
    "id_number",
    "phone",
    "email",
    "address",
    "supplier_name",  # optional: some orgs want to mask
}


def desensitize_dict(
    data: dict[str, Any],
    sensitive_fields: set[str] | None = None,
    mask_mode: str = "mask",
) -> dict[str, Any]:
    """
    Recursively desensitize dict. In-place style; returns copy.
    mask_mode: "mask" (show tail) | "hash" (replace with hash)
    """
    sensitive = sensitive_fields or SENSITIVE_FIELDS
    result: dict[str, Any] = {}

    for k, v in data.items():
        key_lower = k.lower()
        if any(sf in key_lower for sf in sensitive):
            if isinstance(v, str):
                result[k] = hash_for_reference(v) if mask_mode == "hash" else mask_string(v)
            elif isinstance(v, (int, float)):
                result[k] = "***"
            else:
                result[k] = "[REDACTED]"
        elif isinstance(v, dict):
            result[k] = desensitize_dict(v, sensitive, mask_mode)
        elif isinstance(v, list):
            result[k] = [
                desensitize_dict(x, sensitive, mask_mode) if isinstance(x, dict) else x
                for x in v
            ]
        else:
            result[k] = v

    return result


def desensitize_db_uri(uri: str) -> str:
    """
    Desensitize database connection URI (password, db name).
    Example: mysql://root:secret@host:3306/dbname -> mysql://root:****@host:3306/****
    """
    # mysql://user:pass@host:port/db or postgres://user:pass@host:port/db
    m = re.match(
        r"^(\w+://)([^:]+):([^@]+)@([^/]+)(/.+)?$",
        uri.strip(),
    )
    if not m:
        return "***"  # 无法解析则全掩
    scheme, user, _pass, host_port, path = m.groups()
    path_masked = "/****" if path else ""
    return f"{scheme}{user}:****@{host_port}{path_masked}"


def sanitize_for_llm(text: str) -> str:
    """Remove potential injection / illegal chars before LLM."""
    # Strip control chars
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    # Limit length for safety
    return text[:50000] if len(text) > 50000 else text
