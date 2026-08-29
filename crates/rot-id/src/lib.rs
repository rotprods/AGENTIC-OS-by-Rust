use rot_contracts::ContractError;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

macro_rules! opaque_id {
    ($name:ident, $prefix:literal) => {
        #[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
        pub struct $name(String);

        impl $name {
            pub fn new() -> Self {
                Self(format!(concat!($prefix, ":{}"), Uuid::now_v7()))
            }

            pub fn parse(value: impl Into<String>) -> Result<Self, ContractError> {
                let value = value.into();
                let suffix = value
                    .strip_prefix(concat!($prefix, ":"))
                    .ok_or_else(|| ContractError::InvalidIdentifier(value.clone()))?;
                Uuid::parse_str(suffix)
                    .map_err(|_| ContractError::InvalidIdentifier(value.clone()))?;
                Ok(Self(value))
            }

            pub fn as_str(&self) -> &str {
                &self.0
            }
        }

        impl Default for $name {
            fn default() -> Self {
                Self::new()
            }
        }
    };
}

opaque_id!(EntityId, "rot:entity");
opaque_id!(EventId, "rot:event");
opaque_id!(EvidenceId, "rot:evidence");
opaque_id!(RunId, "rot:run");

pub fn deterministic_source_id(
    namespace: &str,
    raw_external_id: &str,
) -> Result<String, ContractError> {
    if namespace.is_empty() {
        return Err(ContractError::EmptyField("namespace"));
    }
    if raw_external_id.is_empty() {
        return Err(ContractError::EmptyField("raw_external_id"));
    }
    let material = format!("rot.source.v1\u{1f}{namespace}\u{1f}{raw_external_id}");
    Ok(format!(
        "rot:source:{}",
        rot_hash::sha256_bytes(material.as_bytes()).trim_start_matches("sha256:")
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn source_id_is_deterministic_and_case_sensitive() {
        assert_eq!(
            deterministic_source_id("github", "ABC").unwrap(),
            deterministic_source_id("github", "ABC").unwrap()
        );
        assert_ne!(
            deterministic_source_id("github", "ABC").unwrap(),
            deterministic_source_id("github", "abc").unwrap()
        );
    }

    #[test]
    fn entity_round_trip() {
        let id = EntityId::new();
        assert_eq!(EntityId::parse(id.as_str()).unwrap(), id);
    }
}
