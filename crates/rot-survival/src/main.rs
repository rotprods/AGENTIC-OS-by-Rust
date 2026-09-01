use rot_survival::{FreshnessSeal, SurvivalState, assert_fresh};
use serde_json::{Value, json};
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process;

const CHECKPOINT_PREFIX: &str = "rot://checkpoint/agentic-os/";
const STATE_PATH: &str = "state/project_state.json";

#[derive(Debug)]
struct CliError {
    code: &'static str,
    message: String,
    exit_code: i32,
}

impl CliError {
    fn new(code: &'static str, message: impl Into<String>, exit_code: i32) -> Self {
        Self {
            code,
            message: message.into(),
            exit_code,
        }
    }
}

fn main() {
    if let Err(error) = run() {
        let payload = json!({
            "ok": false,
            "code": error.code,
            "message": error.message,
            "output_authority": "DERIVED_NON_AUTHORITATIVE"
        });
        eprintln!(
            "{}",
            serde_json::to_string(&payload).expect("error payload must serialize")
        );
        process::exit(error.exit_code);
    }
}

fn run() -> Result<(), CliError> {
    let (root, command) = parse_args()?;
    match command.as_str() {
        "status" => command_status(&root),
        "doctor" => command_doctor(&root),
        "context" => command_context(&root),
        "init" | "claim" | "checkpoint" | "handoff" => Err(CliError::new(
            "AUTHORITY_UNQUALIFIED",
            format!(
                "{command} is disabled until a durable accepted-event writer is empirically qualified"
            ),
            20,
        )),
        "recover" => Err(CliError::new(
            "CAPABILITY_UNQUALIFIED",
            "recover is disabled until a Rust recovery authority is qualified against the canonical durable event ledger",
            21,
        )),
        "help" | "--help" | "-h" => emit(json!({
            "ok": true,
            "command": "help",
            "output_authority": "DERIVED_NON_AUTHORITATIVE",
            "commands": {
                "read_only": ["status", "doctor", "context"],
                "fail_closed_until_writer_qualified": ["init", "claim", "checkpoint", "handoff"],
                "fail_closed_until_recovery_qualified": ["recover"]
            },
            "usage": "rot-survival [--root PATH] <command>"
        })),
        _ => Err(CliError::new(
            "INVALID_COMMAND",
            format!("unsupported operator command: {command}"),
            2,
        )),
    }
}

fn parse_args() -> Result<(PathBuf, String), CliError> {
    let mut values: Vec<String> = env::args().skip(1).collect();
    let mut root = PathBuf::from(".");
    let mut index = 0;
    while index < values.len() {
        if values[index] == "--root" {
            if index + 1 >= values.len() {
                return Err(CliError::new(
                    "INVALID_ARGUMENTS",
                    "--root requires a path",
                    2,
                ));
            }
            root = PathBuf::from(values.remove(index + 1));
            values.remove(index);
            continue;
        }
        index += 1;
    }
    if values.len() != 1 {
        return Err(CliError::new(
            "INVALID_ARGUMENTS",
            "exactly one command is required",
            2,
        ));
    }
    Ok((root, values.remove(0)))
}

fn read_state(root: &Path) -> Result<SurvivalState, CliError> {
    let path = root.join(STATE_PATH);
    let bytes = fs::read(&path).map_err(|error| {
        CliError::new(
            "STATE_NOT_FOUND",
            format!("cannot read {STATE_PATH}: {error}"),
            10,
        )
    })?;
    let state: SurvivalState = serde_json::from_slice(&bytes).map_err(|error| {
        CliError::new(
            "INVALID_STATE",
            format!("canonical project state is not valid SurvivalStateV2: {error}"),
            11,
        )
    })?;
    if state.schema_version != "2" {
        return Err(CliError::new(
            "INVALID_STATE",
            "canonical project state schema_version must be 2",
            11,
        ));
    }
    let seal = FreshnessSeal {
        observed_source_sha: state.observed_source_sha.clone(),
        event_watermark: state.event_watermark,
        projection_hash: state.projection_hash.clone(),
    };
    assert_fresh(&seal, &seal).map_err(|error| {
        CliError::new(
            error.code,
            format!(
                "canonical project state freshness fields are invalid: {}",
                error.message
            ),
            11,
        )
    })?;
    Ok(state)
}

fn command_status(root: &Path) -> Result<(), CliError> {
    let state = read_state(root)?;
    emit(json!({
        "ok": true,
        "command": "status",
        "output_authority": "DERIVED_NON_AUTHORITATIVE",
        "source": STATE_PATH,
        "project_id": state.project_id,
        "current_objective_id": state.current_objective_id,
        "authority_state": state.authority_state,
        "event_watermark": state.event_watermark,
        "latest_checkpoint_id": state.latest_checkpoint_id,
        "active_workstreams": state.active_workstreams,
        "active_claims": state.active_claims,
        "blockers": state.blockers,
        "verified_capabilities": state.verified_capabilities,
        "unverified_capabilities": state.unverified_capabilities
    }))
}

fn command_context(root: &Path) -> Result<(), CliError> {
    let state = read_state(root)?;
    emit(json!({
        "ok": true,
        "command": "context",
        "output_authority": "DERIVED_NON_AUTHORITATIVE",
        "trust": "UNTRUSTED_DATA",
        "instruction_authority": false,
        "promotion_authority": false,
        "source": STATE_PATH,
        "project_id": state.project_id,
        "north_star": state.north_star,
        "current_objective_id": state.current_objective_id,
        "blockers": state.blockers,
        "active_workstreams": state.active_workstreams,
        "next_safe_actions": state.next_safe_actions
    }))
}

fn command_doctor(root: &Path) -> Result<(), CliError> {
    let state = read_state(root)?;
    let checkpoint = match state.latest_checkpoint_id.as_deref() {
        Some(checkpoint_id) => Some(validate_checkpoint_identity(root, checkpoint_id, &state)?),
        None => None,
    };
    emit(json!({
        "ok": true,
        "command": "doctor",
        "result": "PASS_READ_ONLY",
        "output_authority": "DERIVED_NON_AUTHORITATIVE",
        "checks": {
            "state_parse": "PASS",
            "freshness_field_shape": "PASS",
            "checkpoint_identity": if checkpoint.is_some() { "PASS" } else { "NOT_APPLICABLE" },
            "checkpoint_binding": "PARTIAL_REFERENCE_ONLY",
            "writer_authority": "UNQUALIFIED",
            "recovery_authority": "UNQUALIFIED"
        },
        "limitations": [
            "Rust doctor validates checkpoint identity/source/watermark fields but does not replace the canonical checkpoint hash/binding verifier",
            "this command performs no writes and grants no authority"
        ],
        "checkpoint": checkpoint
    }))
}

fn validate_checkpoint_identity(
    root: &Path,
    checkpoint_id: &str,
    state: &SurvivalState,
) -> Result<Value, CliError> {
    let slug = checkpoint_id
        .strip_prefix(CHECKPOINT_PREFIX)
        .ok_or_else(|| {
            CliError::new(
                "INVALID_CHECKPOINT_ID",
                "latest_checkpoint_id must use canonical agentic-os checkpoint URI",
                12,
            )
        })?;
    if !valid_checkpoint_slug(slug) {
        return Err(CliError::new(
            "INVALID_CHECKPOINT_ID",
            "latest_checkpoint_id contains invalid checkpoint slug",
            12,
        ));
    }
    let relative = format!("state/checkpoints/{slug}.json");
    let path = root.join(&relative);
    let bytes = fs::read(&path).map_err(|error| {
        CliError::new(
            "CHECKPOINT_NOT_FOUND",
            format!("cannot read {relative}: {error}"),
            13,
        )
    })?;
    let checkpoint: Value = serde_json::from_slice(&bytes).map_err(|error| {
        CliError::new(
            "INVALID_CHECKPOINT",
            format!("latest checkpoint is not valid JSON: {error}"),
            14,
        )
    })?;
    if checkpoint.get("checkpoint_id").and_then(Value::as_str) != Some(checkpoint_id) {
        return Err(CliError::new(
            "CHECKPOINT_ID_MISMATCH",
            "latest checkpoint identity does not match canonical project state",
            14,
        ));
    }
    if checkpoint.get("schema_version").and_then(Value::as_str) != Some("2") {
        return Err(CliError::new(
            "INVALID_CHECKPOINT",
            "latest checkpoint schema_version must be 2",
            14,
        ));
    }
    if checkpoint
        .get("observed_source_sha")
        .and_then(Value::as_str)
        != Some(state.observed_source_sha.as_str())
    {
        return Err(CliError::new(
            "CHECKPOINT_SOURCE_MISMATCH",
            "latest checkpoint semantic source revision differs from canonical project state",
            14,
        ));
    }
    if checkpoint.get("event_watermark").and_then(Value::as_u64) != Some(state.event_watermark) {
        return Err(CliError::new(
            "CHECKPOINT_WATERMARK_MISMATCH",
            "latest checkpoint event watermark differs from canonical project state",
            14,
        ));
    }
    Ok(json!({
        "checkpoint_id": checkpoint_id,
        "path": relative,
        "observed_source_sha": state.observed_source_sha.as_str(),
        "event_watermark": state.event_watermark
    }))
}

fn valid_checkpoint_slug(slug: &str) -> bool {
    let bytes = slug.as_bytes();
    if bytes.is_empty() || bytes.len() > 160 {
        return false;
    }
    let first = bytes[0];
    if !(first.is_ascii_lowercase() || first.is_ascii_digit()) {
        return false;
    }
    bytes.iter().all(|byte| {
        byte.is_ascii_lowercase() || byte.is_ascii_digit() || matches!(*byte, b'.' | b'_' | b'-')
    })
}

fn emit(value: Value) -> Result<(), CliError> {
    let text = serde_json::to_string(&value).map_err(|error| {
        CliError::new(
            "JSON_ERROR",
            format!("cannot serialize operator output: {error}"),
            30,
        )
    })?;
    println!("{text}");
    Ok(())
}
