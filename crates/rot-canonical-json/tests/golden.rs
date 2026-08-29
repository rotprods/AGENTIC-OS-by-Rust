use rot_canonical_json::canonical_bytes;
use serde::Deserialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{fs, path::PathBuf};

#[derive(Deserialize)]
struct Fixture {
    vectors: Vec<Vector>,
}

#[derive(Deserialize)]
struct Vector {
    name: String,
    value: Value,
    expected_canonical: String,
    expected_sha256: String,
}

fn sha256(bytes: &[u8]) -> String {
    format!("sha256:{}", hex::encode(Sha256::digest(bytes)))
}

#[test]
fn canonical_goldens_match_reference() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../fixtures/golden/canonical-json.v1.json");
    let fixture: Fixture = serde_json::from_str(&fs::read_to_string(path).unwrap()).unwrap();
    for vector in fixture.vectors {
        let bytes = canonical_bytes(&vector.value).unwrap();
        assert_eq!(
            String::from_utf8(bytes.clone()).unwrap(),
            vector.expected_canonical,
            "{}",
            vector.name
        );
        assert_eq!(sha256(&bytes), vector.expected_sha256, "{}", vector.name);
    }
}
