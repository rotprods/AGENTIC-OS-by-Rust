from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any

from .canonical_json import canonicalize

TOKEN = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")


def _require_raw(value: str, label: str, max_length: int) -> str:
    if not value:
        raise TypeError(f"{label}: empty")
    if len(value) > max_length:
        raise TypeError(f"{label}: too long")
    if value.strip() != value:
        raise TypeError(f"{label}: surrounding whitespace")
    if any(ord(char) <= 0x1F or ord(char) == 0x7F for char in value):
        raise TypeError(f"{label}: control character")
    return value


def _normalize_token(value: str, label: str) -> str:
    raw = _require_raw(value, label, 128)
    if not raw.isascii():
        raise TypeError(f"{label}: token non-ASCII")
    normalized = raw.lower()
    if TOKEN.fullmatch(normalized) is None:
        raise TypeError(f"{label}: invalid token")
    return normalized


def normalize_strict_source_identity(value: dict[str, Any]) -> dict[str, Any]:
    provider = _normalize_token(str(value["provider"]), "provider")
    workspace = value.get("workspace_id")
    return {
        "schema_version": "1.0.0",
        "normalization_profile_id": f"acm-source-key-v1:{provider}:strict",
        "provider": provider,
        "account_id": unicodedata.normalize("NFC", _require_raw(str(value["account_id"]), "account_id", 256)),
        "workspace_id": None
        if workspace is None
        else unicodedata.normalize("NFC", _require_raw(str(workspace), "workspace_id", 256)),
        "resource_type": _normalize_token(str(value["resource_type"]), "resource_type"),
        "external_id": unicodedata.normalize("NFC", _require_raw(str(value["external_id"]), "external_id", 1024)),
    }


def _digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonicalize(value).encode("utf-8")).hexdigest()


def derive_source_record_id(key: dict[str, Any]) -> str:
    return "rot:source:sha256:" + _digest(
        {"domain": "rot.acm.source-record-id", "version": "1", "key": key}
    )


def derive_canonical_entity_id(command: dict[str, Any]) -> str:
    entity_type_uri = str(command["entity_type_uri"])
    if not entity_type_uri.startswith("rot://type/") or entity_type_uri == "rot://type/":
        raise TypeError("invalid entity_type_uri")
    tenant_id = _require_raw(str(command["tenant_id"]), "tenant_id", 1024)
    nonce = _require_raw(str(command["creation_nonce"]), "creation_nonce", 1024)
    return "rot:entity:sha256:" + _digest(
        {
            "domain": "rot.acm.canonical-entity-id",
            "version": "1",
            "entity_type_uri": entity_type_uri,
            "tenant_id": tenant_id,
            "scope_class": str(command["scope_class"]),
            "creation_nonce": nonce,
        }
    )
