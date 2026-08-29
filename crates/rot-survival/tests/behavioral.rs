use rot_survival::{assert_fresh, reduce_events, FreshnessSeal, SurvivalEvent};
use serde_json::Value;
use std::{collections::BTreeMap, fs, path::PathBuf};

fn fixture() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
    serde_json::from_str(&fs::read_to_string(root.join("fixtures/golden/survival-behavior-v2.json")).unwrap()).unwrap()
}

#[test]
fn shared_behavioral_corpus_passes() {
    let fixture = fixture();
    let seed = fixture["seed"].clone();
    let cases = fixture["cases"].as_array().unwrap();
    let mut passed = 0usize;
    for vector in cases {
        let expected = &vector["expect"];
        let operation = vector["operation"].as_str().unwrap();
        let outcome = match operation {
            "reduce_events" => {
                let events: Vec<SurvivalEvent> = serde_json::from_value(vector["events"].clone()).unwrap();
                reduce_events(&seed, &events).map(|state| serde_json::to_value(state).unwrap())
            }
            "assert_fresh" => {
                let local: FreshnessSeal = serde_json::from_value(vector["local"].clone()).unwrap();
                let live: FreshnessSeal = serde_json::from_value(vector["live"].clone()).unwrap();
                assert_fresh(&local, &live).map(|_| Value::Object(Default::default()))
            }
            other => panic!("unknown operation {other}"),
        };
        match expected["status"].as_str().unwrap() {
            "PASS" => {
                let result = outcome.unwrap_or_else(|e| panic!("{} unexpectedly rejected: {e}", vector["name"]));
                let checks: BTreeMap<String, Value> = serde_json::from_value(expected.clone()).unwrap();
                for (key, value) in checks {
                    if key == "status" { continue; }
                    assert_eq!(result.get(&key), Some(&value), "{} mismatch for {key}", vector["name"]);
                }
            }
            "REJECT" => {
                let error = outcome.expect_err("expected rejection");
                assert_eq!(error.code, expected["error_code"].as_str().unwrap(), "{} wrong error", vector["name"]);
            }
            other => panic!("unknown expected status {other}"),
        }
        passed += 1;
    }
    assert_eq!(passed, cases.len());
}
