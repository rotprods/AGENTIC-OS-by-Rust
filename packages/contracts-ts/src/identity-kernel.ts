import { createHash } from "node:crypto";
import { canonicalize, type JsonValue } from "./canonical-json.js";

export interface SourceIdentityKeyInput {
  provider: string;
  account_id: string;
  workspace_id: string | null;
  resource_type: string;
  external_id: string;
}

export interface NormalizedSourceIdentityKey {
  schema_version: "1.0.0";
  normalization_profile_id: string;
  provider: string;
  account_id: string;
  workspace_id: string | null;
  resource_type: string;
  external_id: string;
}

export interface CanonicalEntityCreationCommand {
  entity_type_uri: string;
  tenant_id: string;
  scope_class: "TENANT" | "WORKSPACE" | "GLOBAL";
  creation_nonce: string;
}

const TOKEN = /^[a-z][a-z0-9._-]{0,127}$/;

function requireRaw(value: string, label: string, maxLength: number): string {
  if (value.length === 0) throw new TypeError(`${label}: empty`);
  if (value.length > maxLength) throw new TypeError(`${label}: too long`);
  if (value.trim() !== value) throw new TypeError(`${label}: surrounding whitespace`);
  if (/\p{Cc}/u.test(value)) throw new TypeError(`${label}: control character`);
  return value;
}

function normalizeToken(value: string, label: string): string {
  const raw = requireRaw(value, label, 128);
  if (!/^[\x00-\x7F]+$/.test(raw)) throw new TypeError(`${label}: token non-ASCII`);
  const normalized = raw.toLowerCase();
  if (!TOKEN.test(normalized)) throw new TypeError(`${label}: invalid token`);
  return normalized;
}

function strictComponent(value: string, label: string, maxLength: number): string {
  return requireRaw(value, label, maxLength).normalize("NFC");
}

export function normalizeStrictSourceIdentity(input: SourceIdentityKeyInput): NormalizedSourceIdentityKey {
  const provider = normalizeToken(input.provider, "provider");
  return {
    schema_version: "1.0.0",
    normalization_profile_id: `acm-source-key-v1:${provider}:strict`,
    provider,
    account_id: strictComponent(input.account_id, "account_id", 256),
    workspace_id: input.workspace_id === null ? null : strictComponent(input.workspace_id, "workspace_id", 256),
    resource_type: normalizeToken(input.resource_type, "resource_type"),
    external_id: strictComponent(input.external_id, "external_id", 1024),
  };
}

function digest(value: JsonValue): string {
  return createHash("sha256").update(canonicalize(value), "utf8").digest("hex");
}

export function deriveSourceRecordId(key: NormalizedSourceIdentityKey): string {
  return `rot:source:sha256:${digest({
    domain: "rot.acm.source-record-id",
    version: "1",
    key: { ...key },
  })}`;
}

export function deriveCanonicalEntityId(command: CanonicalEntityCreationCommand): string {
  if (!command.entity_type_uri.startsWith("rot://type/") || command.entity_type_uri === "rot://type/") {
    throw new TypeError("invalid entity_type_uri");
  }
  requireRaw(command.tenant_id, "tenant_id", 1024);
  requireRaw(command.creation_nonce, "creation_nonce", 1024);
  return `rot:entity:sha256:${digest({
    domain: "rot.acm.canonical-entity-id",
    version: "1",
    entity_type_uri: command.entity_type_uri,
    tenant_id: command.tenant_id,
    scope_class: command.scope_class,
    creation_nonce: command.creation_nonce,
  })}`;
}
