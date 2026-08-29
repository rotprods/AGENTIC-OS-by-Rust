pub mod cp03;

use rot_contracts::{ContractError, Scope, TenantId};
use rot_hash::canonical_sha256;
use rot_id::EventId;
use rot_provenance::Provenance;
use rot_temporal::Rfc3339Timestamp;
use serde::{Deserialize, Serialize};
use serde_json::Value;

pub const EVENT_ENVELOPE_VERSION: &str = "rot.event-envelope.v1";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EventEnvelope {
    pub schema_version: String,
    pub event_id: EventId,
    pub event_type: String,
    pub tenant_id: TenantId,
    pub scope: Scope,
    pub stream: String,
    pub occurred_at: Rfc3339Timestamp,
    pub observed_at: Rfc3339Timestamp,
    pub provenance: Provenance,
    pub payload: Value,
}

impl EventEnvelope {
    pub fn validate(&self) -> Result<(), ContractError> {
        if self.schema_version != EVENT_ENVELOPE_VERSION {
            return Err(ContractError::InvalidIdentifier(
                self.schema_version.clone(),
            ));
        }
        if self.event_type.is_empty() {
            return Err(ContractError::EmptyField("event_type"));
        }
        if self.stream.is_empty() {
            return Err(ContractError::EmptyField("stream"));
        }
        Ok(())
    }

    pub fn semantic_hash(&self) -> Result<String, ContractError> {
        self.validate()?;
        canonical_sha256(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rot_provenance::{AuthorityClass, Provenance};

    fn event() -> EventEnvelope {
        EventEnvelope {
            schema_version: EVENT_ENVELOPE_VERSION.into(),
            event_id: EventId::new(),
            event_type: "agent.booted".into(),
            tenant_id: TenantId::new("rot").unwrap(),
            scope: Scope::new("project:ROT_AGENTIC_OS").unwrap(),
            stream: "agent:test".into(),
            occurred_at: Rfc3339Timestamp::parse("2026-08-29T17:00:00Z").unwrap(),
            observed_at: Rfc3339Timestamp::parse("2026-08-29T17:00:01Z").unwrap(),
            provenance: Provenance::authoritative_fact(AuthorityClass::ProviderEvidence, vec![]),
            payload: serde_json::json!({"b":2,"a":1}),
        }
    }

    #[test]
    fn validates_versioned_event() {
        assert!(event().validate().is_ok());
    }

    #[test]
    fn semantic_hash_is_deterministic_for_same_event() {
        let event = event();
        assert_eq!(
            event.semantic_hash().unwrap(),
            event.semantic_hash().unwrap()
        );
    }
}
