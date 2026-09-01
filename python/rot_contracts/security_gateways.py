from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import ipaddress
from pathlib import Path
import re
from typing import Iterable, Mapping
from urllib.parse import urlsplit

from .survival import SurvivalContractError


TRUST_CLASSIFICATIONS = frozenset({"UNTRUSTED_EXTERNAL", "TRUSTED_OPERATOR", "PINNED_AUTHORITY"})
_FORBIDDEN_SHELLS = frozenset({
    "sh", "bash", "zsh", "fish", "ksh", "dash",
    "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe",
})
_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

MAX_EXTERNAL_CONTENT_BYTES = 65_536
MAX_PROCESS_ARGS = 128
MAX_PROCESS_ARG_BYTES = 8_192
MAX_PROCESS_TOTAL_ARG_BYTES = 65_536
MAX_ENV_VALUE_BYTES = 8_192
MAX_NETWORK_TIMEOUT_SECONDS = 60.0
MAX_PROCESS_TIMEOUT_SECONDS = 300.0
MAX_RESPONSE_BYTES = 100 * 1024 * 1024
MAX_PROCESS_OUTPUT_BYTES = 16 * 1024 * 1024
MAX_REDIRECTS = 10


@dataclass(frozen=True)
class NetworkPolicy:
    allowed_schemes: tuple[str, ...] = ("https",)
    allowed_hosts: tuple[str, ...] = ()
    denied_hosts: tuple[str, ...] = ()
    allowed_ports: tuple[int, ...] = (443,)
    max_redirects: int = 3
    timeout_seconds: float = 10.0
    max_response_bytes: int = 4 * 1024 * 1024


@dataclass(frozen=True)
class NetworkRequestPlan:
    url: str = field(repr=False)
    scheme: str
    host: str
    port: int | None
    method: str
    trust_classification: str
    provenance: str
    max_redirects: int
    timeout_seconds: float
    max_response_bytes: int
    redirect_policy: str = "REVALIDATE_EACH_HOP"
    requires_resolution_validation: bool = True
    forward_credentials: bool = False

    def audit_record(self) -> dict[str, object]:
        return {
            "scheme": self.scheme,
            "host": self.host,
            "port": self.port,
            "method": self.method,
            "trust_classification": self.trust_classification,
            "provenance": self.provenance,
            "max_redirects": self.max_redirects,
            "timeout_seconds": self.timeout_seconds,
            "max_response_bytes": self.max_response_bytes,
            "redirect_policy": self.redirect_policy,
            "requires_resolution_validation": self.requires_resolution_validation,
            "forward_credentials": False,
        }


@dataclass(frozen=True)
class ProcessPolicy:
    allowed_executables: tuple[str, ...]
    allowed_cwd_root: str
    allowed_env_keys: tuple[str, ...] = ()
    timeout_seconds: float = 30.0
    max_output_bytes: int = 2 * 1024 * 1024


@dataclass(frozen=True)
class ProcessInvocationPlan:
    executable: str
    argv: tuple[str, ...] = field(repr=False)
    argv_hash: str
    cwd: str
    environment_keys: tuple[str, ...]
    timeout_seconds: float
    max_output_bytes: int
    provenance: str
    shell: bool = False
    capture_output: bool = True

    def audit_record(self) -> dict[str, object]:
        return {
            "executable": self.executable,
            "argv_count": len(self.argv),
            "argv_hash": self.argv_hash,
            "cwd": self.cwd,
            "environment_keys": list(self.environment_keys),
            "timeout_seconds": self.timeout_seconds,
            "max_output_bytes": self.max_output_bytes,
            "provenance": self.provenance,
            "shell": False,
            "capture_output": True,
        }


@dataclass(frozen=True)
class UntrustedContentEnvelope:
    source_uri: str
    content: str = field(repr=False)
    content_hash: str
    byte_length: int
    trust_classification: str = "UNTRUSTED_DATA"
    instruction_authority: bool = False
    evidence_authority: bool = False
    promotion_authority: bool = False

    def as_context(self) -> dict[str, object]:
        return {
            "source_uri": self.source_uri,
            "content": self.content,
            "content_hash": self.content_hash,
            "byte_length": self.byte_length,
            "trust_classification": self.trust_classification,
            "instruction_authority": False,
            "evidence_authority": False,
            "promotion_authority": False,
        }


def seal_untrusted_content(
    content: str,
    *,
    source_uri: str,
    max_bytes: int = MAX_EXTERNAL_CONTENT_BYTES,
) -> UntrustedContentEnvelope:
    _require_text(source_uri, "source_uri", code="EXTERNAL_SOURCE_REQUIRED", max_length=2048)
    if not isinstance(content, str):
        _fail("EXTERNAL_CONTENT_INVALID", "external content must be text")
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or not 1 <= max_bytes <= MAX_EXTERNAL_CONTENT_BYTES:
        _fail("EXTERNAL_CONTENT_POLICY_INVALID", "external content byte limit invalid")
    encoded = content.encode("utf-8")
    if len(encoded) > max_bytes:
        _fail("EXTERNAL_CONTENT_TOO_LARGE", "external content exceeds bounded byte limit")
    digest = "sha256:" + hashlib.sha256(encoded).hexdigest()
    return UntrustedContentEnvelope(
        source_uri=source_uri,
        content=content,
        content_hash=digest,
        byte_length=len(encoded),
    )


def plan_network_request(
    url: str,
    *,
    method: str = "GET",
    trust_classification: str,
    provenance: str,
    policy: NetworkPolicy | None = None,
) -> NetworkRequestPlan:
    policy = policy or NetworkPolicy()
    _validate_network_policy(policy)
    _require_trust(trust_classification)
    _require_text(provenance, "provenance", code="NETWORK_PROVENANCE_REQUIRED", max_length=2048)
    _require_text(url, "url", code="NETWORK_URL_INVALID", max_length=8192)
    if _has_ascii_control(url):
        _fail("NETWORK_URL_INVALID", "network URL contains control characters")
    method = method.upper()
    if method not in {"GET", "HEAD"}:
        _fail("NETWORK_METHOD_DENIED", "network method denied by read-only gateway")
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise SurvivalContractError("network URL malformed", code="NETWORK_URL_INVALID") from exc
    scheme = parsed.scheme.lower()
    allowed_schemes = tuple(item.lower() for item in policy.allowed_schemes)
    if scheme not in allowed_schemes:
        _fail("NETWORK_SCHEME_DENIED", "network URL scheme denied")
    if parsed.username is not None or parsed.password is not None:
        _fail("NETWORK_CREDENTIALS_FORBIDDEN", "URL-embedded credentials are forbidden")
    if parsed.fragment:
        _fail("NETWORK_FRAGMENT_FORBIDDEN", "URL fragments are forbidden at gateway boundary")
    host = parsed.hostname
    if not host:
        _fail("NETWORK_HOST_MISSING", "network URL host missing")
    host = _normalize_host(host)
    if host == "localhost" or host.endswith(".localhost"):
        _fail("NETWORK_LOCALHOST_FORBIDDEN", "localhost targets are forbidden")
    if "%" in host:
        _fail("NETWORK_ADDRESS_FORBIDDEN", "scoped or malformed address target forbidden")
    literal = _parse_ip(host)
    if literal is not None and not literal.is_global:
        _fail("NETWORK_ADDRESS_FORBIDDEN", "non-global address target forbidden")
    allowed_hosts = tuple(_normalize_host(item) for item in policy.allowed_hosts)
    if allowed_hosts and host not in allowed_hosts:
        _fail("NETWORK_HOST_NOT_ALLOWED", "network host not in explicit allowlist")
    denied_hosts = tuple(_normalize_host(item) for item in policy.denied_hosts)
    if any(_host_matches_domain(host, denied) for denied in denied_hosts):
        _fail("NETWORK_HOST_DENIED", "network host matches explicit deny policy")
    effective_port = port if port is not None else (443 if scheme == "https" else 80)
    if effective_port not in policy.allowed_ports:
        _fail("NETWORK_PORT_DENIED", "network port not in explicit allowlist")
    return NetworkRequestPlan(
        url=url,
        scheme=scheme,
        host=host,
        port=effective_port,
        method=method,
        trust_classification=trust_classification,
        provenance=provenance,
        max_redirects=policy.max_redirects,
        timeout_seconds=float(policy.timeout_seconds),
        max_response_bytes=policy.max_response_bytes,
    )


def validate_resolved_addresses(
    plan: NetworkRequestPlan,
    resolved_addresses: Iterable[str],
) -> tuple[str, ...]:
    if not isinstance(plan, NetworkRequestPlan):
        _fail("NETWORK_PLAN_INVALID", "network plan required")
    if isinstance(resolved_addresses, (str, bytes)):
        _fail("NETWORK_RESOLUTION_INVALID", "resolved address collection required")
    canonical: list[str] = []
    for raw in resolved_addresses:
        if not isinstance(raw, str) or not raw:
            _fail("NETWORK_RESOLUTION_INVALID", "resolved address malformed")
        try:
            address = ipaddress.ip_address(raw)
        except ValueError as exc:
            raise SurvivalContractError("resolved address malformed", code="NETWORK_RESOLUTION_INVALID") from exc
        if not address.is_global:
            _fail("NETWORK_ADDRESS_FORBIDDEN", "resolved non-global address forbidden")
        canonical.append(str(address))
    if not canonical:
        _fail("NETWORK_RESOLUTION_EMPTY", "at least one resolved address is required")
    return tuple(canonical)


def plan_process_invocation(
    executable: str,
    args: Iterable[str],
    *,
    cwd: str,
    env: Mapping[str, str] | None,
    provenance: str,
    policy: ProcessPolicy,
) -> ProcessInvocationPlan:
    _validate_process_policy(policy)
    _require_text(provenance, "provenance", code="PROCESS_PROVENANCE_REQUIRED", max_length=2048)
    _require_text(executable, "executable", code="PROCESS_EXECUTABLE_INVALID", max_length=4096)
    executable_path = _canonical_path(executable, code="PROCESS_EXECUTABLE_INVALID")
    if Path(executable_path).name.lower() in _FORBIDDEN_SHELLS:
        _fail("PROCESS_SHELL_FORBIDDEN", "shell interpreters are forbidden")
    allowed = tuple(_canonical_path(item, code="PROCESS_POLICY_INVALID") for item in policy.allowed_executables)
    if executable_path not in allowed:
        _fail("PROCESS_EXECUTABLE_DENIED", "executable not in explicit allowlist")

    root = _canonical_path(policy.allowed_cwd_root, code="PROCESS_POLICY_INVALID")
    cwd_path = _canonical_path(cwd, code="PROCESS_CWD_INVALID")
    try:
        Path(cwd_path).relative_to(Path(root))
    except ValueError as exc:
        raise SurvivalContractError("cwd escapes allowed root", code="PROCESS_CWD_OUT_OF_BOUNDS") from exc

    if isinstance(args, (str, bytes)):
        _fail("PROCESS_ARGS_INVALID", "argv must be an iterable of argument tokens")
    normalized_args: list[str] = []
    total_bytes = 0
    for arg in args:
        if not isinstance(arg, str):
            _fail("PROCESS_ARGS_INVALID", "argv tokens must be strings")
        if "\x00" in arg:
            _fail("PROCESS_NUL_FORBIDDEN", "NUL byte forbidden in argv")
        size = len(arg.encode("utf-8"))
        if size > MAX_PROCESS_ARG_BYTES:
            _fail("PROCESS_LIMIT_EXCEEDED", "individual argv token exceeds limit")
        normalized_args.append(arg)
        total_bytes += size
        if len(normalized_args) > MAX_PROCESS_ARGS or total_bytes > MAX_PROCESS_TOTAL_ARG_BYTES:
            _fail("PROCESS_LIMIT_EXCEEDED", "argv exceeds bounded limits")

    environment = env or {}
    if not isinstance(environment, Mapping):
        _fail("PROCESS_ENV_INVALID", "environment must be a mapping")
    allowed_env = set(policy.allowed_env_keys)
    environment_keys: list[str] = []
    for key, value in environment.items():
        if not isinstance(key, str) or not _ENV_NAME.fullmatch(key):
            _fail("PROCESS_ENV_INVALID", "environment key malformed")
        if key not in allowed_env:
            _fail("PROCESS_ENV_DENIED", "environment key not in explicit allowlist")
        if not isinstance(value, str) or "\x00" in value:
            _fail("PROCESS_ENV_INVALID", "environment value malformed")
        if len(value.encode("utf-8")) > MAX_ENV_VALUE_BYTES:
            _fail("PROCESS_LIMIT_EXCEEDED", "environment value exceeds limit")
        environment_keys.append(key)

    argv_digest = "sha256:" + hashlib.sha256(
        "\0".join(normalized_args).encode("utf-8")
    ).hexdigest()
    return ProcessInvocationPlan(
        executable=executable_path,
        argv=tuple(normalized_args),
        argv_hash=argv_digest,
        cwd=cwd_path,
        environment_keys=tuple(sorted(environment_keys)),
        timeout_seconds=float(policy.timeout_seconds),
        max_output_bytes=policy.max_output_bytes,
        provenance=provenance,
    )


def _validate_network_policy(policy: NetworkPolicy) -> None:
    if not isinstance(policy, NetworkPolicy):
        _fail("NETWORK_POLICY_INVALID", "NetworkPolicy required")
    if not policy.allowed_schemes:
        _fail("NETWORK_POLICY_INVALID", "at least one allowed scheme required")
    if any(not isinstance(item, str) or item.lower() not in {"http", "https"} for item in policy.allowed_schemes):
        _fail("NETWORK_POLICY_INVALID", "only explicit http/https schemes may be allowed")
    if not isinstance(policy.max_redirects, int) or isinstance(policy.max_redirects, bool) or not 0 <= policy.max_redirects <= MAX_REDIRECTS:
        _fail("NETWORK_POLICY_INVALID", "redirect bound invalid")
    if not isinstance(policy.timeout_seconds, (int, float)) or isinstance(policy.timeout_seconds, bool) or not 0 < policy.timeout_seconds <= MAX_NETWORK_TIMEOUT_SECONDS:
        _fail("NETWORK_POLICY_INVALID", "timeout bound invalid")
    if not isinstance(policy.max_response_bytes, int) or isinstance(policy.max_response_bytes, bool) or not 1 <= policy.max_response_bytes <= MAX_RESPONSE_BYTES:
        _fail("NETWORK_POLICY_INVALID", "response-size bound invalid")
    for host in policy.allowed_hosts:
        if not isinstance(host, str) or not host:
            _fail("NETWORK_POLICY_INVALID", "allowed host malformed")
        _normalize_host(host)
    for host in policy.denied_hosts:
        if not isinstance(host, str) or not host:
            _fail("NETWORK_POLICY_INVALID", "denied host malformed")
        _normalize_host(host)
    if not policy.allowed_ports or any(
        not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535
        for port in policy.allowed_ports
    ):
        _fail("NETWORK_POLICY_INVALID", "allowed port policy invalid")


def _validate_process_policy(policy: ProcessPolicy) -> None:
    if not isinstance(policy, ProcessPolicy):
        _fail("PROCESS_POLICY_INVALID", "ProcessPolicy required")
    if not policy.allowed_executables:
        _fail("PROCESS_POLICY_INVALID", "at least one executable must be allowed")
    for item in policy.allowed_executables:
        canonical = _canonical_path(item, code="PROCESS_POLICY_INVALID")
        if Path(canonical).name.lower() in _FORBIDDEN_SHELLS:
            _fail("PROCESS_POLICY_INVALID", "shell interpreters cannot be allowlisted")
    _canonical_path(policy.allowed_cwd_root, code="PROCESS_POLICY_INVALID")
    if not isinstance(policy.timeout_seconds, (int, float)) or isinstance(policy.timeout_seconds, bool) or not 0 < policy.timeout_seconds <= MAX_PROCESS_TIMEOUT_SECONDS:
        _fail("PROCESS_POLICY_INVALID", "process timeout bound invalid")
    if not isinstance(policy.max_output_bytes, int) or isinstance(policy.max_output_bytes, bool) or not 1 <= policy.max_output_bytes <= MAX_PROCESS_OUTPUT_BYTES:
        _fail("PROCESS_POLICY_INVALID", "process output bound invalid")
    for key in policy.allowed_env_keys:
        if not isinstance(key, str) or not _ENV_NAME.fullmatch(key):
            _fail("PROCESS_POLICY_INVALID", "allowed environment key malformed")


def _normalize_host(host: str) -> str:
    if not isinstance(host, str) or not host:
        _fail("NETWORK_HOST_MISSING", "network host missing")
    normalized = host.rstrip(".").lower()
    if not normalized:
        _fail("NETWORK_HOST_MISSING", "network host missing")
    try:
        return normalized.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise SurvivalContractError("network host malformed", code="NETWORK_HOST_INVALID") from exc


def _parse_ip(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


def _host_matches_domain(host: str, denied: str) -> bool:
    return host == denied or host.endswith("." + denied)


def _has_ascii_control(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)


def _canonical_path(value: str, *, code: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        _fail(code, "absolute path required")
    path = Path(value)
    if not path.is_absolute():
        _fail(code, "absolute path required")
    return str(path.resolve(strict=False))


def _require_trust(value: str) -> None:
    if value not in TRUST_CLASSIFICATIONS:
        _fail("NETWORK_TRUST_CLASSIFICATION_REQUIRED", "explicit trust classification required")


def _require_text(value: object, field: str, *, code: str, max_length: int) -> None:
    if not isinstance(value, str) or not value or len(value) > max_length or "\x00" in value:
        _fail(code, f"{field} required")


def _fail(code: str, message: str) -> None:
    raise SurvivalContractError(message, code=code)
