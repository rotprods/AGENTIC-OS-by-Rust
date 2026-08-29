from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math
from typing import Any

MAX_SAFE_INTEGER = 9_007_199_254_740_991


class CanonicalJsonError(TypeError):
    pass


def _well_formed(value: str) -> None:
    for char in value:
        if 0xD800 <= ord(char) <= 0xDFFF:
            raise CanonicalJsonError("unpaired surrogate")


def _string(value: str) -> str:
    _well_formed(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _number(value: int | float) -> str:
    if isinstance(value, bool):
        raise CanonicalJsonError("boolean is not a numeric JSON value")
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise CanonicalJsonError("unsafe integer")
        return str(value)
    if not isinstance(value, float) or not math.isfinite(value):
        raise CanonicalJsonError("non-finite or unsupported number")
    if value == 0:
        return "0"
    if value.is_integer() and abs(value) > MAX_SAFE_INTEGER:
        raise CanonicalJsonError("unsafe integer")
    absolute = abs(value)
    token = repr(value).lower()
    if 1e-6 <= absolute < 1e21:
        fixed = format(Decimal(token), "f")
        if "." in fixed:
            fixed = fixed.rstrip("0").rstrip(".")
        return fixed
    if "e" not in token:
        token = format(Decimal(token), "e")
    mantissa, exponent = token.split("e", 1)
    if mantissa.endswith(".0"):
        mantissa = mantissa[:-2]
    exponent_value = int(exponent)
    return f"{mantissa}e+{exponent_value}" if exponent_value >= 0 else f"{mantissa}e-{abs(exponent_value)}"


def _utf16_sort_key(value: str) -> bytes:
    _well_formed(value)
    return value.encode("utf-16-be")


def canonicalize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _string(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _number(value)
    if type(value) is list:
        return "[" + ",".join(canonicalize(item) for item in value) + "]"
    if type(value) is dict:
        if any(not isinstance(key, str) for key in value):
            raise CanonicalJsonError("JSON object keys must be strings")
        return "{" + ",".join(f"{_string(key)}:{canonicalize(value[key])}" for key in sorted(value, key=_utf16_sort_key)) + "}"
    raise CanonicalJsonError(f"unsupported JSON type {type(value).__name__}")


def hash_canonical(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize(value).encode("utf-8")).hexdigest()
