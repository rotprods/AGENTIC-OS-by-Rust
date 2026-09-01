import { createHash } from "node:crypto";

export const AUTHORITY_STATES = new Set([
  "PROPOSED", "IMPLEMENTED", "EXECUTED", "VERIFIED", "EMPIRICALLY_QUALIFIED",
  "BLOCKED", "DEGRADED_EXTERNAL", "SUPERSEDED",
]);

export class SurvivalContractError extends Error {
  constructor(public readonly code: string, message: string) {
    super(message);
    this.name = "SurvivalContractError";
  }
}

export type FreshnessSeal = {
  observed_source_sha: string;
  event_watermark: number;
  projection_hash: string | null;
};

export type SurvivalState = {
  schema_version: "2";
  project_id: string;
  north_star: string;
  current_objective_id: string;
  observed_source_sha: string;
  event_watermark: number;
  authority_state: string;
  active_workstreams: string[];
  active_claims: string[];
  blockers: string[];
  verified_capabilities: string[];
  unverified_capabilities: string[];
  decisions: string[];
  latest_checkpoint_id: string | null;
  projection_hash: string | null;
  next_safe_actions: string[];
};

type SurvivalEvent = {
  event_id: string;
  sequence: number;
  event_type: string;
  project_id: string;
  payload: Record<string, unknown>;
};

const SHA_RE = /^[0-9a-f]{40}$/;
const HASH_RE = /^sha256:[0-9a-f]{64}$/;

export function assertFresh(local: FreshnessSeal, live: FreshnessSeal): void {
  validateSeal(local);
  validateSeal(live);
  if (local.observed_source_sha !== live.observed_source_sha) fail("STALE_SOURCE", "stale observed source revision");
  if (local.event_watermark !== live.event_watermark) fail("STALE_WATERMARK", "stale event watermark");
  if (local.projection_hash !== live.projection_hash) fail("STALE_PROJECTION", "stale projection");
}

export function reduceEvents(seed: Record<string, unknown>, inputEvents: SurvivalEvent[]): SurvivalState {
  const state = normalizeState(seed);
  const seen = new Map<string, string>();
  const events = inputEvents.map(normalizeEvent).sort((a, b) => a.sequence - b.sequence);
  let previousSequence = state.event_watermark;

  for (const event of events) {
    const eventHash = semanticHash(event);
    const existing = seen.get(event.event_id);
    if (existing !== undefined) {
      if (existing !== eventHash) fail("EVENT_ID_COLLISION", "same event identity with different semantic payload");
      continue;
    }
    const expected = previousSequence + 1;
    if (event.sequence !== expected) fail("SEQUENCE_DISCONTINUITY", `event sequence discontinuity: expected ${expected}, got ${event.sequence}`);
    seen.set(event.event_id, eventHash);
    if (event.project_id !== state.project_id) fail("CROSS_PROJECT", "cross-project event rejected");
    applyEvent(state, event);
    previousSequence = event.sequence;
    state.event_watermark = previousSequence;
  }
  return normalizeState(state as unknown as Record<string, unknown>);
}

function applyEvent(state: SurvivalState, event: SurvivalEvent): void {
  const p = event.payload;
  switch (event.event_type) {
    case "objective.set": state.current_objective_id = text(p, "objective_id"); break;
    case "source_revision.observed": {
      const sha = text(p, "observed_source_sha");
      if (!SHA_RE.test(sha)) fail("INVALID_SOURCE_SHA", "invalid observed source revision event");
      state.observed_source_sha = sha; break;
    }
    case "authority.set": {
      const authority = text(p, "authority_state");
      if (!AUTHORITY_STATES.has(authority)) fail("INVALID_AUTHORITY", "invalid authority transition");
      state.authority_state = authority; break;
    }
    case "workstream.started": add(state.active_workstreams, text(p, "workstream_id")); break;
    case "workstream.completed": discard(state.active_workstreams, text(p, "workstream_id")); break;
    case "claim.acquired": add(state.active_claims, text(p, "claim_id")); break;
    case "claim.released": discard(state.active_claims, text(p, "claim_id")); break;
    case "blocker.added": add(state.blockers, text(p, "blocker_id")); break;
    case "blocker.cleared": discard(state.blockers, text(p, "blocker_id")); break;
    case "capability.verified": {
      const capability = text(p, "capability_id"); discard(state.unverified_capabilities, capability); add(state.verified_capabilities, capability); break;
    }
    case "capability.unverified": {
      const capability = text(p, "capability_id"); discard(state.verified_capabilities, capability); add(state.unverified_capabilities, capability); break;
    }
    case "decision.accepted": add(state.decisions, text(p, "decision_id")); break;
    case "checkpoint.created": state.latest_checkpoint_id = text(p, "checkpoint_id"); break;
    case "projection.updated": {
      const hash = text(p, "projection_hash"); if (!HASH_RE.test(hash)) fail("INVALID_PROJECTION_HASH", "invalid projection hash event"); state.projection_hash = hash; break;
    }
    case "next_actions.set": {
      const actions = p["next_safe_actions"];
      if (!isStringArray(actions) || actions.length === 0) fail("INVALID_NEXT_ACTIONS", "next_safe_actions must be non-empty string list");
      state.next_safe_actions = [...actions]; break;
    }
    default: fail("UNSUPPORTED_EVENT", `unsupported event_type ${event.event_type}`);
  }
}

function normalizeState(input: Record<string, unknown>): SurvivalState {
  const watermark = input["event_watermark"] ?? 0;
  if (!isNonNegativeInt(watermark)) fail("INVALID_WATERMARK", "invalid event watermark");
  const state: SurvivalState = {
    schema_version: "2",
    project_id: stateText(input, "project_id"),
    north_star: stateText(input, "north_star"),
    current_objective_id: stateText(input, "current_objective_id"),
    observed_source_sha: stateText(input, "observed_source_sha"),
    event_watermark: watermark,
    authority_state: typeof input["authority_state"] === "string" ? input["authority_state"] : "PROPOSED",
    active_workstreams: normalizedStringSet(input["active_workstreams"] ?? [], "active_workstreams"),
    active_claims: normalizedStringSet(input["active_claims"] ?? [], "active_claims"),
    blockers: normalizedStringSet(input["blockers"] ?? [], "blockers"),
    verified_capabilities: normalizedStringSet(input["verified_capabilities"] ?? [], "verified_capabilities"),
    unverified_capabilities: normalizedStringSet(input["unverified_capabilities"] ?? [], "unverified_capabilities"),
    decisions: normalizedStringSet(input["decisions"] ?? [], "decisions"),
    latest_checkpoint_id: nullableText(input["latest_checkpoint_id"], "latest_checkpoint_id"),
    projection_hash: nullableHash(input["projection_hash"], "projection_hash"),
    next_safe_actions: stringArray(input["next_safe_actions"] ?? [], "next_safe_actions"),
  };
  if (!AUTHORITY_STATES.has(state.authority_state)) fail("INVALID_AUTHORITY", "invalid authority state");
  if (!SHA_RE.test(state.observed_source_sha)) fail("INVALID_SOURCE_SHA", "invalid observed source revision");
  return state;
}

function normalizeEvent(value: SurvivalEvent): SurvivalEvent {
  if (typeof value !== "object" || value === null || Array.isArray(value)) fail("INVALID_EVENT", "event must be object");
  const keys = Object.keys(value).sort();
  if (keys.join(",") !== ["event_id","event_type","payload","project_id","sequence"].sort().join(",")) fail("INVALID_EVENT", "event has invalid fields");
  if (typeof value.event_id !== "string" || value.event_id.length === 0) fail("INVALID_EVENT", "event_id required");
  if (!isNonNegativeInt(value.sequence)) fail("INVALID_SEQUENCE", "sequence must be non-negative integer");
  if (typeof value.event_type !== "string" || value.event_type.length === 0) fail("INVALID_EVENT", "event_type required");
  if (typeof value.project_id !== "string" || value.project_id.length === 0) fail("INVALID_EVENT", "project_id required");
  if (typeof value.payload !== "object" || value.payload === null || Array.isArray(value.payload)) fail("INVALID_EVENT", "payload must be object");
  return structuredClone(value);
}

function validateSeal(seal: FreshnessSeal): void {
  if (!SHA_RE.test(seal.observed_source_sha)) fail("INVALID_SOURCE_SHA", "observed_source_sha must be lowercase git SHA-1 hex");
  if (!isNonNegativeInt(seal.event_watermark)) fail("INVALID_WATERMARK", "event_watermark must be non-negative integer");
  if (seal.projection_hash !== null && !HASH_RE.test(seal.projection_hash)) fail("INVALID_PROJECTION_HASH", "projection_hash must be sha256");
}

function semanticHash(value: unknown): string {
  const canonical = canonicalize(value);
  return `sha256:${createHash("sha256").update(canonical, "utf8").digest("hex")}`;
}

function canonicalize(value: unknown): string {
  if (value === null) return "null";
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number") return JSON.stringify(value);
  if (typeof value === "boolean") return value ? "true" : "false";
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).sort().map(k => `${JSON.stringify(k)}:${canonicalize(record[k])}`).join(",")}}`;
  }
  fail("INVALID_CANONICAL_VALUE", "unsupported canonical value");
}

function text(payload: Record<string, unknown>, key: string): string { return stateText(payload, key); }
function stateText(payload: Record<string, unknown>, key: string): string {
  const value = payload[key]; if (typeof value !== "string" || value.length === 0) fail("INVALID_TEXT", `${key} must be non-empty string`); return value;
}
function nullableText(value: unknown, key: string): string | null { if (value === null || value === undefined) return null; if (typeof value !== "string" || value.length === 0) fail("INVALID_TEXT", `${key} invalid`); return value; }
function nullableHash(value: unknown, key: string): string | null { if (value === null || value === undefined) return null; if (typeof value !== "string" || !HASH_RE.test(value)) fail("INVALID_PROJECTION_HASH", `${key} invalid`); return value; }
function stringArray(value: unknown, key: string): string[] { if (!isStringArray(value)) fail("INVALID_STRING_LIST", `${key} must be string list`); return [...value]; }
function normalizedStringSet(value: unknown, key: string): string[] { return [...new Set(stringArray(value, key))].sort(); }
function isStringArray(value: unknown): value is string[] { return Array.isArray(value) && value.every(v => typeof v === "string" && v.length > 0); }
function isNonNegativeInt(value: unknown): value is number { return typeof value === "number" && Number.isSafeInteger(value) && value >= 0; }
function add(values: string[], value: string): void { if (!values.includes(value)) { values.push(value); values.sort(); } }
function discard(values: string[], value: string): void { const index = values.indexOf(value); if (index >= 0) values.splice(index, 1); }
function fail(code: string, message: string): never { throw new SurvivalContractError(code, message); }
