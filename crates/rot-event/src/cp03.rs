use rot_contracts::ContractError;
use rot_temporal::Rfc3339Timestamp;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Sensitivity {
    Public,
    Internal,
    Private,
    Restricted,
    SecretRef,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct EventStreamKey {
    pub schema_version: String,
    pub tenant_id: String,
    pub stream_kind: String,
    pub stream_id: String,
}

impl EventStreamKey {
    pub const VERSION: &'static str = "event-stream-key/1";

    pub fn validate(&self) -> Result<(), ContractError> {
        if self.schema_version != Self::VERSION {
            return Err(ContractError::InvalidIdentifier(
                self.schema_version.clone(),
            ));
        }
        for (field, value) in [
            ("tenant_id", self.tenant_id.as_str()),
            ("stream_kind", self.stream_kind.as_str()),
            ("stream_id", self.stream_id.as_str()),
        ] {
            if value.is_empty() {
                return Err(ContractError::EmptyField(field));
            }
        }
        if !self.stream_id.starts_with("rot:") {
            return Err(ContractError::InvalidIdentifier(self.stream_id.clone()));
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AppendEventInput {
    pub event_id: String,
    pub event_type: String,
    pub event_schema_version: String,
    pub occurred_at: Rfc3339Timestamp,
    pub actor_id: String,
    pub subject_ids: Vec<String>,
    pub source_record_ids: Vec<String>,
    pub evidence_ids: Vec<String>,
    pub correlation_id: String,
    pub causation_id: Option<String>,
    pub mission_id: Option<String>,
    pub sensitivity: Sensitivity,
    pub payload: Value,
    pub metadata: Value,
}

impl AppendEventInput {
    pub fn validate(&self) -> Result<(), ContractError> {
        if !self.event_id.starts_with("rot:event:v1:") {
            return Err(ContractError::InvalidIdentifier(self.event_id.clone()));
        }
        if !self.event_type.starts_with("rot://event/") || self.event_type == "rot://event/" {
            return Err(ContractError::InvalidIdentifier(self.event_type.clone()));
        }
        for (field, value) in [
            ("event_schema_version", self.event_schema_version.as_str()),
            ("actor_id", self.actor_id.as_str()),
            ("correlation_id", self.correlation_id.as_str()),
        ] {
            if value.is_empty() {
                return Err(ContractError::EmptyField(field));
            }
        }
        if !self.payload.is_object() {
            return Err(ContractError::InvalidIdentifier(
                "payload must be object".into(),
            ));
        }
        if !self.metadata.is_object() {
            return Err(ContractError::InvalidIdentifier(
                "metadata must be object".into(),
            ));
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct EventAccessContext {
    pub caller_id: String,
    pub tenant_id: String,
    pub allowed_sensitivities: Vec<Sensitivity>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AppendRequest {
    pub schema_version: String,
    pub request_id: String,
    pub stream: EventStreamKey,
    pub expected_revision: u64,
    pub idempotency_key: String,
    pub caller: EventAccessContext,
    pub traceparent: Option<String>,
    pub events: Vec<AppendEventInput>,
}

impl AppendRequest {
    pub const VERSION: &'static str = "event-append-request/1";

    pub fn validate(&self) -> Result<(), ContractError> {
        if self.schema_version != Self::VERSION {
            return Err(ContractError::InvalidIdentifier(
                self.schema_version.clone(),
            ));
        }
        self.stream.validate()?;
        if self.request_id.is_empty() {
            return Err(ContractError::EmptyField("request_id"));
        }
        if self.idempotency_key.is_empty() {
            return Err(ContractError::EmptyField("idempotency_key"));
        }
        if self.caller.caller_id.is_empty() {
            return Err(ContractError::EmptyField("caller_id"));
        }
        if self.caller.tenant_id != self.stream.tenant_id {
            return Err(ContractError::InvalidIdentifier(
                "caller tenant mismatch".into(),
            ));
        }
        if self.events.is_empty() {
            return Err(ContractError::EmptyField("events"));
        }
        for event in &self.events {
            event.validate()?;
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StoredEvent {
    pub schema_version: String,
    #[serde(flatten)]
    pub event: AppendEventInput,
    pub tenant_id: String,
    pub stream_kind: String,
    pub stream_id: String,
    pub stream_revision: u64,
    pub global_position: u64,
    pub recorded_at: Rfc3339Timestamp,
    pub previous_event_hash: Option<String>,
    pub event_hash: String,
    pub append_transaction_id: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppendReceiptEvent {
    pub event_id: String,
    pub stream_revision: u64,
    pub global_position: u64,
    pub event_hash: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AppendReceipt {
    pub schema_version: String,
    pub request_id: String,
    pub tenant_id: String,
    pub stream: EventStreamKey,
    pub idempotency_key: String,
    pub request_hash: String,
    pub append_transaction_id: String,
    pub previous_stream_revision: u64,
    pub current_stream_revision: u64,
    pub first_global_position: u64,
    pub last_global_position: u64,
    pub ledger_head_hash: String,
    pub committed_at: Rfc3339Timestamp,
    pub events: Vec<AppendReceiptEvent>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProjectionCursor {
    pub schema_version: String,
    pub projection_name: String,
    pub projection_version: String,
    pub tenant_id: String,
    pub partition_id: String,
    pub last_global_position: u64,
    pub last_event_hash: Option<String>,
    pub projection_state_hash: String,
    pub fencing_token: String,
    pub updated_at: Rfc3339Timestamp,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SnapshotManifest {
    pub schema_version: String,
    pub tenant_id: String,
    pub stream: EventStreamKey,
    pub stream_revision: u64,
    pub event_horizon: u64,
    pub projector_name: String,
    pub projector_version: String,
    pub state_hash: String,
    pub snapshot_content_hash: String,
    pub snapshot_location_ref: String,
    pub source_event_hashes: Vec<String>,
    pub created_at: Rfc3339Timestamp,
}

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_request() -> AppendRequest {
        AppendRequest {
            schema_version: AppendRequest::VERSION.into(),
            request_id: "req-1".into(),
            stream: EventStreamKey {
                schema_version: EventStreamKey::VERSION.into(),
                tenant_id: "rot".into(),
                stream_kind: "identity".into(),
                stream_id: "rot:source:sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa".into(),
            },
            expected_revision: 0,
            idempotency_key: "idem-1".into(),
            caller: EventAccessContext {
                caller_id: "agent:test".into(),
                tenant_id: "rot".into(),
                allowed_sensitivities: vec![Sensitivity::Internal],
            },
            traceparent: None,
            events: vec![AppendEventInput {
                event_id: "rot:event:v1:0198f711-7c00-7000-8000-000000000001".into(),
                event_type: "rot://event/identity/source-observed".into(),
                event_schema_version: "1.0.0".into(),
                occurred_at: Rfc3339Timestamp::parse("2026-08-29T17:00:00Z").unwrap(),
                actor_id: "agent:test".into(),
                subject_ids: vec![],
                source_record_ids: vec![],
                evidence_ids: vec![],
                correlation_id: "corr-1".into(),
                causation_id: None,
                mission_id: None,
                sensitivity: Sensitivity::Internal,
                payload: serde_json::json!({}),
                metadata: serde_json::json!({}),
            }],
        }
    }

    #[test]
    fn accepts_valid_cp03_append_request() {
        assert!(valid_request().validate().is_ok());
    }

    #[test]
    fn rejects_cross_tenant_append_request() {
        let mut request = valid_request();
        request.caller.tenant_id = "other".into();
        assert!(request.validate().is_err());
    }

    #[test]
    fn rejects_empty_event_batch() {
        let mut request = valid_request();
        request.events.clear();
        assert!(request.validate().is_err());
    }
}
