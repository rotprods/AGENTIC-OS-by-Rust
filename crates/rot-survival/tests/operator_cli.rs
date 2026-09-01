use serde_json::{Value, json};
use std::fs;
use std::path::PathBuf;
use std::process::{Command, Output};
use std::time::{SystemTime, UNIX_EPOCH};

fn temp_root(label: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock")
        .as_nanos();
    let root = std::env::temp_dir().join(format!(
        "rot-survival-cli-{label}-{}-{nonce}",
        std::process::id()
    ));
    fs::create_dir_all(root.join("state/checkpoints")).expect("temp state dir");
    root
}

fn write_fixture(root: &PathBuf, checkpoint_id: &str) {
    let source = "a".repeat(40);
    let state = json!({
        "schema_version": "2",
        "project_id": "rot://project/agentic-os",
        "north_star": "survive agent death",
        "current_objective_id": "rot://objective/agentic-os/cli-test",
        "observed_source_sha": source,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": [],
        "active_claims": [],
        "blockers": ["rot://blocker/test"],
        "verified_capabilities": ["rot://capability/reference"],
        "unverified_capabilities": ["rot://capability/writer"],
        "decisions": [],
        "latest_checkpoint_id": checkpoint_id,
        "projection_hash": null,
        "next_safe_actions": ["keep authority fail-closed"]
    });
    fs::write(
        root.join("state/project_state.json"),
        serde_json::to_vec(&state).expect("state json"),
    )
    .expect("state write");

    if let Some(slug) = checkpoint_id.strip_prefix("rot://checkpoint/agentic-os/") {
        if !slug.contains('/') {
            let checkpoint = json!({
                "schema_version": "2",
                "checkpoint_id": checkpoint_id,
                "observed_source_sha": "a".repeat(40),
                "event_watermark": 0
            });
            fs::write(
                root.join(format!("state/checkpoints/{slug}.json")),
                serde_json::to_vec(&checkpoint).expect("checkpoint json"),
            )
            .expect("checkpoint write");
        }
    }
}

fn run(root: &PathBuf, command: &str) -> Output {
    Command::new(env!("CARGO_BIN_EXE_rot-survival"))
        .args(["--root", root.to_str().expect("utf8 temp root"), command])
        .output()
        .expect("operator cli executes")
}

fn stdout_json(output: &Output) -> Value {
    serde_json::from_slice(&output.stdout).expect("stdout json")
}

fn stderr_json(output: &Output) -> Value {
    serde_json::from_slice(&output.stderr).expect("stderr json")
}

#[test]
fn status_is_read_only_machine_readable_projection() {
    let root = temp_root("status");
    write_fixture(&root, "rot://checkpoint/agentic-os/cp-test");
    let before = fs::read(root.join("state/project_state.json")).expect("before");
    let output = run(&root, "status");
    assert!(output.status.success());
    let payload = stdout_json(&output);
    assert_eq!(payload["ok"], true);
    assert_eq!(payload["command"], "status");
    assert_eq!(payload["output_authority"], "DERIVED_NON_AUTHORITATIVE");
    assert_eq!(payload["event_watermark"], 0);
    assert_eq!(
        fs::read(root.join("state/project_state.json")).expect("after"),
        before
    );
    fs::remove_dir_all(root).ok();
}

#[test]
fn doctor_validates_checkpoint_identity_without_claiming_full_binding_authority() {
    let root = temp_root("doctor");
    write_fixture(&root, "rot://checkpoint/agentic-os/cp-test");
    let output = run(&root, "doctor");
    assert!(output.status.success());
    let payload = stdout_json(&output);
    assert_eq!(payload["result"], "PASS_READ_ONLY");
    assert_eq!(payload["checks"]["checkpoint_identity"], "PASS");
    assert_eq!(payload["checks"]["checkpoint_binding"], "PARTIAL_REFERENCE_ONLY");
    assert_eq!(payload["checks"]["writer_authority"], "UNQUALIFIED");
    fs::remove_dir_all(root).ok();
}

#[test]
fn context_marks_derived_output_non_authoritative_and_non_instructive() {
    let root = temp_root("context");
    write_fixture(&root, "rot://checkpoint/agentic-os/cp-test");
    let output = run(&root, "context");
    assert!(output.status.success());
    let payload = stdout_json(&output);
    assert_eq!(payload["output_authority"], "DERIVED_NON_AUTHORITATIVE");
    assert_eq!(payload["trust"], "UNTRUSTED_DATA");
    assert_eq!(payload["instruction_authority"], false);
    assert_eq!(payload["promotion_authority"], false);
    fs::remove_dir_all(root).ok();
}

#[test]
fn mutating_commands_fail_closed_until_writer_authority_exists() {
    let root = temp_root("mutations");
    write_fixture(&root, "rot://checkpoint/agentic-os/cp-test");
    for command in ["init", "claim", "checkpoint", "handoff"] {
        let output = run(&root, command);
        assert!(!output.status.success(), "{command} unexpectedly succeeded");
        assert_eq!(stderr_json(&output)["code"], "AUTHORITY_UNQUALIFIED");
    }
    fs::remove_dir_all(root).ok();
}

#[test]
fn recover_fails_closed_until_rust_recovery_authority_is_qualified() {
    let root = temp_root("recover");
    write_fixture(&root, "rot://checkpoint/agentic-os/cp-test");
    let output = run(&root, "recover");
    assert!(!output.status.success());
    assert_eq!(stderr_json(&output)["code"], "CAPABILITY_UNQUALIFIED");
    fs::remove_dir_all(root).ok();
}

#[test]
fn doctor_rejects_checkpoint_path_escape() {
    let root = temp_root("escape");
    write_fixture(
        &root,
        "rot://checkpoint/agentic-os/../../outside-checkpoint",
    );
    let output = run(&root, "doctor");
    assert!(!output.status.success());
    assert_eq!(stderr_json(&output)["code"], "INVALID_CHECKPOINT_ID");
    fs::remove_dir_all(root).ok();
}
