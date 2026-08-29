use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use thiserror::Error;

#[derive(Debug, Error, PartialEq, Eq)]
#[error("{code}: {message}")]
pub struct SurvivalError {
    pub code: &'static str,
    pub message: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct FreshnessSeal {
    pub observed_source_sha: String,
    pub event_watermark: u64,
    pub projection_hash: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SurvivalState {
    pub schema_version: String,
    pub project_id: String,
    pub north_star: String,
    pub current_objective_id: String,
    pub observed_source_sha: String,
    pub event_watermark: u64,
    pub authority_state: String,
    pub active_workstreams: Vec<String>,
    pub active_claims: Vec<String>,
    pub blockers: Vec<String>,
    pub verified_capabilities: Vec<String>,
    pub unverified_capabilities: Vec<String>,
    pub decisions: Vec<String>,
    pub latest_checkpoint_id: Option<String>,
    pub projection_hash: Option<String>,
    pub next_safe_actions: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SurvivalEvent {
    pub event_id: String,
    pub sequence: u64,
    pub event_type: String,
    pub project_id: String,
    pub payload: BTreeMap<String, Value>,
}

pub fn assert_fresh(local: &FreshnessSeal, live: &FreshnessSeal) -> Result<(), SurvivalError> {
    validate_seal(local)?;
    validate_seal(live)?;
    if local.observed_source_sha != live.observed_source_sha {
        return Err(err("STALE_SOURCE", "stale observed source revision"));
    }
    if local.event_watermark != live.event_watermark {
        return Err(err("STALE_WATERMARK", "stale event watermark"));
    }
    if local.projection_hash != live.projection_hash {
        return Err(err("STALE_PROJECTION", "stale projection"));
    }
    Ok(())
}

pub fn reduce_events(seed: &Value, input: &[SurvivalEvent]) -> Result<SurvivalState, SurvivalError> {
    let mut state = normalize_state(seed)?;
    let mut seen: BTreeMap<String, String> = BTreeMap::new();
    let mut events = input.to_vec();
    events.sort_by_key(|event| event.sequence);
    let mut previous = state.event_watermark;

    for event in events {
        let event_hash = semantic_hash(&event)?;
        if let Some(existing) = seen.get(&event.event_id) {
            if existing != &event_hash {
                return Err(err("EVENT_ID_COLLISION", "same event identity with different semantic payload"));
            }
            continue;
        }
        let expected = previous.checked_add(1).ok_or_else(|| err("SEQUENCE_OVERFLOW", "event sequence overflow"))?;
        if event.sequence != expected {
            return Err(err("SEQUENCE_DISCONTINUITY", format!("event sequence discontinuity: expected {expected}, got {}", event.sequence)));
        }
        seen.insert(event.event_id.clone(), event_hash);
        if event.project_id != state.project_id {
            return Err(err("CROSS_PROJECT", "cross-project event rejected"));
        }
        apply_event(&mut state, &event)?;
        previous = event.sequence;
        state.event_watermark = previous;
    }
    normalize_state(&serde_json::to_value(state).map_err(json_error)?)
}

fn apply_event(state: &mut SurvivalState, event: &SurvivalEvent) -> Result<(), SurvivalError> {
    match event.event_type.as_str() {
        "objective.set" => state.current_objective_id = payload_text(&event.payload, "objective_id")?,
        "source_revision.observed" => {
            let sha = payload_text(&event.payload, "observed_source_sha")?;
            if !is_git_sha(&sha) { return Err(err("INVALID_SOURCE_SHA", "invalid observed source revision event")); }
            state.observed_source_sha = sha;
        }
        "authority.set" => {
            let value = payload_text(&event.payload, "authority_state")?;
            if !valid_authority(&value) { return Err(err("INVALID_AUTHORITY", "invalid authority transition")); }
            state.authority_state = value;
        }
        "workstream.started" => add(&mut state.active_workstreams, payload_text(&event.payload, "workstream_id")?),
        "workstream.completed" => discard(&mut state.active_workstreams, &payload_text(&event.payload, "workstream_id")?),
        "claim.acquired" => add(&mut state.active_claims, payload_text(&event.payload, "claim_id")?),
        "claim.released" => discard(&mut state.active_claims, &payload_text(&event.payload, "claim_id")?),
        "blocker.added" => add(&mut state.blockers, payload_text(&event.payload, "blocker_id")?),
        "blocker.cleared" => discard(&mut state.blockers, &payload_text(&event.payload, "blocker_id")?),
        "capability.verified" => {
            let value = payload_text(&event.payload, "capability_id")?;
            discard(&mut state.unverified_capabilities, &value); add(&mut state.verified_capabilities, value);
        }
        "capability.unverified" => {
            let value = payload_text(&event.payload, "capability_id")?;
            discard(&mut state.verified_capabilities, &value); add(&mut state.unverified_capabilities, value);
        }
        "decision.accepted" => add(&mut state.decisions, payload_text(&event.payload, "decision_id")?),
        "checkpoint.created" => state.latest_checkpoint_id = Some(payload_text(&event.payload, "checkpoint_id")?),
        "projection.updated" => {
            let value = payload_text(&event.payload, "projection_hash")?;
            if !is_hash(&value) { return Err(err("INVALID_PROJECTION_HASH", "invalid projection hash event")); }
            state.projection_hash = Some(value);
        }
        "next_actions.set" => {
            let actions = event.payload.get("next_safe_actions").and_then(Value::as_array).ok_or_else(|| err("INVALID_NEXT_ACTIONS", "next_safe_actions must be non-empty string list"))?;
            if actions.is_empty() { return Err(err("INVALID_NEXT_ACTIONS", "next_safe_actions must be non-empty string list")); }
            state.next_safe_actions = actions.iter().map(|v| v.as_str().map(str::to_owned).ok_or_else(|| err("INVALID_NEXT_ACTIONS", "next_safe_actions must be string list"))).collect::<Result<Vec<_>, _>>()?;
        }
        other => return Err(err("UNSUPPORTED_EVENT", format!("unsupported event_type {other}"))),
    }
    Ok(())
}

fn normalize_state(value: &Value) -> Result<SurvivalState, SurvivalError> {
    let obj = value.as_object().ok_or_else(|| err("INVALID_STATE", "state must be object"))?;
    let watermark = obj.get("event_watermark").and_then(Value::as_u64).unwrap_or(0);
    let authority = obj.get("authority_state").and_then(Value::as_str).unwrap_or("PROPOSED").to_owned();
    if !valid_authority(&authority) { return Err(err("INVALID_AUTHORITY", "invalid authority state")); }
    let sha = required_text(obj, "observed_source_sha")?;
    if !is_git_sha(&sha) { return Err(err("INVALID_SOURCE_SHA", "invalid observed source revision")); }
    let projection_hash = optional_text(obj, "projection_hash")?;
    if projection_hash.as_ref().is_some_and(|v| !is_hash(v)) { return Err(err("INVALID_PROJECTION_HASH", "invalid projection hash")); }
    Ok(SurvivalState {
        schema_version: "2".into(),
        project_id: required_text(obj, "project_id")?,
        north_star: required_text(obj, "north_star")?,
        current_objective_id: required_text(obj, "current_objective_id")?,
        observed_source_sha: sha,
        event_watermark: watermark,
        authority_state: authority,
        active_workstreams: string_set(obj.get("active_workstreams"), "active_workstreams")?,
        active_claims: string_set(obj.get("active_claims"), "active_claims")?,
        blockers: string_set(obj.get("blockers"), "blockers")?,
        verified_capabilities: string_set(obj.get("verified_capabilities"), "verified_capabilities")?,
        unverified_capabilities: string_set(obj.get("unverified_capabilities"), "unverified_capabilities")?,
        decisions: string_set(obj.get("decisions"), "decisions")?,
        latest_checkpoint_id: optional_text(obj, "latest_checkpoint_id")?,
        projection_hash,
        next_safe_actions: string_list(obj.get("next_safe_actions"), "next_safe_actions")?,
    })
}

fn validate_seal(seal: &FreshnessSeal) -> Result<(), SurvivalError> {
    if !is_git_sha(&seal.observed_source_sha) { return Err(err("INVALID_SOURCE_SHA", "invalid observed_source_sha")); }
    if seal.projection_hash.as_ref().is_some_and(|v| !is_hash(v)) { return Err(err("INVALID_PROJECTION_HASH", "invalid projection_hash")); }
    Ok(())
}

fn semantic_hash<T: Serialize>(value: &T) -> Result<String, SurvivalError> {
    let bytes = serde_json::to_vec(value).map_err(json_error)?;
    Ok(format!("sha256:{}", hex::encode(Sha256::digest(bytes))))
}

fn required_text(obj: &serde_json::Map<String, Value>, key: &str) -> Result<String, SurvivalError> {
    obj.get(key).and_then(Value::as_str).filter(|v| !v.is_empty()).map(str::to_owned).ok_or_else(|| err("INVALID_TEXT", format!("{key} must be non-empty string")))
}
fn optional_text(obj: &serde_json::Map<String, Value>, key: &str) -> Result<Option<String>, SurvivalError> {
    match obj.get(key) { None | Some(Value::Null) => Ok(None), Some(Value::String(v)) if !v.is_empty() => Ok(Some(v.clone())), _ => Err(err("INVALID_TEXT", format!("{key} invalid"))) }
}
fn payload_text(payload: &BTreeMap<String, Value>, key: &str) -> Result<String, SurvivalError> {
    payload.get(key).and_then(Value::as_str).filter(|v| !v.is_empty()).map(str::to_owned).ok_or_else(|| err("INVALID_TEXT", format!("{key} must be non-empty string")))
}
fn string_list(value: Option<&Value>, key: &str) -> Result<Vec<String>, SurvivalError> {
    let Some(Value::Array(values)) = value else { return Ok(Vec::new()); };
    values.iter().map(|v| v.as_str().filter(|s| !s.is_empty()).map(str::to_owned).ok_or_else(|| err("INVALID_STRING_LIST", format!("{key} must be string list")))).collect()
}
fn string_set(value: Option<&Value>, key: &str) -> Result<Vec<String>, SurvivalError> {
    Ok(string_list(value, key)?.into_iter().collect::<BTreeSet<_>>().into_iter().collect())
}
fn add(values: &mut Vec<String>, value: String) { if !values.contains(&value) { values.push(value); values.sort(); } }
fn discard(values: &mut Vec<String>, value: &str) { values.retain(|v| v != value); }
fn valid_authority(value: &str) -> bool { matches!(value, "PROPOSED"|"IMPLEMENTED"|"EXECUTED"|"VERIFIED"|"EMPIRICALLY_QUALIFIED"|"BLOCKED"|"DEGRADED_EXTERNAL"|"SUPERSEDED") }
fn is_git_sha(value: &str) -> bool { value.len() == 40 && value.bytes().all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase()) }
fn is_hash(value: &str) -> bool { value.len() == 71 && value.starts_with("sha256:") && value[7..].bytes().all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase()) }
fn err(code: &'static str, message: impl Into<String>) -> SurvivalError { SurvivalError { code, message: message.into() } }
fn json_error(error: serde_json::Error) -> SurvivalError { err("JSON_ERROR", error.to_string()) }
