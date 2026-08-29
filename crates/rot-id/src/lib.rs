use rot_contracts::ContractError;
use rot_hash::canonical_sha256;
use serde::{Deserialize, Serialize};
use serde_json::json;
use unicode_normalization::UnicodeNormalization as UnicodeNormalizationExt;
use uuid::Uuid;

const SHA256_HEX_LEN: usize = 64;

fn is_lower_hex(value: &str) -> bool {
    value.len() == SHA256_HEX_LEN
        && value
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

macro_rules! digest_id {
    ($name:ident, $prefix:literal) => {
        #[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
        pub struct $name(String);

        impl $name {
            pub fn parse(value: impl Into<String>) -> Result<Self, ContractError> {
                let value = value.into();
                let suffix = value
                    .strip_prefix($prefix)
                    .ok_or_else(|| ContractError::InvalidIdentifier(value.clone()))?;
                if !is_lower_hex(suffix) {
                    return Err(ContractError::InvalidIdentifier(value));
                }
                Ok(Self(value))
            }

            pub fn as_str(&self) -> &str {
                &self.0
            }

            fn from_digest(digest: &str) -> Self {
                Self(format!("{}{}", $prefix, digest))
            }
        }
    };
}

digest_id!(CanonicalEntityId, "rot:entity:sha256:");
digest_id!(SourceRecordId, "rot:source:sha256:");
digest_id!(IdentityDecisionId, "rot:revision:sha256:");

macro_rules! runtime_id {
    ($name:ident, $prefix:literal) => {
        #[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
        pub struct $name(String);

        impl $name {
            pub fn new() -> Self {
                Self(format!("{}{}", $prefix, Uuid::now_v7()))
            }

            pub fn parse(value: impl Into<String>) -> Result<Self, ContractError> {
                let value = value.into();
                let suffix = value
                    .strip_prefix($prefix)
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

runtime_id!(EventId, "rot:event:v1:");
runtime_id!(EvidenceId, "rot:evidence:v1:");
runtime_id!(RunId, "rot:run:v1:");

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SourceIdentityComponent {
    pub raw: String,
    pub normalized: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum UnicodeNormalization {
    Nfc,
    None,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct IdentityComponentPolicy {
    pub case_sensitive: bool,
    pub unicode_normalization: UnicodeNormalization,
    pub max_length: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SourceIdentityPolicy {
    pub normalization_profile_id: String,
    pub provider: String,
    pub account_id: IdentityComponentPolicy,
    pub workspace_id: IdentityComponentPolicy,
    pub external_id: IdentityComponentPolicy,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SourceIdentityKeyInput {
    pub provider: String,
    pub account_id: String,
    pub workspace_id: Option<String>,
    pub resource_type: String,
    pub external_id: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct NormalizedSourceIdentityKey {
    pub schema_version: String,
    pub normalization_profile_id: String,
    pub provider: SourceIdentityComponent,
    pub account_id: SourceIdentityComponent,
    pub workspace_id: Option<SourceIdentityComponent>,
    pub resource_type: SourceIdentityComponent,
    pub external_id: SourceIdentityComponent,
}

fn has_control(value: &str) -> bool {
    value.chars().any(|c| c <= '\u{1f}' || c == '\u{7f}')
}

fn require_raw(
    value: &str,
    field: &'static str,
    max_length: usize,
) -> Result<String, ContractError> {
    if value.is_empty() {
        return Err(ContractError::InvalidIdentityComponent {
            field,
            reason: "empty",
        });
    }
    if value.chars().count() > max_length {
        return Err(ContractError::InvalidIdentityComponent {
            field,
            reason: "too_long",
        });
    }
    if has_control(value) {
        return Err(ContractError::InvalidIdentityComponent {
            field,
            reason: "control_character",
        });
    }
    if value.trim() != value {
        return Err(ContractError::InvalidIdentityComponent {
            field,
            reason: "surrounding_whitespace",
        });
    }
    Ok(value.to_owned())
}

fn token_valid(value: &str) -> bool {
    let mut bytes = value.bytes();
    let Some(first) = bytes.next() else {
        return false;
    };
    if !first.is_ascii_lowercase() {
        return false;
    }
    bytes.all(|b| {
        b.is_ascii_lowercase() || b.is_ascii_digit() || matches!(b, b'.' | b'_' | b'-')
    })
}

fn normalize_token(
    value: &str,
    field: &'static str,
) -> Result<SourceIdentityComponent, ContractError> {
    let raw = require_raw(value, field, 128)?;
    if !raw.is_ascii() {
        return Err(ContractError::InvalidIdentityComponent {
            field,
            reason: "token_non_ascii",
        });
    }
    let normalized = raw.to_ascii_lowercase();
    if !token_valid(&normalized) {
        return Err(ContractError::InvalidIdentityComponent {
            field,
            reason: "token_invalid",
        });
    }
    Ok(SourceIdentityComponent { raw, normalized })
}

fn normalize_component(
    value: &str,
    field: &'static str,
    policy: &IdentityComponentPolicy,
) -> Result<SourceIdentityComponent, ContractError> {
    let raw = require_raw(value, field, policy.max_length)?;
    let mut normalized = match policy.unicode_normalization {
        UnicodeNormalization::Nfc => raw.nfc().collect::<String>(),
        UnicodeNormalization::None => raw.clone(),
    };
    if !policy.case_sensitive {
        if !normalized.is_ascii() {
            return Err(ContractError::InvalidIdentityComponent {
                field,
                reason: "non_ascii_case_fold_unsupported",
            });
        }
        normalized.make_ascii_lowercase();
    }
    Ok(SourceIdentityComponent { raw, normalized })
}

pub fn strict_source_identity_policy(
    provider: &str,
) -> Result<SourceIdentityPolicy, ContractError> {
    let provider_token = normalize_token(provider, "provider")?.normalized;
    let strict = IdentityComponentPolicy {
        case_sensitive: true,
        unicode_normalization: UnicodeNormalization::Nfc,
        max_length: 1024,
    };
    Ok(SourceIdentityPolicy {
        normalization_profile_id: format!("acm-source-key-v1:{provider_token}:strict"),
        provider: provider_token,
        account_id: IdentityComponentPolicy {
            max_length: 256,
            ..strict.clone()
        },
        workspace_id: IdentityComponentPolicy {
            max_length: 256,
            ..strict.clone()
        },
        external_id: strict,
    })
}

pub fn normalize_source_identity_key(
    input: &SourceIdentityKeyInput,
    policy: &SourceIdentityPolicy,
) -> Result<NormalizedSourceIdentityKey, ContractError> {
    let provider = normalize_token(&input.provider, "provider")?;
    let expected_provider = normalize_token(&policy.provider, "policy.provider")?.normalized;
    if provider.normalized != expected_provider {
        return Err(ContractError::InvalidIdentityComponent {
            field: "provider",
            reason: "policy_mismatch",
        });
    }
    let profile = require_raw(
        &policy.normalization_profile_id,
        "normalization_profile_id",
        128,
    )?;
    Ok(NormalizedSourceIdentityKey {
        schema_version: "1.0.0".into(),
        normalization_profile_id: profile,
        provider,
        account_id: normalize_component(&input.account_id, "account_id", &policy.account_id)?,
        workspace_id: input
            .workspace_id
            .as_deref()
            .map(|value| normalize_component(value, "workspace_id", &policy.workspace_id))
            .transpose()?,
        resource_type: normalize_token(&input.resource_type, "resource_type")?,
        external_id: normalize_component(&input.external_id, "external_id", &policy.external_id)?,
    })
}

pub fn derive_source_record_id(
    key: &NormalizedSourceIdentityKey,
) -> Result<SourceRecordId, ContractError> {
    let material = json!({
        "domain": "rot.acm.source-record-id",
        "version": "1",
        "key": {
            "schema_version": key.schema_version.as_str(),
            "normalization_profile_id": key.normalization_profile_id.as_str(),
            "provider": key.provider.normalized.as_str(),
            "account_id": key.account_id.normalized.as_str(),
            "workspace_id": key.workspace_id.as_ref().map(|v| v.normalized.as_str()),
            "resource_type": key.resource_type.normalized.as_str(),
            "external_id": key.external_id.normalized.as_str(),
        }
    });
    let hash = canonical_sha256(&material)?;
    Ok(SourceRecordId::from_digest(
        hash.trim_start_matches("sha256:"),
    ))
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ScopeClass {
    Tenant,
    Workspace,
    Global,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CanonicalEntityCreationCommand {
    pub entity_type_uri: String,
    pub tenant_id: String,
    pub scope_class: ScopeClass,
    pub creation_nonce: String,
}

pub fn derive_canonical_entity_id(
    command: &CanonicalEntityCreationCommand,
) -> Result<CanonicalEntityId, ContractError> {
    if !command.entity_type_uri.starts_with("rot://type/")
        || command.entity_type_uri.len() == "rot://type/".len()
    {
        return Err(ContractError::InvalidIdentifier(
            command.entity_type_uri.clone(),
        ));
    }
    if command.tenant_id.is_empty() || command.tenant_id.trim() != command.tenant_id {
        return Err(ContractError::InvalidIdentifier(command.tenant_id.clone()));
    }
    if command.creation_nonce.is_empty() || command.creation_nonce.trim() != command.creation_nonce {
        return Err(ContractError::InvalidIdentifier(
            command.creation_nonce.clone(),
        ));
    }
    let material = json!({
        "domain": "rot.acm.canonical-entity-id",
        "version": "1",
        "entity_type_uri": command.entity_type_uri.as_str(),
        "tenant_id": command.tenant_id.as_str(),
        "scope_class": command.scope_class,
        "creation_nonce": command.creation_nonce.as_str(),
    });
    let hash = canonical_sha256(&material)?;
    Ok(CanonicalEntityId::from_digest(
        hash.trim_start_matches("sha256:"),
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn source_input(external_id: &str) -> SourceIdentityKeyInput {
        SourceIdentityKeyInput {
            provider: "github".into(),
            account_id: "acct".into(),
            workspace_id: Some("workspace".into()),
            resource_type: "repository".into(),
            external_id: external_id.into(),
        }
    }

    #[test]
    fn source_identity_is_provider_scoped_and_case_sensitive_by_default() {
        let policy = strict_source_identity_policy("GitHub").unwrap();
        let upper = normalize_source_identity_key(&source_input("ABC"), &policy).unwrap();
        let lower = normalize_source_identity_key(&source_input("abc"), &policy).unwrap();
        assert_ne!(
            derive_source_record_id(&upper).unwrap(),
            derive_source_record_id(&lower).unwrap()
        );
    }

    #[test]
    fn nfc_normalization_converges_equivalent_external_ids() {
        let policy = strict_source_identity_policy("github").unwrap();
        let a = normalize_source_identity_key(
            &SourceIdentityKeyInput {
                provider: "github".into(),
                account_id: "acct".into(),
                workspace_id: None,
                resource_type: "issue".into(),
                external_id: "e\u{301}".into(),
            },
            &policy,
        )
        .unwrap();
        let b = normalize_source_identity_key(
            &SourceIdentityKeyInput {
                provider: "github".into(),
                account_id: "acct".into(),
                workspace_id: None,
                resource_type: "issue".into(),
                external_id: "é".into(),
            },
            &policy,
        )
        .unwrap();
        assert_eq!(a.external_id.normalized, b.external_id.normalized);
        assert_eq!(
            derive_source_record_id(&a).unwrap(),
            derive_source_record_id(&b).unwrap()
        );
    }

    #[test]
    fn rejects_whitespace_and_non_ascii_casefold_policy() {
        let mut policy = strict_source_identity_policy("github").unwrap();
        assert!(
            normalize_source_identity_key(
                &SourceIdentityKeyInput {
                    provider: "github".into(),
                    account_id: " acct".into(),
                    workspace_id: None,
                    resource_type: "issue".into(),
                    external_id: "1".into(),
                },
                &policy
            )
            .is_err()
        );
        policy.external_id.case_sensitive = false;
        assert!(
            normalize_source_identity_key(
                &SourceIdentityKeyInput {
                    provider: "github".into(),
                    account_id: "acct".into(),
                    workspace_id: None,
                    resource_type: "issue".into(),
                    external_id: "é".into(),
                },
                &policy
            )
            .is_err()
        );
    }

    #[test]
    fn digest_ids_reject_invalid_shape() {
        assert!(CanonicalEntityId::parse("rot:entity:sha256:ABC").is_err());
        assert!(SourceRecordId::parse(format!(
            "rot:source:sha256:{}",
            "a".repeat(64)
        ))
        .is_ok());
    }

    #[test]
    fn event_id_round_trip_uses_cp03_versioned_prefix() {
        let id = EventId::new();
        assert_eq!(EventId::parse(id.as_str()).unwrap(), id);
    }
}
