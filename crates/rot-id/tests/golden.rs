use rot_id::{
    CanonicalEntityCreationCommand, ScopeClass, SourceIdentityKeyInput, derive_canonical_entity_id,
    derive_source_record_id, normalize_source_identity_key, strict_source_identity_policy,
};
use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct Fixture {
    source_vectors: Vec<SourceVector>,
    entity_vectors: Vec<EntityVector>,
}

#[derive(Debug, Deserialize)]
struct SourceVector {
    name: String,
    input: SourceIdentityKeyInput,
    expected: ExpectedSource,
}

#[derive(Debug, Deserialize)]
struct ExpectedSource {
    schema_version: String,
    normalization_profile_id: String,
    provider: String,
    account_id: String,
    workspace_id: Option<String>,
    resource_type: String,
    external_id: String,
    source_record_id: String,
}

#[derive(Debug, Deserialize)]
struct EntityVector {
    name: String,
    command: EntityCommandFixture,
    expected_entity_id: String,
}

#[derive(Debug, Deserialize)]
struct EntityCommandFixture {
    entity_type_uri: String,
    tenant_id: String,
    scope_class: ScopeClass,
    creation_nonce: String,
}

#[test]
fn cp02_identity_goldens_are_stable() {
    let fixture: Fixture = serde_json::from_str(include_str!("../../../fixtures/golden/identity.v1.json")).unwrap();

    for vector in fixture.source_vectors {
        let policy = strict_source_identity_policy(&vector.input.provider).unwrap();
        let normalized = normalize_source_identity_key(&vector.input, &policy).unwrap();
        assert_eq!(normalized.schema_version, vector.expected.schema_version, "{}", vector.name);
        assert_eq!(normalized.normalization_profile_id, vector.expected.normalization_profile_id, "{}", vector.name);
        assert_eq!(normalized.provider.normalized, vector.expected.provider, "{}", vector.name);
        assert_eq!(normalized.account_id.normalized, vector.expected.account_id, "{}", vector.name);
        assert_eq!(normalized.workspace_id.as_ref().map(|v| v.normalized.clone()), vector.expected.workspace_id, "{}", vector.name);
        assert_eq!(normalized.resource_type.normalized, vector.expected.resource_type, "{}", vector.name);
        assert_eq!(normalized.external_id.normalized, vector.expected.external_id, "{}", vector.name);
        assert_eq!(derive_source_record_id(&normalized).unwrap().as_str(), vector.expected.source_record_id, "{}", vector.name);
    }

    for vector in fixture.entity_vectors {
        let command = CanonicalEntityCreationCommand {
            entity_type_uri: vector.command.entity_type_uri,
            tenant_id: vector.command.tenant_id,
            scope_class: vector.command.scope_class,
            creation_nonce: vector.command.creation_nonce,
        };
        assert_eq!(derive_canonical_entity_id(&command).unwrap().as_str(), vector.expected_entity_id, "{}", vector.name);
    }
}
