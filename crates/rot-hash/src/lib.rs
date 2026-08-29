use rot_contracts::ContractError;
use serde::Serialize;
use sha2::{Digest, Sha256};

pub fn sha256_bytes(bytes: &[u8]) -> String {
    format!("sha256:{}", hex::encode(Sha256::digest(bytes)))
}

pub fn canonical_sha256<T: Serialize>(value: &T) -> Result<String, ContractError> {
    Ok(sha256_bytes(&rot_canonical_json::canonical_bytes(value)?))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn known_sha256_vector() {
        assert_eq!(sha256_bytes(b"abc"), "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    }
    #[test]
    fn object_order_does_not_change_hash() {
        assert_eq!(canonical_sha256(&json!({"b":2,"a":1})).unwrap(), canonical_sha256(&json!({"a":1,"b":2})).unwrap());
    }
}
